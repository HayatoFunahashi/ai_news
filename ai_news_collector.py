import requests
import feedparser
import json
from datetime import datetime, timedelta
from typing import List, Dict
import time
from dataclasses import dataclass
import anthropic
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown2
from dotenv import load_dotenv
import os
import sys
from jinja2 import Environment, FileSystemLoader

@dataclass
class NewsItem:
    title: str
    url: str
    published: datetime
    content: str
    source: str

class AINewsCollector:
    def __init__(self, anthropic_api_key: str, test_mode: bool = False):
        self.test_mode = test_mode
        if not test_mode:
            self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        else:
            self.client = None
        
        # AI関連のRSSフィードとニュースソース
        self.rss_feeds = [
            "https://feeds.feedburner.com/venturebeat/SZYF",  # VentureBeat AI
            "https://www.artificialintelligence-news.com/feed/",  # AI News
            "https://feeds.feedburner.com/oreilly/radar/atom",  # O'Reilly Radar
            "https://blog.openai.com/rss.xml",  # OpenAI Blog
            "https://deepmind.com/blog/feed/basic/",  # DeepMind
        ]
        
        # ニュースAPI（例：NewsAPI）
        self.news_api_key = None  # NewsAPIのキーを設定
        # GitHubのWebページ
        self.github_url = "https://github.com/HayatoFunahashi/ai_news"
        
    def collect_rss_news(self, hours_back: int = 24) -> List[NewsItem]:
        """RSSフィードからニュースを収集"""
        news_items = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    # 日付解析
                    if hasattr(entry, 'published_parsed'):
                        pub_date = datetime(*entry.published_parsed[:6])
                    else:
                        pub_date = datetime.now()
                    
                    if pub_date > cutoff_time:
                        content = entry.get('summary', entry.get('description', ''))
                        
                        news_item = NewsItem(
                            title=entry.title,
                            url=entry.link,
                            published=pub_date,
                            content=content,
                            source=feed.feed.get('title', 'Unknown')
                        )
                        news_items.append(news_item)
                        
            except Exception as e:
                print(f"Error processing RSS feed {feed_url}: {e}")
                
        return news_items
    
    def collect_news_api(self, hours_back: int = 24) -> List[NewsItem]:
        """News APIからニュースを収集"""
        if not self.news_api_key:
            return []
            
        news_items = []
        
        # AI関連のキーワード
        keywords = [
            "artificial intelligence",
            "machine learning", 
            "deep learning",
            "ChatGPT",
            "OpenAI",
            "Google AI",
            "Microsoft AI",
            "NVIDIA AI"
        ]
        
        from_date = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%d')
        
        for keyword in keywords:
            try:
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': keyword,
                    'from': from_date,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'apiKey': self.news_api_key,
                    'pageSize': 20
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                for article in data.get('articles', []):
                    pub_date = datetime.fromisoformat(
                        article['publishedAt'].replace('Z', '+00:00')
                    ).replace(tzinfo=None)
                    
                    news_item = NewsItem(
                        title=article['title'],
                        url=article['url'],
                        published=pub_date,
                        content=article.get('description', ''),
                        source=article['source']['name']
                    )
                    news_items.append(news_item)
                    
                time.sleep(1)  # API制限対策
                
            except Exception as e:
                print(f"Error collecting news for keyword '{keyword}': {e}")
                
        return news_items
    
    def filter_and_deduplicate(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """ニュースのフィルタリングと重複除去"""
        # AI関連キーワードでフィルタリング
        ai_keywords = [
            'AI', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'ChatGPT', 'OpenAI', 'Google AI', 'Microsoft AI',
            'NVIDIA', 'autonomous', 'computer vision', 'natural language processing',
            'LLM', 'large language model', 'generative AI', 'AGI'
        ]
        
        filtered_items = []
        seen_titles = set()
        
        for item in news_items:
            # AI関連かチェック
            is_ai_related = any(
                keyword.lower() in item.title.lower() or 
                keyword.lower() in item.content.lower()
                for keyword in ai_keywords
            )
            
            if is_ai_related and item.title not in seen_titles:
                filtered_items.append(item)
                seen_titles.add(item.title)
                
        # 日付順でソート（新しい順）
        return sorted(filtered_items, key=lambda x: x.published, reverse=True)
    
    def load_test_data(self) -> tuple[List[NewsItem], str]:
        """テスト用データを読み込み"""
        try:
            with open('test_data.json', 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            # テスト用NewsItemsを作成
            test_items = []
            for item_data in test_data['test_news_items']:
                news_item = NewsItem(
                    title=item_data['title'],
                    url=item_data['url'],
                    published=datetime.fromisoformat(item_data['published']),
                    content=item_data['content'],
                    source=item_data['source']
                )
                test_items.append(news_item)
            
            return test_items, test_data['expected_summary']
            
        except Exception as e:
            print(f"テストデータの読み込みエラー: {e}")
            return [], "テストデータが利用できません。"
    
    def summarize_with_claude(self, news_items: List[NewsItem]) -> str:
        """Claudeを使ってニュースを要約（テストモード対応）"""
        if self.test_mode:
            # テストモード：固定の要約を返す
            _, test_summary = self.load_test_data()
            print("[TEST MODE] 固定の要約を使用しています")
            return test_summary
        
        if not news_items:
            return "今日はAI関連の重要なニュースはありませんでした。"
        
        # ニュース情報を整理
        news_text = "\n\n".join([
            f"タイトル: {item.title}\n"
            f"ソース: {item.source}\n"
            f"内容: {item.content}\n"
            f"URL: {item.url}"
            for item in news_items[:20]  # 上位20件のみ
        ])
        
        prompt = f"""
"あなたはAI関連の経済ニュースを分析するアナリストです。"
"投資家が素早く判断できるよう、複数記事の要点を簡潔に、かつ出典を含めて整理してください。\n\n"        
以下のAI関連ニュースを分析して、投資判断に役立つ要約を作成してください。
それぞれの要約には【出典】としてニュースソースとURLも明示してください。

{news_text}

出力形式の例：

---
- タイトル: ◯◯◯
- 概要: ...
- 影響: ...
- 出典: ◯◯（URL）
---

以下の観点で要約してください：
1. 主要なトレンドや動向
2. 注目すべき企業や技術
3. 市場への潜在的影響
4. 投資家が注目すべきポイント

わかりやすく、具体性のある日本語で簡潔に書いてください。
出力形式はマークダウン形式に準拠してください．
"""
        
        try:
            message = self.client.messages.create(
                model="claude-opus-4-20250514", # Claude 3.7 sonetとClaude 4.0 sonetと比較したがopus-4の出力結果が目視で最も良かったため
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"Claude API error: {e}")
            return "要約の生成中にエラーが発生しました。"
    
    def send_email_summary(self, summary: str, recipient_emails: List[str], 
                          smtp_server: str, smtp_port: int, 
                          sender_email: str, sender_password: str,
                          news_items: List[NewsItem]):
        """テンプレートを使って複数の宛先にHTMLメールを送信"""
        if not recipient_emails:
            print("送信先メールアドレスが指定されていません")
            return
            
        try:
            # Jinja2テンプレート読み込み
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('email_template.html')

            # Markdown要約をHTMLに変換
            summary_html = markdown2.markdown(summary)

            # テンプレートに渡すデータ
            html_content = template.render(
                date=datetime.now().strftime('%Y-%m-%d'),
                generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                news_items=news_items[:20],
                summary_html=summary_html
            )

            # SMTP接続を一度だけ確立
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            
            success_count = 0
            failed_recipients = []
            
            # 各受信者に個別にメール送信
            for recipient_email in recipient_emails:
                try:
                    # メール構築
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient_email
                    msg['Subject'] = f"🧠 AI News Summary - {datetime.now().strftime('%Y-%m-%d')}"
                    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

                    # 個別送信
                    server.send_message(msg)
                    success_count += 1
                    print(f"メール送信成功: {recipient_email}")
                    
                except Exception as e:
                    failed_recipients.append(recipient_email)
                    print(f"メール送信失敗 ({recipient_email}): {e}")
            
            server.quit()
            
            print(f"メール送信完了: 成功 {success_count}件, 失敗 {len(failed_recipients)}件")
            if failed_recipients:
                print(f"送信失敗した宛先: {', '.join(failed_recipients)}")
            
        except Exception as e:
            print(f"メール送信エラー (SMTP接続): {e}")

    def run_daily_collection(self, recipient_emails: List[str] = None):
        """日次のニュース収集・要約・配信"""
        print(f"ニュース収集開始: {datetime.now()}")
        
        if self.test_mode:
            # テストモード：テストデータを使用
            print("[TEST MODE] テストデータを使用しています")
            filtered_news, _ = self.load_test_data()
            print(f"テストニュース数: {len(filtered_news)}")
        else:
            # 本番モード：実際のニュース収集
            rss_news = self.collect_rss_news()
            api_news = self.collect_news_api()
            all_news = rss_news + api_news
            
            print(f"収集したニュース数: {len(all_news)}")
            
            # フィルタリング・重複除去
            filtered_news = self.filter_and_deduplicate(all_news)
            print(f"フィルタリング後: {len(filtered_news)}")
             
        # Claude で要約
        summary = self.summarize_with_claude(filtered_news)
        
        # 結果を保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON形式で保存
        with open(f'ai_news_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'summary': summary,
                'news_count': len(filtered_news),
                'news_items': [
                    {
                        'title': item.title,
                        'url': item.url,
                        'published': item.published.isoformat(),
                        'source': item.source
                    }
                    for item in filtered_news
                ]
            }, f, ensure_ascii=False, indent=2)
        
        # テキスト形式で保存
        with open(f'ai_news_summary_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("ファイル保存完了")
        
        # メール設定の読み込み
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        sender_email = os.getenv('EMAIL_ADDRESS')
        sender_password = os.getenv('EMAIL_PASSWORD')

        # メール送信（設定されている場合）
        if recipient_emails and len(recipient_emails) > 0:
            self.send_email_summary(
                summary, 
                recipient_emails,
                smtp_server,
                smtp_port,
                sender_email,
                sender_password,
                filtered_news,
            )
        
        return summary


def parse_recipient_emails(email_env_var: str) -> List[str]:
    """環境変数から複数のメールアドレスをパースする（カンマ区切り対応）"""
    if not email_env_var:
        return []
    
    # カンマ区切りでメールアドレスを分割し、空白を除去
    emails = [email.strip() for email in email_env_var.split(',')]
    
    # 空の要素を除去し、有効なメールアドレスのみを返す
    valid_emails = []
    for email in emails:
        if email and '@' in email:  # 簡単な検証
            valid_emails.append(email)
        elif email:  # 無効なアドレスがある場合は警告
            print(f"警告: 無効なメールアドレス形式をスキップしました: '{email}'")
    
    return valid_emails

# 使用例
def main():
    load_dotenv()  # .envファイルから環境変数を読み込む
    
    # テストモードの判定（環境変数またはコマンドライン引数）
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true" or "--test" in sys.argv
    
    if test_mode:
        print("=== テストモードで実行中 ===")
        collector = AINewsCollector("", test_mode=True)
    else:
        # API Key設定
        ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        if not ANTHROPIC_API_KEY:
            print("エラー: ANTHROPIC_API_KEYが設定されていません")
            return
        collector = AINewsCollector(ANTHROPIC_API_KEY, test_mode=False)
    
    # メールアドレスの取得・パース（テストモードでは無効）
    recipient_emails = None
    if not test_mode:
        # RECIPIENT_EMAILS (複数対応) または RECIPIENT_EMAIL (後方互換性) から取得
        email_env = os.getenv('RECIPIENT_EMAILS') or os.getenv('RECIPIENT_EMAIL')
        recipient_emails = parse_recipient_emails(email_env)
        if recipient_emails:
            print(f"メール送信対象: {len(recipient_emails)}件 - {', '.join(recipient_emails)}")
    
    # ニュース収集・要約実行
    summary = collector.run_daily_collection(recipient_emails)
    
    print("\n=== 今日のAIニュース要約 ===")
    print(summary)


if __name__ == "__main__":
    main()
