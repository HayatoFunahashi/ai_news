class AINewsDashboard {
    constructor() {
        this.newsData = [];
        this.filteredData = [];
        this.filters = {
            date: 'all',
            source: 'all',
            company: 'all',
            keyword: ''
        };
        
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.updateStats();
        this.renderNews();
        this.renderSummaries();
    }

    async loadData() {
        try {
            const response = await fetch('data/aggregated_news.json');
            if (!response.ok) {
                throw new Error('Failed to load data');
            }
            const data = await response.json();
            this.newsData = data.news_items || [];
            this.summaryData = data.summaries || [];
            this.filteredData = [...this.newsData];
            
            // Populate source filter
            this.populateSourceFilter();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('データの読み込みに失敗しました。');
        }
    }

    populateSourceFilter() {
        const sourceSelect = document.getElementById('sourceFilter');
        const sources = [...new Set(this.newsData.map(item => item.source))];
        
        // Clear existing options except "all"
        sourceSelect.innerHTML = '<option value="all">すべて</option>';
        
        sources.forEach(source => {
            const option = document.createElement('option');
            option.value = source;
            option.textContent = source;
            sourceSelect.appendChild(option);
        });
    }

    setupEventListeners() {
        // Filter event listeners
        document.getElementById('dateFilter').addEventListener('change', (e) => {
            this.filters.date = e.target.value;
            this.applyFilters();
        });

        document.getElementById('sourceFilter').addEventListener('change', (e) => {
            this.filters.source = e.target.value;
            this.applyFilters();
        });

        document.getElementById('companyFilter').addEventListener('change', (e) => {
            this.filters.company = e.target.value;
            this.applyFilters();
        });

        document.getElementById('keywordSearch').addEventListener('input', (e) => {
            this.filters.keyword = e.target.value.toLowerCase();
            this.applyFilters();
        });

        document.getElementById('clearFilters').addEventListener('click', () => {
            this.clearFilters();
        });
    }

    applyFilters() {
        this.filteredData = this.newsData.filter(item => {
            // Date filter
            if (this.filters.date !== 'all') {
                const itemDate = new Date(item.published);
                const now = new Date();
                const diffTime = now - itemDate;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

                if (this.filters.date === 'today' && diffDays > 1) return false;
                if (this.filters.date === 'week' && diffDays > 7) return false;
                if (this.filters.date === 'month' && diffDays > 30) return false;
            }

            // Source filter
            if (this.filters.source !== 'all' && item.source !== this.filters.source) {
                return false;
            }

            // Company filter
            if (this.filters.company !== 'all') {
                const titleLower = item.title.toLowerCase();
                const companyLower = this.filters.company.toLowerCase();
                if (!titleLower.includes(companyLower)) {
                    return false;
                }
            }

            // Keyword filter
            if (this.filters.keyword) {
                const searchText = `${item.title} ${item.content || ''}`.toLowerCase();
                if (!searchText.includes(this.filters.keyword)) {
                    return false;
                }
            }

            return true;
        });

        this.updateStats();
        this.renderNews();
    }

    clearFilters() {
        this.filters = {
            date: 'all',
            source: 'all',
            company: 'all',
            keyword: ''
        };

        document.getElementById('dateFilter').value = 'all';
        document.getElementById('sourceFilter').value = 'all';
        document.getElementById('companyFilter').value = 'all';
        document.getElementById('keywordSearch').value = '';

        this.filteredData = [...this.newsData];
        this.updateStats();
        this.renderNews();
    }

    updateStats() {
        const totalNews = this.filteredData.length;
        const recentNews = this.getRecentNewsCount();
        const uniqueCompanies = this.getUniqueCompaniesCount();
        const lastUpdate = this.getLastUpdateTime();

        document.getElementById('totalNews').textContent = totalNews;
        document.getElementById('recentUpdates').textContent = recentNews;
        document.getElementById('uniqueCompanies').textContent = uniqueCompanies;
        document.getElementById('lastUpdate').textContent = lastUpdate;
    }

    getRecentNewsCount() {
        const oneDayAgo = new Date();
        oneDayAgo.setDate(oneDayAgo.getDate() - 1);
        
        return this.filteredData.filter(item => {
            const itemDate = new Date(item.published);
            return itemDate >= oneDayAgo;
        }).length;
    }

    getUniqueCompaniesCount() {
        const companies = new Set();
        const companyKeywords = ['OpenAI', 'Google', 'Microsoft', 'Apple', 'NVIDIA', 'Meta', 'Amazon'];
        
        this.filteredData.forEach(item => {
            const titleLower = item.title.toLowerCase();
            companyKeywords.forEach(company => {
                if (titleLower.includes(company.toLowerCase())) {
                    companies.add(company);
                }
            });
        });
        
        return companies.size;
    }

    getLastUpdateTime() {
        if (this.filteredData.length === 0) return '-';
        
        const latestItem = this.filteredData.reduce((latest, item) => {
            return new Date(item.published) > new Date(latest.published) ? item : latest;
        });
        
        const date = new Date(latestItem.published);
        return this.formatDate(date);
    }

    renderNews() {
        const container = document.getElementById('newsTimeline');
        
        if (this.filteredData.length === 0) {
            container.innerHTML = '<div class="loading">フィルタに一致するニュースが見つかりません。</div>';
            return;
        }

        // Sort by date (newest first)
        const sortedData = [...this.filteredData].sort((a, b) => 
            new Date(b.published) - new Date(a.published)
        );

        container.innerHTML = sortedData.map(item => this.renderNewsItem(item)).join('');
        
        // Add fade-in animation
        container.classList.add('fadeIn');
    }

    renderNewsItem(item) {
        const date = new Date(item.published);
        const formattedDate = this.formatDate(date);
        const timeAgo = this.getTimeAgo(date);

        return `
            <div class="news-item fadeIn">
                <div class="news-header">
                    <div class="news-meta">
                        <span class="news-source">${this.escapeHtml(item.source)}</span>
                        <span class="news-date">${formattedDate} (${timeAgo})</span>
                    </div>
                    <h3 class="news-title">
                        <a href="${item.url}" target="_blank" rel="noopener noreferrer">
                            ${this.escapeHtml(item.title)}
                            <i class="fas fa-external-link-alt" style="font-size: 0.8em; margin-left: 0.5rem;"></i>
                        </a>
                    </h3>
                </div>
                <div class="news-content">
                    <div class="news-summary">
                        ${this.escapeHtml(item.content || 'コンテンツが利用できません。')}
                    </div>
                </div>
            </div>
        `;
    }

    renderSummaries() {
        const container = document.getElementById('summaryContainer');
        
        if (!this.summaryData || this.summaryData.length === 0) {
            container.innerHTML = '<div class="loading">サマリーデータが利用できません。</div>';
            return;
        }

        // Sort summaries by timestamp (newest first)
        const sortedSummaries = [...this.summaryData].sort((a, b) => 
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        container.innerHTML = sortedSummaries.map(summary => this.renderSummaryItem(summary)).join('');
    }

    renderSummaryItem(summary) {
        const date = new Date(summary.timestamp);
        const formattedDate = this.formatDate(date);

        return `
            <div class="summary-item fadeIn">
                <div class="summary-header">
                    <div class="summary-date">${formattedDate}</div>
                    <div class="summary-stats">
                        ${summary.news_count}件のニュースを分析
                    </div>
                </div>
                <div class="summary-content">
                    ${summary.headlines ? `
                        <div class="headlines-section">
                            <h4><i class="fas fa-newspaper"></i> 主要見出し</h4>
                            <div>${this.formatHeadlines(summary.headlines)}</div>
                        </div>
                    ` : ''}
                    <div class="summary-text">
                        ${this.formatMarkdown(summary.summary)}
                    </div>
                </div>
            </div>
        `;
    }

    formatHeadlines(headlines) {
        if (typeof headlines === 'string') {
            // Parse headlines from string format
            return headlines
                .split('\n')
                .filter(line => line.trim())
                .map(line => {
                    const match = line.match(/- (.+?) \((.+?)\)\s*(https?:\/\/.+)/);
                    if (match) {
                        const [, title, source, url] = match;
                        return `<div style="margin-bottom: 0.5rem;">
                            <a href="${url}" target="_blank" rel="noopener noreferrer" style="color: #333; text-decoration: none;">
                                📰 ${this.escapeHtml(title)} 
                                <span style="color: #666; font-size: 0.9rem;">(${this.escapeHtml(source)})</span>
                                <i class="fas fa-external-link-alt" style="font-size: 0.7em; margin-left: 0.3rem; color: #999;"></i>
                            </a>
                        </div>`;
                    }
                    return `<div style="margin-bottom: 0.5rem;">${this.escapeHtml(line.replace(/^- /, ''))}</div>`;
                })
                .join('');
        }
        return this.escapeHtml(headlines);
    }

    formatMarkdown(text) {
        if (!text) return '';
        
        return text
            // Headers
            .replace(/^### (.+$)/gim, '<h3>$1</h3>')
            .replace(/^## (.+$)/gim, '<h2>$1</h2>')
            .replace(/^# (.+$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            // Lists
            .replace(/^- (.+$)/gim, '<li>$1</li>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
            // Line breaks
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            // Wrap in paragraphs
            .replace(/^(.+)/gim, '<p>$1</p>')
            // Fix list items
            .replace(/<p><li>/g, '<ul><li>')
            .replace(/<\/li><\/p>/g, '</li></ul>');
    }

    formatDate(date) {
        return date.toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    getTimeAgo(date) {
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));

        if (diffDays === 1) return '1日前';
        if (diffDays > 1) return `${diffDays}日前`;
        if (diffHours === 1) return '1時間前';
        if (diffHours > 1) return `${diffHours}時間前`;
        return '1時間以内';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        const container = document.getElementById('newsTimeline');
        container.innerHTML = `
            <div class="loading" style="color: #ef4444;">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
        `;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AINewsDashboard();
});