//registro con validaciones dinámicas


// Referencias a elementos del DOM 
const formulario = document.getElementById("formRegistro");
const mensaje = document.getElementById("mensaje");
const listaRegistros = document.getElementById("listaRegistros");
const total = document.getElementById("total");

const campoNombre = document.getElementById("nombre");
const campoCorreo = document.getElementById("correo");
const campoCategoria = document.getElementById("categoria");
const campoDescripcion = document.getElementById("descripcion");

const feedbackNombre = document.getElementById("feedback-nombre");
const feedbackCorreo = document.getElementById("feedback-correo");
const feedbackCategoria = document.getElementById("feedback-categoria");
const feedbackDescripcion = document.getElementById("feedback-descripcion");

//  Configuración de reglas 
const LONGITUD_MINIMA_NOMBRE = 3;
const LONGITUD_MINIMA_DESCRIPCION = 15;

// Referencia al mensaje de "no hay registros"
const estadoVacio = document.getElementById("estadoVacio");

// Elementos para el botón de envío con spinner
const btnEnviar = document.getElementById("btnEnviar");
const spinnerEnviar = document.getElementById("spinnerEnviar");
const textoEnviar = document.getElementById("textoEnviar");

// Elementos y modales para "Ver detalles" y "Confirmar eliminación"
const listaServicios = document.getElementById("listaServicios");

const modalDetalleEl = document.getElementById("modalDetalle");
const modalDetalle = modalDetalleEl ? new bootstrap.Modal(modalDetalleEl) : null;

const modalConfirmarEl = document.getElementById("modalConfirmarEliminar");
const modalConfirmar = modalConfirmarEl ? new bootstrap.Modal(modalConfirmarEl) : null;

const btnConfirmarEliminar = document.getElementById("btnConfirmarEliminar");

// Guarda temporalmente el id del registro que se quiere eliminar
// mientras se espera la confirmación del usuario en el modal.
let idPendienteEliminar = null;

// Array que guarda TODOS los registros. Es la única "fuente de verdad":
// cada vez que cambia, volvemos a dibujar la lista completa a partir de él.
let registros = [];


// Marca un campo como válido o inválido.
function marcarCampo(campo, elementoFeedback, esValido, mensajeError) {
    if (esValido) {
        campo.classList.remove("is-invalid");
        campo.classList.add("is-valid");
        if (elementoFeedback) elementoFeedback.textContent = "";
    } else {
        campo.classList.remove("is-valid");
        campo.classList.add("is-invalid");
        if (elementoFeedback) elementoFeedback.textContent = mensajeError;
    }
    return esValido;
}

//Quita cualquier clase de validación de un campo (estado neutro)
function limpiarValidacion(campo) {
    campo.classList.remove("is-valid", "is-invalid");
}

// Funciones de validación individuales (una por campo)
function validarNombre() {
    const valor = campoNombre.value.trim();

    if (valor === "") {
        return marcarCampo(campoNombre, feedbackNombre, false, "El nombre es obligatorio.");
    }

    if (valor.length < LONGITUD_MINIMA_NOMBRE) {
        return marcarCampo(
            campoNombre,
            feedbackNombre,
            false,
            `El nombre debe tener al menos ${LONGITUD_MINIMA_NOMBRE} caracteres.`
        );
    }

    return marcarCampo(campoNombre, feedbackNombre, true, "");
}

function validarCorreo() {
    const valor = campoCorreo.value.trim();
    // Expresión regular simple para validar formato de correo
    const patronCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (valor === "") {
        return marcarCampo(campoCorreo, feedbackCorreo, false, "El correo electrónico es obligatorio.");
    }

    if (!patronCorreo.test(valor)) {
        return marcarCampo(campoCorreo, feedbackCorreo, false, "Ingresa un correo electrónico válido.");
    }

    return marcarCampo(campoCorreo, feedbackCorreo, true, "");
}

function validarCategoria() {
    const valor = campoCategoria.value;

    if (valor === "") {
        return marcarCampo(campoCategoria, feedbackCategoria, false, "Debes seleccionar una categoría.");
    }

    return marcarCampo(campoCategoria, feedbackCategoria, true, "");
}

function validarDescripcion() {
    const valor = campoDescripcion.value.trim();

    if (valor === "") {
        return marcarCampo(campoDescripcion, feedbackDescripcion, false, "La descripción es obligatoria.");
    }

    if (valor.length < LONGITUD_MINIMA_DESCRIPCION) {
        return marcarCampo(
            campoDescripcion,
            feedbackDescripcion,
            false,
            `La descripción debe tener al menos ${LONGITUD_MINIMA_DESCRIPCION} caracteres.`
        );
    }

    return marcarCampo(campoDescripcion, feedbackDescripcion, true, "");
}

