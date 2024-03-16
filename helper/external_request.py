import requests

def consultar_datos_ruc(numero_documento):
    # Define la URL base de la API
    url_base = 'https://api.migo.pe/api/v1/sunat/ruc/'
    # Tu token de autenticación
    token = 'hqHfONaufIuSyoZ3YeFmOAwGaPqweLgQmWtNMfaytziBaSHwQ1hmFo3GpfwU'
    
    url = f"{url_base}{numero_documento}?token={token}"
    
    respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        False
