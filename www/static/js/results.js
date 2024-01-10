document.addEventListener("DOMContentLoaded", function() {
	var messageText = document.getElementById("link-text").textContent;
	// Esta expresión regular busca una URL que empiece con https://
	var urlRegex = /(https:\/\/[^\s]+)/g;
	var urlMatch = messageText.match(urlRegex);
	var copyButton = document.querySelector(".copy-button");
  
	if (urlMatch) {
	  // Si hay una URL en el mensaje, mostramos el botón
	  copyButton.style.display = "block";
	} else {
	  // Si no hay una URL, ocultamos el botón
	  copyButton.style.display = "none";
	}
  });


function copyToClipboard() {
	var messageText = document.getElementById("link-text").textContent;
	// Esta expresión regular busca una URL que empiece con https://
	var urlRegex = /(https:\/\/[^\s]+)/g;
	var url = messageText.match(urlRegex)[0]; // Encuentra la primera coincidencia que debería ser tu URL.
  
	if (url && navigator.clipboard && window.isSecureContext) {
	  // Navegador soporta la nueva API del portapapeles y estamos en un contexto seguro (HTTPS)
	  navigator.clipboard.writeText(url)
		.then(function() {
		  console.log("Enlace copiado al portapapeles");
		})
		.catch(function(error) {
		  console.error("No se pudo copiar el texto: ", error);
		});
	} else {
	  // Fallback para navegadores que no soportan la API del portapapeles o que no están en un contexto seguro
	  var textArea = document.createElement("textarea");
	  textArea.value = url;
	  document.body.appendChild(textArea);
	  textArea.select();
	  try {
		var successful = document.execCommand('copy');
		console.log('Fallback: Copying text command was ' + (successful ? 'successful' : 'unsuccessful'));
	  } catch (err) {
		console.error('Fallback: Oops, unable to copy', err);
	  }
	  document.body.removeChild(textArea);
	}
  }
  