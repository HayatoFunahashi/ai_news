import markdown2
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    sender_email: str
    sender_password: str


class EmailHandler:
    def __init__(self, config: EmailConfig = None):
        self.config = config
    
    def _create_html_content(self, summary: str, news_items: List, max_items: int = 20) -> str:
        """HTMLメールのコンテンツを生成"""
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('email_template.html')

        # Markdown要約をHTMLに変換
        summary_html = markdown2.markdown(summary)

        # テンプレートに渡すデータ
        return template.render(
            date=datetime.now().strftime('%Y-%m-%d'),
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            news_items=news_items[:max_items],
            summary_html=summary_html
        )

    def send_email_summary(self, summary: str, recipient_emails: List[str], 
                          news_items: List, config: EmailConfig = None):
        """テンプレートを使って複数の宛先にHTMLメールを送信"""
        # 設定の優先順位: 引数 > インスタンス変数
        email_config = config or self.config
        
        if not email_config:
            raise ValueError("EmailConfigが設定されていません")
            
        if not recipient_emails:
            print("送信先メールアドレスが指定されていません")
            return
            
        try:
            html_content = self._create_html_content(summary, news_items)

            # SMTP接続を一度だけ確立
            server = smtplib.SMTP(email_config.smtp_server, email_config.smtp_port)
            server.starttls()
            server.login(email_config.sender_email, email_config.sender_password)
            
            success_count = 0
            failed_recipients = []
            
            # 各受信者に個別にメール送信
            for recipient_email in recipient_emails:
                try:
                    # メール構築
                    msg = MIMEMultipart()
                    msg['From'] = email_config.sender_email
                    msg['To'] = recipient_email
                    msg['Subject'] = f"🤖 AI News Summary - {datetime.now().strftime('%Y-%m-%d')}"
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

    @staticmethod
    def get_email_config_from_env() -> EmailConfig:
        """環境変数からメール設定を取得"""
        return EmailConfig(
            smtp_server=os.getenv('SMTP_SERVER'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            sender_email=os.getenv('EMAIL_ADDRESS'),
            sender_password=os.getenv('EMAIL_PASSWORD')
        )

    @staticmethod
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