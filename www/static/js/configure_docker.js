window.onload = function() {
	document.getElementById("valorSeleccionado").value = document.getElementById("rango").value;
};

function toggleAdvancedOptions() {
    var advancedOptions = document.getElementById('advancedOptions');
    var link = document.querySelector('.advanced-options-link');
    if (advancedOptions.style.display === 'none') {
        advancedOptions.style.display = 'block';
        link.classList.add('active');
    } else {
        advancedOptions.style.display = 'none';
        link.classList.remove('active');
    }
}

document.addEventListener("DOMContentLoaded", function() {
    function toggleVisibilityBasedOnSelection() {
        var browserType = document.getElementById("browser_type").value;
        var emlInputContainer = document.querySelector(".emlfile_upload");
        var emlInput = document.getElementById("eml_file"); // Obtiene el input de archivo .eml
        var advancedOptionsLink = document.querySelector(".advanced-options-link"); // Referencia al enlace de Opciones Avanzadas
        var advancedOptionsContainer = document.getElementById("advancedOptions");
        var optionContainers = advancedOptionsContainer.querySelectorAll(".checkbox-group");

        // Mostrar/Ocultar el contenedor de carga del archivo .eml para Thunderbird
        if (browserType === "thunderbird") {
            emlInputContainer.style.display = "block";
            emlInput.required = true; // Hace el campo requerido si está visible
        } else {
            emlInputContainer.style.display = "none";
            emlInput.required = false; // No hace el campo requerido si está oculto
        }

        let anyOptionVisible = false; // Inicia suponiendo que ninguna opción estará visible

        // Iterar sobre cada opción avanzada para determinar su visibilidad
        optionContainers.forEach(function(container) {
            // Asumiendo que deseas ocultar/mostrar estas opciones basado en ciertas condiciones
            if (browserType === "chrome" || browserType === "outlook") {
                container.style.display = "flex";
                anyOptionVisible = true; // Al menos una opción es visible
            } else {
                container.style.display = "none";
            }
        });

        // Mostrar/Ocultar el enlace y el recuadro de Opciones Avanzadas basado en la visibilidad de sus opciones
        var displayValue = anyOptionVisible ? "block" : "none";
        advancedOptionsLink.style.display = displayValue; // Aplicar la misma lógica de visibilidad al enlace
        advancedOptionsContainer.style.display = displayValue;
    }

    // Añade un event listener al select de navegador para escuchar cambios
    document.getElementById("browser_type").addEventListener("change", toggleVisibilityBasedOnSelection);

    // Ejecuta la función al cargar para establecer el estado inicial basado en la selección predeterminada
    toggleVisibilityBasedOnSelection();
});

