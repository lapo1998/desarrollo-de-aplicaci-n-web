# Formularios de productos con Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, InputRequired


# Formulario para registrar y editar productos
class ProductoForm(FlaskForm):

    # Nombre del producto
    nombre = StringField(
        "Nombre del producto",
        validators=[
            DataRequired(message="El nombre del producto es obligatorio."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
        ],
    )

    # Categoría del producto
    categoria = SelectField(
        "Categoría",
        choices=[
            ("Hogar", "Hogar"),
            ("Tecnología", "Tecnología"),
            ("Moda", "Moda"),
            ("Alimentos", "Alimentos"),
            ("Otros", "Otros"),
        ],
        validators=[DataRequired(message="Debes seleccionar una categoría.")],
    )

    # Precio del producto
    precio = FloatField(
        "Precio ($)",
        validators=[
            DataRequired(message="El precio es obligatorio."),
            NumberRange(min=0.01, message="El precio debe ser mayor a 0."),
        ],
    )

    # Cantidad disponible en stock
    stock = IntegerField(
        "Stock disponible",
        validators=[
            DataRequired(message="El stock es obligatorio."),
            NumberRange(min=0, message="El stock no puede ser negativo."),
        ],
    )

    # Proveedor del producto (relación FK con la tabla proveedores)
    # Los choices se llenan en app.py con los proveedores que hay en la BD
    proveedor = SelectField(
        "Proveedor",
        coerce=int,
        validators=[InputRequired(message="Debes seleccionar un proveedor.")],
    )

    # Botón para guardar el formulario
    submit = SubmitField("Guardar Producto")
