# salon-reservation-app

Hair Salon Flare

予約管理システムヘアサロン「Flare（フレア）」の業務効率化を目的とした、会員制予約管理システムです。
スタイリストのランクに応じた自動料金計算や、予約ステータスのリアルタイム管理を実現します。

## 📋 プロジェクト概要背景
現在このサロンでは表計算ソフトで管理を行っていますが、繁忙期における予約の重複、料金の入力ミス、スタイリストの稼働状況の不透明さが課題となっています。

解決する課題予約重複の防止: スタイリストごとのスケジュールをDBで一元管理し、物理的な重複を阻止。
計算ミスの排除: 「メニュー × スタイリストランク」に基づいた料金・所要時間の自動算出。
情報の集約: 分散していた会員情報、スタイリスト情報、施術履歴を統合。


## 🛠 技術スタック

Framework: Python / Flask
Database: SQLite(ローカル) / PostgreSQL(本番予定) (SQLAlchemy ORM)
Template Engine: Jinja2
Frontend: HTML5, Tailwind CSS, JavaScript
Forms: Flask-WTF (バリデーション用)

## 📐 システム設計
1. データベース構造 (ER図の核)
一対多: Customers → Reservations / Ranks → Stylists
多対多: Reservations ↔ Menus (中間テーブル: ReservationMenus)
依存関係: MenuPrices は Menus と Ranks の組み合わせで一意に決定。

## ER図を挿入予定

3. ルーティング設計


## 🚀 主要機能と業務フロー予約作成フロー会員検索: 既存顧客の特定（または新規登録）。
条件入力: スタイリスト選択、日付選択。動的計算: メニュー選択時、スタイリストランクに基づき料金と所要時間を自動計算。
重複チェック: 保存前に該当スタイリストの空き枠を最終確認。当日運用フロー予約一覧画面からワンクリックでステータスを更新し、店内の稼働状況を可視化します。reserved → checked_in → in_progress → completedキャンセル時はログ保持のため cancelled へ更新（枠は自動解放）。

## 🔐 権限と運用ルール職能制限 (Role-based Access Control)
スタッフ: 予約の作成・編集、会員情報の閲覧、ステータス更新。
店長 (Admin): 上記に加え、メニュー価格の変更、税率設定、マスタ削除権限。
休日・スケジュールルール定休日：毎週月曜日（システム側で選択不可に制御）。
特殊休暇：スタイリスト個別の休暇は、今後のアップデートにて stylist_attendance テーブルで管理予定。

## 🛠 セットアップリポジトリのクローン
Bashgit clone https://github.com/your-repo/salon-reservation-app.git
cd salon-reservation-app
依存パッケージのインストールBash pip install -r requirements.txt
データベースの初期化とデータ投入 Bash   # 初期マスタデータの投入（Ranks, Menus, Stylists, MenuPrices etc.）
   python seed_data.py
アプリケーションの起動Bashflask run

## 📅 今後のロードマップ (Update Plan)
[ ] 個別休日管理: スタイリストごとの有給・特別休暇設定機能。
[ ] 税率管理機能: 店長画面からの消費税率一括変更。
[ ] 売上集計ダッシュボード: 日次・月次の簡易売上レポート表示。

## 💡 補足
予約作成時の料金計算ロジックは services/reservation_service.py に集約されています。
スタイリストランク A〜C によって menu_prices テーブルから取得する値が変動します。
