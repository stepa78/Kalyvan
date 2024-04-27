import os
import threading
import datetime

from werkzeug.utils import secure_filename

from slugify import slugify

from flask import Flask, render_template, redirect, url_for, request, jsonify, abort

from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

from forms import LoginForm, RegisterForm
from models import db, User, Account, AccountStock, Stock, Tick, StockTick

from sqlalchemy import func, and_, select
from sqlalchemy.orm import aliased
from ticker import run_ticker, BURSE_START_DATE


def UNIQUE_STRING(length=6):
    import uuid
    return uuid.uuid4().hex[:length].upper()


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/media/upload'

bcrypt = Bcrypt(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    success = True
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            success = False
    return render_template('login.html', form=form, success=success)


@app.route('/dashboard', methods=['GET', 'POST'])
@app.route('/dashboard/<account_code>', methods=['GET'])
@login_required
def dashboard(account_code=None):
    selected_account = None
    if account_code:
        selected_account = Account.query.filter(
            Account.user_id == current_user.id,
            Account.code == account_code
        ).first()
        if not selected_account:
            abort(404)

    return render_template('dashboard.html',
        user=current_user,
        accounts=current_user.get_accounts(),
        selected_account=selected_account,
        all_stocks=Stock.query.all()
    )


@app.route('/account', methods=['POST', 'GET'])
@app.route('/account/<account_id>', methods=['GET', 'DELETE'])
@login_required
def account(account_id=0):
    if request.method == 'POST':
        # создаем новый счет (запись в таблице Account)
        user_account = Account(user_id=current_user.id, code=UNIQUE_STRING(6))
        db.session.add(user_account)
        db.session.commit()
        return jsonify(user_account.as_dict())

    elif request.method == 'GET':
        if account_id > 0:
            # возвращаем account с id == account_id
            user_account = Account.query.filter(Account.user_id==current_user.id, Account.id==account_id).first()
            if user_account is None:
                abort(404)
            return jsonify(user_account.as_dict())
        else:
            # возвращаем список всех счетов пользователя
            user_accounts = [a.as_dict() for a in Account.query.filter(Account.user_id==current_user.id)]
            return jsonify(user_accounts)

    elif request.method == 'DELETE':
        #удаляем account с id == account_id
        pass


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password1.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@login_required
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        if 'user_avatar' in request.files:
            file = request.files['user_avatar']
            if file and file.filename != '':

                name, ext = os.path.splitext(file.filename)
                filename = secure_filename(f'{slugify(name)}{ext}')
                final_filename = os.path.join(*os.path.split(app.config['UPLOAD_FOLDER']), filename)
                file.save(final_filename)

                current_user.avatar = final_filename
                db.session.commit()

    return render_template('user_settings.html',
                           user=current_user,
                           accounts=current_user.get_accounts())


@app.route('/api/prices')
def stock_prices():
    stock_id = request.args.get('stock_id')

    try:
        tick = int(request.args.get('timestamp'))
    except ValueError:
        tick = None

    if not tick:
        tick = (datetime.datetime.now() + datetime.timedelta(minutes=-120)).timestamp()

    res = []
    if stock_id:
        pricesOpen = aliased(StockTick)
        pricesClose = aliased(StockTick)

        time_frame = 300
        group_by_time_frame = time_frame * func.floor(StockTick.tick / time_frame)

        agg_prices = (
            select(
                group_by_time_frame.label('tick'),
                StockTick.stock_id,
                func.max(StockTick.tick).label("open_tick"),
                func.min(StockTick.tick).label("close_tick"),
                func.max(StockTick.price).label("hi"),
                func.min(StockTick.price).label("lo"),
            ).
            filter(
                StockTick.tick > tick + time_frame, StockTick.stock_id == stock_id
            ).group_by(
                StockTick.stock_id,
                group_by_time_frame
            ).order_by(group_by_time_frame).subquery()
        )

        a = (
            select(
                agg_prices.c.tick,
                pricesOpen.price,
                pricesClose.price,
                agg_prices.c.hi,
                agg_prices.c.lo,
            ).join(
                pricesOpen,
                and_(
                    pricesOpen.stock_id == agg_prices.c.stock_id,
                    pricesOpen.tick == agg_prices.c.open_tick
                )
            ).join(
                pricesClose,
                and_(
                    pricesClose.stock_id == agg_prices.c.stock_id,
                    pricesClose.tick == agg_prices.c.close_tick
                )
            )
        )

        for r in db.session.execute(a):
            res.append({
                'x': r[0],
                'y': [float(r[1]), float(r[2]), float(r[3]), float(r[4])]}
            )

    return res


def create_stock():
    Stock.query.delete()
    db.session.add_all(
        [
            Stock(
                name='ПАО Тындекс',
                code='TDX',
                start_date=datetime.datetime(year=2020, month=1, day=1),
                start_price=100.0,
                lot_size=10),
            Stock(
                name='ПАО Жыр и лопаты',
                code='JRS',
                start_date=datetime.datetime(year=2021, month=1, day=1),
                start_price=120.0,
                lot_size=100),
            Stock(
                name='ПАО Гуголь',
                code='GGL',
                start_date=datetime.datetime(year=2021, month=1, day=1),
                start_price=200.0,
                lot_size=1000),
        ]
    )
    db.session.commit()


def start_ticker():
    threading.Timer(30, start_ticker).start()
    run_ticker(app)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_stock()

    #start_ticker()

    #run_ticker(app)
    app.run()
