#!/usr/bin/env python3
"""
毎朝ニュースダイジェスト送信スクリプト
キンコーズ・ジャパン 渡辺浩基社長向け
"""

import feedparser
import smtplib
import os
import hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# ─────────────────────────────────────────
# 設定
# ─────────────────────────────────────────
RECIPIENT = "wkoki2000@gmail.com"
SENDER    = os.environ.get("GMAIL_ADDRESS", "wkoki2000@gmail.com")
APP_PASS  = os.environ.get("GMAIL_APP_PASSWORD", "")   # Gmailアプリパスワード

JST = timezone(timedelta(hours=9))

# ─────────────────────────────────────────
# ニュースカテゴリ（優先順位順）
# ─────────────────────────────────────────
CATEGORIES = [
    {
        "id": "konica",
        "label": "📊 コニカミノルタ関連",
        "color": "#1a56db",
        "keywords": [
            "コニカミノルタ",
            "Konica Minolta",
        ],
    },
    {
        "id": "print_tech",
        "label": "🖨️ 印刷・コピー・オフィスサービス",
        "color": "#0e9f6e",
        "keywords": [
            "印刷 新技術",
            "デジタル印刷 新商品",
            "コピーサービス 新製品",
            "オフィスサービス DX",
            "印刷機 新製品",
        ],
    },
    {
        "id": "competitor",
        "label": "⚔️ 競合・ネットプリント動向",
        "color": "#e3a008",
        "keywords": [
            "ラクスル",
            "プリントパック",
            "グラフィック 印刷",
            "アクセア",
            "ネットプリント",
            "プリントショップ 新サービス",
        ],
    },
    {
        "id": "economy_dx",
        "label": "🌐 日本経済・DX・SX",
        "color": "#7e3af2",
        "keywords": [
            "日本経済 最新",
            "DX デジタルトランスフォーメーション",
            "SX サステナビリティトランスフォーメーション",
            "日銀 金融政策",
            "円相場 為替",
        ],
    },
    {
        "id": "ai",
        "label": "🤖 AI最新動向",
        "color": "#ff5a1f",
        "keywords": [
            "生成AI 最新",
            "ChatGPT 新機能",
            "Claude AI",
            "Gemini AI",
            "AI 企業活用",
            "LLM 大規模言語モデル",
        ],
    },
    {
        "id": "saas",
        "label": "☁️ SaaS関連",
        "color": "#3f83f8",
        "keywords": [
            "SaaS 新サービス",
            "クラウド サービス 日本",
            "企業向けSaaS",
        ],
    },
    {
        "id": "stocks_realestate",
        "label": "💹 株価・不動産",
        "color": "#c81e1e",
        "keywords": [
            "日経平均 株価",
            "東証 株式市場",
            "不動産 市況",
            "REIT 不動産",
            "オフィス賃料 東京",
        ],
    },
]

# ─────────────────────────────────────────
# Google News RSSからフェッチ
# ─────────────────────────────────────────
def google_news_url(keyword: str) -> str:
    from urllib.parse import quote
    return f"https://news.google.com/rss/search?q={quote(keyword)}&hl=ja&gl=JP&ceid=JP:ja"

def fetch_articles(keyword: str, max_hours: int = 24) -> list:
    url = google_news_url(keyword)
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    cutoff = datetime.now(tz=JST) - timedelta(hours=max_hours)
    articles = []

    for entry in feed.entries[:8]:
        # 日時パース
        pub = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(JST)

        if pub and pub < cutoff:
            continue

        articles.append({
            "title": entry.get("title", "（タイトルなし）"),
            "link":  entry.get("link", "#"),
            "source": entry.get("source", {}).get("title", ""),
            "published": pub.strftime("%m/%d %H:%M") if pub else "日時不明",
            "hash": hashlib.md5(entry.get("link", "").encode()).hexdigest(),
        })

    return articles

