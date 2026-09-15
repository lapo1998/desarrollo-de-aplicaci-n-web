from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

from forms.productos_forms import ProductoForm
from forms.clientes_forms import ClienteForm
from forms.proveedores_forms import ProveedorForm
from forms.facturacion_forms import FacturaForm
from forms.login_form import LoginForm
from forms.usuario_form import UsuarioForm
from conexion.conexion import obtener_conexion
from models import Usuario


# Configuración principal de la aplicación
app = Flask(__name__)

# Clave para proteger los formularios con CSRF y las sesiones de login
app.config["SECRET_KEY"] = "clave-secreta-ecuacompras-dev-2026"


# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "warning"


# Recupera el usuario desde la base de datos a partir de su id (lo pide Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()

    if fila is None:
        return None

    return Usuario(fila["id"], fila["usuario"], fila["password"])


# Devuelve la lista de proveedores (id, nombre) para llenar el select del formulario
def obtener_choices_proveedores():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id_proveedor, nombre FROM proveedores")
    choices = cursor.fetchall()
    cursor.close()
    conn.close()
    return choices


# Datos temporales de clientes
clientes_ejemplo = [
    {"nombre": "María Torres", "correo": "maria.torres@email.com", "ciudad": "Loja", "telefono": "0991234567"},
    {"nombre": "Carlos Jiménez", "correo": "carlos.jimenez@email.com", "ciudad": "Cariamanga", "telefono": "0987654321"},
    {"nombre": "Ana Suárez", "correo": "ana.suarez@email.com", "ciudad": "Quito", "telefono": "0965432198"},
]


# Datos temporales de proveedores
proveedores_ejemplo = [
    {"nombre": "Textiles Loja", "rubro": "Moda", "ciudad": "Loja", "contacto": "textilesloja@email.com"},
    {"nombre": "TecnoImport EC", "rubro": "Tecnología", "ciudad": "Quito", "contacto": "ventas@tecnoimport.com"},
    {"nombre": "Sabores del Sur", "rubro": "Alimentos", "ciudad": "Cariamanga", "contacto": "contacto@saboresdelsur.com"},
]


# Datos temporales de facturación
facturas_ejemplo = [
    {"numero": "F001", "cliente": "María Torres", "fecha": "2026-08-01", "total": 45.50, "estado": "Pagada"},
    {"numero": "F002", "cliente": "Carlos Jiménez", "fecha": "2026-08-05", "total": 18.99, "estado": "Pendiente"},
    {"numero": "F003", "cliente": "Ana Suárez", "fecha": "2026-08-10", "total": 32.75, "estado": "Pagada"},
]


# Información general del sistema
info_sistema = {
    "nombre": "EcuaCompras",
    "version": "1.0",
    "anio": 2026,
    "estudiante": "Elvio Manuel Lapo Agreda",
    "asignatura": "Desarrollo de Aplicaciones Web",
}


# Envía información general a las plantillas
@app.context_processor
def inject_info_sistema():
    return {"info_sistema": info_sistema}


# Página principal
@app.route("/")
def index():
    return render_template("index.html")


# Inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (form.usuario.data,))
        fila = cursor.fetchone()
        cursor.close()
        conn.close()

        # Nunca comparamos la contraseña escrita directo con la guardada: usamos check_password_hash
        if fila and check_password_hash(fila["password"], form.password.data):
            usuario = Usuario(fila["id"], fila["usuario"], fila["password"])
            login_user(usuario)
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for("index"))

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("login.html", form=form)


# Registrar un nuevo usuario del sistema
@app.route("/registro", methods=["GET", "POST"])
def registro():
    form = UsuarioForm()

    if form.validate_on_submit():
        # Nunca guardamos la contraseña en texto plano: la transformamos con hash
        password_hash = generate_password_hash(form.password.data)

        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, password) VALUES (%s, %s)",
                (form.usuario.data, password_hash),
            )
            conn.commit()
            flash("Usuario registrado correctamente. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        except mysql.connector.IntegrityError:
            flash("Ese nombre de usuario ya existe.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("registro.html", form=form)


# Cerrar sesión
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("login"))


# Módulo de productos (ahora persistido en MySQL)
@app.route("/productos")
@login_required
def productos():
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    # JOIN con proveedores para mostrar también el nombre del proveedor
    cursor.execute("""
        SELECT p.id_producto, p.nombre, p.categoria, p.precio, p.stock,
               p.id_proveedor, pr.nombre AS proveedor
        FROM productos p
        JOIN proveedores pr ON p.id_proveedor = pr.id_proveedor
    """)
    productos_bd = cursor.fetchall()

    cursor.close()
    conn.close()

    total_productos = len(productos_bd)
    return render_template(
        "productos.html",
        productos=productos_bd,
        total_productos=total_productos,
    )


# Registrar un producto (INSERT en la base de datos)
@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    form = ProductoForm()
    form.proveedor.choices = obtener_choices_proveedores()

    # Solo guardamos si el formulario pasa las validaciones
    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, categoria, precio, stock, id_proveedor) VALUES (%s, %s, %s, %s, %s)",
            (form.nombre.data, form.categoria.data, form.precio.data, form.stock.data, form.proveedor.data),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Producto registrado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template("productos_form.html", form=form, producto=None)


