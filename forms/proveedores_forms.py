# Formularios de proveedores con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp


# Formulario para registrar y editar proveedores
class ProveedorForm(FlaskForm):

    # Nombre del proveedor
    nombre = StringField(
        "Nombre del proveedor",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
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

    # Correo electrónico del proveedor
    correo = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(message="El correo electrónico es obligatorio."),
            Email(message="Ingresa un correo electrónico válido."),
            Length(max=120, message="El correo no puede superar los 120 caracteres."),
        ],
    )

    # Botón para guardar el formulario
    submit = SubmitField("Guardar Proveedor")
