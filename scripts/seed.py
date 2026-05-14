# scripts/seed.py

from datetime import date, datetime, time

from app import create_app
from app.extensions import db

from app.models import (
    Ranks,
    Menus,
    MenuPrices,
    Stylists,
    Customers,
    Reservations,
    ReservationMenus
)

app = create_app()

with app.app_context():

    # データ投入
    rank_a = Ranks(
        rank_id='A',
        title='チーフスタイリスト'
    )

    db.session.add(rank_a)

    db.session.commit()

    print("seed ok")




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
