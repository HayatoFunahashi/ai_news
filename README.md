# AI News Collector & Summarizer

AI関連ニュースを自動収集し、投資判断に役立つ要約を生成するPythonアプリケーションです。

## 概要

このプロジェクトは、急速に変化するAI業界の情報を効率的に収集・分析し、株式投資の判断材料として活用することを目的としています。Claude APIを活用して高精度な要約を生成し、メール配信やファイル出力により情報を自動配信します。

## 主な機能

- **自動ニュース収集**: 複数のRSSフィードとNews APIからAI関連ニュースを自動取得
- **インテリジェントフィルタリング**: AI関連キーワードによる記事の絞り込みと重複除去
- **AI要約**: Claude APIを使用した投資観点での要約生成
- **テストモード**: 開発・デバッグ用にAPI呼び出しを行わないモード
- **自動配信**: 複数宛先へのHTMLメール送信とファイル保存による結果配信
- **データ保存**: JSON形式での構造化データ保存
- **Webダッシュボード**: GitHub Pagesによる静的Webサイト形式でのニュース閲覧

## 必要要件

### システム要件
- Python 3.8以上
- インターネット接続

### 必要なライブラリ
```bash
pip install requests feedparser anthropic python-dotenv markdown2 jinja2
```

### API キー
- **Anthropic API Key** (必須): [Console](https://console.anthropic.com/)から取得
- **News API Key** (オプション): [NewsAPI](https://newsapi.org/)から取得

## インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd ai_news
```

2. 依存関係をインストール
```bash
pip install requests feedparser anthropic python-dotenv markdown2 jinja2
```

3. 環境設定ファイルを作成
```bash
touch .env  # .envファイルを手動で作成
```

## 設定

### 1. API キーの設定
`.env`ファイルで以下を設定：

```bash
# Anthropic API Key (必須)
ANTHROPIC_API_KEY=your-anthropic-api-key

# News API Key (オプション - 未設定でもRSSフィードは動作)
# NEWS_API_KEY=your-news-api-key
```

### 2. メール設定（オプション）
メール配信を使用する場合、`.env`ファイルに追加：

```bash
# SMTP設定
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # Gmailの場合はアプリパスワード

# メール送信先アドレス（複数指定可能）
# 複数の場合はカンマ区切りで指定
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com,recipient3@example.com

# または単一の場合（後方互換性のため）
# RECIPIENT_EMAIL=recipient@example.com
```

### 3. 収集対象の設定
`AINewsCollector`クラスの`rss_feeds`リストを編集して、収集対象のRSSフィードを追加・削除できます。

現在の収集源：
- VentureBeat AI
- AI News
- O'Reilly Radar  
- OpenAI Blog
- DeepMind Blog

### 4. 複数受信者の設定
メール送信は複数の宛先に対応しています：

```bash
# 複数のメールアドレスをカンマ区切りで設定
RECIPIENT_EMAILS=investor1@company.com,analyst@firm.com,researcher@university.edu

# スペースがあっても自動でトリミングされます
RECIPIENT_EMAILS=user1@example.com, user2@example.com, user3@example.com
```

**特徴:**
- 各受信者に個別にメール送信（プライバシー保護）
- 送信失敗した宛先も個別に報告
- SMTP接続は一度だけ確立して効率化
- 無効なメールアドレス形式は自動でスキップ

### 5. HTMLメールテンプレート
メール送信機能では`templates/email_template.html`のJinja2テンプレートを使用してHTMLメールを生成します。

## 使用方法

### 基本的な使用方法

```python
from ai_news_collector import AINewsCollector, parse_recipient_emails

# インスタンス作成
collector = AINewsCollector("your-anthropic-api-key")

# 複数の受信者にメール送信する場合
recipient_emails = ["user1@example.com", "user2@example.com"]
summary = collector.run_daily_collection(recipient_emails)

# または環境変数から自動取得（推奨）
summary = collector.run_daily_collection()
print(summary)
```

### コマンドライン実行

```bash
# 通常モード（Claude API使用、APIキー必須）
python3 ai_news_collector.py

# テストモード（API使用しない、開発・デバッグ用）
python3 ai_news_collector.py --test

# または環境変数でテストモード
TEST_MODE=true python3 ai_news_collector.py
```

### 定期実行の設定

#### Linux/Mac (crontab)
```bash
# 毎日午前8時に実行（作業ディレクトリに注意）
0 8 * * * cd /path/to/ai_news && /usr/bin/python3 ai_news_collector.py
```

#### Windows (タスクスケジューラ)
1. タスクスケジューラを開く
2. 基本タスクの作成
3. トリガー: 毎日午前8時
4. 操作: プログラムの開始
5. プログラム: `python.exe`
6. 引数: `ai_news_collector.py`の絶対パス
7. 開始フォルダー: プロジェクトのディレクトリを指定

## 出力ファイル

実行後、以下のファイルが生成されます：

- `ai_news_YYYYMMDD_HHMMSS.json`: 構造化されたニュースデータ
- `ai_news_summary_YYYYMMDD_HHMMSS.txt`: 要約テキスト
- `templates/email_template.html`: HTMLメール用Jinja2テンプレート
- `test_data.json`: テスト用のサンプルデータ（管理用）
- `tools/ai_commit.sh`: Claude Code CLIを使用したAI powered コミットメッセージ生成スクリプト

### JSON出力形式

```json
{
  "timestamp": "20250721_083000",
  "summary": "今日のAI要約...",
  "news_count": 15,
  "news_items": [
    {
      "title": "記事タイトル",
      "url": "https://example.com/article",
      "published": "2025-07-21T08:30:00",
      "source": "ニュースソース"
    }
  ]
}
```

## カスタマイズ

### ニュースソースの追加
新しいRSSフィードを追加するには、`rss_feeds`リストに追加：

```python
self.rss_feeds = [
    "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat AI
    "https://www.artificialintelligence-news.com/feed/",  # AI News
    "https://feeds.feedburner.com/oreilly/radar/atom",  # O'Reilly Radar
    "https://blog.openai.com/rss.xml",  # OpenAI Blog
    "https://deepmind.com/blog/feed/basic/",  # DeepMind
    # 新しいフィードを追加
    "https://new-source.com/feed"
]
```

### フィルタリングキーワードの調整
`filter_and_deduplicate`メソッドの`ai_keywords`リストを編集：

```python
ai_keywords = [
    'AI', 'artificial intelligence', 'machine learning', 'deep learning',
    'neural network', 'ChatGPT', 'OpenAI', 'Google AI', 'Microsoft AI',
    'NVIDIA', 'autonomous', 'computer vision', 'natural language processing',
    'LLM', 'large language model', 'generative AI', 'AGI'
    # 新しいキーワードを追加
    # 'transformer', 'GPT', 'BERT'
]
```

### 要約プロンプトのカスタマイズ
`summarize_with_claude`メソッドのプロンプトを編集して、要約の観点や形式を変更できます。現在は投資判断に特化した観点で以下の要素を含む要約を生成します：
- 主要なトレンドや動向
- 注目すべき企業や技術
- 市場への潜在的影響  
- 投資家が注目すべきポイント

使用モデル: `claude-opus-4-20250514` (Claude Opus 4)

## トラブルシューティング

### よくある問題

1. **API Key エラー**
   - Anthropic API Keyが正しく設定されているか確認
   - API使用量の上限に達していないか確認

2. **メール送信エラー**
   - SMTP設定が正しいか確認
   - Gmailの場合、2段階認証とアプリパスワードが設定されているか確認

3. **RSS フィードエラー**
   - インターネット接続を確認
   - 一部のRSSフィードが利用できない場合があります

### ログ確認
詳細なログは標準出力に表示されます。問題がある場合はコンソール出力を確認してください。

## ライセンス

MIT License

## 貢献

プルリクエストやIssuesを歓迎します。

## テストモード

開発・デバッグ時にClaude APIの利用料を節約するため、テストモードを提供しています。

### テストモードの特徴
- Claude APIを呼び出さない
- `test_data.json`のサンプルニュースデータを使用
- 固定の要約結果を返す
- メール送信は実行されない

### テストモードの起動方法
```bash
# コマンドライン引数
python3 ai_news_collector.py --test

# 環境変数
TEST_MODE=true python3 ai_news_collector.py
```

## Webダッシュボード

### 概要
GitHub Pagesを使用した静的Webサイト形式のダッシュボードで、どこからでもAIニュースを閲覧できます。

### 特徴
- **📊 リアルタイム表示**: 最新のAIニュースと分析結果
- **🔍 高度なフィルタリング**: 日付、ソース、企業、キーワード別の検索
- **📱 レスポンシブデザイン**: デスクトップ・モバイル対応
- **📈 統計情報**: 総記事数、更新状況、関連企業数
- **🎯 投資判断支援**: Claude AIによる投資観点での分析
- **📰 タイムライン表示**: 時系列でのニュース表示

### GitHub Pages設定

1. **リポジトリ設定**
   ```bash
   # GitHub Pagesを有効化（リポジトリ設定 > Pages）
   # Source: GitHub Actions
   ```

2. **Secretsの設定**（リポジトリ設定 > Secrets and variables > Actions）
   ```
   ANTHROPIC_API_KEY=your-anthropic-api-key
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   RECIPIENT_EMAILS=user1@example.com,user2@example.com
   ```

3. **自動デプロイ**
   - 毎日8:00（日本時間）に自動実行
   - 手動実行も可能（Actions タブから "Deploy AI News Dashboard" を選択）
   - コミット時も自動デプロイ

### URL例
```
https://hayatofunahashi.github.io/ai_news/
```

### 技術スタック
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+)
- **スタイリング**: CSS Grid, Flexbox, FontAwesome アイコン
- **データ**: JSON API形式での動的データ読み込み
- **デプロイ**: GitHub Actions + GitHub Pages

## 追加機能・ツール

### AI Commit Message Generator
`tools/ai_commit.sh`は、Claude Code CLIを使用してコミットメッセージを自動生成するスクリプトです。

```bash
# 使用方法
./tools/ai_commit.sh
```

特徴：
- Conventional Commits形式でのメッセージ生成
- Git差分の自動解析
- インタラクティブな承認・編集機能

## 今後の計画

- [ ] 感情分析機能の追加
- [ ] Webダッシュボードの実装
- [ ] より多くのニュースソース対応
- [ ] 銘柄影響分析機能（第二段階）
- [ ] リアルタイム通知機能
- [x] テストモードの実装（API利用料節約）
- [x] HTMLメール送信機能の実装
- [x] AI powered コミットメッセージ生成ツールの追加
- [x] Webダッシュボードの実装（GitHub Pages対応）
- [x] GitHub Actions による自動デプロイ機能

## サポート

質問や問題がある場合は、Issuesページで報告してください。

---

このプロジェクトは投資判断支援ツールであり、投資助言を提供するものではありません。投資は自己責任で行ってください。