// Ejecuta todas las validaciones del formulario.
function validarFormulario() {
    const nombreValido = validarNombre();
    const correoValido = validarCorreo();
    const categoriaValida = validarCategoria();
    const descripcionValida = validarDescripcion();

    return nombreValido && correoValido && categoriaValida && descripcionValida;
}

// Mensajes generales (arriba del listado de registros)

function mostrarMensajeExito(texto) {
    mensaje.innerHTML = `<div class="alert alert-success">${texto}</div>`;
}

function mostrarMensajeError(texto) {
    mensaje.innerHTML = `<div class="alert alert-danger">${texto}</div>`;
}

// Manejo de registros (crear, listar, eliminar)

// Contador de IDs únicos para poder identificar cada registro al eliminarlo
let siguienteId = 1;

function actualizarContador() {
    total.textContent = registros.length;
}

// Crea el HTML de UN solo registro. Esta es la "plantilla" que se
// reutiliza dentro del bucle, para no repetir bloques HTML manualmente.
function crearElementoTarjeta(registro) {
    const columna = document.createElement("div");
    columna.className = "col-md-6";

    const tarjeta = document.createElement("div");
    tarjeta.className = "card tarjeta-registro p-3 mt-3 shadow-sm";

    const titulo = document.createElement("h5");
    titulo.textContent = registro.nombre;

    const correoTexto = document.createElement("p");
    correoTexto.className = "mb-1";
    correoTexto.innerHTML = "<strong>Correo:</strong> ";
    correoTexto.append(registro.correo);

    const tipo = document.createElement("p");
    tipo.className = "mb-1";
    tipo.innerHTML = "<strong>Categoría:</strong> ";
    const insignia = document.createElement("span");
    insignia.className = "badge bg-success";
    insignia.textContent = registro.categoria;
    tipo.appendChild(insignia);

    const texto = document.createElement("p");
    texto.className = "mt-2";
    texto.textContent = registro.descripcion;

    // Botón "Ver detalles": abre un modal con la información completa del registro
    const botonDetalle = document.createElement("button");
    botonDetalle.textContent = "Ver detalles";
    botonDetalle.type = "button";
    botonDetalle.className = "btn btn-primary btn-sm me-2";
    botonDetalle.addEventListener("click", function () {
        document.getElementById("detalleNombre").textContent = registro.nombre;
        document.getElementById("detalleCorreo").textContent = registro.correo;
        document.getElementById("detalleCategoria").textContent = registro.categoria;
        document.getElementById("detalleDescripcion").textContent = registro.descripcion;
        if (modalDetalle) modalDetalle.show();
    });

    // El botón "Eliminar": ya no borra directamente, pide confirmación en un modal
    const boton = document.createElement("button");
    boton.textContent = "Eliminar";
    boton.type = "button";
    boton.className = "btn btn-danger btn-sm";

    boton.addEventListener("click", function () {
        idPendienteEliminar = registro.id;
        document.getElementById("nombreAEliminar").textContent = registro.nombre;
        if (modalConfirmar) modalConfirmar.show();
    });

    tarjeta.appendChild(titulo);
    tarjeta.appendChild(correoTexto);
    tarjeta.appendChild(tipo);
    tarjeta.appendChild(texto);
    tarjeta.appendChild(botonDetalle);
    tarjeta.appendChild(boton);
    columna.appendChild(tarjeta);

    return columna;
}

// recorre el array "registros" con forEach y
// construye la lista completa de tarjetas a partir de él.
// Además aplica una CONDICIÓN según el estado de los datos:
// si no hay registros, muestra un mensaje; si hay, muestra la lista.
function renderizarRegistros() {
    listaRegistros.innerHTML = "";

    if (registros.length === 0) {
        // Condición: no hay datos -> mostramos mensaje de estado vacío
        estadoVacio.classList.remove("d-none");
        listaRegistros.classList.add("d-none");
    } else {
        // Condición: sí hay datos -> ocultamos el mensaje y pintamos la lista
        estadoVacio.classList.add("d-none");
        listaRegistros.classList.remove("d-none");

        registros.forEach(function (registro) {
            const elemento = crearElementoTarjeta(registro);
            listaRegistros.appendChild(elemento);
        });
    }

    actualizarContador();
}

