from sqlalchemy import desc, func
from sqlalchemy.orm import aliased

from models import *


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


def get_user_credits_and_applications(user):
    user_credits = Credit.query.filter_by(user_id=user).all()
    user_applications = CreditRequest.query.filter_by(user_id=user, status=False).all()
    return user_credits, user_applications


def get_admin_credits_and_applications(user):
    admin_department_id = Admin.query.filter_by(id=user).first().department_id
    credit_requests = CreditRequest.query.filter_by(department_id=admin_department_id).all()
    return credit_requests


def get_application(application):
    credit_requests = CreditRequest.query.filter_by(id=application).first()
    return credit_requests


def get_user_deposits(user):
    user_deposits = Deposit.query.filter_by(user_id=user.id).all()
    return user_deposits


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


def get_all_user_accounts(user):
    user_accounts = BankAccount.query.filter_by(user_id=user.id).all()
    return user_accounts


def get_user_credits(user):
    user_credits = Credit.query.filter_by(user_id=user.id, is_closed=False).all()
    return user_credits


def get_user_byn_accounts(user):
    user_accounts = BankAccount.query.filter_by(user_id=user.id,
                                                currency_id=Currency.query.filter_by(currency_name='BYN').first().id,
                                                ).all()
    return user_accounts


def get_user_currency_accounts(user, currency):
    user_accounts = BankAccount.query.filter_by(user_id=user.id,
                                                currency_id=currency,
                                                ).all()
    return user_accounts


def get_user_deposits(user):
    user_deposits = Deposit.query.filter_by(user_id=user.id, is_closed=False).all()
    return user_deposits


def get_user_transactions(user, date_filter=None, period_start=None, period_end=None, transaction_type='all'):
    query = Transaction.query.join(BankAccount, (BankAccount.id == Transaction.from_account_id) | (
                BankAccount.id == Transaction.to_account_id))

    query = query.filter(BankAccount.user_id == user.id)

    if date_filter:
        query = query.filter(func.date(Transaction.transaction_date) == date_filter.date())

    if period_start and period_end:
        query = query.filter(Transaction.transaction_date.between(period_start, period_end))

    if transaction_type != 'all':
        category_alias = aliased(Category)
        category_type_alias = aliased(CategoryType)

        query = (
            query
            .join(category_alias, category_alias.id == Transaction.category_id)
            .join(category_type_alias, category_type_alias.id == category_alias.type_id)
            .filter(category_type_alias.type_name == transaction_type)
        )

    user_transactions = query.all()

    return user_transactions


def get_currency_rate_from_database(from_currency_id, to_currency_id):
    currency_rate = CurrencyRate.query.filter_by(
        from_currency_id=from_currency_id,
        to_currency_id=to_currency_id
    ).first()

    if currency_rate:
        return currency_rate.rate
    else:
        return 1.0


def user_exists(email):
    user = User.query.filter_by(email=email).first()
    return user is not None


def get_transfer_requests_by_user_email(email):
    return TransferRequest.query.filter_by(to_user=email).all()


def get_account_by_user_email(user):
    return BankAccount.equest.query.filter_by(user_id=user.id).all()