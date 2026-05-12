#  salon_reservation_app/app.py
import os
from flask import render_template, url_for, request, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from datetime import datetime, date, time, timedelta
from collections import defaultdict
import locale
# モデル読み込み

from app import create_app

from app.models import Stylists, Customers, Reservations, MenuPrices, Menus, Ranks
from app.services.reservation_service import calculate_end_time, get_or_create_customer, is_conflict, calculate_reservation_price
from app.services.dashboard_service import calc_position
from app.services.stylists_service import calculate_experience_years

from app.forms import CustomerForm, SignUpForm, LoginForm


# =================
# ルーティング
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝

# ダッシュボード(トップページ)
@app.route('/', methods=['GET'])
@login_required
def index():


    # routeで1日分を取得
    today = date.today()

    stylists = Stylists.query.all()

    for stylist in stylists:
        stylist.daily_reservations = [
            r for r in stylist.reservations
            if r.reservation_date == today and not r.is_cancelled
        ]


    # 全予約に適用
    for stylist in stylists:
        for r in stylist.daily_reservations:
            calc_position(r)



    return render_template(
        'dashboard/index.html', 
        page_title='ダッシュボード', 
        stylists=stylists
    )


# =================
#   STYLISTS
# =================
# スタイリスト一覧
@app.route('/stylists', methods=['GET'])
def stylists_index():
    stylists = Stylists.query.all()
    
    return render_template(
        'stylists/index.html', 
        stylists=stylists, 
        page_title='スタイリスト一覧',
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("index")},
            {"label": "スタイリスト一覧"}
        ]
    )


# スタイリスト詳細
@app.route("/stylists/<stylist_id>")
def stylists_detail(stylist_id):
    stylist = Stylists.query.get(stylist_id)

    years = calculate_experience_years(stylist.hire_date)

    return render_template(
        "stylists/detail.html",
        stylist=stylist,
        experience_years=years,
        page_title=stylist.stylist_name,
        sub_title="スタイリストの情報・予約・実績を確認します。",
        breadcrumb_items=[
            {"label": "スタイリスト一覧", "url": url_for("stylists_index")},
            {"label": stylist.stylist_name }
        ]
    )

# スタイリスト登録

# スタイリスト情報編集
# スタイリスト情報削除

# =================
#   MENU
# =================
# メニュー一覧
@app.route('/menus', methods=['GET'])
def menus_index():
    menus = Menus.query.all()
    ranks = Ranks.query.all()

    TAX_RATE = 0.10 # 10%の消費税
    
    # MenuPricesを辞書化する
    prices = defaultdict(dict)

    for mp in MenuPrices.query.all():
        prices[mp.menu_id][mp.rank_id] = {
            "ex": mp.price,
            "in": int(mp.price * (1 + TAX_RATE))
        }

    return render_template(
        'menus/index.html', 
        menus=menus, 
        ranks=ranks,
        prices=prices,
        page_title='メニュー一覧',
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("index")},
            {"label": "メニュー一覧"}
        ]
    )

