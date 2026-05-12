# app/reservations/routes.py

from flask import (
    Blueprint, render_template,
    request, redirect, url_for, flash
)

from datetime import datetime, date
from collections import defaultdict

from app.extensions import db

from app.models import (
    Reservations,
    Customers,
    Stylists,
    Menus,
    MenuPrices
)

from app.services.reservation_service import (
    calculate_end_time,
    calculate_reservation_price
)

reservations_bp = Blueprint(
    "reservations",
    __name__
)


# =================
#   RESERVATION
# =================
# 予約一覧
@reservations_bp.route('/reservations', methods=['GET'])
def reservations_index():

    now = datetime.now()

    date_str = request.args.get("date")

    # 基本のクエリ
    query = Reservations.query

    # 日付がある場合だけ絞る
    if date_str:
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        target_date = current_date.date()

        query = query.filter(
            db.func.date(Reservations.start_time) == target_date
        )
    else:
        current_date = now

    # 並び替え（デフォルト昇順）
    query = query.order_by(Reservations.start_time.asc())

    # ここで一回だけ取得
    reservations = query.all()

    # UI用
    is_today = current_date.date() == now.date()
    today_str = now.strftime("%Y-%m-%d")

    stylist_id = request.args.get("stylist")

    if stylist_id:
        query = query.filter(Reservations.stylist_id == stylist_id)

    sort = request.args.get("sort", "asc")

    if sort == "desc":
        query = query.order_by(Reservations.start_time.desc())
    else:
        query = query.order_by(Reservations.start_time.asc())

    
    TAX_RATE = 0.10

    # 料金マスタ作成
    prices = {}
    for mp in MenuPrices.query.all():
        prices.setdefault(mp.menu_id, {})[mp.rank_id] = {
            "ex": mp.price,
            "in": int(mp.price * (1 + TAX_RATE))
        }

    # 各予約ごとに合計を計算
    for reservation in reservations:
        total_ex, total_in = calculate_reservation_price(reservation, prices)
        reservation.total_ex = total_ex
        reservation.total_in = total_in

    return render_template(
        'reservations/index.html', 
        reservations=reservations, 
        current_date = current_date,
        is_today=is_today,
        today_str=today_str,
        page_title="予約一覧",
        sub_title = "本日の予約状況を確認・管理します。",
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("dashboard.index")},
            {"label": "予約一覧"}
        ]
    )

# 予約作成
@reservations_bp.route('/reservations/create', methods=['GET', 'POST'])
def reservations_create():

    if request.method == 'POST':
        # 複数選択
        menu_ids = request.form.getlist('menu_ids')

        customer_id = request.form.get('customer_id')
        stylist_id = request.form.get('stylist_id')
        # Todo: string → date/time に変換する
        date = request.form.get('reservation_date')
        date = datetime.strptime(date, "%Y/%m/%d").date() # YYYY-MM-DD
        start_time = request.form.get('start_time')
        start_time = datetime.strptime(start_time, "%H:%M").time()
        end_time = calculate_end_time(start_time, menu_ids)

        flash('POST受け取った')
        return redirect(url_for('reservations.reservations_index'))

    customers = Customers.query.all()
    stylists = Stylists.query.all()
    menus = Menus.query.all()

    return render_template(
        'reservations/form.html',
        customers=customers,
        stylists=stylists,
        menus=menus, 
        page_title='予約??'
    )

# 予約詳細
@reservations_bp.route('/reservations/<int:reservation_id>')
def reservations_detail(reservation_id):

    reservation = Reservations.query.get_or_404(reservation_id)
    rank_id = reservation.stylist.rank_id
    stylist = reservation.stylist

    # 時間と予想所要時間
    duration = (
        datetime.combine(date.today(), reservation.end_time) -
        datetime.combine(date.today(), reservation.start_time)
    ).seconds // 60
    time_range = f"{reservation.start_time.strftime('%H:%M')} - {reservation.end_time.strftime('%H:%M')} ({duration}分)"

    # 合計所要時間計算
    total_duration = 0

    for menu in reservation.menus:
        total_duration += menu.duration_minutes

    total_duration = sum(menu.duration_minutes for menu in reservation.menus)

    # 料金関係
    # ①料金計算
    TAX_RATE = 0.10
    prices = {}

    for mp in MenuPrices.query.all():
        prices.setdefault(mp.menu_id, {})[mp.rank_id] = {
            "ex": mp.price,
            "in": int(mp.price * (1 + TAX_RATE))
        }

    # ②使用フェーズ
# 各予約ごとに合計を計算
    total_ex, total_in = calculate_reservation_price(reservation, prices)
    reservation.total_ex = total_ex
    reservation.total_in = total_in

    # 勤続年数計算
    today = date.today()
    years = today.year - stylist.hire_date.year
    
    # まだ今年の入店日を迎えてない場合は-1
    if (today.month, today.day) < (stylist.hire_date.month, stylist.hire_date.day):
        years -= 1

    return render_template(
        'reservations/detail.html', 
        reservation=reservation, 
        time_range=time_range,
        prices=prices,
        total_duration=total_duration,
        total_ex=total_ex,
        total_in=total_in,
        experience_years=years,
        page_title="予約詳細",
        sub_title = "予約の詳細情報を確認します。",
        breadcrumb_items=[
            {"label": "予約一覧", "url": url_for("reservations.reservations_index")},
            {"label": "予約詳細"}
        ]
    )

# 予約削除
@reservations_bp.route('/reservations/<int:reservation_id>/delete')
def reservations_delete(reservation_id):
    return "delete"
