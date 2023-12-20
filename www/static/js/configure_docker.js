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
