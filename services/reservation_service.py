# salon_reservation_app/services/reservation_service.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.exc import SQLAlchemyError

from models import Customers, Reservations
from db import db

# 
def get_or_create_customer(email, name, phone):
    try:
        customer = Customers.query.filter(
            (Customers.email == email) |
            (Customers.phone_number == phone)
        ).first()

        if not customer:
            customer = Customers(
                full_name=name,
                email=email,
                phone_number=phone
            )
            db.session.add(customer)

        return customer

    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Customer取得/作成失敗: {str(e)}")

# 
def calculate_end_time(start_time, menus):
    try:
        if not start_time or not menus:
            raise ValueError("start_time または menus が不正です")

        total_min = sum(menu.duration_minutes for menu in menus)

        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        start_dt = datetime.combine(now.date(), start_time)

        end_dt = start_dt + timedelta(minutes=total_min)

        return end_dt.time()

    except Exception as e:
        raise ValueError(f"終了時間計算エラー: {str(e)}")

# 
def is_conflict(stylist_id, date, start_time, end_time):
    try:
        conflict = Reservations.query.filter(
            Reservations.stylist_id == stylist_id,
            Reservations.reservation_date == date,
            Reservations.is_cancelled == False,
            Reservations.end_time > start_time,
            Reservations.start_time < end_time
        ).first()

        return conflict is not None

    except SQLAlchemyError as e:
        raise Exception(f"予約競合チェック失敗: {str(e)}")
    
# 
def calculate_reservation_price(reservation, prices):
    rank_id = reservation.stylist.rank_id

    total_ex = 0
    total_in = 0

    for menu in reservation.menus:
        price_data = prices.get(menu.menu_id, {}).get(rank_id)

        if price_data:
            total_ex += price_data["ex"]
            total_in += price_data["in"]

    return total_ex, total_in