'''
# SQL
@app.route('/init-db')
def init_db():

    # ランク
    rank_a = Ranks(rank_id='A', title='チーフスタイリスト')
    rank_b = Ranks(rank_id='B', title='トップスタイリスト')
    rank_c = Ranks(rank_id='C', title='スタイリスト')

    db.session.add_all([rank_a, rank_b, rank_c])
    db.session.commit()

    # メニュー
    menus = [
        Menus(menu_id='C', menu_name='カット', duration_minutes=30),
        Menus(menu_id='P', menu_name='パーマ', duration_minutes=60),
        Menus(menu_id='R', menu_name='カラー', duration_minutes=60),
        Menus(menu_id='T', menu_name='トリートメント', duration_minutes=30),
    ]
    db.session.add_all(menus)
    db.session.commit()

    # メニュー料金
    prices = [
        # A
        MenuPrices(menu_id='C', rank_id='A', price=12000),
        MenuPrices(menu_id='P', rank_id='A', price=18000),
        MenuPrices(menu_id='R', rank_id='A', price=9600),
        MenuPrices(menu_id='T', rank_id='A', price=14400),

        # B
        MenuPrices(menu_id='C', rank_id='B', price=10000),
        MenuPrices(menu_id='P', rank_id='B', price=15000),
        MenuPrices(menu_id='R', rank_id='B', price=8000),
        MenuPrices(menu_id='T', rank_id='B', price=12000),

        # C
        MenuPrices(menu_id='C', rank_id='C', price=8000),
        MenuPrices(menu_id='P', rank_id='C', price=12000),
        MenuPrices(menu_id='R', rank_id='C', price=6400),
        MenuPrices(menu_id='T', rank_id='C', price=9600),
    ]
    db.session.add_all(prices)
    db.session.commit()


    # スタイリスト
    stylists = [
        Stylists(stylist_id='01', stylist_name='秋葉ちか', hire_date=date(2004,4,1), rank_id='A'),
        Stylists(stylist_id='02', stylist_name='佐藤茜', hire_date=date(2006,6,1), rank_id='B'),
        Stylists(stylist_id='03', stylist_name='井上博之', hire_date=date(2009,1,8), rank_id='B'),
        Stylists(stylist_id='04', stylist_name='小島正', hire_date=date(2016,5,2), rank_id='C'),
        Stylists(stylist_id='05', stylist_name='山田雄介', hire_date=date(2021,4,1), rank_id='C'),
        Stylists(stylist_id='06', stylist_name='市川紀子', hire_date=date(2024,6,10))
    ]
    db.session.add_all(stylists)
    db.session.commit()


    # 会員
    customers = [
        Customers(full_name='吉田康子', phone_number='09001234567', email='yoshida@example.com', first_visit_date=date(2006,4,10)),
        Customers(full_name='荒木和子', phone_number='09001234567', email='araki@example.com', first_visit_date=date(2018,8,11)),
        Customers(full_name='下田正一', phone_number='09001234567', email='shimoda@example.com', first_visit_date=date(2019,4,12)),
        Customers(full_name='風間由美子', phone_number='09001234567', email=None, first_visit_date=date(2019,6,13)),
        Customers(full_name='秋山美奈', phone_number='09001234567', email='akiyama@example.com', first_visit_date=date(2021,1,14)),
        Customers(full_name='木下博之', phone_number='09001234567', email='kinoshita@example.com', first_visit_date=date(2021,4,15)),
        Customers(full_name='広瀬正隆', phone_number=None, email=None, first_visit_date=date(2022,9,16)),
        Customers(full_name='斉藤美紀', phone_number='09001234567', email='saitou@example.com', first_visit_date=date(2024,4,17)),
    ]

    db.session.add_all(customers)
    db.session.commit()

    # 予約
    reservations = [
        Reservations(
            customer_id=2,
            reserved_at=datetime(2024,9,6,16,28),
            reservation_date=date(2024,10,1),
            start_time=time(17,0),
            end_time=time(18,30),
            stylist_id='01'
        ),
        Reservations(
            customer_id=4,
            reserved_at=datetime(2024,9,26,12,42),
            reservation_date=date(2024,10,1),
            start_time=time(10,0),
            end_time=time(10,30),
            stylist_id='03'
    ),
        Reservations(
            customer_id=8,
            reserved_at=datetime(2024,9,30,10,30),
            reservation_date=date(2024,10,1),
            start_time=time(15,0),
            end_time=time(17,30),
            stylist_id='05'
        ),
    ]
    db.session.add_all(reservations)
    db.session.commit()
    
    # 予約メニュー
    reservation_menus = [
        # 予約1 → C,R
        ReservationMenus(reservation_id=1, menu_id='C'),
        ReservationMenus(reservation_id=1, menu_id='R'),

        # 予約2 → C
        ReservationMenus(reservation_id=2, menu_id='C'),

        # 予約3 → C,P,R
        ReservationMenus(reservation_id=3, menu_id='C'),
        ReservationMenus(reservation_id=3, menu_id='P'),
        ReservationMenus(reservation_id=3, menu_id='R'),
    ]
    db.session.add_all(reservation_menus)
    db.session.commit()

    return "初期データ投入OK"
    '''

# =================
# 実行
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝
if __name__ == '__main__':
    app.run(debug=True, port=5001)