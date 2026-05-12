# app/stylists/routes.py

from flask import (
    Blueprint, render_template,
    request, redirect, url_for, flash
)

from datetime import datetime, date
from collections import defaultdict

from app.extensions import db

from app.models import (
    
    Stylists,
    
)

from app.services.stylists_service import (
    calculate_experience_years
)

stylists_bp = Blueprint(
    "stylists",
    __name__,
    url_prefix="/stylists"
)


# =================
#   STYLISTS
# =================
# スタイリスト一覧
@stylists_bp.route('/', methods=['GET'])
def stylists_index():
    stylists = Stylists.query.all()
    
    return render_template(
        'stylists/index.html', 
        stylists=stylists, 
        page_title='スタイリスト一覧',
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("dashboard.index")},
            {"label": "スタイリスト一覧"}
        ]
    )


# スタイリスト詳細
@stylists_bp.route("/<stylist_id>")
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
            {"label": "スタイリスト一覧", "url": url_for("stylists.stylists_index")},
            {"label": stylist.stylist_name }
        ]
    )