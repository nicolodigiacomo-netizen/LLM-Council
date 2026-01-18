"""
EPUB and PDF generation module for Kindle
"""

import os
import logging
import markdown
import requests
from io import BytesIO
from ebooklib import epub
from datetime import datetime
from PIL import Image
from src.utils import sanitize_filename

logger = logging.getLogger(__name__)


class EbookGenerator:
    """
    Generates EPUB and PDF files optimized for Kindle
    """

    def __init__(self, output_dir='downloads'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_epub(self, markdown_content, episode_info, cover_image_url=None):
        """
        Generate an EPUB file from markdown content
        """
        try:
            # Create EPUB book
            book = epub.EpubBook()

            # Set metadata
            title = episode_info.get('title', 'Untitled Episode')
            author = episode_info.get('author', 'Unknown Author')
            podcast_name = episode_info.get('podcast_name', 'Unknown Podcast')

            book.set_identifier(f"podcast-{episode_info.get('guid', 'unknown')}")
            book.set_title(title)
            book.set_language('en')
            book.add_author(author)

            # Add cover image if available
            if cover_image_url:
                try:
                    cover_image = self._download_cover_image(cover_image_url)
                    if cover_image:
                        book.set_cover('cover.jpg', cover_image)
                except Exception as e:
                    logger.warning(f"Could not add cover image: {str(e)}")

            # Convert markdown to HTML
            html_content = self._markdown_to_html(markdown_content)

            # Create chapter
            chapter = epub.EpubHtml(
                title=title,
                file_name='chapter_1.xhtml',
                lang='en'
            )
            chapter.content = html_content

            # Add chapter to book
            book.add_item(chapter)

            # Define Table of Contents
            book.toc = (epub.Link('chapter_1.xhtml', title, 'chapter_1'),)

            # Add navigation files
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # Define CSS style
            style = self._get_kindle_css()
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=style
            )
            book.add_item(nav_css)

            # Create spine
            book.spine = ['nav', chapter]

            # Generate filename
            safe_title = sanitize_filename(title)
            filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d')}.epub"
            filepath = os.path.join(self.output_dir, filename)

            # Write EPUB file
            epub.write_epub(filepath, book)

            logger.info(f"Generated EPUB file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating EPUB: {str(e)}")
            raise

    def _download_cover_image(self, image_url):
        """
        Download and process cover image
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Open image with PIL
            img = Image.open(BytesIO(response.content))

            # Resize if too large (Kindle optimal: 1600x2560 or 800x1280)
            max_width = 800
            max_height = 1280

            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Save to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            return output.getvalue()

        except Exception as e:
            logger.warning(f"Error downloading cover image: {str(e)}")
            return None

    def _markdown_to_html(self, markdown_content):
        """
        Convert markdown to HTML with proper formatting
        """
        # Configure markdown extensions
        extensions = ['extra', 'smarty', 'meta', 'toc']

        html = markdown.markdown(markdown_content, extensions=extensions)

        # Wrap in proper HTML structure
        html_template = f"""
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
        <head>
            <meta charset="UTF-8"/>
            <title>Podcast Episode</title>
            <link rel="stylesheet" href="style/nav.css" type="text/css"/>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

        return html_template

    def _get_kindle_css(self):
        """
        Return CSS optimized for Kindle reading
        """
        return """
        body {
            font-family: "Georgia", "Times New Roman", serif;
            font-size: 1em;
            line-height: 1.6;
            margin: 1em;
            text-align: justify;
        }

        h1 {
            font-size: 2em;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
            text-align: left;
            page-break-before: always;
        }

        h2 {
            font-size: 1.5em;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            text-align: left;
        }

        h3 {
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }

        p {
            margin: 0.5em 0;
            text-indent: 1.5em;
        }

        p:first-of-type {
            text-indent: 0;
        }

        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }

        li {
            margin: 0.5em 0;
        }

        hr {
            border: none;
            border-top: 1px solid #ccc;
            margin: 2em 0;
        }

        em {
            font-style: italic;
        }

        strong {
            font-weight: bold;
        }

        blockquote {
            margin: 1em 2em;
            padding-left: 1em;
            border-left: 3px solid #ccc;
            font-style: italic;
        }

        code {
            font-family: "Courier New", monospace;
            background-color: #f4f4f4;
            padding: 0.2em 0.4em;
        }

        pre {
            background-color: #f4f4f4;
            padding: 1em;
            overflow-x: auto;
        }
        """

    def generate_pdf(self, markdown_content, episode_info):
        """
        Generate a PDF file from markdown content (simplified version)
        For production use, consider using WeasyPrint or ReportLab
        """
        try:
            # Convert markdown to HTML
            html_content = self._markdown_to_html(markdown_content)

            # Generate filename
            title = episode_info.get('title', 'Untitled Episode')
            safe_title = sanitize_filename(title)
            filename = f"{safe_title}_{datetime.now().strftime('%Y%m%d')}.html"
            filepath = os.path.join(self.output_dir, filename)

            # For now, save as HTML (can be converted to PDF by browser)
            # In production, use proper PDF library
            with open(filepath, 'w', encoding='utf-8') as f:
                # Add print-friendly CSS
                pdf_html = html_content.replace(
                    '<link rel="stylesheet" href="style/nav.css" type="text/css"/>',
                    f'<style>{self._get_pdf_css()}</style>'
                )
                f.write(pdf_html)

            logger.info(f"Generated HTML file for PDF conversion: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    def _get_pdf_css(self):
        """
        Return CSS optimized for PDF printing
        """
        return """
        @page {
            size: A4;
            margin: 2cm;
        }

        body {
            font-family: "Georgia", "Times New Roman", serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000;
        }

        h1 {
            font-size: 24pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
            page-break-before: always;
        }

        h1:first-of-type {
            page-break-before: avoid;
        }

        h2 {
            font-size: 18pt;
            font-weight: bold;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }

        h3 {
            font-size: 14pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }

        p {
            margin: 0.5em 0;
            text-align: justify;
        }

        ul, ol {
            margin: 1em 0;
            padding-left: 2em;
        }

        li {
            margin: 0.3em 0;
        }

        hr {
            border: none;
            border-top: 1px solid #000;
            margin: 2em 0;
        }

        @media print {
            body {
                margin: 0;
            }

            h1, h2, h3 {
                page-break-after: avoid;
            }

            p {
                orphans: 3;
                widows: 3;
            }
        }
        """

    def batch_generate(self, episodes_data, format='epub'):
        """
        Generate multiple ebook files from a batch of episodes
        """
        generated_files = []

        for episode_data in episodes_data:
            try:
                markdown_content = episode_data.get('markdown_content')
                episode_info = episode_data.get('episode_info')
                cover_image_url = episode_data.get('cover_image_url')

                if format == 'epub':
                    filepath = self.generate_epub(
                        markdown_content,
                        episode_info,
                        cover_image_url
                    )
                elif format == 'pdf':
                    filepath = self.generate_pdf(markdown_content, episode_info)
                else:
                    logger.error(f"Unsupported format: {format}")
                    continue

                generated_files.append(filepath)

            except Exception as e:
                logger.error(f"Error generating ebook for episode: {str(e)}")
                continue

        return generated_files
