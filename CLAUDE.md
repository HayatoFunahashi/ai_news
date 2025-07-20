# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI news collection and summarization system that automatically gathers AI-related news from RSS feeds and News API, filters relevant content, generates investment-focused summaries using Claude API, and distributes results via email or file output.

## Development Commands

### Running the Application
```bash
python ai_news_collector.py
```

### Installing Dependencies
Since there's no requirements.txt file, install dependencies manually:
```bash
pip install requests feedparser anthropic python-dotenv
```

### Environment Setup
1. Create a `.env` file with required API keys and email configuration:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

2. Optional News API integration:
```
NEWS_API_KEY=your-news-api-key
```

## Code Architecture

### Core Components

**`NewsItem` dataclass**: Represents individual news articles with title, URL, publication date, content, and source.

**`AINewsCollector` class**: Main application logic organized into distinct phases:
- **Collection Phase**: `collect_rss_news()` and `collect_news_api()` gather news from multiple sources
- **Processing Phase**: `filter_and_deduplicate()` applies AI keyword filtering and removes duplicates
- **Analysis Phase**: `summarize_with_claude()` generates investment-focused summaries using Claude API
- **Distribution Phase**: `send_email_summary()` handles email delivery and file output

### Data Flow
1. **Multi-source Collection**: RSS feeds (OpenAI, DeepMind, VentureBeat, etc.) + optional News API
2. **Intelligent Filtering**: AI-keyword based filtering with deduplication by title
3. **Claude Summarization**: Investment-focused analysis with structured prompts
4. **Dual Output**: JSON data files + plain text summaries with timestamp naming
5. **Email Distribution**: Optional SMTP-based delivery

### Configuration Management
- Environment variables via `.env` file using python-dotenv
- RSS feed sources defined in `self.rss_feeds` list
- AI filtering keywords in `filter_and_deduplicate()` method
- Claude model: `claude-3-7-sonnet-20250219`

## File Organization

### Generated Output Files
- `ai_news_YYYYMMDD_HHMMSS.json`: Structured data with metadata and article details
- `ai_news_summary_YYYYMMDD_HHMMSS.txt`: Plain text summaries
- Files are automatically excluded from git via .gitignore

### Key Files
- `ai_news_collector.py`: Main application code
- `REAME.md`: Comprehensive documentation (note: typo in filename)
- `.env`: Environment configuration (git-ignored)

## Important Notes

### Missing Development Infrastructure
- No `requirements.txt` file - dependencies must be installed manually
- No testing framework or test files
- No linting/formatting configuration
- No CI/CD pipeline setup

### Current Limitations
- Hard-coded recipient email in main() function
- No comprehensive error handling for API rate limits
- No logging configuration beyond print statements
- News API integration exists but requires separate API key

### Email Configuration Requirements
For Gmail SMTP, users need:
- 2-factor authentication enabled
- App-specific password (not regular Gmail password)
- Correct SMTP settings (smtp.gmail.com:587)