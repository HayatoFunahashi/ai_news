# AI News Dashboard

This directory contains the static files for the AI News Dashboard, hosted on GitHub Pages.

## Features

- 📊 **Real-time AI news aggregation** from multiple sources
- 🔍 **Advanced filtering** by date, source, company, and keywords
- 📈 **Investment-focused analysis** powered by Claude AI
- 📱 **Responsive design** for desktop and mobile
- 📰 **Historical data** with timeline view
- 🎯 **Company-specific insights** for major AI players

## Structure

- `index.html` - Main dashboard page
- `css/` - Stylesheets
- `js/` - JavaScript functionality
- `data/` - Generated JSON data files
- `_config.yml` - GitHub Pages configuration

## Data Sources

The dashboard aggregates AI news from:
- VentureBeat AI
- AI News
- O'Reilly Radar
- OpenAI Blog
- DeepMind Blog
- NewsAPI (optional)

## Automatic Updates

The dashboard is automatically updated via GitHub Actions when:
- New news data is collected (scheduled daily at 8:00 JST)
- Manual workflow dispatch
- Changes to dashboard files are pushed to main branch

## Disclaimer

This dashboard provides investment analysis for informational purposes only and does not constitute investment advice. Please conduct your own research and consult with financial advisors before making investment decisions.