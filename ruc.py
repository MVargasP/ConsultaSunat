import requests
from bs4 import BeautifulSoup

class Ruc:
    def __init__(self):
        pass
    
    def get_random(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        input_tag = soup.find('input', {'name': 'numRnd'})
        if input_tag:
            return input_tag['value']
        return ''
    
    def get(self, ruc):
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0"
        }
        data = {
            'accion': 'consPorRuc',
            'nroRuc': ruc,
        }

        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            html = response.text
            numRnd = self.get_random(html)
            data['numRnd'] = numRnd
            
            response = requests.post(url, data=data, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Aquí puedes agregar el código para parsear la respuesta HTML y obtener la información que necesitas
                print(soup.prettify())  # Esto es solo un ejemplo, imprime la respuesta HTML para visualización
            else:
                print("Error al obtener la información del RUC en la segunda solicitud:", response.status_code)
        else:
            print("Error al obtener la información del RUC en la primera solicitud:", response.status_code)


# Ejemplo de uso:
if __name__ == "__main__":
    ruc_service = Ruc()
    ruc_service.get('20507771204')  # Reemplaza XXXXXXXX con el número de RUC que deseas consultar
