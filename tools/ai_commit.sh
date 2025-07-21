#!/bin/bash
# Claude Code CLI を使用したコミットメッセージ自動生成
set -euo pipefail

# 色付きログ関数
log_info() { echo -e "\033[0;32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[0;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# 設定
CLAUDE_MODEL="sonnet"  # sonnet または opus

# Gitリポジトリチェック
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [[ -z "$REPO_ROOT" ]]; then
    log_error "このディレクトリはGitリポジトリではありません。"
    exit 1
fi
cd "$REPO_ROOT"

# 一時ファイル作成（自動削除設定）
TMP_DIFF=$(mktemp)
trap 'rm -f "$TMP_DIFF"' EXIT

# ステージング状況確認とファイル生成
if ! git diff --cached --quiet; then
    # ステージング済み変更をファイルに保存
    echo "=== STAGED CHANGES SUMMARY ===" > "$TMP_DIFF"
    git diff --cached --stat >> "$TMP_DIFF"
    echo -e "\n=== DETAILED DIFF ===" >> "$TMP_DIFF"
    git diff --cached --diff-filter=ACMRT >> "$TMP_DIFF"
    log_info "ステージング済み変更を検出しました"
elif git diff --quiet; then
    log_warn "変更がありません。ファイルを編集してからステージングしてください。"
    exit 0
else
    log_warn "ステージングされた差分がありません。'git add' でファイルをステージングしてください。"
    echo -e "\n変更されたファイル:"
    git status --porcelain | head -5
    exit 0
fi

# Claude Code CLI の存在確認
if ! command -v claude &> /dev/null; then
    log_error "Claude Code CLI が見つかりません。"
    echo "インストール方法: https://docs.anthropic.com/claude-code/quickstart"
    exit 1
fi

log_info "AI分析によるコミットメッセージ生成中..."

# プロンプトの最適化版
PROMPT="以下のGit差分から、Conventional Commits形式の**1行**コミットメッセージを生成してください。

**厳格な要件:**
- 形式: \`<type>(<scope>): <description>\`
- type: feat/fix/docs/style/refactor/test/chore/perf/ci/build
- scope: 変更対象モジュール（省略可）
- description: 50文字以内、命令形、小文字開始
- **メッセージのみ出力** - 説明や追加テキスト不要

**良い例:**
feat(auth): add OAuth2 authentication
fix: resolve memory leak in parser
docs: update API documentation
refactor(db): simplify query logic

差分データ:"

# Claude Code CLI でメッセージ生成
if MESSAGE=$(cat "$TMP_DIFF" | claude -p "$PROMPT" --model "$CLAUDE_MODEL" 2>/dev/null); then
    
    # Extract just the commit message from the response (remove markdown formatting and explanations)
    MESSAGE=$(echo "$MESSAGE" | grep -E '^[a-z]+(\([^)]+\))?:[[:space:]]' | head -1)
    
    # If no properly formatted message found, try to extract from code blocks
    if [[ -z "$MESSAGE" ]]; then
        MESSAGE=$(echo "$MESSAGE" | sed -n '/```/,/```/p' | grep -E '^[a-z]+(\([^)]+\))?:[[:space:]]' | head -1)
    fi
    
    # Final fallback: use raw response if still empty
    if [[ -z "$MESSAGE" ]]; then
        FULL_RESPONSE=$(cat "$TMP_DIFF" | claude -p "$PROMPT" --model "$CLAUDE_MODEL" 2>/dev/null)
        MESSAGE=$(echo "$FULL_RESPONSE" | head -1)
        log_warn "使用された非標準メッセージ: 手動確認が必要です"
    fi
else
    log_error "Claude Code CLI へのリクエストが失敗しました。"
    echo "確認事項:"
    echo "- claude コマンドが正しくインストールされているか"
    echo "- APIキーが設定されているか (claude で初回セットアップ)"
    echo "- インターネット接続が正常か"
    exit 1
fi

# メッセージのクリーニング（余分な文字・改行除去）
MESSAGE=$(echo "$MESSAGE" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//' | tr -d '\n\r' | head -c 100)

# 基本的な形式検証
if ! echo "$MESSAGE" | grep -q "^[a-z][a-z]*\(([^)]*)\)\?:"; then
    log_warn "生成されたメッセージが Conventional Commits 形式ではありません"
fi

# 結果表示
echo
echo "╭─────────────────────────────────────────────────╮"
echo "│          AI Generated Commit Message            │"
echo "╰─────────────────────────────────────────────────╯"
echo -e "\033[1;36m$MESSAGE\033[0m"
echo

# ユーザー選択
echo "選択してください:"
echo "  1) このメッセージでコミット"
echo "  2) メッセージを編集"
echo "  3) 再生成する"
echo "  4) キャンセル"
echo

read -p "番号を入力 (1-4) [1]: " -r choice
choice=${choice:-1}

case "$choice" in
    1)
        git commit -m "$MESSAGE"
        log_info "コミット完了: $MESSAGE"
        ;;
    2)
        TEMP_MSG=$(mktemp)
        echo "$MESSAGE" > "$TEMP_MSG"
        ${EDITOR:-nano} "$TEMP_MSG"
        
        if [[ -s "$TEMP_MSG" ]]; then
            EDITED_MESSAGE=$(cat "$TEMP_MSG")
            git commit -m "$EDITED_MESSAGE"
            log_info "編集されたメッセージでコミット完了: $EDITED_MESSAGE"
        else
            log_warn "空のメッセージのためキャンセルされました。"
        fi
        rm -f "$TEMP_MSG"
        ;;
    3)
        log_info "メッセージを再生成中..."
        # スクリプト自体を再実行
        exec "$0"
        ;;
    4|*)
        log_info "コミットがキャンセルされました。"
        ;;
esac