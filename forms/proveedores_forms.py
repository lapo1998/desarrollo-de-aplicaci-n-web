# Formularios de proveedores con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email


# Formulario para registrar y editar proveedores
class ProveedorForm(FlaskForm):

    # Nombre del proveedor
    nombre = StringField(
        "Nombre del proveedor",
        validators=[
            DataRequired(message="El nombre del proveedor es obligatorio."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
        ],
    )

    # Rubro al que pertenece el proveedor
    rubro = SelectField(
        "Rubro",
        choices=[
            ("Hogar", "Hogar"),
            ("Tecnología", "Tecnología"),
            ("Moda", "Moda"),
            ("Alimentos", "Alimentos"),
            ("Otros", "Otros"),
        ],
        validators=[DataRequired(message="Debes seleccionar un rubro.")],
    )

    # Ciudad del proveedor
    ciudad = StringField(
        "Ciudad",
        validators=[
            DataRequired(message="La ciudad es obligatoria."),
            Length(min=3, max=60, message="La ciudad debe tener entre 3 y 60 caracteres."),
        ],
    )

    # Correo de contacto
    contacto = StringField(
        "Correo de contacto",
        validators=[
            DataRequired(message="El contacto es obligatorio."),
            Email(message="Ingresa un correo electrónico válido."),
        ],
    )

    # Botón para guardar el formulario
    submit = SubmitField("Guardar Proveedor")