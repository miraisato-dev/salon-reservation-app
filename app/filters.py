# filters.py
# Jinja2フィルター
from flask import current_app
from datetime import timedelta

WEEKDAYS = ['月', '火', '水', '木', '金', '土', '日']

# =================
# フィルター
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝

# 日付計算フィルター(カレンダー系)
def add_days(value, days):
    if not value:
        return None
    return value + timedelta(days=days)

# 
def to_date_str(value):
    if not value:
        return ''
    return value.strftime('%Y-%m-%d')

# 日付フィルター
def date_jp(value):
    if not value:
        return '-'
    return value.strftime('%Y/%m/%d')
# {{ reservation.reservation_date | date_jp_full }}

# 時間フィルター
def time_hm(value):
    if not value:
        return '-'
    return value.strftime('%H:%M')
# {{ reservation.start_time | time_hm }}

# 日時まとめフィルター
def datetime_jp(value):
    if not value:
        return '-'
    return value.strftime('%Y/%m/%d %H:%M')

# 日付フィルター
def date_jp_full(value):
    if not value:
        return '-'
    return f"{value.year}年{value.month}月{value.day}日({WEEKDAYS[value.weekday()]})"
# {{ customer.last_visit_date | date_jp_full }}

# 電話番号フィルタ
def phone(value):
    if not value:
        return '-'

    value = value.replace('-', '')

    if len(value) == 11:
        return f"{value[:3]}-{value[3:7]}-{value[7:]}"
    elif len(value) == 10:
        return f"{value[:2]}-{value[2:6]}-{value[6:]}"
    
    return value

# 金額フィルタ
def yen(value):
    if value is None:
        return '-'
    try:
        return f"¥{int(value):,}"
    except (ValueError, TypeError):
        return '-'