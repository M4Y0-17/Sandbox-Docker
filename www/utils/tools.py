from flask import render_template



def is_email_content(file_path):
    """Determina si el contenido del archivo corresponde a un correo electrónico."""
    required_headers = ['From:', 'To:', 'Subject:', 'Date:']
    strong_indicators = ['Message-ID:', 'MIME-Version:']
    headers_found = 0
    strong_indicator_found = False

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                # Verifica los encabezados requeridos
                if any(header in line for header in required_headers):
                    headers_found += 1
                # Verifica los indicadores fuertes
                if any(indicator in line for indicator in strong_indicators):
                    strong_indicator_found = True
                # Si encuentra suficientes encabezados y al menos un indicador fuerte, es probablemente un correo
                if headers_found >= len(required_headers) / 2 and strong_indicator_found:
                    return True
                # Limita la búsqueda a las primeras partes del archivo para mejorar la eficiencia
                if file.tell() > 4096:
                    break
    except Exception as e:
        return render_template('results.html', message="El contenido de este archivo no es el de un correo electrónico. Error: {e}", color="red")

    return False
