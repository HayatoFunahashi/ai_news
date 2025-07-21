# AI News Collector & Summarizer

AI関連ニュースを自動収集し、投資判断に役立つ要約を生成するPythonアプリケーションです。

## 概要

このプロジェクトは、急速に変化するAI業界の情報を効率的に収集・分析し、株式投資の判断材料として活用することを目的としています。Claude APIを活用して高精度な要約を生成し、メール配信やファイル出力により情報を自動配信します。

## 主な機能

- **自動ニュース収集**: 複数のRSSフィードとNews APIからAI関連ニュースを自動取得
- **インテリジェントフィルタリング**: AI関連キーワードによる記事の絞り込みと重複除去
- **AI要約**: Claude APIを使用した投資観点での要約生成
- **テストモード**: 開発・デバッグ用にAPI呼び出しを行わないモード
- **自動配信**: メール送信とファイル保存による結果配信
- **データ保存**: JSON形式での構造化データ保存

## 必要要件

### システム要件
- Python 3.8以上
- インターネット接続

### 必要なライブラリ
```bash
pip install requests feedparser anthropic python-dotenv
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
pip install requests feedparser anthropic python-dotenv
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
RECIPIENT_EMAIL=recipient@example.com  # メール送信先アドレス
```

### 3. 収集対象の設定
`AINewsCollector`クラスの`rss_feeds`リストを編集して、収集対象のRSSフィードを追加・削除できます。

## 使用方法

### 基本的な使用方法

```python
from ai_news_collector import AINewsCollector

# インスタンス作成
collector = AINewsCollector("your-anthropic-api-key")

# ニュース収集・要約実行
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
- `test_data.json`: テスト用のサンプルデータ（管理用）

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
    "https://example.com/ai-news/rss",
    # 新しいフィードを追加
    "https://new-source.com/feed"
]
```

### フィルタリングキーワードの調整
`filter_and_deduplicate`メソッドの`ai_keywords`リストを編集：

```python
ai_keywords = [
    'AI', 'artificial intelligence',
    # 新しいキーワードを追加
    'transformer', 'GPT', 'BERT'
]
```

### 要約プロンプトのカスタマイズ
`summarize_with_claude`メソッドのプロンプトを編集して、要約の観点や形式を変更できます。

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

## 今後の計画

- [ ] 感情分析機能の追加
- [ ] Webダッシュボードの実装
- [ ] より多くのニュースソース対応
- [ ] 銘柄影響分析機能（第二段階）
- [ ] リアルタイム通知機能
- [x] テストモードの実装（API利用料節約）

## サポート

質問や問題がある場合は、Issuesページで報告してください。

---

このプロジェクトは投資判断支援ツールであり、投資助言を提供するものではありません。投資は自己責任で行ってください。