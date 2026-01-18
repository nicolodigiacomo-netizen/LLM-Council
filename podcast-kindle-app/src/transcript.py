"""
Transcript retrieval module - focuses on free transcript sources
"""

import os
import re
import hashlib
import time
import logging
import requests
import feedparser
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from src.utils import retry_on_failure, clean_html

logger = logging.getLogger(__name__)


class TranscriptRetriever:
    """
    Retrieves transcripts from various free sources
    """

    def __init__(self):
        self.podcast_index_key = os.getenv('PODCAST_INDEX_KEY')
        self.podcast_index_secret = os.getenv('PODCAST_INDEX_SECRET')

    def check_transcript_availability(self, episode):
        """
        Check if an episode has a transcript available
        Returns: (has_transcript, source, transcript_data)
        """
        # Try different sources in order of reliability

        # 1. Check for YouTube URL
        youtube_id = self._extract_youtube_id(episode)
        if youtube_id:
            transcript = self.get_youtube_transcript(youtube_id)
            if transcript:
                return (True, 'youtube', {'youtube_id': youtube_id})

        # 2. Check RSS feed for embedded transcript
        if episode.get('link'):
            transcript = self._check_rss_transcript(episode)
            if transcript:
                return (True, 'rss', {'link': episode.get('link')})

        # 3. Check Podcast Index for transcript
        if self.podcast_index_key and episode.get('guid'):
            has_transcript = self._check_podcast_index_transcript(episode.get('guid'))
            if has_transcript:
                return (True, 'podcastindex', {'guid': episode.get('guid')})

        return (False, None, None)

    def get_transcript(self, episode, source, transcript_data):
        """
        Retrieve full transcript based on source
        """
        try:
            if source == 'youtube':
                youtube_id = transcript_data.get('youtube_id')
                return self.get_youtube_transcript(youtube_id)

            elif source == 'rss':
                link = transcript_data.get('link')
                return self._get_rss_transcript(link)

            elif source == 'podcastindex':
                guid = transcript_data.get('guid')
                return self._get_podcast_index_transcript(guid)

            return None

        except Exception as e:
            logger.error(f"Error retrieving transcript: {str(e)}")
            return None

    @retry_on_failure(max_retries=2)
    def get_youtube_transcript(self, youtube_id):
        """
        Get transcript from YouTube using youtube-transcript-api
        """
        try:
            # Try to get English transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(youtube_id)

            # Prefer manually created transcripts over auto-generated
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['en'])

            # Get the actual transcript
            transcript_data = transcript.fetch()

            # Combine all text segments
            full_text = ' '.join([item['text'] for item in transcript_data])

            logger.info(f"Retrieved YouTube transcript for {youtube_id}")
            return full_text

        except Exception as e:
            logger.warning(f"Could not get YouTube transcript for {youtube_id}: {str(e)}")
            return None

    def _extract_youtube_id(self, episode):
        """
        Extract YouTube video ID from episode data
        """
        # Check common fields for YouTube links
        fields_to_check = [
            episode.get('link', ''),
            episode.get('audio_url', ''),
            episode.get('description', '')
        ]

        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]

        for field in fields_to_check:
            if not field:
                continue

            for pattern in youtube_patterns:
                match = re.search(pattern, field)
                if match:
                    return match.group(1)

        return None

    def _check_rss_transcript(self, episode_link):
        """
        Check if episode page has transcript embedded
        """
        try:
            response = requests.get(episode_link, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for common transcript indicators
            transcript_indicators = [
                soup.find('div', class_=re.compile('transcript', re.I)),
                soup.find('div', id=re.compile('transcript', re.I)),
                soup.find('section', class_=re.compile('transcript', re.I)),
                soup.find('article', class_=re.compile('transcript', re.I))
            ]

            for indicator in transcript_indicators:
                if indicator and len(indicator.get_text(strip=True)) > 500:
                    return True

            return False

        except Exception as e:
            logger.warning(f"Error checking RSS transcript: {str(e)}")
            return False

    def _get_rss_transcript(self, episode_link):
        """
        Extract transcript from episode webpage
        """
        try:
            response = requests.get(episode_link, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to find transcript section
            transcript_section = (
                soup.find('div', class_=re.compile('transcript', re.I)) or
                soup.find('div', id=re.compile('transcript', re.I)) or
                soup.find('section', class_=re.compile('transcript', re.I)) or
                soup.find('article', class_=re.compile('transcript', re.I))
            )

            if transcript_section:
                # Clean and extract text
                transcript_text = transcript_section.get_text(separator='\n', strip=True)

                if len(transcript_text) > 500:  # Minimum length check
                    logger.info(f"Retrieved transcript from RSS for {episode_link}")
                    return transcript_text

            return None

        except Exception as e:
            logger.error(f"Error extracting RSS transcript: {str(e)}")
            return None

    def _check_podcast_index_transcript(self, episode_guid):
        """
        Check if Podcast Index has transcript for episode
        """
        if not self.podcast_index_key or not self.podcast_index_secret:
            return False

        try:
            # Generate authorization headers
            epoch_time = int(time.time())
            data_to_hash = self.podcast_index_key + self.podcast_index_secret + str(epoch_time)
            sha_1 = hashlib.sha1(data_to_hash.encode()).hexdigest()

            headers = {
                'X-Auth-Date': str(epoch_time),
                'X-Auth-Key': self.podcast_index_key,
                'Authorization': sha_1,
                'User-Agent': 'PodcastToKindle/1.0'
            }

            # Note: This is a placeholder - actual Podcast Index transcript API
            # endpoint may vary. Check documentation at https://podcastindex-org.github.io/docs-api/
            url = f"https://api.podcastindex.org/api/1.0/episodes/byguid"
            params = {'guid': episode_guid}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                episode_data = data.get('episode', {})
                # Check if transcript field exists and has content
                return bool(episode_data.get('transcriptUrl'))

            return False

        except Exception as e:
            logger.warning(f"Error checking Podcast Index transcript: {str(e)}")
            return False

    def _get_podcast_index_transcript(self, episode_guid):
        """
        Get transcript from Podcast Index
        """
        if not self.podcast_index_key or not self.podcast_index_secret:
            return None

        try:
            # Generate authorization headers
            epoch_time = int(time.time())
            data_to_hash = self.podcast_index_key + self.podcast_index_secret + str(epoch_time)
            sha_1 = hashlib.sha1(data_to_hash.encode()).hexdigest()

            headers = {
                'X-Auth-Date': str(epoch_time),
                'X-Auth-Key': self.podcast_index_key,
                'Authorization': sha_1,
                'User-Agent': 'PodcastToKindle/1.0'
            }

            # Get episode details with transcript URL
            url = f"https://api.podcastindex.org/api/1.0/episodes/byguid"
            params = {'guid': episode_guid}

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            episode_data = data.get('episode', {})
            transcript_url = episode_data.get('transcriptUrl')

            if transcript_url:
                # Fetch the transcript
                transcript_response = requests.get(transcript_url, timeout=10)
                transcript_response.raise_for_status()

                # Transcript might be in various formats (JSON, SRT, VTT, plain text)
                content_type = transcript_response.headers.get('Content-Type', '')

                if 'json' in content_type:
                    transcript_json = transcript_response.json()
                    # Extract text from JSON transcript format
                    return self._parse_json_transcript(transcript_json)
                else:
                    # Assume plain text or parse as needed
                    return transcript_response.text

            return None

        except Exception as e:
            logger.error(f"Error getting Podcast Index transcript: {str(e)}")
            return None

    def _parse_json_transcript(self, transcript_json):
        """
        Parse transcript from JSON format
        """
        try:
            # Common JSON transcript format has segments with text
            if isinstance(transcript_json, dict):
                segments = transcript_json.get('segments', [])
                if segments:
                    return ' '.join([seg.get('body', '') for seg in segments])

                # Alternative format
                if 'text' in transcript_json:
                    return transcript_json['text']

            elif isinstance(transcript_json, list):
                return ' '.join([seg.get('body', seg.get('text', '')) for seg in transcript_json])

            return str(transcript_json)

        except Exception as e:
            logger.error(f"Error parsing JSON transcript: {str(e)}")
            return None

    def batch_check_episodes(self, episodes):
        """
        Check transcript availability for multiple episodes
        Returns list of episodes with transcript info added
        """
        enriched_episodes = []

        for episode in episodes:
            has_transcript, source, transcript_data = self.check_transcript_availability(episode)

            episode_copy = episode.copy()
            episode_copy['has_transcript'] = has_transcript
            episode_copy['transcript_source'] = source
            episode_copy['transcript_data'] = transcript_data

            enriched_episodes.append(episode_copy)

        # Filter to only episodes with transcripts
        episodes_with_transcripts = [ep for ep in enriched_episodes if ep['has_transcript']]

        logger.info(f"Found {len(episodes_with_transcripts)} episodes with transcripts out of {len(episodes)}")

        return episodes_with_transcripts
