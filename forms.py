from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo, DataRequired

from models import User


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Имя пользователя"})
    password1 = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Пароль"})
    password2 = PasswordField(
        validators=[
            InputRequired(),
            Length(min=8, max=20),
            EqualTo('password1', 'Пароли не совпадают')
        ],
        render_kw={"placeholder": "Введите пароль повторно"}
    )
    submit = SubmitField('Зарегистрироваться')

    # def validate(self, extra_validators=None):
    #     if self.password1 != self.password2:
    #         raise ValidationError(
    #             'Пороли не софпадают'
    #         )

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'Пользователь с таким именем уже существует'
            )


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Имя пользователя"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Пароль"})

    submit = SubmitField('Войти')
