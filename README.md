# EcuaCompras - Proyecto Flask

## Estructura del proyecto

```
EcuaCompras_Flask/
├── app.py
├── requirements.txt
├── templates/
│   ├── base.html          <- plantilla madre (header, nav, footer)
│   ├── index.html          <- página principal (extiende base.html)
│   ├── productos.html
│   ├── clientes.html
│   ├── proveedores.html
│   └── facturacion.html
└── static/
    ├── css/style.css
    ├── js/script.js
    └── img/                <- coloca aquí ecuacompras-logo.png
```

## Pasos para correrlo en tu computadora (VS Code)

1. Abre esta carpeta en Visual Studio Code.

2. Crea el entorno virtual (solo la primera vez):

   ```
   python -m venv venv
   ```

3. Activa el entorno virtual:

   - **Windows (PowerShell):**
     ```
     venv\Scripts\activate
     ```
   - **Mac / Linux:**
     ```
     source venv/bin/activate
     ```

   Sabrás que está activo porque tu terminal mostrará `(venv)` al inicio.

4. Instala Flask:

   ```
   pip install flask
   ```

5. Coloca tu imagen `ecuacompras-logo.png` dentro de `static/img/` (no venía incluida en este paquete).

6. Ejecuta la aplicación:

   ```
   python app.py
   ```

7. Abre en el navegador:

   ```
   http://127.0.0.1:5000
   ```

8. Prueba las demás rutas:
   - http://127.0.0.1:5000/productos
   - http://127.0.0.1:5000/clientes
   - http://127.0.0.1:5000/proveedores
   - http://127.0.0.1:5000/facturacion

9. Para detener el servidor: `CTRL + C` en la terminal.

## Nota

Los datos de productos, clientes, proveedores y facturas son listas de ejemplo
definidas directamente en `app.py` (variables `productos_ejemplo`, `clientes_ejemplo`, etc.).
Todavía no hay base de datos — eso se agregará en una semana posterior.
