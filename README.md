# AI News Collector & Summarizer

AI関連ニュースを自動収集し、投資判断に役立つ要約を生成するPythonアプリケーションです。

## 概要

このプロジェクトは、急速に変化するAI業界の情報を効率的に収集・分析し、株式投資の判断材料として活用することを目的としています。Claude APIを活用して高精度な要約を生成し、メール配信やファイル出力により情報を自動配信します。

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
# 複数の場合はカンマ区切りで指定 スペースがあっても自動でトリミングされます
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com,recipient3@example.com
# 単一の場合
RECIPIENT_EMAIL=recipient@example.com
```

### 3. 収集対象の設定
`AINewsCollector`クラスの`rss_feeds`リストを編集して、収集対象のRSSフィードを追加・削除できます。

### 4. フィルタリングキーワードの調整
`filter_and_deduplicate`メソッドの`ai_keywords`リストを編集できます．

### 5. HTMLメールテンプレート
メール送信機能では`templates/email_template.html`のJinja2テンプレートを使用してHTMLメールを生成します。

## 実行

```bash
# 通常モード（Claude API使用、APIキー必須）
python3 ai_news_collector.py

# テストモード（API使用しない、開発・デバッグ用）
python3 ai_news_collector.py --test

# または環境変数でテストモード
TEST_MODE=true python3 ai_news_collector.py
```

## 出力ファイル

実行後、以下のファイルが生成されます：

- `ai_news_YYYYMMDD_HHMMSS.json`: 構造化されたニュースデータ
- `ai_news_summary_YYYYMMDD_HHMMSS.txt`: 要約テキスト

## ライセンス

MIT License

## テストモード

開発・デバッグ時にClaude APIの利用料を節約するため、テストモードを提供しています。

- 固定の要約結果を返す
- メール送信は実行されない

### テストモードの起動方法
```bash
# コマンドライン引数
python3 ai_news_collector.py --test

# 環境変数
TEST_MODE=true python3 ai_news_collector.py
```

## 今後の計画

- [ ] 感情分析機能の追加
- [ ] Webダッシュボードの実装
- [ ] より多くのニュースソース対応
- [ ] 銘柄影響分析機能（第二段階）
- [ ] リアルタイム通知機能

---

このプロジェクトは投資判断支援ツールであり、投資助言を提供するものではありません。投資は自己責任で行ってください。