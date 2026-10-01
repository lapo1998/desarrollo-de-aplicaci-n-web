# Formularios de clientes con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp


# Formulario para registrar y editar clientes
class ClienteForm(FlaskForm):

    # Nombre del cliente
    nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
        ],
    )

    # Cédula ecuatoriana (10 dígitos)
    cedula = StringField(
        "Cédula",
        validators=[
            DataRequired(message="La cédula es obligatoria."),
            Regexp(r"^\d{10}$", message="La cédula debe tener exactamente 10 dígitos."),
        ],
    )

    # Correo electrónico del cliente
    correo = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(message="El correo electrónico es obligatorio."),
            Email(message="Ingresa un correo electrónico válido."),
        ],
    )

    # Teléfono con formato ecuatoriano
    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(message="El teléfono es obligatorio."),
            Regexp(
                r"^0\d{9}$",
                message="El teléfono debe tener 10 dígitos y empezar con 0 (ej: 0991234567).",
            ),
        ],
    )

    # Botón para guardar el formulario
    submit = SubmitField("Guardar Cliente")
