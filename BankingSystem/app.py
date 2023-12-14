from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required
from config import Config
from models import *
from forms import *
from utils import *
from init_db import db


app = Flask(__name__)
app.config.from_object(Config)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    currencies = Currency.query.filter(Currency.currency_name != 'BYN').all()

    date = CurrencyRate.query.order_by(CurrencyRate.date.desc()).first().date
    date_str = date.strftime("%d.%m.%Y %H:%M")

    rates = []
    for currency in currencies:
        rates.append([
            CurrencyRate.query.filter(
                CurrencyRate.from_currency_id == Currency.query.filter_by(currency_name='BYN').first().id,
                CurrencyRate.to_currency_id == Currency.query.filter_by(currency_name=currency.currency_name).first().id
            ).all(),
            CurrencyRate.query.filter(
                CurrencyRate.from_currency_id == Currency.query.filter_by(
                    currency_name=currency.currency_name).first().id,
                CurrencyRate.to_currency_id == Currency.query.filter_by(currency_name='BYN').first().id
            ).all()
        ])

    return render_template('home.html', currencies=currencies, rates=rates, date=date_str)


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    currency1 = data['currency1']
    input_currency1 = data['input_currency1']
    currency2 = data['currency2']
    input_currency2 = data['input_currency2']

    if input_currency1:
        # Конвертируем из currency1 в currency2
        amount = float(input_currency1)
        from_currency = currency1
        to_currency = currency2
        rate = get_rates(to_currency, from_currency)
        converted_amount = float(amount) / rate
    elif input_currency2:
        # Конвертируем из currency2 в currency1
        amount = float(input_currency2)
        from_currency = currency2
        to_currency = currency1
        rate = get_rates(to_currency, from_currency)
        converted_amount = float(amount) * rate
    else:
        return jsonify(error='Введите сумму для конвертации')

    # rate = get_rates(to_currency, from_currency)
    # converted_amount = convert_currency(amount, rate)

    return jsonify(converted_amount=converted_amount)


def get_rates(to_currency, from_currency):
    latest_date = CurrencyRate.query.order_by(CurrencyRate.date.desc()).first().date
    latest_rates = (CurrencyRate.query.filter_by(
        date=latest_date,
        to_currency_id=Currency.query.filter_by(currency_name=to_currency).first().id,
        from_currency_id=Currency.query.filter_by(currency_name=from_currency).first().id)
    .first())

    return latest_rates.rate


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            # Если имя пользователя или пароль неверны
            pass
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    roles = Role.query.with_entities(Role.id, Role.role_name).all()
    form.role.choices = [(role.id, role.role_name) for role in roles]
    departments = Department.query.with_entities(Department.id, Department.department_address).all()
    form.department.choices = [(dept.id, dept.department_address) for dept in departments]

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            patronymic=form.patronymic.data,
            phone_number=form.phone_number.data,
            birth_date=form.birth_date.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        user_id = user.id
        user_role = UserRole(
            user_id=user_id,
            role_id=form.role.data
        )
        db.session.add(user_role)

        id = form.role.data
        if form.role.data == '1':  # ID роли клиента
            client = Client(id=user_id)
            db.session.add(client)
        elif form.role.data == '2':  # ID роли админа
            admin = Admin(id=user_id, department_id=form.department.data)
            db.session.add(admin)

        db.session.commit()

        login_user(user)
        return redirect(url_for('home'))
    else:
        print(form.errors)
    return render_template('register.html', form=form)


if __name__ == '__main__':
    app.debug = True
    app.run()
