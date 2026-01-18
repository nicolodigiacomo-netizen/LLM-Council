"""
Transform podcast transcripts into narrative prose format
"""

import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TranscriptTransformer:
    """
    Transforms conversational transcripts into readable narrative prose
    """

    # Filler words to remove
    FILLER_WORDS = [
        r'\bum+\b', r'\buh+\b', r'\bah+\b', r'\beh+\b',
        r'\byou know\b', r'\bi mean\b', r'\blike\b(?! to| that)',
        r'\bkind of\b', r'\bsort of\b',
        r'\bbasically\b', r'\bliterally\b',
        r'\bright\??', r'\bokay\??',
        r'\bwell,?\b', r'\bso,?\b(?= )'
    ]

    # Meta-references to remove
    META_REFERENCES = [
        r'in this episode',
        r'on this podcast',
        r'as I mentioned (before|earlier)',
        r'like I said',
        r'as we discussed',
        r'we\'?re talking about',
        r'I\'?m going to talk about',
        r'today we\'?re',
        r'in today\'?s episode'
    ]

    # Timestamp patterns
    TIMESTAMP_PATTERNS = [
        r'\[\d{1,2}:\d{2}:\d{2}\]',  # [00:12:34]
        r'\d{1,2}:\d{2}:\d{2}',      # 00:12:34
        r'\[\d{1,2}:\d{2}\]',        # [12:34]
        r'\d{1,2}:\d{2}\s*[-–]\s*',  # 12:34 -
    ]

    def __init__(self):
        self.filler_pattern = re.compile('|'.join(self.FILLER_WORDS), re.IGNORECASE)
        self.meta_pattern = re.compile('|'.join(self.META_REFERENCES), re.IGNORECASE)
        self.timestamp_pattern = re.compile('|'.join(self.TIMESTAMP_PATTERNS))

    def transform(self, transcript, episode_info):
        """
        Main transformation function
        """
        try:
            # Step 1: Clean the transcript
            cleaned = self._clean_transcript(transcript)

            # Step 2: Remove filler words
            cleaned = self._remove_filler_words(cleaned)

            # Step 3: Remove meta-references
            cleaned = self._remove_meta_references(cleaned)

            # Step 4: Convert to narrative prose
            narrative = self._convert_to_narrative(cleaned)

            # Step 5: Organize into chapters
            chapters = self._organize_into_chapters(narrative)

            # Step 6: Extract key takeaways
            takeaways = self._extract_key_takeaways(narrative)

            # Step 7: Format final output
            formatted = self._format_output(
                chapters=chapters,
                takeaways=takeaways,
                episode_info=episode_info
            )

            logger.info(f"Successfully transformed transcript for episode: {episode_info.get('title')}")
            return formatted

        except Exception as e:
            logger.error(f"Error transforming transcript: {str(e)}")
            raise

    def _clean_transcript(self, transcript):
        """
        Basic cleaning of transcript text
        """
        # Remove timestamps
        cleaned = self.timestamp_pattern.sub('', transcript)

        # Remove speaker labels (e.g., "Speaker 1:", "Host:", etc.)
        cleaned = re.sub(r'^[A-Za-z\s]+\d*:\s*', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'\n[A-Za-z\s]+\d*:\s*', '\n', cleaned)

        # Remove multiple spaces
        cleaned = re.sub(r' {2,}', ' ', cleaned)

        # Remove multiple newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()

        return cleaned

    def _remove_filler_words(self, text):
        """
        Remove filler words and verbal tics
        """
        # Remove filler words
        text = self.filler_pattern.sub('', text)

        # Clean up punctuation after removal
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        text = re.sub(r'([,.!?])\s*([,.!?])', r'\1', text)

        # Remove multiple spaces
        text = re.sub(r' {2,}', ' ', text)

        return text

    def _remove_meta_references(self, text):
        """
        Remove meta-references to the podcast itself
        """
        text = self.meta_pattern.sub('', text)

        # Clean up resulting sentence fragments
        text = re.sub(r'\s+,', ',', text)
        text = re.sub(r',\s*\.', '.', text)

        return text

    def _convert_to_narrative(self, text):
        """
        Convert conversational text to narrative prose
        """
        # Split into sentences
        sentences = re.split(r'([.!?]+)', text)

        narrative_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i].strip()
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else '.'

            if not sentence:
                continue

            # Convert contractions to full forms for more formal tone
            sentence = self._expand_contractions(sentence)

            # Capitalize first letter
            if sentence:
                sentence = sentence[0].upper() + sentence[1:]

            narrative_sentences.append(sentence + punctuation)

        # Join sentences into paragraphs
        narrative = ' '.join(narrative_sentences)

        # Create paragraph breaks at natural points
        narrative = self._add_paragraph_breaks(narrative)

        return narrative

    def _expand_contractions(self, text):
        """
        Expand common contractions for more formal tone
        """
        contractions = {
            r"won't": "will not",
            r"can't": "cannot",
            r"n't": " not",
            r"'re": " are",
            r"'ve": " have",
            r"'ll": " will",
            r"'d": " would",
            r"'m": " am"
        }

        for contraction, expansion in contractions.items():
            text = re.sub(contraction, expansion, text, flags=re.IGNORECASE)

        return text

    def _add_paragraph_breaks(self, text):
        """
        Add paragraph breaks at natural transition points
        """
        # Split into sentences
        sentences = text.split('. ')

        # Group sentences into paragraphs (3-5 sentences per paragraph)
        paragraphs = []
        current_paragraph = []

        for i, sentence in enumerate(sentences):
            current_paragraph.append(sentence)

            # Check for natural break points
            is_transition = any(phrase in sentence.lower() for phrase in [
                'however', 'therefore', 'moreover', 'furthermore',
                'in contrast', 'on the other hand', 'another',
                'first', 'second', 'third', 'finally',
                'for example', 'for instance'
            ])

            # Create paragraph break
            if len(current_paragraph) >= 3 and (is_transition or len(current_paragraph) >= 5):
                paragraph_text = '. '.join(current_paragraph)
                if not paragraph_text.endswith('.'):
                    paragraph_text += '.'
                paragraphs.append(paragraph_text)
                current_paragraph = []

        # Add remaining sentences
        if current_paragraph:
            paragraph_text = '. '.join(current_paragraph)
            if not paragraph_text.endswith('.'):
                paragraph_text += '.'
            paragraphs.append(paragraph_text)

        return '\n\n'.join(paragraphs)

    def _organize_into_chapters(self, narrative):
        """
        Organize narrative into thematic chapters
        """
        # Split text into paragraphs
        paragraphs = [p.strip() for p in narrative.split('\n\n') if p.strip()]

        # Simple chapter organization (could be enhanced with NLP)
        # For now, create chapters every ~5-7 paragraphs
        chapters = []
        chapter_size = 6

        for i in range(0, len(paragraphs), chapter_size):
            chapter_paragraphs = paragraphs[i:i + chapter_size]

            # Generate a simple chapter title based on content
            chapter_num = len(chapters) + 1
            chapter_title = self._generate_chapter_title(chapter_paragraphs, chapter_num)

            chapters.append({
                'title': chapter_title,
                'content': '\n\n'.join(chapter_paragraphs)
            })

        return chapters

    def _generate_chapter_title(self, paragraphs, chapter_num):
        """
        Generate a simple chapter title based on content
        """
        # Simple approach: use first sentence keywords
        if not paragraphs:
            return f"Chapter {chapter_num}"

        first_paragraph = paragraphs[0]
        first_sentence = first_paragraph.split('.')[0]

        # Extract key nouns (simple heuristic - words that are capitalized or important)
        words = first_sentence.split()

        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                       'of', 'with', 'by', 'from', 'this', 'that', 'these', 'those', 'is',
                       'are', 'was', 'were', 'when', 'i', 'you', 'we', 'they'}

        key_words = [w for w in words if w.lower() not in common_words and len(w) > 3]

        if key_words:
            # Use first 3-4 key words
            title_words = key_words[:4]
            title = ' '.join(title_words).title()
            return f"Chapter {chapter_num}: {title}"
        else:
            return f"Chapter {chapter_num}"

    def _extract_key_takeaways(self, narrative):
        """
        Extract key takeaways from the narrative
        """
        # Look for sentences with actionable or important information
        sentences = [s.strip() for s in narrative.split('.') if s.strip()]

        # Indicators of important points
        importance_indicators = [
            'important', 'key', 'critical', 'essential', 'must',
            'should', 'need to', 'remember', 'always', 'never',
            'first', 'second', 'third', 'framework', 'strategy',
            'technique', 'method', 'approach', 'principle'
        ]

        takeaways = []

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Check if sentence contains importance indicators
            has_indicator = any(indicator in sentence_lower for indicator in importance_indicators)

            # Check if sentence is not too long
            is_concise = 10 < len(sentence.split()) < 30

            if has_indicator and is_concise:
                # Clean up and add to takeaways
                cleaned = sentence.strip()
                if cleaned and not cleaned.startswith(('However', 'Therefore', 'Moreover')):
                    takeaways.append(cleaned)

        # Limit to top 5-8 takeaways
        return takeaways[:8]

    def _format_output(self, chapters, takeaways, episode_info):
        """
        Format the final output in Markdown
        """
        output = []

        # Header
        title = episode_info.get('title', 'Untitled Episode')
        podcast_name = episode_info.get('podcast_name', 'Unknown Podcast')
        author = episode_info.get('author', 'Unknown Host')
        published = episode_info.get('published', '')

        output.append(f"# {title}\n")
        output.append(f"*Podcast: {podcast_name} | Host: {author}*")

        if published:
            try:
                # Try to format date nicely
                date_str = datetime.strptime(published[:10], '%Y-%m-%d').strftime('%B %d, %Y')
                output.append(f"*Published: {date_str}*")
            except:
                output.append(f"*Published: {published}*")

        output.append("\n---\n")

        # Chapters
        for chapter in chapters:
            output.append(f"## {chapter['title']}\n")
            output.append(f"{chapter['content']}\n")

        # Key Takeaways
        if takeaways:
            output.append("\n---\n")
            output.append("## Key Takeaways\n")

            for takeaway in takeaways:
                output.append(f"- {takeaway}")

            output.append("")

        return '\n'.join(output)
