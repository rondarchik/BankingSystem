from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, PasswordField, SubmitField, DateField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length


class RegistrationForm(FlaskForm):
    role = RadioField('Выберете роль:', choices=[], validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email(message='Invalid email format')])
    first_name = StringField('Имя', validators=[])
    last_name = StringField('Фамилия', validators=[])
    patronymic = StringField('Отчество', validators=[])
    phone_number = StringField('Номер телефона',
                               validators=[Regexp(r'^\+?\d{12}$', message='Invalid phone format')])
    birth_date = DateField('Дата рождения', format='%Y-%m-%d', validators=[])
    password = PasswordField('Пароль',
                             validators=[DataRequired(),
                                         Regexp(r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$', message='Invalid password'),
                                         Length(min=8, message='Password must be at least 8 characters long')
                                         ])
    confirm_password = PasswordField('Повторите пароль',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    department = SelectField('Отдел', choices=[], validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ProfileEditForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Электронная почта', validators=[DataRequired(), Email(message='Invalid email format')])
    first_name = StringField('Имя', validators=[])
    last_name = StringField('Фамилия', validators=[])
    patronymic = StringField('Отчество', validators=[])
    phone_number = StringField('Номер телефона',
                               validators=[Regexp(r'^\+?\d{12}$', message='Invalid phone format')])
    birth_date = DateField('Дата рождения', format='%Y-%m-%d', validators=[])
    password = PasswordField('Новый пароль',
                             validators=[DataRequired(),
                                         Regexp(r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$', message='Invalid password'),
                                         Length(min=8, message='Password must be at least 8 characters long')
                                         ])
    confirm_password = PasswordField('Повторите пароль',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

    submit = SubmitField('Сохранить изменения')


class BankAccountForm(FlaskForm):
    account_name = StringField('Название счета', validators=[DataRequired()])
    balance = FloatField('Баланс', default=0.0, validators=[DataRequired()])
    currency = SelectField('Валюта', choices=[], validators=[DataRequired()])

    submit = SubmitField('Сохранить')


class CreditRequestForm(FlaskForm):
    amount = FloatField('Сумма', default=0.0, validators=[DataRequired()])
    credit_type = SelectField('Тип кредита', choices=[], validators=[DataRequired()])
    interest_rate = FloatField('Процентная ставка', default=0.0, validators=[])
    department = SelectField('Отделение', choices=[], validators=[DataRequired()])
    term = IntegerField('Длительность', default=0, validators=[])

    submit = SubmitField('Отправить')


class DepositRequestForm(FlaskForm):
    amount = FloatField('Сумма', default=0.0, validators=[DataRequired()])
    deposit_type = SelectField('Тип кредита', choices=[], validators=[DataRequired()])
    interest_rate = FloatField('Процентная ставка', default=0.0, validators=[])
    term = IntegerField('Длительность', default=0, validators=[])

    submit = SubmitField('Отправить')


class ApproveRequestForm(FlaskForm):
    status = BooleanField('Статус', default=False)
    submit = SubmitField('Ok')


class TransferTransactionForm(FlaskForm):
    from_account = SelectField('Счет пользователя', choices=[], validators=[DataRequired()])
    to_account = StringField('Электронная почта получателя',
                             validators=[Email(message='Invalid email format'), DataRequired()])
    amount = FloatField('Сумма', default=0.0, validators=[DataRequired()])

    submit = SubmitField('Перевести')


class RefillTransactionForm(FlaskForm):
    to_account = SelectField('Счет пользователя', choices=[], validators=[DataRequired()])
    amount = FloatField('Сумма', default=0.0, validators=[DataRequired()])

    submit = SubmitField('Подтвердить')


class CreditTransactionForm(FlaskForm):
    from_account = SelectField('Счет пользователя', choices=[], validators=[DataRequired()])
    amount = FloatField('Сумма', default=0.0, validators=[DataRequired()])
    credit = SelectField('Кредит пользователя', choices=[], validators=[DataRequired()])

    submit = SubmitField('Подтвердить')


class CurrencyOperationTransactionForm(FlaskForm):
    from_account = SelectField('Исходный счет', choices=[], validators=[DataRequired()])
    amount = FloatField('Сумма', default=0.0, validators=[DataRequired()])
    from_currency = SelectField('Исходная валюта', choices=[], validators=[DataRequired()])
    to_account = SelectField('Счет', choices=[], validators=[DataRequired()])
    res_amount = FloatField('Итоговая сумма', default=0.0, validators=[DataRequired()])
    to_currency = SelectField('Валюта', choices=[], validators=[DataRequired()])

    submit = SubmitField('Подтвердить')


class DepositTransactionForm(FlaskForm):
    from_account = SelectField('Счет пользователя', choices=[], validators=[DataRequired()])
    amount = FloatField('Сумма', default=0.0, validators=[DataRequired()])
    deposit = SelectField('Депозит пользователя', choices=[], validators=[DataRequired()])

    submit = SubmitField('Подтвердить')
