#!/usr/bin/env python3
"""GPT-4oで飲食店の日報を生成してGoogle Chatへ投稿する。"""

import json
import os
import urllib.error
import urllib.request

from openai import OpenAI


def generate_daily_report(data: dict) -> str:
    """GPT-4oで日報テキストを生成する。"""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt = f"""
あなたは飲食店の優秀な店長です。
以下の本日の実績データをもとに、スタッフ向けの日報を作成してください。

実績データ：
{json.dumps(data, ensure_ascii=False, indent=2)}

レポートの要件：
1. 冒頭に「{data['日付']} 日報」と入れる
2. 売上・客数・客単価をまとめる（客単価はデータから自動計算する）
3. 【良かった点】を1〜2つ挙げる
4. 【課題・改善点】を1〜2つ挙げる
5. 【明日に向けて】を一言添える
6. 特記事項がある場合はそれも反映する

出力形式：
- 必ずプレーンテキストで出力する
- #、##、*、**、- などのMarkdown記法は絶対に使わない
- 【】と・を使った読みやすい形式にする
- LINEに投稿することを想定した簡潔な文章
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()


def post_to_google_chat(text: str, webhook_url: str) -> None:
    """Google Chatにテキストを投稿する。"""
    payload = {"text": text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            if not (200 <= response.getcode() < 300):
                raise RuntimeError(f"Google Chat投稿に失敗しました: HTTP {response.getcode()}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Google Chat投稿に失敗しました: HTTP {exc.code} {detail}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Google Chatへの接続に失敗しました: {exc.reason}")
