# Formularios de facturación con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


# Formulario para registrar y editar facturas
class FacturaForm(FlaskForm):

    # Número de factura
    numero = StringField(
        "N° Factura",
        validators=[
            DataRequired(message="El número de factura es obligatorio."),
            Length(min=2, max=20, message="El número debe tener entre 2 y 20 caracteres."),
        ],
    )

    # Cliente de la factura
    cliente = StringField(
        "Cliente",
        validators=[
            DataRequired(message="El nombre del cliente es obligatorio."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
        ],
    )

    # Fecha de la factura
    fecha = DateField(
        "Fecha",
        format="%Y-%m-%d",
        validators=[DataRequired(message="La fecha es obligatoria.")],
    )

    # Total de la factura
    total = FloatField(
        "Total ($)",
        validators=[
            DataRequired(message="El total es obligatorio."),
            NumberRange(min=0.01, message="El total debe ser mayor a 0."),
        ],
    )

    # Estado de la factura
    estado = SelectField(
        "Estado",
        choices=[("Pagada", "Pagada"), ("Pendiente", "Pendiente")],
        validators=[DataRequired(message="Debes seleccionar un estado.")],
    )

    # Botón para guardar el formulario
    submit = SubmitField("Guardar Factura")