from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, RadioField, SelectField
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

