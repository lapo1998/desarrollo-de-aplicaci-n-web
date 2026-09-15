# Formulario de registro de usuarios con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo


# Formulario para registrar un nuevo usuario del sistema
class UsuarioForm(FlaskForm):

    # Nombre de usuario (debe ser único en la base de datos)
    usuario = StringField(
        "Usuario",
        validators=[
            DataRequired(message="El usuario es obligatorio."),
            Length(min=3, max=50, message="El usuario debe tener entre 3 y 50 caracteres."),
        ],
    )

    # Contraseña (se guarda con hash, nunca en texto plano)
    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres."),
        ],
    )

    # Confirmación de la contraseña
    confirmar = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Debes confirmar la contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )

    # Botón para registrarse
    submit = SubmitField("Registrarse")
