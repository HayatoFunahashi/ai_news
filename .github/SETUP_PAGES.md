# GitHub Pages セットアップガイド

このガイドでは、AI News DashboardをGitHub Pagesで公開するためのセットアップ手順を説明します。

## 🔧 必須設定

### 1. GitHub Pagesの有効化

1. GitHubリポジトリのページにアクセス
2. **Settings** タブをクリック
3. 左サイドバーから **Pages** をクリック
4. **Source** を `GitHub Actions` に設定
5. **Save** をクリック

### 2. Secretsの設定

**Settings** > **Secrets and variables** > **Actions** で以下のSecretsを追加：

#### 必須 (メール送信機能用)
```
ANTHROPIC_API_KEY         # Anthropic APIキー
SMTP_SERVER              # smtp.gmail.com
SMTP_PORT                # 587
EMAIL_ADDRESS            # 送信元メールアドレス
EMAIL_PASSWORD           # Gmailアプリパスワード
RECIPIENT_EMAILS         # 受信者メールアドレス（カンマ区切り）
```

#### オプション
```
NEWS_API_KEY             # NewsAPI キー（オプション）
```

### 3. リポジトリ権限の確認

**Settings** > **Actions** > **General** で以下を確認：

- **Actions permissions**: `Allow all actions and reusable workflows`
- **Workflow permissions**: `Read and write permissions`

## 🚀 デプロイ方法

### 自動デプロイ
- **毎日 8:00 (JST)** に自動実行
- 新しいニュース収集・分析・デプロイが行われます

### 手動デプロイ
1. **Actions** タブをクリック
2. **Deploy AI News Dashboard** ワークフローを選択
3. **Run workflow** をクリック
4. **Run workflow** ボタンをクリック

## 🔍 トラブルシューティング

### よくある問題

#### ❌ "Pages not enabled" エラー
**解決方法**: GitHub Pagesが有効化されていません。上記の手順1を実行してください。

#### ❌ "Secrets not found" エラー
**解決方法**: 必要なSecretsが設定されていません。上記の手順2を実行してください。

#### ❌ "Permission denied" エラー
**解決方法**: ワークフローの権限が不足しています。上記の手順3を確認してください。

### デバッグ方法

1. **Actions** タブでワークフローの実行ログを確認
2. 各ステップの詳細ログを展開して確認
3. `Verify generated files` ステップで必要なファイルが生成されているか確認

## 📱 アクセス方法

設定完了後、以下のURLでダッシュボードにアクセス可能：

```
https://[ユーザー名].github.io/[リポジトリ名]/
```

例: `https://hayatofunahashi.github.io/ai_news/`

## 🔄 更新プロセス

1. **データ収集**: RSS/NewsAPIからニュース取得
2. **AI分析**: Claude APIで投資観点での要約生成
3. **データ集約**: JSONファイルを統合してダッシュボード用データ作成
4. **デプロイ**: GitHub Pagesに静的サイトをデプロイ

## 💡 Tips

- テストモードでは既存データを使用してAPIコストを節約
- 本番実行はスケジュール実行時のみ
- 手動実行では既存データでダッシュボードを更新