// Limpia el formulario y las validaciones.
function limpiarFormulario() {
    formulario.reset();
    [campoNombre, campoCorreo, campoCategoria, campoDescripcion].forEach(limpiarValidacion);
}


// Confirmación de eliminación desde el modal

if (btnConfirmarEliminar) {
    btnConfirmarEliminar.addEventListener("click", function () {
        if (idPendienteEliminar !== null) {
            registros = registros.filter(function (r) {
                return r.id !== idPendienteEliminar;
            });
            renderizarRegistros();
            mostrarMensajeExito("Registro eliminado correctamente.");
        }
        idPendienteEliminar = null;
        if (modalConfirmar) modalConfirmar.hide();
    });
}

// Servicios y Productos: contenido dinámico simulando una carga (spinner)

const datosServicios = [
    {
        nombre: "Ropa y Accesorios de Moda",
        categoria: "Moda",
        descripcion: "Prendas y accesorios de emprendedores ecuatorianos, con envíos a todo el país."
    },
    {
        nombre: "Tecnología y Electrónica",
        categoria: "Tecnología",
        descripcion: "Dispositivos y accesorios tecnológicos ofrecidos por proveedores locales confiables."
    },
    {
        nombre: "Productos para el Hogar",
        categoria: "Hogar",
        descripcion: "Artículos de decoración, cocina y organización para renovar cada espacio de tu casa."
    },
    {
        nombre: "Alimentos y Productos Locales",
        categoria: "Alimentos",
        descripcion: "Productos frescos y procesados elaborados por pequeños productores de distintas provincias."
    }
];

function crearTarjetaServicio(servicio) {
    const columna = document.createElement("div");
    columna.className = "col-md-6 col-lg-3 mb-4";

    columna.innerHTML = `
        <div class="card h-100 text-center p-3 shadow-sm">
            <div class="card-body">
                <h5 class="card-title">${servicio.nombre}</h5>
                <span class="badge bg-success mb-2">${servicio.categoria}</span>
                <p class="card-text">${servicio.descripcion}</p>
            </div>
        </div>
    `;

    return columna;
}

// Simula un pequeño tiempo de carga (spinner) antes de mostrar los
// servicios, representando un proceso asincrónico típico (ej: una
// consulta a un servidor).
function renderizarServicios() {
    setTimeout(function () {
        listaServicios.innerHTML = "";
        datosServicios.forEach(function (servicio) {
            listaServicios.appendChild(crearTarjetaServicio(servicio));
        });
    }, 1200);
}

renderizarServicios();

// Eventos: validación en tiempo real (input y blur)

campoNombre.addEventListener("input", validarNombre);
campoNombre.addEventListener("blur", validarNombre);

campoCorreo.addEventListener("input", validarCorreo);
campoCorreo.addEventListener("blur", validarCorreo);

campoCategoria.addEventListener("change", validarCategoria);
campoCategoria.addEventListener("blur", validarCategoria);

campoDescripcion.addEventListener("input", validarDescripcion);
campoDescripcion.addEventListener("blur", validarDescripcion);


// Evento: envío del formulario

formulario.addEventListener("submit", function (event) {
    // Evita que la página se recargue
    event.preventDefault();

    const formularioValido = validarFormulario();

    if (!formularioValido) {
        mostrarMensajeError("Revisa los campos marcados en rojo antes de continuar.");
        return;
    }

    // Datos ya validados
    const nombre = campoNombre.value.trim();
    const correo = campoCorreo.value.trim();
    const categoria = campoCategoria.value;
    const descripcion = campoDescripcion.value.trim();

    // Mostramos un spinner en el botón para simular un proceso de guardado
    btnEnviar.disabled = true;
    spinnerEnviar.classList.remove("d-none");
    textoEnviar.textContent = "Guardando...";

    setTimeout(function () {
        // Guardamos el nuevo registro en el array (fuente de datos)
        registros.push({
            id: siguienteId++,
            nombre: nombre,
            correo: correo,
            categoria: categoria,
            descripcion: descripcion
        });

        // Volvemos a dibujar toda la lista a partir del array actualizado
        renderizarRegistros();

        mostrarMensajeExito("Registro agregado correctamente.");
        limpiarFormulario();

        // Restauramos el botón a su estado normal
        btnEnviar.disabled = false;
        spinnerEnviar.classList.add("d-none");
        textoEnviar.textContent = "Enviar Mensaje";
    }, 900);
});

// Renderizado inicial al cargar la página (con el array vacío,
// esto mostrará el mensaje de "no hay registros")
renderizarRegistros();
