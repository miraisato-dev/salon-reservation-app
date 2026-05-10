# salon_reservation_app/models.py
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import CheckConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# db.pyから
from db import db

# =================
# モデル
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# 1. お客様情報テーブル
class Customers(db.Model):
    # テーブル名
    __tablename__ = 'customers'
    # お客様ID
    customer_id = db.Column(
        db.Integer, 
        nullable=False, 
        primary_key=True, 
        autoincrement=True # 自動採番一応明示
    )
    reservations = db.relationship(
        'Reservations', 
        back_populates='customer',
        cascade='all, delete-orphan'
    )
    # 氏名
    full_name = db.Column(db.String(30), nullable=False)
    # 電話番号
    phone_number = db.Column(db.String(15), nullable=True)
    # メールアドレス
    email = db.Column(db.String(40), nullable=True)
    # 初回来店日
    first_visit_date = db.Column(db.DateTime, nullable=True)

# 2. 予約情報テーブル
class Reservations(db.Model):
    # テーブル名
    __tablename__ = 'reservations'
    # 予約ID
    reservation_id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True, # 自動採番一応明示
        nullable=False
    )
    reservation_menus = db.relationship(
        'ReservationMenus', 
        back_populates='reservation',
        cascade='all, delete-orphan'
    )
    menus = db.relationship(
        'Menus',
        secondary='reservation_menus',
        back_populates='reservations'
    )
    # お客様ID
    customer_id = db.Column(
        db.Integer, 
        db.ForeignKey('customers.customer_id'),
        nullable=False, 
    )
    customer = db.relationship('Customers', back_populates='reservations')
    # 予約受付日
    reserved_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=lambda: datetime.now(ZoneInfo('Asia/Tokyo'))
    )
    # 予約日
    reservation_date = db.Column(db.Date, nullable=False)
    # 開始時間
    start_time = db.Column(db.Time, nullable=False)
    # 終了時間
    end_time = db.Column(db.Time, nullable=False)
    # スタイリストID
    stylist_id = db.Column(
        db.String(10), 
        db.ForeignKey('stylists.stylist_id'),
        nullable=False
    )
    stylist = db.relationship('Stylists', back_populates='reservations')
    # キャンセルフラグ
    is_cancelled = db.Column(db.Boolean, default=False)
    # 備考
    notes = db.Column(db.String(100), default="特になし")

    # 
    __table_args__ = (
        db.UniqueConstraint(
            'stylist_id',
            'reservation_date',
            'start_time',
            name='unique_reservation'
        ),
    )

# 3. メニューテーブル
class Menus(db.Model):
    # テーブル名
    __tablename__ = 'menus'
    # メニューコード
    menu_id = db.Column(db.String(5), primary_key=True, nullable=False)
    reservation_menus = db.relationship('ReservationMenus', back_populates='menu')
    reservations = db.relationship(
        'Reservations',
        secondary='reservation_menus',
        back_populates='menus'
    )
    # メニュー名
    menu_name = db.Column(db.String(30), nullable=False)
    # 所要時間
    duration_minutes = db.Column(db.Integer, nullable=False)

# 4. スタイリスト表
class Stylists(db.Model):
    # テーブル名
    __tablename__ = 'stylists'
    # スタイリストID
    stylist_id = db.Column(db.String(10), primary_key=True, nullable=False)
    # スタイリスト氏名
    stylist_name = db.Column(db.String(30), nullable=False)
    # 入店日
    hire_date = db.Column(db.Date, nullable=False)
    # スタイリストランク
    rank_id = db.Column(
        db.String(1), 
        db.ForeignKey('ranks.rank_id'),
        nullable=True
    )
    
    rank = db.relationship('Ranks', back_populates='stylists')
    reservations = db.relationship('Reservations', back_populates='stylist')

    # スタイリスト画像（S3 URL or static path）
    image_path = db.Column(db.String(255), nullable=True)

# 5. 予約メニューテーブル
class ReservationMenus(db.Model):
    # テーブル名
    __tablename__ = 'reservation_menus'
    # 予約ID
    reservation_id = db.Column(
        db.Integer,
        db.ForeignKey('reservations.reservation_id'),
        primary_key=True, 
        nullable=False
    )
    reservation = db.relationship('Reservations', back_populates='reservation_menus')
    # メニューコード
    menu_id = db.Column(
        db.String(5), 
        db.ForeignKey('menus.menu_id'),
        primary_key=True, 
        nullable=False
    )
    menu = db.relationship('Menus', back_populates='reservation_menus')

# 6. ランクテーブル
class Ranks(db.Model):
    # テーブル名
    __tablename__ = 'ranks'
    # ランク
    rank_id = db.Column(db.String(1), primary_key=True, nullable=False)
    stylists = db.relationship('Stylists', back_populates='rank')
    # 詳細
    description = db.Column(db.String(100), default='特になし')
    # 肩書き
    title = db.Column(db.String(20), nullable=True)

# 7. メニュープライステーブル
class MenuPrices(db.Model):
    # テーブル名
    __tablename__ = 'menu_prices'
    # メニューコード
    menu_id = db.Column(
        db.String(5), 
        db.ForeignKey('menus.menu_id'), 
        primary_key=True,
        nullable=False
    )
    # ランク
    rank_id = db.Column(
        db.String(1),
        db.ForeignKey('ranks.rank_id'),
        primary_key=True,
        nullable=False
    )
    # 料金
    price = db.Column(db.Integer, nullable=False)
    
    # 料金は負の数であってはいけない
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
    )



#ログイン認証のため
class Users(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="staff")

    # パスワードをハッシュ化して保存
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 入力されたパスワードとDBのハッシュを比較
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)