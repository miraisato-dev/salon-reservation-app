# app/dashboard/routes.py
from flask import (
    Blueprint,
    render_template
)

from flask_login import login_required

from datetime import date

from app.models import Stylists
from app.services.dashboard_service import calc_position

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)

# =================
# ルーティング
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝

# ダッシュボード(トップページ)
@dashboard_bp.route('/', methods=['GET'])
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
