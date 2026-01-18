"""
Utility functions for the Podcast to Kindle application
"""

import os
import hashlib
import time
import logging
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=3, backoff_base=2):
    """
    Decorator to retry a function on failure with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    wait_time = backoff_base ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


def sanitize_filename(filename):
    """
    Sanitize a filename to be safe for filesystem
    """
    # Replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length
    max_length = 200
    if len(filename) > max_length:
        filename = filename[:max_length]

    return filename.strip()


def generate_file_hash(text):
    """
    Generate a unique hash for a text
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def format_duration(seconds):
    """
    Format duration in seconds to human readable format
    """
    if not seconds:
        return "Unknown"

    minutes = int(seconds / 60)
    hours = int(minutes / 60)

    if hours > 0:
        return f"{hours}h {minutes % 60}min"
    else:
        return f"{minutes}min"


def is_english_podcast(title, description):
    """
    Simple heuristic to check if a podcast is in English
    Most non-English podcasts have special characters or patterns
    """
    # This is a simple check - in production you might want to use langdetect
    common_english_words = ['the', 'and', 'with', 'for', 'how', 'what', 'this', 'that']

    text = f"{title} {description}".lower()

    # Count English words
    english_word_count = sum(1 for word in common_english_words if word in text)

    # If we find at least 2 common English words, likely English
    return english_word_count >= 2


def clean_html(text):
    """
    Remove HTML tags from text
    """
    from bs4 import BeautifulSoup

    if not text:
        return ""

    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


def truncate_text(text, max_length=200):
    """
    Truncate text to a maximum length with ellipsis
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(' ', 1)[0] + '...'


def cleanup_old_files(directory, max_age_hours=24):
    """
    Clean up files older than max_age_hours
    """
    try:
        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)

        for filename in os.listdir(directory):
            if filename == '.gitkeep':
                continue

            filepath = os.path.join(directory, filename)

            # Check if file is older than cutoff
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))

            if file_modified < cutoff:
                os.remove(filepath)
                logger.info(f"Cleaned up old file: {filename}")

    except Exception as e:
        logger.error(f"Error cleaning up files: {str(e)}")


def validate_url(url):
    """
    Validate if a string is a valid URL
    """
    import re

    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return url_pattern.match(url) is not None
