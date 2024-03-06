function copyToClipboard() {
    var copyText = document.getElementById("user-output");
    navigator.clipboard.writeText(copyText.value)
        .then(() => {
            // Cambia la clase del botón para mostrar el tooltip "Copied!"
            var copyButton = document.querySelector(".copy-btn");
            copyButton.classList.add("copied");

            // Opcional: restablece el tooltip después de un tiempo
            setTimeout(() => {
                copyButton.classList.remove("copied");
            }, 2000); // 2 segundos antes de volver al estado original
        })
        .catch(err => {
            console.error('Error al copiar texto: ', err);
        });
}
