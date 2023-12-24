from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, PasswordField, SubmitField, DateField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    role = RadioField('Выберете роль:', choices=[], validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    first_name = StringField('Имя', validators=[])
    last_name = StringField('Фамилия', validators=[])
    patronymic = StringField('Отчество', validators=[])
    phone_number = StringField('Номер телефона', validators=[])
    birth_date = DateField('Дата рождения', format='%Y-%m-%d', validators=[])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    department = SelectField('Отдел', choices=[], validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ProfileEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[])
    email = StringField('Электронная почта', validators=[Email()])
    first_name = StringField('Имя', validators=[])
    last_name = StringField('Фамилия', validators=[])
    patronymic = StringField('Отчество', validators=[])
    phone_number = StringField('Номер телефона', validators=[])
    birth_date = DateField('Дата рождения', format='%Y-%m-%d', validators=[])
    password = PasswordField('Новый пароль', validators=[])
    confirm_password = PasswordField('Повторите пароль', validators=[EqualTo('password')])

    submit = SubmitField('Сохранить изменения')


class BankAccountForm(FlaskForm):
    account_name = StringField('Название счета', validators=[DataRequired()])
    balance = FloatField('Баланс', default=0.0)
    currency = SelectField('Валюта', choices=[], validators=[DataRequired()])

    submit = SubmitField('Сохранить')


class CreditRequestForm(FlaskForm):
    amount = FloatField('Сумма', default=0.0)
    credit_type = SelectField('Тип кредита', choices=[], validators=[DataRequired()])
    interest_rate = FloatField('Процентная ставка', default=0.0)
    department = SelectField('Отделение', choices=[], validators=[DataRequired()])
    term = IntegerField('Длительность', default=0)

    submit = SubmitField('Отправить')


class DepositRequestForm(FlaskForm):
    amount = FloatField('Сумма', default=0.0)
    deposit_type = SelectField('Тип кредита', choices=[], validators=[DataRequired()])
    interest_rate = FloatField('Процентная ставка', default=0.0)
    term = IntegerField('Длительность', default=0)

    submit = SubmitField('Отправить')


class ApproveRequestForm(FlaskForm):
    status = BooleanField('Статус', default=False)
    submit = SubmitField('Ok')


# class TransferTransactionForm(FlaskForm):
#     from_account = SelectField('Счет пользователя', choices=[], validators=[DataRequired()])
#     to_account = StringField('Электронная почта получателя','Электронная почта',
#                              validators=[Email(), DataRequired()])
#     amount = FloatField('Сумма', default=0.0)
#     category = SelectField('Категория перевода', choices=[], validators=[DataRequired()])
#
#     submit = SubmitField('Перевести')
