# salon_reservation_app/services/reservation_service.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from models import Customers
from db import db

def get_or_create_customer(email, name, phone):
    customer = Customers.query.filter_by

    if not customer:
        customer = Customers(
            full_name = name,
            email = email,
            phone_number = phone
        )
        db.session.add(customer)

    return customer

def calculate_end_time(start_time, menus):
    total_min = sum(menu.duration_minutes for menu in menus)
    now = datetime.now(ZoneInfo('Asia/Tokyo'))
    dt = datetime.combine(now.date(), start_time)
    end_dt = dt + timedelta(minutes=total_min)
    return end_dt.time()

def is_conflict(stylist_id, date, start_time, end_time):
    from models import Reservations # 関数内import

    # SQLで絞り込んで取得
    conflict = Reservations.query.filter(
        Reservations.stylist_id == stylist_id,
        Reservations.reservation_date == date,
        Reservations.is_cancelled == False,
        Reservations.end_time > start_time,
        Reservations.start_time < end_time
    ).first()
    return conflict is not None