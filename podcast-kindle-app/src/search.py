"""
Podcast search module using free APIs
"""

import os
import requests
import hashlib
import time
import logging
from datetime import datetime
from src.utils import retry_on_failure, is_english_podcast, clean_html, truncate_text

logger = logging.getLogger(__name__)


class PodcastSearcher:
    """
    Handles podcast search across multiple free APIs
    """

    def __init__(self):
        self.podcast_index_key = os.getenv('PODCAST_INDEX_KEY')
        self.podcast_index_secret = os.getenv('PODCAST_INDEX_SECRET')
        self.listen_notes_key = os.getenv('LISTEN_NOTES_KEY')

    @retry_on_failure(max_retries=3)
    def search_itunes(self, query, limit=20):
        """
        Search podcasts using iTunes Search API (completely free)
        """
        try:
            url = "https://itunes.apple.com/search"
            params = {
                'term': query,
                'media': 'podcast',
                'entity': 'podcast',
                'limit': limit,
                'lang': 'en_us'
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('results', []):
                # Filter to ensure English podcasts
                if not is_english_podcast(item.get('collectionName', ''),
                                         item.get('description', '')):
                    continue

                podcast = {
                    'id': str(item.get('collectionId')),
                    'title': item.get('collectionName'),
                    'author': item.get('artistName'),
                    'description': clean_html(item.get('description', '')),
                    'image_url': item.get('artworkUrl600', item.get('artworkUrl100')),
                    'feed_url': item.get('feedUrl'),
                    'genre': item.get('primaryGenreName'),
                    'source': 'itunes'
                }
                results.append(podcast)

            logger.info(f"iTunes search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"iTunes search error: {str(e)}")
            return []

    @retry_on_failure(max_retries=3)
    def search_podcast_index(self, query, limit=20):
        """
        Search podcasts using Podcast Index API (free with registration)
        """
        if not self.podcast_index_key or not self.podcast_index_secret:
            logger.warning("Podcast Index API credentials not configured")
            return []

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

            url = "https://api.podcastindex.org/api/1.0/search/byterm"
            params = {
                'q': query,
                'max': limit,
                'clean': ''  # No explicit content
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('feeds', []):
                # Filter English podcasts
                if item.get('language') and not item.get('language').startswith('en'):
                    continue

                podcast = {
                    'id': str(item.get('id')),
                    'title': item.get('title'),
                    'author': item.get('author'),
                    'description': clean_html(item.get('description', '')),
                    'image_url': item.get('image') or item.get('artwork'),
                    'feed_url': item.get('url'),
                    'genre': ', '.join(item.get('categories', {}).values()) if item.get('categories') else None,
                    'has_transcripts': item.get('newestItemPublishTime', 0) > 0,  # Heuristic
                    'source': 'podcastindex'
                }
                results.append(podcast)

            logger.info(f"Podcast Index search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Podcast Index search error: {str(e)}")
            return []

    @retry_on_failure(max_retries=3)
    def search_listen_notes(self, query, limit=10):
        """
        Search podcasts using Listen Notes API (optional, free tier limited)
        """
        if not self.listen_notes_key:
            logger.warning("Listen Notes API key not configured")
            return []

        try:
            url = "https://listen-api.listennotes.com/api/v2/search"
            headers = {
                'X-ListenAPI-Key': self.listen_notes_key
            }
            params = {
                'q': query,
                'type': 'podcast',
                'language': 'English',
                'only_in': 'title,description',
                'len_min': 10
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('results', [])[:limit]:
                podcast = {
                    'id': item.get('id'),
                    'title': item.get('title_original'),
                    'author': item.get('publisher_original'),
                    'description': clean_html(item.get('description_original', '')),
                    'image_url': item.get('image'),
                    'feed_url': item.get('rss'),
                    'genre': item.get('genre_ids'),
                    'source': 'listennotes'
                }
                results.append(podcast)

            logger.info(f"Listen Notes search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Listen Notes search error: {str(e)}")
            return []

    def search(self, query, max_results=20):
        """
        Search podcasts across all available APIs and combine results
        """
        all_results = []

        # Try all APIs
        itunes_results = self.search_itunes(query, limit=max_results)
        all_results.extend(itunes_results)

        podcast_index_results = self.search_podcast_index(query, limit=max_results)
        all_results.extend(podcast_index_results)

        # Listen Notes is optional and has lower limits
        if self.listen_notes_key:
            listen_notes_results = self.search_listen_notes(query, limit=10)
            all_results.extend(listen_notes_results)

        # Remove duplicates based on title similarity
        unique_results = self._deduplicate_results(all_results)

        # Sort by relevance (simple heuristic: title match)
        query_lower = query.lower()
        unique_results.sort(
            key=lambda x: query_lower in x.get('title', '').lower(),
            reverse=True
        )

        return unique_results[:max_results]

    def _deduplicate_results(self, results):
        """
        Remove duplicate podcasts based on title similarity
        """
        seen_titles = set()
        unique_results = []

        for result in results:
            title_normalized = result.get('title', '').lower().strip()

            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                unique_results.append(result)

        return unique_results

    @retry_on_failure(max_retries=3)
    def get_episodes(self, feed_url, limit=50):
        """
        Get episodes from a podcast RSS feed
        """
        import feedparser

        try:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                logger.warning(f"No episodes found in feed: {feed_url}")
                return []

            episodes = []

            for entry in feed.entries[:limit]:
                # Extract episode information
                episode = {
                    'title': entry.get('title', 'Untitled'),
                    'description': clean_html(entry.get('summary', '')),
                    'published': entry.get('published', ''),
                    'duration': self._parse_duration(entry),
                    'audio_url': self._get_audio_url(entry),
                    'guid': entry.get('id', entry.get('link', '')),
                    'link': entry.get('link', '')
                }

                episodes.append(episode)

            logger.info(f"Retrieved {len(episodes)} episodes from feed")
            return episodes

        except Exception as e:
            logger.error(f"Error getting episodes from feed: {str(e)}")
            return []

    def _parse_duration(self, entry):
        """
        Parse episode duration from various RSS formats
        """
        # Try itunes:duration
        if hasattr(entry, 'itunes_duration'):
            duration_str = entry.itunes_duration

            # Format: HH:MM:SS or MM:SS or just seconds
            parts = duration_str.split(':')

            try:
                if len(parts) == 3:
                    hours, minutes, seconds = map(int, parts)
                    return hours * 3600 + minutes * 60 + seconds
                elif len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    return minutes * 60 + seconds
                else:
                    return int(duration_str)
            except ValueError:
                pass

        # Try other duration fields
        for key in ['duration', 'enclosure_length']:
            if hasattr(entry, key):
                try:
                    return int(getattr(entry, key))
                except (ValueError, TypeError):
                    pass

        return None

    def _get_audio_url(self, entry):
        """
        Extract audio URL from RSS entry
        """
        # Check enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if 'audio' in enclosure.get('type', ''):
                    return enclosure.get('href')

        # Check links
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('audio'):
                    return link.get('href')

        return entry.get('link', '')


def get_quick_filters():
    """
    Return preset quick filter keywords for common podcast topics
    """
    return [
        {'label': 'Persuasion', 'query': 'persuasion influence'},
        {'label': 'Sales', 'query': 'sales tactics techniques'},
        {'label': 'Psychology', 'query': 'psychology behavior mind'},
        {'label': 'Business', 'query': 'business entrepreneurship'},
        {'label': 'Motivation', 'query': 'motivation success mindset'},
        {'label': 'Communication', 'query': 'communication skills speaking'}
    ]
