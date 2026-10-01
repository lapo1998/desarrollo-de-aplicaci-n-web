# Formularios de facturación con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


# Formulario para registrar y editar facturas
class FacturaForm(FlaskForm):

    # Número de la factura
    numero = StringField(
        "Número de factura",
        validators=[
            DataRequired(message="El número de factura es obligatorio."),
            Length(min=1, max=20, message="El número puede tener máximo 20 caracteres."),
        ],
    )

    # Cliente (las opciones se cargan desde la base de datos en app.py)
    id_cliente = SelectField(
        "Cliente",
        coerce=int,
        validators=[DataRequired(message="Selecciona un cliente.")],
    )

    # Fecha de la factura
    fecha = DateField(
        "Fecha",
        format="%Y-%m-%d",
        validators=[DataRequired(message="La fecha es obligatoria.")],
    )

    # Total de la factura
    total = DecimalField(
        "Total ($)",
        places=2,
        validators=[
            DataRequired(message="El total es obligatorio."),
            NumberRange(min=0.01, message="El total debe ser mayor a 0."),
        ],
    )

    # Estado de la factura
    estado = SelectField(
        "Estado",
        choices=[("Pendiente", "Pendiente"), ("Pagada", "Pagada")],
        validators=[DataRequired(message="Selecciona un estado.")],
    )

    # Botón para guardar el formulario
    submit = SubmitField("Guardar Factura")
