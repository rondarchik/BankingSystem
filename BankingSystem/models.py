from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from init_db import db
from werkzeug.security import generate_password_hash,  check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    patronymic = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    birth_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Client(db.Model):
    __tablename__ = 'Clients'
    id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    # pref_currency_id = db.Column(db.Integer, db.ForeignKey('Currencies.id'), default=1)  # default = BYN (1)
    client_id = db.relationship('User', foreign_keys=[id])


class Admin(db.Model):
    __tablename__ = 'Admins'
    id = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('Departments.id'), nullable=False)

    admin_id = db.relationship('User', foreign_keys=[id])
    department = db.relationship('Department', foreign_keys=[department_id])


class Role(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)


class UserRole(db.Model):
    __tablename__ = 'UsersRoles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('Roles.id'), nullable=False)

    user = db.relationship('User', foreign_keys=[user_id])
    role = db.relationship('Role', foreign_keys=[role_id])


class Department(db.Model):
    __tablename__ = 'Departments'
    id = db.Column(db.Integer, primary_key=True)
    department_address = db.Column(db.String(200), nullable=False)


class Currency(db.Model):
    __tablename__ = 'Currencies'
    id = db.Column(db.Integer, primary_key=True)
    currency_name = db.Column(db.String(3), nullable=False)


class CurrencyRate(db.Model):
    __tablename__ = 'CurrencyRates'
    id = db.Column(db.Integer, primary_key=True)
    from_currency_id = db.Column(db.Integer, db.ForeignKey('Currencies.id'), nullable=False)
    to_currency_id = db.Column(db.Integer, db.ForeignKey('Currencies.id'), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    rate_type = db.Column(db.Integer, db.ForeignKey('RateTypes.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    from_currency = db.relationship('Currency', foreign_keys=[from_currency_id])
    to_currency = db.relationship('Currency', foreign_keys=[to_currency_id])


class RateType(db.Model):
    __tablename__ = 'RateTypes'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False)


class BankAccount(db.Model):
    __tablename__ = 'BankAccounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('Currencies.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    account_name = db.Column(db.String(50), nullable=False)


class Category(db.Model):
    __tablename__ = 'Categories'
    id = db.Column(db.Integer, primary_key=True)
    currency_name = db.Column(db.String(50), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('CategoryTypes.id'), nullable=False)  # default?


class CategoryType(db.Model):
    __tablename__ = 'CategoryTypes'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), nullable=False)


class Transaction(db.Model):
    __tablename__ = 'Transactions'
    id = db.Column(db.Integer, primary_key=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('BankAccounts.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('BankAccounts.id'))
    amount = db.Column(db.Float, default=0.0)
    transaction_date = db.Column(db.DateTime, default=datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey('Categories.id'), nullable=False)
    status = db.Column(db.Boolean, default=False)


class Credit(db.Model):
    __tablename__ = 'Credits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    repaid_amount = db.Column(db.Float, default=0.0)
    interest_rate = db.Column(db.Float, default=0.1)
    start_date = db.Column(db.DateTime, default=datetime.now)
    end_date = db.Column(db.DateTime, default=datetime.now)
    is_closed = db.Column(db.Boolean, default=False)


class CreditRequest(db.Model):
    __tablename__ = 'CreditsRequests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('Departments.id'), nullable=False)
    status = db.Column(db.Boolean, default=False)
    request_date = db.Column(db.DateTime, default=datetime.now)


class Deposit(db.Model):
    __tablename__ = 'Deposits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    deposit_amount = db.Column(db.Float, default=0.0)
    interest_rate = db.Column(db.Float, default=0.1)
    start_date = db.Column(db.DateTime, default=datetime.now)
    end_date = db.Column(db.DateTime, default=datetime.now)
    is_closed = db.Column(db.Boolean, default=False)