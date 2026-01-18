"""
Email Digest Generator for Financial News Monitoring
Creates HTML email digest and sends via SMTP
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)


class DigestGenerator:
    """Generates HTML email digest from articles"""

    def __init__(self, asset_classes: Dict):
        """
        Initialize digest generator

        Args:
            asset_classes: Dictionary of asset class configurations
        """
        self.asset_classes = asset_classes

    def generate_html(self, articles: List[Dict], date: str = None) -> str:
        """
        Generate HTML digest from articles

        Args:
            articles: List of article dictionaries
            date: Date string for digest title

        Returns:
            HTML string
        """
        if date is None:
            date = datetime.now().strftime('%B %d, %Y')

        # Separate articles by priority
        priority_1 = [a for a in articles if a['priority'] == 1]
        priority_2 = [a for a in articles if a['priority'] == 2]
        priority_3 = [a for a in articles if a['priority'] == 3]

        # Group priority 3 articles by asset class
        by_asset_class = {}
        for article in priority_3:
            asset_class = article['asset_class']
            if asset_class not in by_asset_class:
                by_asset_class[asset_class] = []
            by_asset_class[asset_class].append(article)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Private Markets News Digest</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 28px;
        }}
        .date {{
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-header {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        .priority-1 .section-header {{
            color: #e74c3c;
            border-bottom-color: #e74c3c;
        }}
        .priority-2 .section-header {{
            color: #f39c12;
            border-bottom-color: #f39c12;
        }}
        .priority-3 .section-header {{
            color: #3498db;
            border-bottom-color: #3498db;
        }}
        .article {{
            margin-bottom: 25px;
            padding: 15px;
            background-color: #fafafa;
            border-radius: 6px;
            border-left: 4px solid #ecf0f1;
        }}
        .priority-1 .article {{
            border-left-color: #e74c3c;
            background-color: #fef5f4;
        }}
        .priority-2 .article {{
            border-left-color: #f39c12;
            background-color: #fef9f3;
        }}
        .priority-3 .article {{
            border-left-color: #3498db;
        }}
        .article-title {{
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .article-title a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        .article-title a:hover {{
            color: #3498db;
            text-decoration: underline;
        }}
        .article-meta {{
            font-size: 13px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        .article-summary {{
            font-size: 14px;
            color: #555;
            line-height: 1.5;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
            margin-right: 5px;
            margin-bottom: 5px;
        }}
        .badge-fund {{
            background-color: #e74c3c;
            color: white;
        }}
        .badge-keyword {{
            background-color: #95a5a6;
            color: white;
        }}
        .no-articles {{
            color: #7f8c8d;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }}
        @media only screen and (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .container {{
                padding: 20px;
            }}
            h1 {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Private Markets News Digest</h1>
            <div class="date">{date}</div>
        </div>
"""

        # Priority 1 Section
        if priority_1:
            html += """
        <div class="section priority-1">
            <div class="section-header">🔴 Priority Alerts - Key Funds</div>
"""
            for article in priority_1:
                html += self._format_article(article, show_funds=True)

            html += """
        </div>
"""

        # Priority 2 Section
        if priority_2:
            html += """
        <div class="section priority-2">
            <div class="section-header">🟡 Major Deals & Fund Closes</div>
"""
            for article in priority_2:
                html += self._format_article(article)

            html += """
        </div>
"""

        # Priority 3 Sections (grouped by asset class)
        if by_asset_class:
            for asset_class_key, asset_articles in by_asset_class.items():
                asset_class_name = self.asset_classes.get(asset_class_key, {}).get('name', asset_class_key)

                html += f"""
        <div class="section priority-3">
            <div class="section-header">📊 {asset_class_name}</div>
"""
                for article in asset_articles:
                    html += self._format_article(article, show_keywords=True)

                html += """
        </div>
"""

        # No articles message
        if not articles:
            html += """
        <div class="no-articles">
            No new articles found in the last 24 hours.
        </div>
"""

        # Footer
        html += f"""
        <div class="footer">
            Generated by Private Markets Monitor on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

        return html

    def _format_article(self, article: Dict, show_funds: bool = False,
                       show_keywords: bool = False) -> str:
        """
        Format a single article as HTML

        Args:
            article: Article dictionary
            show_funds: Whether to show matched priority funds
            show_keywords: Whether to show matched keywords

        Returns:
            HTML string
        """
        # Format published date
        published_str = "Unknown date"
        if article.get('published_date'):
            try:
                if isinstance(article['published_date'], str):
                    pub_date = datetime.fromisoformat(article['published_date'].replace('Z', '+00:00'))
                else:
                    pub_date = article['published_date']

                published_str = pub_date.strftime('%b %d, %Y %I:%M %p')
            except:
                published_str = str(article['published_date'])

        html = f"""
            <div class="article">
                <div class="article-title">
                    <a href="{article['url']}" target="_blank">{article['title']}</a>
                </div>
                <div class="article-meta">
                    <strong>{article['source']}</strong> • {published_str}
                </div>
"""

        # Show matched priority funds
        if show_funds and article.get('matched_priority_funds'):
            html += """
                <div style="margin-bottom: 10px;">
"""
            for fund in article['matched_priority_funds']:
                html += f"""
                    <span class="badge badge-fund">{fund.title()}</span>
"""
            html += """
                </div>
"""

        # Show matched keywords
        if show_keywords and article.get('matched_keywords'):
            html += """
                <div style="margin-bottom: 10px;">
"""
            for keyword in article['matched_keywords'][:5]:  # Limit to 5 keywords
                html += f"""
                    <span class="badge badge-keyword">{keyword}</span>
"""
            html += """
                </div>
"""

        # Show summary
        if article.get('summary'):
            summary = article['summary']
            # Truncate long summaries
            if len(summary) > 300:
                summary = summary[:297] + '...'

            html += f"""
                <div class="article-summary">
                    {summary}
                </div>
"""

        html += """
            </div>
"""

        return html

    def save_digest(self, html: str, filepath: str) -> bool:
        """
        Save digest HTML to file

        Args:
            html: HTML string
            filepath: Path to save file

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"Digest saved to: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving digest: {e}")
            return False


class EmailSender:
    """Sends email digest via SMTP"""

    def __init__(self, smtp_server: str, smtp_port: int,
                 smtp_user: str, smtp_password: str,
                 from_name: str = "Private Markets Monitor"):
        """
        Initialize email sender

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_name: Display name for sender
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_name = from_name

    def send_digest(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send email digest

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content

        Returns:
            True if successful
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.smtp_user}>"
            msg['To'] = to_email

            # Attach HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            # Send email
            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.set_debuglevel(0)
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to: {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            logger.error("Please check your SMTP credentials in .env file")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
