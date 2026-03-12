# 毎朝ニュースダイジェスト セットアップガイド

## 概要

毎朝6時にニュースを自動収集して `wkoki2000@gmail.com` へ送信するスクリプトです。

---

## ステップ1：Gmailアプリパスワードの取得

Gmailの通常パスワードは使えません。以下の手順で**アプリパスワード**を取得してください。

1. Googleアカウント（wkoki2000@gmail.com）にログイン
2. [Googleアカウント設定](https://myaccount.google.com/) → **セキュリティ**
3. **2段階認証プロセス** を有効化（未設定の場合）
4. 2段階認証設定ページ下部の **「アプリパスワード」** をクリック
5. アプリ名に「ニュースダイジェスト」と入力 → **作成**
6. 表示された **16桁のパスワード**（スペースなし）をメモ

---

## ステップ2：スクリプトのセットアップ

### 必要なもの
- Python 3.8以上
- 常時起動のPC または サーバー

### インストール

```bash
cd news-digest
pip install -r requirements.txt
```

### 環境変数の設定

```bash
# ~/.bashrc または ~/.zshrc に追記
export GMAIL_ADDRESS="wkoki2000@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"   # 取得した16桁
```

設定を反映：
```bash
source ~/.bashrc
```

### 動作テスト（手動実行）

```bash
python3 news_digest.py
```

メールが届けば成功です。

---

## ステップ3：毎朝6時に自動実行（cron設定）

### Macの場合

```bash
crontab -e
```

以下を追記：

```cron
0 6 * * * GMAIL_ADDRESS="wkoki2000@gmail.com" GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx" /usr/bin/python3 /path/to/news-digest/news_digest.py >> /tmp/news_digest.log 2>&1
```

### Windowsの場合（タスクスケジューラ）

1. タスクスケジューラを開く
2. 「タスクの作成」→ トリガー：毎日 6:00
3. 操作：`python C:\path\to\news_digest.py`
4. 環境変数を「開始オプション」またはバッチファイル経由で設定

### クラウド（Google Cloud Run Jobs / AWS Lambda）を使う場合

PCを起動しっぱなしにしたくない場合はご相談ください。
月数十円〜無料枠で運用できます。

---

## カスタマイズ

`news_digest.py` の `CATEGORIES` リストを編集することで、
キーワードの追加・削除・順序変更ができます。

```python
{
    "id": "my_category",
    "label": "🔍 カテゴリ名",
    "color": "#ff0000",      # ヘッダーの色（16進数カラーコード）
    "keywords": [
        "キーワード1",
        "キーワード2",
    ],
},
```

---

## トラブルシューティング

| エラー | 対処 |
|--------|------|
| `SMTPAuthenticationError` | アプリパスワードが間違っている。再発行して再設定 |
| `記事が0件` | インターネット接続を確認。VPN使用時は解除して試す |
| メールが迷惑メールに入る | 送受信ともに同じGmailアドレスの場合は通常届きます |
