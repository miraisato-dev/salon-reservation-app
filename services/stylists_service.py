# services/stylists_service.py
from datetime import date

# スタイリストの入社日から現在までの勤続年数を計算する
def calculate_experience_years(hire_date):
    today = date.today()
    years = today.year - hire_date.year

    if (today.month, today.day) < (hire_date.month, hire_date.day):
        years -= 1

    return years