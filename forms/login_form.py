# Formulario de inicio de sesión con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


# Formulario para iniciar sesión
class LoginForm(FlaskForm):

    # Nombre de usuario
    usuario = StringField(
        "Usuario",
        validators=[DataRequired(message="El usuario es obligatorio.")],
    )

    # Contraseña
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria.")],
    )

    # Botón para ingresar
    submit = SubmitField("Ingresar")
