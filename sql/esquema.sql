-- Esquema de la base de datos del proyecto EcuaCompras (ferretería)
-- Ejecutar este archivo completo vuelve a crear toda la estructura

-- Proveedores: quién nos surte los productos
CREATE TABLE IF NOT EXISTS proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(120)
) ENGINE=InnoDB;

-- Clientes: quién nos compra
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    cedula VARCHAR(10),
    telefono VARCHAR(20),
    correo VARCHAR(120)
) ENGINE=InnoDB;

-- Productos: cada producto pertenece a un proveedor (FK)
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    id_proveedor INT NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
) ENGINE=InnoDB;

-- Facturas: cada factura pertenece a un cliente (FK)
CREATE TABLE IF NOT EXISTS facturas (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    id_cliente INT NOT NULL,
    fecha DATE NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
) ENGINE=InnoDB;

-- Proveedores de ejemplo, para poder asociarlos a productos desde ya
-- (INSERT IGNORE evita duplicados si vuelves a ejecutar este archivo)
INSERT IGNORE INTO proveedores (id_proveedor, nombre, telefono, correo) VALUES
    (1, 'Textiles Loja', '0991111111', 'textilesloja@email.com'),
    (2, 'TecnoImport EC', '0992222222', 'ventas@tecnoimport.com'),
    (3, 'Sabores del Sur', '0993333333', 'contacto@saboresdelsur.com');
