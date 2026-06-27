const formulario = document.getElementById("formRegistro");

const mensaje = document.getElementById("mensaje");
const listaRegistros = document.getElementById("listaRegistros");
const total = document.getElementById("total");

let contador = 0;

formulario.addEventListener("submit", function (event) {

    // Evita que la página se recargue
    event.preventDefault();

    // Obtener datos
    const nombre = document.getElementById("nombre").value.trim();
    const categoria = document.getElementById("categoria").value.trim();
    const descripcion = document.getElementById("descripcion").value.trim();

    // Valida los campos
    if (nombre === "" || categoria === "" || descripcion === "") {

        mensaje.innerHTML =
        '<div class="alert alert-danger">Todos los campos son obligatorios.</div>';

        return;
    }

    // muestra mensaje de éxito
    mensaje.innerHTML =
    '<div class="alert alert-success">Registro agregado correctamente.</div>';

    // Crear tarjeta
    const tarjeta = document.createElement("div");
    tarjeta.className = "card p-3 mt-3 shadow";

    const titulo = document.createElement("h5");
    titulo.textContent = nombre;

    const tipo = document.createElement("p");
    tipo.innerHTML = "<strong>Categoría:</strong> " + categoria;

    const texto = document.createElement("p");
    texto.textContent = descripcion;

    const boton = document.createElement("button");
    boton.textContent = "Eliminar";
    boton.className = "btn btn-danger btn-sm";

    // Evento para eliminar
    boton.addEventListener("click", function () {

        tarjeta.remove();

        contador--;

        total.textContent = contador;

    });

    // Agregar elementos a la tarjeta
    tarjeta.appendChild(titulo);
    tarjeta.appendChild(tipo);
    tarjeta.appendChild(texto);
    tarjeta.appendChild(boton);

    // Agregar tarjeta a la página
    listaRegistros.appendChild(tarjeta);

    // Actualizar contador
    contador++;
    total.textContent = contador;

    // Limpiar formulario
    formulario.reset();

});