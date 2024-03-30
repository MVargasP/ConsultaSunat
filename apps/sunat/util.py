# imports
import random
import re
import requests

#rest
from rest_framework import serializers
from django.db.models import F

#models
from .models import InteractionSunat,Ruc
from apps.company.models import Company

from bs4 import BeautifulSoup


def update_models(numero_documento,response,made_scraping):
    InteractionSunat.objects.create(document_number=numero_documento,company_id=1,payload=response,scraping=made_scraping)
    Company.objects.filter(id=1).update(total_sunat=F('total_sunat') + 1)
    Ruc.objects.get_or_create(document_number=numero_documento,defaults={'payload':response})

class ConsultaRUC:
    def __init__(self):
        self.textoAleatorio = "IMPORTANTE LAS PALABRAS CLAVES DEBE SER ALEATORIO EXISTIR LETRAS Y ESTAR EN MAYUSCULA COMO RANDOM UAP UPC LIMA HOLA MUNDO COMO ESTAS TEST comparte LOS VIDEOS EN TUS REDES SOCIALES PARA MAS CONTENIDOS si quieres aprender sobre web api revisa lista de reproduccion del canal mr angel".upper()
        self.arrNombreAleatorio = self.textoAleatorio.split(' ')
        self.sesion = requests.Session()
        self.headers = {
            'Host': 'e-consultaruc.sunat.gob.pe',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
    def get_payload_direccion(self, direccion):
        nombre_via_regex = r'(.*?)\s+NRO\.'
        codigo_zona_regex = r'(URB\.|ASOC\.|P\.J\.|A\.H\.|A\.V\.|COOP\.|FUNDO|PARCELA|PROG\.|RES\.|UNIDAD|VALLE|ZONA)\.'
        tipo_zona_regex = r'(.*?)\s+\w+\s*-'
        numero_regex = r'NRO\.\s*(\d+)'

        # Extraer los campos utilizando las expresiones regulares
        nombre_via_match = re.search(nombre_via_regex, direccion)
        codigo_zona_match = re.search(codigo_zona_regex, direccion)
        tipo_zona_match = re.search(tipo_zona_regex, direccion)
        numero_match = re.search(numero_regex, direccion)

        # Obtener los grupos capturados de las coincidencias
        nombre_via = nombre_via_match.group(1) if nombre_via_match else None
        codigo_zona = codigo_zona_match.group(1) if codigo_zona_match else None
        tipo_zona = tipo_zona_match.group(1) if tipo_zona_match else None
        numero = numero_match.group(1) if numero_match else None

        # Construir la dirección simple y la dirección completa
        direccion_simple = f"{nombre_via}, NRO. {numero}"
        direccion_list = direccion.split('  ')

        direccion_list = [elemento for elemento in direccion_list if elemento]
        distrito = None
        provincia = None
        departamento = None
        if len(direccion_list) >2:
            distrito = direccion_list[-1].replace('-','').strip()
            provincia = direccion_list[-2].replace('-','').strip()
            departamento =direccion_list[-3].replace('-','').strip()
        datos = {
            "tipo_de_via": direccion.split()[0] if direccion else None,
            "nombre_de_via": nombre_via,
            "codigo_de_zona": codigo_zona,
            "tipo_de_zona": tipo_zona,
            "numero": numero,
            "interior": "-",
            "lote": "-",
            "dpto": "-",
            "manzana": "-",
            "kilometro": "-",
            "distrito":distrito,
            "provincia":provincia,
            "departamento":departamento,
            "direccion_simple": direccion_simple,
            "direccion": " ".join(direccion_list)

        }
        return datos


    def ExtraerContenidoEntreTagString(self, cadena, inicio, tag_inicio, tag_fin):
        pos_inicio = cadena.find(tag_inicio, inicio)
        if pos_inicio >= 0:
            pos_fin = cadena.find(tag_fin, pos_inicio + len(tag_inicio))
            if pos_fin >= 0:
                return cadena[pos_inicio + len(tag_inicio):pos_fin]
        return ""

    def ConsultarContenidoRUC(self, urlInicial, ruc, numRandom):
        payload = {
            'numRnd': numRandom,
            'accion': 'consPorRuc',
            'nroRuc': ruc,
            'nroRuc_modalidadBusqueda': 1,
            'nroDocumento': '',
            'tpDocumento': '',
            'desRuc': '',
            'search2': '',
            'codigo': '',
            'provCodigo': '',
            'modo': '1'
        }
        headers = self.headers.copy()
        headers['Origin'] = 'https://e-consultaruc.sunat.gob.pe'
        headers['Referer'] = urlInicial

        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
        response = self.sesion.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            mensaje = soup.select_one(".list-group-item-text")
            if mensaje:
                if ruc.startswith("10"):
                    datos = self.ExtraerDatosRUC10(soup, ruc)
                else:
                    datos = self.ExtraerDatosRUC20(soup, ruc)

                return "Exito", datos, 200
            else:
                raise serializers.ValidationError(
                        {"error": "No se encontraron datos"}
                )
        else:
            raise serializers.ValidationError(
                {"error": "No pudimos conectarnos a la sunat"}
            )

    def ExtraerDatosRUC20(self, soup, ruc):
        datos = {'success':True}
        adicional = {}
        datos["ruc"] = ruc
        razon_social =soup.select_one(".list-group-item:nth-of-type(1) .col-sm-7 .list-group-item-heading").text
        datos["nombre_o_razon_social"] = razon_social.split('-')[1]
        datos["estado_del_contribuyente"] = soup.select_one(".list-group-item:nth-of-type(5) .list-group-item-text").text.strip()
        datos["condicion_de_domicilio"] = soup.select_one(".list-group-item:nth-of-type(6) .list-group-item-text").text.strip()
        direccion_elemento = soup.select_one(".list-group-item:nth-of-type(7) .list-group-item-text").text
        datos_direccion = self.get_payload_direccion( direccion_elemento)
        datos.update(datos_direccion) 
        datos['ubigeo']= None
        datos["fecha_inscripcion"] = soup.select_one(".list-group-item:nth-of-type(4) .list-group-item-text").text
        
        datos["fecha_inicio_actividades"] = soup.select(".list-group-item:nth-of-type(4) .list-group-item-text")[1].text
        
        datos["comprobantes_pago"] = soup.select_one(".list-group-item:nth-of-type(11) .table.tblResultado").text.strip()

        sistema_emision_electronica = self.ValidarContenido(soup.select_one(".list-group-item:nth-of-type(12) .table.tblResultado"))
        datos["sistema_emision_electronica"] = sistema_emision_electronica

        datos["emisor_electronico_comprobante"] = soup.select_one(".list-group-item:nth-of-type(13) .list-group-item-text").text
        datos["comprobantes_electronicos"] = soup.select_one(".list-group-item:nth-of-type(14) .list-group-item-text").text
        datos["afiliado_ple_desde"] = soup.select_one(".list-group-item:nth-of-type(15) .list-group-item-text").text
        datos["padrones"] = soup.select_one(".list-group-item:nth-of-type(16) .table.tblResultado").text.strip()

        adicional["tipo"] = soup.select_one(".list-group-item:nth-of-type(2) .list-group-item-text").text
        tabla_actividades = soup.select_one(".list-group-item:nth-of-type(10) .table.tblResultado")

        for fila in tabla_actividades.find_all('tr'):
            partes = fila.text.strip().split(' - ')
            tipo_actividad = partes[0].strip()
            adicional[f'actividad_economica_{tipo_actividad}'] = tipo_actividad

        adicional["comercio_exterior"] = soup.select(".list-group-item:nth-of-type(8) .list-group-item-text")[1].text
        adicional["tipo_contabilidad"] = soup.select_one(".list-group-item:nth-of-type(9) .list-group-item-text").text
        adicional["tipo_facturacion"] = soup.select_one(".list-group-item:nth-of-type(8) .list-group-item-text").text
        datos['informacion_adicional']=adicional

        return datos
    
    def ExtraerDatosRUC10(self, soup, ruc):
        datos = {'success':True}
        adicional = {}
        datos["ruc"] = ruc
        datos["nombre_o_razon_social"] = soup.select_one(".list-group-item:nth-of-type(1) .col-sm-7 .list-group-item-heading").text
        datos["estado_del_contribuyente"] = soup.select_one(".list-group-item:nth-of-type(6) .list-group-item-text").text.strip()
        datos["condicion_de_domicilio"] = soup.select_one(".list-group-item:nth-of-type(7) .list-group-item-text").text.strip()
        direccion_elemento = soup.select_one(".list-group-item:nth-of-type(8) .list-group-item-text").text
        datos_direccion = self.get_payload_direccion( direccion_elemento)
        datos.update(datos_direccion) 
        datos['ubigeo']= None
        datos["fecha_inscripcion"] = soup.select_one(".list-group-item:nth-of-type(5) .list-group-item-text").text
        
        datos["fecha_inicio_actividades"] = soup.select(".list-group-item:nth-of-type(5) .list-group-item-text")[1].text
        
        datos["comprobantes_pago"] = soup.select_one(".list-group-item:nth-of-type(12) .table.tblResultado").text.strip()

        sistema_emision_electronica = self.ValidarContenido(soup.select_one(".list-group-item:nth-of-type(13) .table.tblResultado"))
        datos["sistema_emision_electronica"] = sistema_emision_electronica

        datos["emisor_electronico_desde"] = soup.select_one(".list-group-item:nth-of-type(14) .list-group-item-text").text
        datos["comprobantes_electronicos"] = soup.select_one(".list-group-item:nth-of-type(15) .list-group-item-text").text
        datos["afiliado_ple_desde"] = soup.select_one(".list-group-item:nth-of-type(16) .list-group-item-text").text
        datos["padrones"] = soup.select_one(".list-group-item:nth-of-type(17) .table.tblResultado").text.strip()

        adicional["tipo"] = soup.select_one(".list-group-item:nth-of-type(2) .list-group-item-text").text
        tabla_actividades = soup.select_one(".list-group-item:nth-of-type(11) .table.tblResultado")

        for fila in tabla_actividades.find_all('tr'):
            partes = fila.text.strip().split(' - ')
            tipo_actividad = partes[0].strip()
            adicional[f'actividad_economica_{tipo_actividad}'] = tipo_actividad

        adicional["comercio_exterior"] = soup.select(".list-group-item:nth-of-type(9) .list-group-item-text")[1].text
        adicional["tipo_contabilidad"] = soup.select_one(".list-group-item:nth-of-type(10) .list-group-item-text").text
        adicional["tipo_facturacion"] = soup.select_one(".list-group-item:nth-of-type(9) .list-group-item-text").text
        datos['informacion_adicional']=adicional

        return datos
    def ValidarContenido(self,value):
        if value:
            return re.sub(r'\s+', ' ', value.text)
        else:
            return None

    def ObtenerInformacionTrabajadores(self, urlInicial, ruc, numRandom, desRuc):
        payload = {
            'numRnd': numRandom,
            'accion': 'getCantTrab',
            'nroRuc': ruc,
            'contexto': 'ti-it',
            'modo': '1',
            'desRuc': desRuc
        }
        headers = self.headers.copy()
        headers['Origin'] = 'https://e-consultaruc.sunat.gob.pe'
        headers['Referer'] = urlInicial

        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
        response = self.sesion.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.select_one(".table tbody")
            if table:
                rows = table.find_all("tr")
                last_row = rows[-1]
                cells = last_row.find_all("td")
                trabajadores = {
                    "periodo": cells[0].text,
                    "trabajadores": cells[1].text,
                    "pensionistas": cells[2].text,
                    "prestadores_servicio": cells[3].text
                }
                return True, trabajadores, 200
            else:
                return False, None, 200
        else:
            return False, f"Ocurrió un inconveniente ({response.status_code}) al obtener la información de trabajadores para el RUC {ruc}.", response.status_code

    def obtener_datos_por_ruc(self, ruc):
        nPalabra = random.randint(0, len(self.arrNombreAleatorio) - 1)
        urlInicial = f"https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRazonSoc&razSoc={self.arrNombreAleatorio[nPalabra]}"

        response = self.sesion.get(urlInicial, headers=self.headers)

        if response.status_code == 200:
            headers = self.headers.copy()
            headers['Origin'] = 'https://e-consultaruc.sunat.gob.pe'
            headers['Referer'] = urlInicial

            numeroDNI = "76675919"
            url = f"https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorTipdoc&razSoc=&nroRuc=&nrodoc={numeroDNI}&contexto=ti-it&modo=1&search1=&rbtnTipo=2&tipdoc=1&search2={numeroDNI}&search3=&codigo="

            contenidoHTML = ""
            nIntentos = 0
            codigoEstado = 401
            while nIntentos < 3 and codigoEstado == 401:
                response = self.sesion.post(url, headers=headers, data={})
                codigoEstado = response.status_code
                contenidoHTML = response.text
                nIntentos += 1

            if codigoEstado == 200:
                numeroRandom = self.ExtraerContenidoEntreTagString(contenidoHTML, 0, "name=\"numRnd\" value=\"", "\">")
                nIntentos = 0
                codigoEstado = 401
                while nIntentos < 3 and codigoEstado == 401:
                    tipoRespuesta, mensajeRespuesta, codigoEstado = self.ConsultarContenidoRUC(urlInicial, ruc, numeroRandom)
                    nIntentos += 1

                if tipoRespuesta == "Exito":
                    datos = mensajeRespuesta
                    desRuc = datos["nombre_o_razon_social"]
                    tipoRespuesta, trabajadores, codigoEstado = self.ObtenerInformacionTrabajadores(urlInicial, ruc, numeroRandom, desRuc)
                    datos["trabajadores"] = trabajadores
                    datos['informacion_adicional']['numero_trabajadores']=None
                    if tipoRespuesta:
                        datos['informacion_adicional']['numero_trabajadores']=trabajadores['trabajadores']

                    return datos
                
            else:
                mensajeRespuesta = f"Ocurrió un inconveniente ({response.status_code}) al consultar el número random del RUC {ruc}.\r\nDetalle: {contenidoHTML}"
                raise serializers.ValidationError({"error": mensajeRespuesta} )
        else:
            mensajeRespuesta = f"Ocurrió un inconveniente ({response.status_code}) al consultar la página principal con el RUC {ruc}.\r\nDetalle: {response.text}"
            raise serializers.ValidationError({"error": mensajeRespuesta} )

