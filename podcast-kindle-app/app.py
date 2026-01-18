"""
Podcast to Kindle - Flask Application
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.search import PodcastSearcher, get_quick_filters
from src.transcript import TranscriptRetriever
from src.transform import TranscriptTransformer
from src.ebook import EbookGenerator
from src.utils import cleanup_old_files, format_duration, truncate_text

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
MAX_EPISODES_PER_SESSION = int(os.getenv('MAX_EPISODES_PER_SESSION', 5))
CACHE_DURATION_HOURS = int(os.getenv('CACHE_DURATION_HOURS', 24))
DOWNLOADS_DIR = 'downloads'

# Initialize modules
podcast_searcher = PodcastSearcher()
transcript_retriever = TranscriptRetriever()
transcript_transformer = TranscriptTransformer()
ebook_generator = EbookGenerator(output_dir=DOWNLOADS_DIR)


@app.before_request
def before_request():
    """
    Initialize session variables
    """
    if 'processed_count' not in session:
        session['processed_count'] = 0


@app.route('/')
def index():
    """
    Home page - Podcast search
    """
    quick_filters = get_quick_filters()
    return render_template('index.html', quick_filters=quick_filters)


@app.route('/api/search', methods=['POST'])
def search_podcasts():
    """
    API endpoint to search podcasts
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({'error': 'Search query is required'}), 400

        logger.info(f"Searching for podcasts: {query}")

        # Search podcasts
        results = podcast_searcher.search(query, max_results=20)

        # Format results for frontend
        formatted_results = []
        for podcast in results:
            formatted_results.append({
                'id': podcast.get('id'),
                'title': podcast.get('title'),
                'author': podcast.get('author'),
                'description': truncate_text(podcast.get('description', ''), max_length=200),
                'image_url': podcast.get('image_url'),
                'feed_url': podcast.get('feed_url'),
                'genre': podcast.get('genre'),
                'source': podcast.get('source')
            })

        return jsonify({
            'success': True,
            'results': formatted_results,
            'count': len(formatted_results)
        })

    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({'error': 'Search failed. Please try again.'}), 500


@app.route('/api/episodes', methods=['POST'])
def get_episodes():
    """
    API endpoint to get episodes for a podcast with transcript availability
    """
    try:
        data = request.get_json()
        feed_url = data.get('feed_url')
        podcast_info = data.get('podcast_info', {})

        if not feed_url:
            return jsonify({'error': 'Feed URL is required'}), 400

        logger.info(f"Getting episodes for feed: {feed_url}")

        # Get episodes from feed
        episodes = podcast_searcher.get_episodes(feed_url, limit=50)

        if not episodes:
            return jsonify({'error': 'No episodes found'}), 404

        # Check transcript availability for each episode
        episodes_with_transcripts = transcript_retriever.batch_check_episodes(episodes)

        # Format results
        formatted_episodes = []
        for episode in episodes_with_transcripts:
            formatted_episodes.append({
                'title': episode.get('title'),
                'description': truncate_text(episode.get('description', ''), max_length=150),
                'published': episode.get('published'),
                'duration': format_duration(episode.get('duration')),
                'duration_seconds': episode.get('duration'),
                'has_transcript': episode.get('has_transcript'),
                'transcript_source': episode.get('transcript_source'),
                'transcript_data': episode.get('transcript_data'),
                'guid': episode.get('guid'),
                'link': episode.get('link')
            })

        # Store podcast info in session for later use
        session['podcast_info'] = podcast_info

        return jsonify({
            'success': True,
            'episodes': formatted_episodes,
            'total_count': len(episodes),
            'with_transcripts': len(formatted_episodes)
        })

    except Exception as e:
        logger.error(f"Error getting episodes: {str(e)}")
        return jsonify({'error': 'Failed to retrieve episodes. Please try again.'}), 500


