import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash

from forms.productos_forms import ProductoForm
from forms.clientes_forms import ClienteForm
from forms.proveedores_forms import ProveedorForm
from forms.facturacion_forms import FacturaForm


# Configuración principal de la aplicación
app = Flask(__name__)

# Clave para proteger los formularios con CSRF
app.config["SECRET_KEY"] = "clave-secreta-ecuacompras-dev-2026"


# Rutas de la carpeta data y de la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "ferreteria.db")


# Crea la carpeta data y la tabla de productos si todavía no existen
def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Abre una conexión a la base de datos y permite leer columnas por nombre
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Inicializa la base de datos al arrancar la aplicación
init_db()


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


# Módulo de productos (ahora persistido en SQLite)
@app.route("/productos")
def productos():
    conn = get_db_connection()
    productos_bd = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()

    total_productos = len(productos_bd)
    return render_template(
        "productos.html",
        productos=productos_bd,
        total_productos=total_productos,
    )


# Registrar un producto (INSERT en la base de datos)
@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    form = ProductoForm()

    # Solo guardamos si el formulario pasa las validaciones
    if form.validate_on_submit():
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO productos (nombre, categoria, precio, stock) VALUES (?, ?, ?, ?)",
            (form.nombre.data, form.categoria.data, form.precio.data, form.stock.data),
        )
        conn.commit()
        conn.close()

        flash("Producto registrado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template("productos_form.html", form=form, producto=None)


# Editar un producto (SELECT para cargar y UPDATE para guardar cambios)
@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    conn = get_db_connection()
    producto = conn.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()

    # Si el producto no existe, regresamos al listado
    if producto is None:
        conn.close()
        flash("El producto solicitado no existe.", "danger")
        return redirect(url_for("productos"))

    form = ProductoForm(data=dict(producto))

    # Actualiza el producto si los datos son válidos
    if form.validate_on_submit():
        conn.execute(
            "UPDATE productos SET nombre = ?, categoria = ?, precio = ?, stock = ? WHERE id = ?",
            (form.nombre.data, form.categoria.data, form.precio.data, form.stock.data, id),
        )
        conn.commit()
        conn.close()

        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos"))

    conn.close()
    return render_template("productos_form.html", form=form, producto=producto)


# Módulo de clientes
@app.route("/clientes")
def clientes():
    return render_template("clientes.html", clientes=clientes_ejemplo)


# Registrar un cliente
@app.route("/clientes/nuevo", methods=["GET", "POST"])
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
def proveedores():
    return render_template("proveedores.html", proveedores=proveedores_ejemplo)


# Registrar un proveedor
@app.route("/proveedores/nuevo", methods=["GET", "POST"])
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
def facturacion():
    return render_template("facturacion.html", facturas=facturas_ejemplo)


# Registrar una factura
@app.route("/facturacion/nueva", methods=["GET", "POST"])
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
