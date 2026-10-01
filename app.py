from flask import Flask, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
import psycopg2.errors

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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
    cursor.execute("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre")
    choices = cursor.fetchall()
    cursor.close()
    conn.close()
    return choices


# Devuelve la lista de clientes (id, nombre) para llenar el select de facturas
def obtener_choices_clientes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre")
    choices = cursor.fetchall()
    cursor.close()
    conn.close()
    return choices


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
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
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


# ---------------------------------------------------------------
# MÓDULO DE PRODUCTOS (CRUD en base de datos)
# ---------------------------------------------------------------
@app.route("/productos")
@login_required
def productos():
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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


@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    form = ProductoForm()
    form.proveedor.choices = obtener_choices_proveedores()

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


@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_producto(id):
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cursor.fetchone()

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


@app.route("/productos/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_producto(id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))
        conn.commit()
        flash("Producto eliminado correctamente.", "success")
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        flash("No se puede eliminar: el producto está siendo usado en otro registro.", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("productos"))


# ---------------------------------------------------------------
# MÓDULO DE CLIENTES (CRUD en base de datos)
# ---------------------------------------------------------------
@app.route("/clientes")
@login_required
def clientes():
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT id_cliente, nombre, cedula, correo, telefono FROM clientes ORDER BY id_cliente"
    )
    clientes_bd = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("clientes.html", clientes=clientes_bd)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO clientes (nombre, cedula, telefono, correo) VALUES (%s, %s, %s, %s)",
                (form.nombre.data, form.cedula.data, form.telefono.data, form.correo.data),
            )
            conn.commit()
            flash("Cliente registrado correctamente.", "success")
            return redirect(url_for("clientes"))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Ya existe un cliente con esos datos.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("clientes_form.html", form=form, cliente=None)


@app.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_cliente(id):
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()

    if cliente is None:
        flash("El cliente solicitado no existe.", "danger")
        return redirect(url_for("clientes"))

    form = ClienteForm(data=dict(cliente))

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE clientes SET nombre = %s, cedula = %s, telefono = %s, correo = %s WHERE id_cliente = %s",
                (form.nombre.data, form.cedula.data, form.telefono.data, form.correo.data, id),
            )
            conn.commit()
            flash("Cliente actualizado correctamente.", "success")
            return redirect(url_for("clientes"))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Ya existe un cliente con esos datos.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("clientes_form.html", form=form, cliente=cliente)


@app.route("/clientes/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_cliente(id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id,))
        conn.commit()
        flash("Cliente eliminado correctamente.", "success")
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        flash("No se puede eliminar: el cliente tiene facturas asociadas.", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("clientes"))


# ---------------------------------------------------------------
# MÓDULO DE PROVEEDORES (CRUD en base de datos)
# ---------------------------------------------------------------
@app.route("/proveedores")
@login_required
def proveedores():
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT id_proveedor, nombre, telefono, correo FROM proveedores ORDER BY id_proveedor"
    )
    proveedores_bd = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("proveedores.html", proveedores=proveedores_bd)


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO proveedores (nombre, telefono, correo) VALUES (%s, %s, %s)",
                (form.nombre.data, form.telefono.data, form.correo.data),
            )
            conn.commit()
            flash("Proveedor registrado correctamente.", "success")
            return redirect(url_for("proveedores"))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Ya existe un proveedor con esos datos.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("proveedores_form.html", form=form, proveedor=None)


@app.route("/proveedores/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_proveedor(id):
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM proveedores WHERE id_proveedor = %s", (id,))
    proveedor = cursor.fetchone()
    cursor.close()
    conn.close()

    if proveedor is None:
        flash("El proveedor solicitado no existe.", "danger")
        return redirect(url_for("proveedores"))

    form = ProveedorForm(data=dict(proveedor))

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE proveedores SET nombre = %s, telefono = %s, correo = %s WHERE id_proveedor = %s",
                (form.nombre.data, form.telefono.data, form.correo.data, id),
            )
            conn.commit()
            flash("Proveedor actualizado correctamente.", "success")
            return redirect(url_for("proveedores"))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Ya existe un proveedor con esos datos.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("proveedores_form.html", form=form, proveedor=proveedor)


@app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_proveedor(id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s", (id,))
        conn.commit()
        flash("Proveedor eliminado correctamente.", "success")
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        flash("No se puede eliminar: el proveedor tiene productos asociados.", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("proveedores"))


# ---------------------------------------------------------------
# MÓDULO DE FACTURACIÓN (CRUD en base de datos, relacionado con clientes)
# ---------------------------------------------------------------
@app.route("/facturacion")
@login_required
def facturacion():
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # JOIN con clientes para mostrar el nombre del cliente de cada factura
    cursor.execute("""
        SELECT f.id_factura, f.numero, f.fecha, f.total, f.estado,
               f.id_cliente, c.nombre AS cliente
        FROM facturas f
        JOIN clientes c ON f.id_cliente = c.id_cliente
        ORDER BY f.id_factura
    """)
    facturas_bd = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("facturacion.html", facturas=facturas_bd)


@app.route("/facturacion/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    form = FacturaForm()
    form.id_cliente.choices = obtener_choices_clientes()

    # Sin clientes no se puede facturar
    if not form.id_cliente.choices:
        flash("Primero debes registrar al menos un cliente.", "warning")
        return redirect(url_for("clientes"))

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO facturas (numero, id_cliente, fecha, total, estado) VALUES (%s, %s, %s, %s, %s)",
                (form.numero.data, form.id_cliente.data, form.fecha.data, form.total.data, form.estado.data),
            )
            conn.commit()
            flash("Factura registrada correctamente.", "success")
            return redirect(url_for("facturacion"))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Ya existe una factura con ese número.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("facturacion_form.html", form=form, factura=None)


@app.route("/facturacion/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_factura(id):
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM facturas WHERE id_factura = %s", (id,))
    factura = cursor.fetchone()
    cursor.close()
    conn.close()

    if factura is None:
        flash("La factura solicitada no existe.", "danger")
        return redirect(url_for("facturacion"))

    form = FacturaForm(data=dict(factura))
    form.id_cliente.choices = obtener_choices_clientes()

    if form.validate_on_submit():
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE facturas SET numero = %s, id_cliente = %s, fecha = %s, total = %s, estado = %s WHERE id_factura = %s",
                (form.numero.data, form.id_cliente.data, form.fecha.data, form.total.data, form.estado.data, id),
            )
            conn.commit()
            flash("Factura actualizada correctamente.", "success")
            return redirect(url_for("facturacion"))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Ya existe una factura con ese número.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("facturacion_form.html", form=form, factura=factura)


@app.route("/facturacion/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_factura(id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM facturas WHERE id_factura = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Factura eliminada correctamente.", "success")
    return redirect(url_for("facturacion"))


# Inicia la aplicación
if __name__ == "__main__":
    app.run(debug=True)
