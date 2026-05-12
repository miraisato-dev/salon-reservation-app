# app/menus/routes.py MENU関係
from flask import (
    Blueprint, render_template,
)

from collections import defaultdict

from app.extensions import db

from app.models import (
    Menus,
    MenuPrices,
    Ranks
)

menus_bp = Blueprint(
    "menus",
    __name__
)



# =================
#   MENU
# =================
# メニュー一覧
@menus_bp.route('/menus', methods=['GET'])
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