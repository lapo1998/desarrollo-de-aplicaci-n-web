from flask import Flask, render_template

app = Flask(__name__)

# datos de ejemplo, todavia no hay base de datos
productos_ejemplo = [
    {"nombre": "Juego de sábanas", "categoria": "Hogar", "precio": 25.50, "stock": 40},
    {"nombre": "Audífonos inalámbricos", "categoria": "Tecnología", "precio": 18.99, "stock": 15},
    {"nombre": "Camiseta artesanal", "categoria": "Moda", "precio": 12.00, "stock": 60},
    {"nombre": "Café orgánico 500g", "categoria": "Alimentos", "precio": 6.75, "stock": 0},
]

clientes_ejemplo = [
    {"nombre": "María Torres", "correo": "maria.torres@email.com", "ciudad": "Loja", "telefono": "0991234567"},
    {"nombre": "Carlos Jiménez", "correo": "carlos.jimenez@email.com", "ciudad": "Cariamanga", "telefono": "0987654321"},
    {"nombre": "Ana Suárez", "correo": "ana.suarez@email.com", "ciudad": "Quito", "telefono": "0965432198"},
]

proveedores_ejemplo = [
    {"nombre": "Textiles Loja", "rubro": "Moda", "ciudad": "Loja", "contacto": "textilesloja@email.com"},
    {"nombre": "TecnoImport EC", "rubro": "Tecnología", "ciudad": "Quito", "contacto": "ventas@tecnoimport.com"},
    {"nombre": "Sabores del Sur", "rubro": "Alimentos", "ciudad": "Cariamanga", "contacto": "contacto@saboresdelsur.com"},
]

facturas_ejemplo = [
    {"numero": "F001", "cliente": "María Torres", "fecha": "2026-08-01", "total": 45.50, "estado": "Pagada"},
    {"numero": "F002", "cliente": "Carlos Jiménez", "fecha": "2026-08-05", "total": 18.99, "estado": "Pendiente"},
    {"numero": "F003", "cliente": "Ana Suárez", "fecha": "2026-08-10", "total": 32.75, "estado": "Pagada"},
]

# diccionario con info general del sistema
info_sistema = {
    "nombre": "EcuaCompras",
    "version": "1.0",
    "anio": 2026,
    "estudiante": "Elvio Manuel Lapo Agreda",
    "asignatura": "Desarrollo de Aplicaciones Web",
}


# asi info_sistema llega a todas las plantillas sin repetirlo en cada ruta
@app.context_processor
def inject_info_sistema():
    return {"info_sistema": info_sistema}


# pagina principal, la informativa de siempre
@app.route("/")
def index():
    return render_template("index.html")


# modulo de productos
@app.route("/productos")
def productos():
    total_productos = len(productos_ejemplo)
    return render_template("productos.html", productos=productos_ejemplo, total_productos=total_productos)


# modulo de clientes
@app.route("/clientes")
def clientes():
    return render_template("clientes.html", clientes=clientes_ejemplo)


# modulo de proveedores
@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html", proveedores=proveedores_ejemplo)


# modulo de facturacion
@app.route("/facturacion")
def facturacion():
    return render_template("facturacion.html", facturas=facturas_ejemplo)


if __name__ == "__main__":
    app.run(debug=True)
