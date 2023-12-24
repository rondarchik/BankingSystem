from datetime import date
from functools import wraps
from sqlalchemy import event, desc
from dateutil.relativedelta import relativedelta
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

        if user_role == 'Админ':
            return render_template('profile_admin.html', form=form, user_role=user_role, dept=dept)

    return render_template('profile.html', form=form, user_role=user_role, dept=dept)


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
            return redirect(url_for('credit_admin'))

    return render_template('home.html', currencies=currencies, rates=rates, date=date_str)


@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    currency1 = data['currency1']
    input_currency1 = data['input_currency1']
    currency2 = data['currency2']
    input_currency2 = data['input_currency2']

    if input_currency1:
        amount = float(input_currency1)
        from_currency = currency1
        to_currency = currency2
        rate = get_rates(to_currency, from_currency)
        converted_amount = float(amount) / rate
    elif input_currency2:
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


def get_user_accounts(user):
    user_accounts = BankAccount.query.filter_by(user_id=user.id).all()
    return user_accounts


@app.route('/bank_account', methods=['POST', 'GET'])
@login_required
def bank_account():
    user_accounts = get_user_accounts(current_user)
    return render_template('bank_account.html', user_accounts=user_accounts)


@app.route('/create_account', methods=['POST', 'GET'])
@login_required
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
def credit():
    new_credits, applications = get_user_credits_and_applications(current_user.id)

    user_role = UserRole.query.filter_by(user_id=current_user.id).first().role.role_name
    if user_role == 'Админ':
        return render_template('credit_admin.html')

    return render_template('credit.html', credits=new_credits, applications=applications)


@app.route('/get_credit_data/<int:credit_type_id>', methods=['GET'])
def get_credit_data(credit_type_id):
    credit_type = CreditType.query.get(credit_type_id)

    if credit_type:
        data = {
            'interest_rate': credit_type.interest_rate,
            'term': credit_type.term,
            'min_amount': credit_type.min_amount,
            'max_amount': credit_type.max_amount,
        }
        return jsonify(data)
    else:
        return jsonify({'error': 'Credit type not found'}), 404


@app.route('/create_credit', methods=['POST', 'GET'])
@login_required
def create_credit():
    form = CreditRequestForm()

    departments = Department.query.with_entities(Department.id, Department.department_address).all()
    form.department.choices = [(dept.id, dept.department_address) for dept in departments]

    types = CreditType.query.all()
    form.credit_type.choices = [(_type.id, _type.type_name, _type.min_amount,
                                _type.max_amount, _type.interest_rate, _type.term) for _type in types]

    if current_user.get_age() < 18:
        flash('Вам должно быть не менее 18 лет, чтобы подать заявку на кредит.',
              'error')
        return redirect(url_for('credit'))
    elif (current_user.phone_number or current_user.first_name
          or current_user.last_name or current_user.patronymic) == '':
        flash('Не достаточно личных данных.',
              'error')
        return redirect(url_for('credit'))

    if form.validate_on_submit():
        application = CreditRequest(
            user_id=current_user.id,
            amount=form.amount.data,
            department_id=form.department.data,
            type_id=form.credit_type.data
        )

        db.session.add(application)
        db.session.commit()
        return redirect(url_for('credit'))
    else:
        print(form.errors)

    return render_template('new_credit.html', form=form)


def get_admin_credits_and_applications(user):
    admin_department_id = Admin.query.filter_by(id=user).first().department_id
    credit_requests = CreditRequest.query.filter_by(department_id=admin_department_id).all()
    return credit_requests


def get_application(application):
    credit_requests = CreditRequest.query.filter_by(id=application).first()
    return credit_requests


@app.route('/update_status', methods=['POST'])
def update_credit_request():
    application_id = request.form.get('app_id')
    application = get_application(application_id)

    if application:
        application.status = True

        new_credit = Credit(
            user_id=application.user.id,
            amount=application.amount,
            repaid_amount=0,
            interest_rate=application.interest_rate,
            start_date=date.today(),
            end_date=date.today() + relativedelta(months=+application.date_term),
            is_closed=False
        )
        db.session.add(new_credit)
        db.session.commit()

    return redirect(url_for('credit_admin'))


@app.route('/credit_admin', methods=['POST', 'GET'])
@login_required
def credit_admin():
    applications = get_admin_credits_and_applications(current_user.id)

    return render_template('credit_admin.html', applications=applications)


