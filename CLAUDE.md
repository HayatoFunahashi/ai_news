# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI news collection and summarization system that automatically gathers AI-related news from RSS feeds and News API, filters relevant content, generates investment-focused summaries using Claude API, and distributes results via email or file output.

## Development Commands

### Running the Application
```bash
# Normal mode (requires API key)
python3 ai_news_collector.py

# Test mode (no API calls, uses test data)
python3 ai_news_collector.py --test

# Test mode via environment variable
TEST_MODE=true python3 ai_news_collector.py
```

### Installing Dependencies
Since there's no requirements.txt file, install dependencies manually:
```bash
pip install requests feedparser anthropic python-dotenv markdown2 jinja2
```

### Environment Setup
1. Create a `.env` file with required API keys and email configuration:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
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
- **Distribution Phase**: `send_email_summary()` handles HTML email delivery to multiple recipients using Jinja2 templates and file output
- **Test Phase**: `load_test_data()` loads test data from `test_data.json` for development testing

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
- Claude model: `claude-opus-4-20250514` (Claude Opus 4 for improved output quality)

## File Organization

### Generated Output Files
- `ai_news_YYYYMMDD_HHMMSS.json`: Structured data with metadata and article details
- `ai_news_summary_YYYYMMDD_HHMMSS.txt`: Plain text summaries
- Files are automatically excluded from git via .gitignore

### Key Files
- `ai_news_collector.py`: Main application code
- `README.md`: Comprehensive documentation
- `CLAUDE.md`: Project instructions for Claude Code (this file)
- `.env`: Environment configuration (git-ignored)
- `templates/email_template.html`: Jinja2 template for HTML email generation
- `test_data.json`: Test data with sample news items and expected summary
- `tools/ai_commit.sh`: AI-powered commit message generator using Claude Code CLI

## Test Mode

The application includes a test mode to avoid Claude API usage during development:

### Test Data Structure
- `test_data.json`: Contains sample news items and expected summary
- Test mode uses fixed test data instead of fetching real news
- Returns pre-defined summary without API calls

### Activation Methods
1. Command line: `--test` flag
2. Environment variable: `TEST_MODE=true`

## Important Notes

### Development Infrastructure
- No `requirements.txt` file - dependencies must be installed manually
- No formal testing framework, but includes test mode with `test_data.json`
- No linting/formatting configuration
- No CI/CD pipeline setup
- Includes AI-powered commit message generation tool (`tools/ai_commit.sh`)

### Current Features & Limitations
**Features:**
- HTML email generation with Jinja2 templates
- Multiple recipient email support with individual sending
- Test mode for development without API calls
- Investment-focused AI analysis using Claude Opus 4
- Multi-source news collection (RSS + News API)
- Conventional commit message generation tool
- Backward compatibility for single recipient configuration

**Limitations:**
- No comprehensive error handling for API rate limits
- No logging configuration beyond print statements
- News API integration exists but requires separate API key

### Email Configuration Requirements
For Gmail SMTP, users need:
- 2-factor authentication enabled
- App-specific password (not regular Gmail password)
- Correct SMTP settings (smtp.gmail.com:587)
- Multiple recipient emails configured via RECIPIENT_EMAILS environment variable (comma-separated)
- Backward compatibility: single recipient via RECIPIENT_EMAIL still supported
- HTML email template at `templates/email_template.html` (Jinja2 format)

#### Multiple Recipients Support
- Environment variable: `RECIPIENT_EMAILS=user1@example.com,user2@example.com,user3@example.com`
- Individual email sending (no CC/BCC - privacy protection)
- Automatic error handling per recipient
- Invalid email format detection and skipping
- Efficient SMTP connection reuse

### Tools Directory
- `tools/ai_commit.sh`: Bash script for AI-powered commit message generation
  - Uses Claude Code CLI to analyze git diffs
  - Generates Conventional Commits format messages
  - Interactive approval/editing interface
  - Requires `claude` command to be installed and configured