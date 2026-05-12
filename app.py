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

# ログイン(Form使用)
@app.route('/login', methods=["GET", "POST"])
def login():
    # Formインスタンス生成
    form = LoginForm()
    if form.validate_on_submit():
        # データ入力取得
        username = form.username.data
        password = form.password.data
        # 対象User取得
        user = Users.query.filter_by(username=username).first()
        # 認証判定
        if user is not None and user.check_password(password):
            # 成功
            # 引数として渡されたuserオブジェクトを使用してユーザーをログイン状態にする
            login_user(user)
            # 画面遷移
            return redirect(url_for("index"))
        # 失敗
        flash("認証不備です")
    # GETの時
    # 画面遷移図
    return render_template("auth/login.html", form=form)

# ログアウト
@app.route("/logout")
@login_required
def logout():
    # 現在ログインしているユーザーをログアウトする
    logout_user()
    # フラッシュメッセージ
    flash("ログアウトしました")
    # 画面遷移
    return redirect(url_for("login"))

# サインアップ(Form使用)
@app.route("/register", methods=["GET", "POST"])
def register():
    # Formインスタンス生成
    form = SignUpForm()
    if form.validate_on_submit():
        # データ入力取得
        username = form.username.data
        password = form.password.data
        # モデルを生成
        user = Users(username=username)
        # パスワードハッシュ化
        user.set_password(password)
        # 登録処理
        db.session.add(user)
        db.session.commit()
        # フラッシュメッセージ
        flash("ユーザー登録しました")
        # 画面遷移
        return redirect(url_for("login"))
    # GET時
    # 画面遷移
    return render_template("auth/register.html", form=form)


# ゲストログイン
@app.route("/guest-login", methods=["POST"])
def guest_login():

    guest_user = Users.query.filter_by(username="guest").first()

    login_user(guest_user)

    flash("ゲストログインしました")

    return redirect(url_for("index"))



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
#   CUSTOMER
# =================
# 会員一覧
@app.route('/customers', methods=['GET'])
def customers_index():
    customers = Customers.query.all()

    # 各顧客の最終来店日を付与
    for c in customers:
        last_reservation = (
            Reservations.query
            .filter_by(customer_id=c.customer_id)
            .order_by(Reservations.reservation_date.desc())
            .first()
        )
        c.last_visit_date = last_reservation.reservation_date if last_reservation else None

    return render_template(
        'customers/index.html', 
        customers=customers, 
        page_title='会員一覧',
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("index")},
            {"label": "会員一覧"}
        ]
    )

# 会員登録
@app.route('/customers/new', methods=['GET', 'POST'])
def customers_new():
    form = CustomerForm()

    # POSTの場合
    if form.validate_on_submit():
        full_name = form.full_name.data
        email = form.email.data
        phone_number = form.phone_number.data

        filters = []

        if email:
            filters.append(Customers.email == email)

        if phone_number:
            filters.append(Customers.phone_number == phone_number)

        customer = None
        if filters:
            customer = Customers.query.filter(or_(*filters)).first()

        if not customer:
            customer = Customers(
                full_name=full_name,
                email=email,
                phone_number=phone_number
            )
            db.session.add(customer)
            flash('顧客を登録しました')
        else:
            flash(f'{customer.full_name} は既に登録されています')

        db.session.commit()
        # customers_indexは関数名
        return redirect(url_for('customers_index'))
    # GETの場合
    return render_template(
        'customers/new.html', 
        form=form, 
        page_title='新規会員登録',
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("index")},
            {"label": "会員一覧", "url": url_for("customers_index")},
            {"label": "会員登録"}
        ]
    )

# 会員詳細(GET)
@app.route('/customers/<int:customer_id>', methods=['GET'])
def customers_detail(customer_id):
    customer = Customers.query.get_or_404(customer_id)

    reservations = Reservations.query.filter_by(
        customer_id = customer_id
    ).all()

    last_reservation = (
        Reservations.query
        .filter_by(customer_id=customer_id)
        .order_by(Reservations.reservation_date.desc())
        .first()
    )

    return render_template(
        'customers/detail.html',
        customer=customer,
        reservations=reservations, 
        last_visit=last_reservation,
        total_visits=len(reservations), # 来店回数のため
        page_title=f"{customer.full_name} 様",
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("index")},
            {"label": "会員一覧", "url": url_for("customers_index")},
            {"label": customer.full_name}
        ]
    )

# 会員情報変更
@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
def customers_edit(customer_id):
    
    # データ取得
    customer = Customers.query.get_or_404(customer_id)

    # POSTの場合 更新処理を実行
    if request.method == 'POST':
        customer.full_name = request.form.get('full_name')
        db.session.commit()

        # 更新後はリダイレクト()
        return redirect(url_for(
            'customers_detail', 
            customer_id=customer_id),
            page_title='会員詳細',
            breadcrumb_items=[
                # {"label": "Home", "url": url_for("index")},
                {"label": "会員一覧", "url": url_for("customers_index")},
                {"label": customer.full_name}
            ]
        )

    # GET(編集画面表示)
    return render_template(
        'customers/edit.html', 
        customer=customer, 
        page_title='会員情報変更',
        breadcrumb_items=[
                # {"label": "Home", "url": url_for("index")},
                {"label": "会員一覧", "url": url_for("customers_index")},
                {"label": customer.full_name}
            ]
    )

# 顧客情報削除
# @app.route('/customers/<int:customer_id>/delete')
# def customers_delete(customer_id):
#     return "delete"

# =================
#   RESERVATION
# =================
# 予約一覧
@app.route('/reservations', methods=['GET'])
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
            # {"label": "Home", "url": url_for("index")},
            {"label": "予約一覧"}
        ]
    )

# 予約作成
@app.route('/reservations/create', methods=['GET', 'POST'])
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
        return redirect(url_for('reservations_index'))

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
@app.route('/reservations/<int:reservation_id>')
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
            {"label": "予約一覧", "url": url_for("reservations_index")},
            {"label": "予約詳細"}
        ]
    )

# 予約削除
@app.route('/reservations/<int:reservation_id>/delete')
def reservations_delete(reservation_id):
    return "delete"

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