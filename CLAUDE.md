# nisshi-bot プロジェクト概要

## このツールの目的
飲食店スタッフが毎日の売上・客数を入力するだけで、
AIが日報を自動生成してGoogle Chat（将来的にはLINE）に投稿するツール。

## 想定ユーザー
- 飲食店の店舗スタッフ（ITリテラシー問わず）
- スマホからでも使えるシンプルなUIを維持すること

## ファイル構成
- app.py：StreamlitのUI（入力画面・確認画面）
- report.py：GPT-4oによる日報生成・Google Chat投稿
- requirements.txt：Streamlit Cloud用の依存パッケージ
- .env：APIキー（ローカル開発用・Gitに含めない）

## 開発ルール
- UIはシンプルに保つ（項目を増やしすぎない）
- 出力テキストはMarkdown記法を使わない（LINEで表示するため）
- APIキーは必ず.envまたはStreamlit Secrets経由で管理する

## 投稿先の方針

現時点ではGoogle Chat Webhookは未設定（日報生成機能のみで運用）。

実際のクライアント提案時にLINE連携を実装する方針：
- 飲食店の業務連絡はLINEが主流のため、Google ChatよりLINEの方が実用的
- LINE連携は report.py の post_to_google_chat() をLINE Messaging API呼び出しに差し替えるだけ
- LINE公式アカウント（月額費用あり）が必要なため、クライアント確定後に設定する

## 将来的な拡張予定
- 投稿先をLINEに変更（LINE Messaging API）
- 週報・月報の自動集計機能
- 売上目標との比較表示
