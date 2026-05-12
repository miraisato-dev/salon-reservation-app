# app/customers/routes.py

from flask import (
    Blueprint, render_template,
    request, redirect, url_for, flash
)

from sqlalchemy import or_

from app.extensions import db

from app.models import (
    Customers,
    Reservations
)

from app.forms import CustomerForm

customers_bp = Blueprint(
    "customers",
    __name__
)

# =================
#   CUSTOMER
# =================
# 会員一覧
@customers_bp.route('/customers', methods=['GET'])
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
@customers_bp.route('/customers/new', methods=['GET', 'POST'])
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
        return redirect(url_for('customers.customers_index'))
    # GETの場合
    return render_template(
        'customers/new.html', 
        form=form, 
        page_title='新規会員登録',
        breadcrumb_items=[
            # {"label": "Home", "url": url_for("index")},
            {"label": "会員一覧", "url": url_for("customers.customers_index")},
            {"label": "会員登録"}
        ]
    )

# 会員詳細(GET)
@customers_bp.route('/customers/<int:customer_id>', methods=['GET'])
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
            {"label": "会員一覧", "url": url_for("customers.customers_index")},
            {"label": customer.full_name}
        ]
    )

# 会員情報変更
@customers_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
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
                {"label": "会員一覧", "url": url_for("customers.customers_index")},
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
                {"label": "会員一覧", "url": url_for("customers.customers_index")},
                {"label": customer.full_name}
            ]
    )

# 顧客情報削除
# @customers_bp.route('/customers/<int:customer_id>/delete')
# def customers_delete(customer_id):
#     return "delete"