def get_user_deposits(user):
    user_deposits = Deposit.query.filter_by(user_id=user.id).all()
    return user_deposits


@app.route('/deposit', methods=['POST', 'GET'])
@login_required
def deposit():
    deposits = get_user_deposits(current_user)

    return render_template('deposit.html', deposits=deposits)


@app.route('/get_deposit_data/<int:deposit_type_id>', methods=['GET'])
def get_deposit_data(deposit_type_id):
    deposit_type = DepositType.query.get(deposit_type_id)

    if deposit_type:
        data = {
            'interest_rate': deposit_type.interest_rate,
            'term': deposit_type.term,
            'min_amount': deposit_type.min_amount,
        }
        return jsonify(data)
    else:
        return jsonify({'error': 'Deposit type not found'}), 404


def get_account_for_deposit_trans(user, sum):
    account = BankAccount.query.filter(
        BankAccount.user_id == user.id,
        BankAccount.currency_id == Currency.query.filter_by(currency_name='BYN').first().id,
        BankAccount.balance >= sum
    ).order_by(desc(BankAccount.balance)).first()

    return account


def get_category_for_deposit_trans():
    category_id = Category.query.filter_by(category_name='Пополнение вклада').first().id
    return category_id


@app.route('/create_deposit', methods=['POST', 'GET'])
@login_required
def create_deposit():
    form = DepositRequestForm()

    types = DepositType.query.all()
    form.deposit_type.choices = [(_type.id, _type.type_name, _type.min_amount,
                                  _type.interest_rate, _type.term) for _type in types]

    if current_user.get_age() < 18:
        flash('Вам должно быть не менее 18 лет, чтобы подать заявку на вклад.',
              'error')
        return redirect(url_for('deposit'))
    elif (current_user.phone_number or current_user.first_name
          or current_user.last_name or current_user.patronymic) == '':
        flash('Не достаточно личных данных.',
              'error')
        return redirect(url_for('deposit'))

    if form.validate_on_submit():
        amount = form.amount.data
        account = get_account_for_deposit_trans(current_user, amount)
        if account:
            new_deposit = Deposit(
                user_id=current_user.id,
                amount=amount,
                type_id=form.deposit_type.data,
                start_date=date.today(),
                end_date=date.today(),
                is_closed=False
            )

            db.session.add(new_deposit)
            db.session.commit()

            new_deposit.end_date = date.today() + relativedelta(months=+new_deposit.type.term),
            db.session.commit()

            new_transaction = Transaction(
                from_account_id=account.id,
                amount=amount,
                transaction_date=date.today(),
                category_id=get_category_for_deposit_trans(),
                status=True,
            )

            account.balance -= amount

            db.session.add(new_transaction)
            db.session.commit()

            return redirect(url_for('deposit'))
        else:
            flash('Не существует счета в валюте BYN или недостаточно средств.',
                  'error')
    else:
        print(form.errors)

    return render_template('new_deposit.html', form=form)


def get_user_accounts(user):
    user_accounts = BankAccount.query.filter_by(user_id=user.id).all()
    return user_accounts


@app.route('/transfer_transaction', methods=['POST', 'GET'])
@login_required
def transfer_transaction():
    return render_template('trans_transfer.html')


@app.route('/currency_transaction', methods=['POST', 'GET'])
@login_required
def currency_transaction():
    return render_template('trans_currency.html')


def get_payment_categories():
    selected_category_ids = [2, 3, 6]
    selected_categories = Category.query.filter(Category.id.in_(selected_category_ids)).all()

    return selected_categories


@app.route('/refill_transaction', methods=['POST', 'GET'])
@login_required
def refill_transaction():
    form = RefillTransactionForm()

    accounts = get_user_accounts(current_user)
    form.to_account.choices = [(account.id, account.account_name) for account in accounts]

    if form.validate_on_submit():
        category_id = Category.query.filter_by(category_name='Пополнение счета').first().id
        to_account_id = int(request.form['to_account'])
        account = BankAccount.query.get(to_account_id)

        new_transaction = Transaction(
            to_account_id=to_account_id,
            amount=form.amount.data,
            transaction_date=date.today(),
            category_id=category_id,
            status=True,
        )

        account.balance += new_transaction.amount

        db.session.add(new_transaction)
        db.session.commit()
    else:
        print(form.errors)

    return render_template('trans_refill.html', form=form)


if __name__ == '__main__':
    app.debug = True
    app.run()