@app.route('/api/process', methods=['POST'])
def process_episodes():
    """
    API endpoint to process selected episodes and generate preview
    """
    try:
        # Check rate limiting
        if session.get('processed_count', 0) >= MAX_EPISODES_PER_SESSION:
            return jsonify({
                'error': f'Session limit reached. Maximum {MAX_EPISODES_PER_SESSION} episodes per session.'
            }), 429

        data = request.get_json()
        selected_episodes = data.get('episodes', [])

        if not selected_episodes:
            return jsonify({'error': 'No episodes selected'}), 400

        if len(selected_episodes) > MAX_EPISODES_PER_SESSION:
            return jsonify({
                'error': f'Too many episodes. Maximum {MAX_EPISODES_PER_SESSION} episodes allowed.'
            }), 400

        podcast_info = session.get('podcast_info', {})

        processed_episodes = []

        for episode_data in selected_episodes:
            try:
                # Get transcript
                transcript = transcript_retriever.get_transcript(
                    episode_data,
                    episode_data.get('transcript_source'),
                    episode_data.get('transcript_data')
                )

                if not transcript:
                    logger.warning(f"No transcript available for: {episode_data.get('title')}")
                    continue

                # Prepare episode info for transformation
                episode_info = {
                    'title': episode_data.get('title'),
                    'author': podcast_info.get('author', 'Unknown Host'),
                    'podcast_name': podcast_info.get('title', 'Unknown Podcast'),
                    'published': episode_data.get('published'),
                    'guid': episode_data.get('guid')
                }

                # Transform transcript to narrative
                markdown_content = transcript_transformer.transform(transcript, episode_info)

                processed_episodes.append({
                    'episode_info': episode_info,
                    'markdown_content': markdown_content,
                    'cover_image_url': podcast_info.get('image_url')
                })

                # Increment processed count
                session['processed_count'] = session.get('processed_count', 0) + 1

            except Exception as e:
                logger.error(f"Error processing episode: {str(e)}")
                continue

        if not processed_episodes:
            return jsonify({'error': 'Failed to process any episodes'}), 500

        # Store processed episodes in session for download
        session['processed_episodes'] = processed_episodes

        # Return preview (first episode or combined)
        preview_content = processed_episodes[0]['markdown_content']

        return jsonify({
            'success': True,
            'preview': preview_content,
            'episode_count': len(processed_episodes),
            'remaining_quota': MAX_EPISODES_PER_SESSION - session.get('processed_count', 0)
        })

    except Exception as e:
        logger.error(f"Error processing episodes: {str(e)}")
        return jsonify({'error': 'Processing failed. Please try again.'}), 500


@app.route('/api/download', methods=['POST'])
def download_ebook():
    """
    API endpoint to generate and download ebook
    """
    try:
        data = request.get_json()
        format_type = data.get('format', 'epub')

        if format_type not in ['epub', 'pdf']:
            return jsonify({'error': 'Invalid format. Use "epub" or "pdf"'}), 400

        processed_episodes = session.get('processed_episodes')

        if not processed_episodes:
            return jsonify({'error': 'No processed episodes found'}), 400

        # Generate ebook
        if format_type == 'epub':
            filepaths = ebook_generator.batch_generate(processed_episodes, format='epub')
        else:
            filepaths = ebook_generator.batch_generate(processed_episodes, format='pdf')

        if not filepaths:
            return jsonify({'error': 'Failed to generate ebook'}), 500

        # For simplicity, return first file (could zip multiple files)
        filepath = filepaths[0]

        # Return file info for download
        return jsonify({
            'success': True,
            'filename': os.path.basename(filepath),
            'download_url': f'/download/{os.path.basename(filepath)}'
        })

    except Exception as e:
        logger.error(f"Error generating download: {str(e)}")
        return jsonify({'error': 'Download generation failed. Please try again.'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """
    Serve download file
    """
    try:
        filepath = os.path.join(DOWNLOADS_DIR, filename)

        if not os.path.exists(filepath):
            return "File not found", 404

        # Determine mimetype
        if filename.endswith('.epub'):
            mimetype = 'application/epub+zip'
        elif filename.endswith('.pdf'):
            mimetype = 'application/pdf'
        else:
            mimetype = 'text/html'

        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        logger.error(f"Error serving download: {str(e)}")
        return "Download failed", 500


@app.route('/api/stats')
def get_stats():
    """
    Get session statistics
    """
    return jsonify({
        'processed_count': session.get('processed_count', 0),
        'remaining_quota': MAX_EPISODES_PER_SESSION - session.get('processed_count', 0)
    })


@app.errorhandler(404)
def not_found(e):
    """
    404 error handler
    """
    return render_template('index.html'), 404


@app.errorhandler(500)
def server_error(e):
    """
    500 error handler
    """
    logger.error(f"Server error: {str(e)}")
    return "Internal server error", 500


# Cleanup old files on startup
@app.before_first_request
def startup_cleanup():
    """
    Clean up old files on application startup
    """
    logger.info("Starting application and cleaning up old files")
    cleanup_old_files(DOWNLOADS_DIR, max_age_hours=CACHE_DURATION_HOURS)


if __name__ == '__main__':
    # Development server
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') != 'production')
