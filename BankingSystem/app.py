from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, jsonify, abort, flash
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import *
from forms import *
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

    if current_user.is_authenticated:
        user_role = UserRole.query.filter_by(user_id=current_user.id).first().role.role_name
        if user_role == 'Админ':
            return render_template('home_admin.html')

    return render_template('home.html', currencies=currencies, rates=rates, date=date_str)


@login_manager.user_loader
def load_user(user_id):  # ?????
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
        print(form.errors)
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


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = UserRole.query.filter_by(user_id=current_user.id).first().role.role_name
            if user_role != role:
                logout()
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_accounts(user_id):
    user_accounts = BankAccount.query.filter_by(user_id=user_id).all()
    return user_accounts

@app.route('/bank_account', methods=['POST', 'GET'])
@login_required
# @role_required('Клиент')
def bank_account():
    user_accounts = get_user_accounts(current_user.id)
    return render_template('bank_account.html', accounts=user_accounts)


@app.route('/create_account', methods=['POST', 'GET'])
@login_required
# @role_required('Клиент')
def create_account():
    form = BankAccountForm()

    currencies = Currency.query.with_entities(Currency.id, Currency.currency_name).all()
    form.currency.choices = [(currency.id, currency.currency_name) for currency in currencies]

    if form.validate_on_submit():
        account = BankAccount(
            user_id=current_user.id,
            currency_id=form.currency.data,
            balance=form.balance.data,
            account_name=form.account_name.data,
        )

        db.session.add(account)
        db.session.commit()
        return redirect(url_for('bank_account'))
    else:
        print(form.errors)

    return render_template('new_bank_account.html', form=form)


def get_user_credits_and_applications(user):
    user_credits = Credit.query.filter_by(user_id=user).all()
    user_applications = CreditRequest.query.filter_by(user_id=user, status=False).all()
    return user_credits, user_applications


@app.route('/credit', methods=['POST', 'GET'])
@login_required
# @role_required('Клиент')
def credit():
    credits, applications = get_user_credits_and_applications(current_user.id)
    return render_template('credit.html', credits=credits, applications=applications)


@app.route('/create_credit', methods=['POST', 'GET'])
@login_required
# @role_required('Клиент')
def create_credit():
    form = CreditRequestForm()

    departments = Department.query.with_entities(Department.id, Department.department_address).all()
    form.department.choices = [(dept.id, dept.department_address) for dept in departments]

    if form.validate_on_submit():
        appliction = CreditRequest(
            user_id=current_user.id,
            amount=form.amount.data,
            interest_rate=form.interest_rate.data,
            date_term=form.term.data,
            department_id=form.department.data,
        )

        db.session.add(appliction)
        db.session.commit()
        return redirect(url_for('credit'))
    else:
        print(form.errors)

    return render_template('new_credit.html', form=form)


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    form = ProfileEditForm(request.form)
    dept = None

    if current_user.is_authenticated:
        user_role = UserRole.query.filter_by(user_id=current_user.id).first().role.role_name
        user = User.query.filter_by(id=current_user.id).first()
        if request.method == 'GET':
            form.username.data = user.username
            form.email.data = user.email
            form.first_name.data = user.first_name
            form.last_name.data = user.last_name
            form.patronymic.data = user.patronymic
            birth_date = datetime.strptime(str(user.birth_date), "%Y-%m-%d %H:%M:%S")
            form.birth_date.data = birth_date.date()
            form.phone_number.data = user.phone_number

            if user_role == 'Админ':
                admin = Admin.query.filter_by(id=current_user.id).first()
                dept = (Department.query.with_entities(Department.id, Department.department_address)
                    .filter(Department.id == admin.department_id).all())

        if form.validate_on_submit():
            # user.username = form.username.data  - я сделала так, что изменять нельзя, потому что кому нужны эти заморочки
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.patronymic = form.patronymic.data
            user.birth_date = form.birth_date.data
            user.phone_number = form.phone_number.data

            if form.password.data != '':
                user.set_password(form.password.data)

            db.session.commit()
            return redirect(url_for('home'))
        else:
            print(form.errors)

    return render_template('profile.html', form=form, user_role=user_role, dept=dept)


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

    return jsonify(converted_amount=converted_amount)


def get_rates(to_currency, from_currency):
    latest_date = CurrencyRate.query.order_by(CurrencyRate.date.desc()).first().date
    latest_rates = (CurrencyRate.query.filter_by(
        date=latest_date,
        to_currency_id=Currency.query.filter_by(currency_name=to_currency).first().id,
        from_currency_id=Currency.query.filter_by(currency_name=from_currency).first().id)
    .first())

    return latest_rates.rate


if __name__ == '__main__':
    app.debug = True
    app.run()