def collect_news() -> dict:
    """全カテゴリのニュースを収集し、重複を除いて返す"""
    seen_hashes = set()
    result = {}

    for cat in CATEGORIES:
        cat_articles = []
        for kw in cat["keywords"]:
            for art in fetch_articles(kw):
                if art["hash"] not in seen_hashes:
                    seen_hashes.add(art["hash"])
                    cat_articles.append(art)
            if len(cat_articles) >= 10:
                break

        result[cat["id"]] = cat_articles[:10]

    return result

# ─────────────────────────────────────────
# HTMLメール生成
# ─────────────────────────────────────────
def build_html(news_by_cat: dict) -> str:
    now = datetime.now(tz=JST)
    date_str = now.strftime("%Y年%m月%d日（%a）%H:%M")

    # カテゴリセクション生成
    sections_html = ""
    total_count = sum(len(v) for v in news_by_cat.values())

    for cat in CATEGORIES:
        articles = news_by_cat.get(cat["id"], [])
        if not articles:
            continue

        items_html = ""
        for art in articles:
            source_badge = f'<span style="background:#f3f4f6;color:#6b7280;font-size:11px;padding:1px 6px;border-radius:10px;margin-left:6px;">{art["source"]}</span>' if art["source"] else ""
            items_html += f"""
            <tr>
              <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
                <a href="{art['link']}" style="color:#111827;text-decoration:none;font-size:14px;line-height:1.5;font-weight:500;">
                  {art['title']}
                </a>
                <div style="margin-top:3px;">
                  <span style="color:#9ca3af;font-size:11px;">{art['published']}</span>
                  {source_badge}
                </div>
              </td>
            </tr>
            """

        sections_html += f"""
        <div style="margin-bottom:28px;">
          <div style="background:{cat['color']};color:#fff;padding:8px 16px;border-radius:6px 6px 0 0;font-size:14px;font-weight:700;">
            {cat['label']} <span style="font-weight:400;font-size:12px;">({len(articles)}件)</span>
          </div>
          <div style="border:1px solid #e5e7eb;border-top:none;border-radius:0 0 6px 6px;padding:0 16px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {items_html}
            </table>
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:'Helvetica Neue',Arial,'Hiragino Kaku Gothic ProN',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:20px 0;">
    <tr><td align="center">
      <table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1);">

        <!-- ヘッダー -->
        <tr>
          <td style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);padding:24px 32px;">
            <div style="color:#fff;font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">KINKO'S JAPAN</div>
            <div style="color:#fff;font-size:22px;font-weight:700;">毎朝ニュースダイジェスト</div>
            <div style="color:#93c5fd;font-size:13px;margin-top:4px;">{date_str} ／ 本日 {total_count}件</div>
          </td>
        </tr>

        <!-- 本文 -->
        <tr>
          <td style="padding:24px 32px;">
            {sections_html}
          </td>
        </tr>

        <!-- フッター -->
        <tr>
          <td style="background:#f3f4f6;padding:16px 32px;text-align:center;color:#9ca3af;font-size:11px;border-top:1px solid #e5e7eb;">
            このメールはキンコーズ・ジャパン ニュースダイジェストシステムにより自動送信されています。<br>
            ニュースはGoogle News RSSから取得しています。
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""
    return html

# ─────────────────────────────────────────
# メール送信
# ─────────────────────────────────────────
def send_email(html: str):
    now = datetime.now(tz=JST)
    subject = f"【朝刊ダイジェスト】{now.strftime('%Y/%m/%d')} キンコーズ・ジャパン 渡辺社長向けニュース"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT

    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, APP_PASS)
        server.sendmail(SENDER, [RECIPIENT], msg.as_string())

    print(f"[OK] 送信完了: {RECIPIENT}  ({now.strftime('%H:%M:%S')})")

# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────
def main():
    print(f"[INFO] ニュース収集開始 ({datetime.now(tz=JST).strftime('%Y-%m-%d %H:%M')})")
    news = collect_news()

    total = sum(len(v) for v in news.values())
    print(f"[INFO] 収集完了: 合計 {total} 件")

    if total == 0:
        print("[WARN] 記事が0件のため送信をスキップします")
        return

    html = build_html(news)
    send_email(html)

if __name__ == "__main__":
    main()