# Editar un producto (SELECT para cargar y UPDATE para guardar cambios)
@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_producto(id):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()

    # Si el producto no existe, regresamos al listado
    if producto is None:
        cursor.close()
        conn.close()
        flash("El producto solicitado no existe.", "danger")
        return redirect(url_for("productos"))

    form = ProductoForm(data={
        "nombre": producto["nombre"],
        "categoria": producto["categoria"],
        "precio": producto["precio"],
        "stock": producto["stock"],
        "proveedor": producto["id_proveedor"],
    })
    form.proveedor.choices = obtener_choices_proveedores()

    # Actualiza el producto si los datos son válidos
    if form.validate_on_submit():
        cursor.execute(
            "UPDATE productos SET nombre = %s, categoria = %s, precio = %s, stock = %s, id_proveedor = %s WHERE id_producto = %s",
            (form.nombre.data, form.categoria.data, form.precio.data, form.stock.data, form.proveedor.data, id),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos"))

    cursor.close()
    conn.close()
    return render_template("productos_form.html", form=form, producto=producto)


# Eliminar un producto (DELETE en la base de datos)
@app.route("/productos/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_producto(id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Producto eliminado correctamente.", "success")
    return redirect(url_for("productos"))


# Módulo de clientes
@app.route("/clientes")
@login_required
def clientes():
    return render_template("clientes.html", clientes=clientes_ejemplo)


# Registrar un cliente
@app.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    form = ClienteForm()

    # Procesa el formulario si pasa las validaciones
    if form.validate_on_submit():
        clientes_ejemplo.append({
            "nombre": form.nombre.data,
            "correo": form.correo.data,
            "ciudad": form.ciudad.data,
            "telefono": form.telefono.data,
        })
        flash("Cliente registrado correctamente.", "success")
        return redirect(url_for("clientes"))

    return render_template("clientes_form.html", form=form, cliente=None)


# Editar un cliente
@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cliente(id):
    if id < 0 or id >= len(clientes_ejemplo):
        flash("El cliente solicitado no existe.", "danger")
        return redirect(url_for("clientes"))

    cliente = clientes_ejemplo[id]
    form = ClienteForm(data=cliente)

    # Actualiza el cliente si los datos son válidos
    if form.validate_on_submit():
        cliente["nombre"] = form.nombre.data
        cliente["correo"] = form.correo.data
        cliente["ciudad"] = form.ciudad.data
        cliente["telefono"] = form.telefono.data
        flash("Cliente actualizado correctamente.", "success")
        return redirect(url_for("clientes"))

    return render_template("clientes_form.html", form=form, cliente=cliente)


# Módulo de proveedores
@app.route("/proveedores")
@login_required
def proveedores():
    return render_template("proveedores.html", proveedores=proveedores_ejemplo)


# Registrar un proveedor
@app.route("/proveedores/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()

    # Procesa el formulario si pasa las validaciones
    if form.validate_on_submit():
        proveedores_ejemplo.append({
            "nombre": form.nombre.data,
            "rubro": form.rubro.data,
            "ciudad": form.ciudad.data,
            "contacto": form.contacto.data,
        })
        flash("Proveedor registrado correctamente.", "success")
        return redirect(url_for("proveedores"))

    return render_template("proveedores_form.html", form=form, proveedor=None)


# Editar un proveedor
@app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_proveedor(id):
    if id < 0 or id >= len(proveedores_ejemplo):
        flash("El proveedor solicitado no existe.", "danger")
        return redirect(url_for("proveedores"))

    proveedor = proveedores_ejemplo[id]
    form = ProveedorForm(data=proveedor)

    # Actualiza el proveedor si los datos son válidos
    if form.validate_on_submit():
        proveedor["nombre"] = form.nombre.data
        proveedor["rubro"] = form.rubro.data
        proveedor["ciudad"] = form.ciudad.data
        proveedor["contacto"] = form.contacto.data
        flash("Proveedor actualizado correctamente.", "success")
        return redirect(url_for("proveedores"))

    return render_template("proveedores_form.html", form=form, proveedor=proveedor)


# Módulo de facturación
@app.route("/facturacion")
@login_required
def facturacion():
    return render_template("facturacion.html", facturas=facturas_ejemplo)


# Registrar una factura
@app.route("/facturacion/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    form = FacturaForm()

    # Procesa la factura si pasa las validaciones
    if form.validate_on_submit():
        facturas_ejemplo.append({
            "numero": form.numero.data,
            "cliente": form.cliente.data,
            "fecha": form.fecha.data.strftime("%Y-%m-%d"),
            "total": form.total.data,
            "estado": form.estado.data,
        })
        flash("Factura registrada correctamente.", "success")
        return redirect(url_for("facturacion"))

    return render_template("facturacion_form.html", form=form, factura=None)


# Editar una factura
@app.route("/facturacion/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_factura(id):
    if id < 0 or id >= len(facturas_ejemplo):
        flash("La factura solicitada no existe.", "danger")
        return redirect(url_for("facturacion"))

    factura = facturas_ejemplo[id]

    # Convierte la fecha para mostrarla correctamente
    datos_iniciales = dict(factura)
    datos_iniciales["fecha"] = datetime.strptime(
        factura["fecha"], "%Y-%m-%d"
    ).date()

    form = FacturaForm(data=datos_iniciales)

    # Actualiza la factura si los datos son válidos
    if form.validate_on_submit():
        factura["numero"] = form.numero.data
        factura["cliente"] = form.cliente.data
        factura["fecha"] = form.fecha.data.strftime("%Y-%m-%d")
        factura["total"] = form.total.data
        factura["estado"] = form.estado.data
        flash("Factura actualizada correctamente.", "success")
        return redirect(url_for("facturacion"))

    return render_template("facturacion_form.html", form=form, factura=factura)


# Inicia la aplicación
if __name__ == "__main__":
    app.run(debug=True)
