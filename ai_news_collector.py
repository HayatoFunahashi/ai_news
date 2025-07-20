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
from dotenv import load_dotenv
import os

@dataclass
class NewsItem:
    title: str
    url: str
    published: datetime
    content: str
    source: str

class AINewsCollector:
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        
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
    
    def summarize_with_claude(self, news_items: List[NewsItem]) -> str:
        """Claudeを使ってニュースを要約"""
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
以下のAI関連ニュースを分析して、投資判断に役立つ要約を作成してください：

{news_text}

以下の観点で要約してください：
1. 主要なトレンドや動向
2. 注目すべき企業や技術
3. 市場への潜在的影響
4. 投資家が注目すべきポイント

簡潔で分かりやすい日本語でお願いします。
"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-7-sonnet-20250219",
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
    
    def send_email_summary(self, summary: str, recipient_email: str, 
                          smtp_server: str, smtp_port: int, 
                          sender_email: str, sender_password: str):
        """メールで要約を送信"""
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"AI News Summary - {datetime.now().strftime('%Y-%m-%d')}"
            
            body = f"""
AI関連ニュース要約レポート
生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{summary}

---
このメールは自動生成されました。
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            print("メール送信完了")
            
        except Exception as e:
            print(f"メール送信エラー: {e}")
    
    def run_daily_collection(self, recipient_email: str = None):
        """日次のニュース収集・要約・配信"""
        print(f"ニュース収集開始: {datetime.now()}")
        
        # ニュース収集
        rss_news = self.collect_rss_news()
        api_news = self.collect_news_api()
        all_news = rss_news + api_news
        
        print(f"収集したニュース数: {len(all_news)}")
        
        # フィルタリング・重複除去
        filtered_news = self.filter_and_deduplicate(all_news)
        print(f"フィルタリング後: {len(filtered_news)}")
        
        # Claude で要約
        summary = self.summarize_with_claude(filtered_news)
        # summary = ""
        
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
        smtp_port = int(os.getenv('SMTP_PORT'))
        sender_email = os.getenv('EMAIL_ADDRESS')
        sender_password = os.getenv('EMAIL_PASSWORD')

        # メール送信（設定されている場合）
        if recipient_email:
            self.send_email_summary(
                summary, 
                recipient_email,
                smtp_server,
                smtp_port,
                sender_email,
                sender_password
            )
        
        return summary


# 使用例
def main():
    load_dotenv()  # .envファイルから環境変数を読み込む
    # API Key設定
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # インスタンス作成
    collector = AINewsCollector(ANTHROPIC_API_KEY)
    
    # ニュース収集・要約実行
    summary = collector.run_daily_collection("hayato_funahashi@icloud.com")
    
    print("\n=== 今日のAIニュース要約 ===")
    print(summary)


if __name__ == "__main__":
    main()
