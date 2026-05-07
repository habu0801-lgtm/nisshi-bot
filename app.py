import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# ローカル開発用：.envを読み込む
NISSHI_BOT_DIR = Path.home() / "nisshi-bot"
load_dotenv(NISSHI_BOT_DIR / ".env", override=True)

# Streamlit Cloud用：Secretsがあれば環境変数に設定する（ローカルはsecretsなしでも動く）
try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    if "GOOGLE_CHAT_WEBHOOK" in st.secrets:
        os.environ["GOOGLE_CHAT_WEBHOOK"] = st.secrets["GOOGLE_CHAT_WEBHOOK"]
except Exception:
    pass

sys.path.insert(0, str(NISSHI_BOT_DIR))
from report import generate_daily_report, post_to_google_chat

st.title("飲食店 日報Bot")

if "stage" not in st.session_state:
    st.session_state.stage = "input"

# --- Stage 1: データ入力 ---
if st.session_state.stage == "input":
    st.header("本日の実績を入力してください")

    date = st.text_input("日付", placeholder="例：2026年4月30日")

    st.subheader("売上（円）")
    col1, col2 = st.columns(2)
    with col1:
        lunch_sales = st.number_input("ランチ売上", min_value=0, step=1000)
    with col2:
        dinner_sales = st.number_input("ディナー売上", min_value=0, step=1000)

    st.subheader("客数（人）")
    col3, col4 = st.columns(2)
    with col3:
        lunch_count = st.number_input("ランチ客数", min_value=0, step=1)
    with col4:
        dinner_count = st.number_input("ディナー客数", min_value=0, step=1)

    staff_count = st.number_input("スタッフ数（人）", min_value=1, step=1)
    memo = st.text_area("特記事項（任意）", placeholder="例：雨天で出足が遅かった、新メニュー好評など")

    if date and st.button("日報を生成する", type="primary"):
        total_sales = lunch_sales + dinner_sales
        total_count = lunch_count + dinner_count

        data = {
            "日付": date,
            "売上": {
                "ランチ": lunch_sales,
                "ディナー": dinner_sales,
                "合計": total_sales,
            },
            "客数": {
                "ランチ": lunch_count,
                "ディナー": dinner_count,
                "合計": total_count,
            },
            "スタッフ数": staff_count,
            "特記事項": memo if memo else "なし",
        }

        with st.spinner("日報を生成中..."):
            report = generate_daily_report(data)

        st.session_state.report = report
        st.session_state.stage = "confirm"
        st.rerun()

# --- Stage 2: 確認・投稿 ---
elif st.session_state.stage == "confirm":
    st.header("生成された日報を確認")

    report = st.session_state.report
    st.text(report)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        webhook_url = os.environ.get("GOOGLE_CHAT_WEBHOOK")
        if st.button("Google Chatに投稿する", type="primary"):
            if not webhook_url:
                st.error("GOOGLE_CHAT_WEBHOOK が設定されていません。")
            else:
                try:
                    post_to_google_chat(report, webhook_url)
                    st.success("Google Chatに投稿しました！")
                    st.session_state.stage = "input"
                    st.rerun()
                except RuntimeError as e:
                    st.error(str(e))

    with col2:
        if st.button("やり直す"):
            st.session_state.stage = "input"
            st.rerun()
