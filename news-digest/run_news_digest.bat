@echo off
REM =====================================================
REM  毎朝ニュースダイジェスト 起動バッチ
REM  キンコーズ・ジャパン 渡辺浩基社長向け
REM =====================================================

REM ── Gmailアプリパスワードをここに設定 ──────────────
set GMAIL_ADDRESS=wkoki2000@gmail.com
set GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
REM ────────────────────────────────────────────────────

REM スクリプトのあるフォルダに移動
cd /d "%~dp0"

REM ログファイルに日付付きで記録
echo. >> news_digest.log
echo ========================================== >> news_digest.log
echo 実行日時: %DATE% %TIME% >> news_digest.log
echo ========================================== >> news_digest.log

REM Python実行（python.exeのパスはご自身の環境に合わせて変更）
python news_digest.py >> news_digest.log 2>&1

echo 完了: %DATE% %TIME% >> news_digest.log
