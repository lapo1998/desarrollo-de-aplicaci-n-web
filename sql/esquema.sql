-- Esquema de la base de datos del proyecto EcuaCompras (ferretería) - PostgreSQL
-- Ejecutar este archivo completo vuelve a crear toda la estructura

-- Proveedores: quién nos surte los productos
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(120)
);

-- Clientes: quién nos compra
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    cedula VARCHAR(10),
    telefono VARCHAR(20),
    correo VARCHAR(120)
);

-- Productos: cada producto pertenece a un proveedor (FK)
CREATE TABLE IF NOT EXISTS productos (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL,
    id_proveedor INT NOT NULL REFERENCES proveedores(id_proveedor)
);

-- Facturas: cada factura pertenece a un cliente (FK)
CREATE TABLE IF NOT EXISTS facturas (
    id_factura SERIAL PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    id_cliente INT NOT NULL REFERENCES clientes(id_cliente),
    fecha DATE NOT NULL,
    total NUMERIC(10, 2) NOT NULL,
    estado VARCHAR(20) NOT NULL
);

-- Usuarios autorizados para ingresar al sistema (login)
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Proveedores de ejemplo, para poder asociarlos a productos desde ya.
-- Se usa "INSERT ... WHERE NOT EXISTS" porque PostgreSQL no tiene INSERT IGNORE.
INSERT INTO proveedores (nombre, telefono, correo)
SELECT 'Textiles Loja', '0991111111', 'textilesloja@email.com'
WHERE NOT EXISTS (SELECT 1 FROM proveedores WHERE nombre = 'Textiles Loja');

INSERT INTO proveedores (nombre, telefono, correo)
SELECT 'TecnoImport EC', '0992222222', 'ventas@tecnoimport.com'
WHERE NOT EXISTS (SELECT 1 FROM proveedores WHERE nombre = 'TecnoImport EC');

INSERT INTO proveedores (nombre, telefono, correo)
SELECT 'Sabores del Sur', '0993333333', 'contacto@saboresdelsur.com'
WHERE NOT EXISTS (SELECT 1 FROM proveedores WHERE nombre = 'Sabores del Sur');
