# imports
import random
import re
import requests
#rest
from rest_framework import serializers
from django.db.models import F

#models
from .models import InteractionSunat,Direccion
from apps.company.models import Company

from bs4 import BeautifulSoup


def update_models(numero_documento,response,made_scraping,company_id):
    InteractionSunat.objects.create(document_number=numero_documento,company_id=1,payload=response,scraping=made_scraping)
    Company.objects.filter(id=company_id).update(total_sunat=F('total_sunat') + 1)

class GetTextSoup():
    def __init__(self,soup):
        self.soup = soup

    def obtener_valor(self,texto_buscar, elemento_valor):
        elemento_h4 = self.soup.find('h4', text=texto_buscar)
        if elemento_h4:
            elemento_valor_tag = elemento_h4.find_next(elemento_valor)
            if elemento_valor_tag:
                valor = elemento_valor_tag.get_text(strip=True)
                valor = valor.replace('\r\n', '').replace('\n', '').replace('\t', '').strip()  # Eliminar saltos de línea y espacios
                return valor
        return ""
    
    def obtener_valor_tabla(self,texto_buscar, elemento_valor):
        tablas = self.soup.find_all('table', class_='tblResultado', text=texto_buscar)
        valores = []
        for tabla in tablas:
            filas = tabla.find_all(elemento_valor)
            valores.extend([fila.get_text(strip=True) for fila in filas])
        return valores
    
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
    def get_payload_direccion(self, direccion,ruc):
        direccion_list = direccion.split('  ')
        direccion_list = [elemento for elemento in direccion_list if elemento]
        distrito = None
        provincia = None
        departamento = None
        direccion_object = Direccion.objects.filter(ruc = ruc)

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
            "ubigeo":None,
            "direccion_simple": direccion_simple,
            "direccion":" ".join(direccion_list)
            }
        
        if direccion_object:
            obj = direccion_object.first()
            datos["distrito"]= obj.distrito
            datos["provincia"]= obj.provincia
            datos["departamento"]=  obj.departamento
            datos["ubigeo"]=  obj.ubigeo
        else:
            if len(direccion_list) >2:
                distrito = direccion_list[-1].replace('-','').strip()
                provincia = direccion_list[-2].replace('-','').strip()
                departamento =direccion_list[-3].replace('-','').strip()
            datos["distrito"]= distrito
            datos["provincia"]= provincia
            datos["departamento"]= departamento
            datos["ubigeo"]= None
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
                datos = self.ExtraerDatosRUC(soup, ruc)
                return "Exito", datos, 200
            else:
                raise serializers.ValidationError(
                        {"error": "No se encontraron datos"}
                )
        else:
            raise serializers.ValidationError(
                {"error": "No pudimos conectarnos a la sunat"}
            )
    
    def ExtraerDatosRUC(self, soup, ruc):
        datos = {'success':True}
        adicional = {"actividad_economica_principal":None,"actividad_economica_secundaria_1":None,"actividad_economica_secundaria_2":None}
        datos["ruc"] = ruc
        get_soup =GetTextSoup(soup)
        datos["nombre_o_razon_social"] = "-".join(get_soup.obtener_valor("Número de RUC:", 'h4').split('-')[1:])
        datos["tipo"] = get_soup.obtener_valor("Tipo Contribuyente:", 'p')
        datos["nombre_comercial"] = get_soup.obtener_valor("Nombre Comercial:", 'p')
        datos["estado_del_contribuyente"] = get_soup.obtener_valor("Estado del Contribuyente:", 'p')
        datos["condicion_de_domicilio"] = get_soup.obtener_valor("Condición del Contribuyente:", 'p')

        direccion = get_soup.obtener_valor("Domicilio Fiscal:", 'p')
        #datos["direccion"] = direccion.replace('  ', '')

        datos["fecha_inscripcion"] = get_soup.obtener_valor("Fecha de Inscripción:", 'p')
        datos["fecha_inicio_actividades"] = get_soup.obtener_valor("Fecha de Inicio de Actividades:", 'p')
        datos["comprobantes_pago"] = get_soup.obtener_valor("Comprobantes de Pago c/aut. de impresión (F. 806 u 816):", 'p')

        datos["sistema_emision_electronica"] = get_soup.obtener_valor("Sistema de Emisión Electrónica:", 'p')
        datos["emisor_electronico_comprobante"] = get_soup.obtener_valor("Emisor electrónico desde:", 'p')
        #datos["comprobantes_electronicos"] = get_soup.obtener_valor("Comprobantes Electrónicos:", 'p')
        datos["afiliado_ple_desde"] = get_soup.obtener_valor("Afiliado al PLE desde:", 'p')
        

        datos_direccion = self.get_payload_direccion(direccion ,ruc)
        datos.update(datos_direccion) 

        actividades_economicas = soup.find('table', class_='tblResultado').find_all('tr')
        actividades_economicas = [tr.td.get_text(strip=True) for tr in actividades_economicas]

        adicional['actividad_economica_principal'] = actividades_economicas[0] if len(actividades_economicas) >= 1 else None
        adicional['actividad_economica_secundaria_1'] = actividades_economicas[1] if len(actividades_economicas) >= 2 else None
        adicional['actividad_economica_secundaria_2'] = actividades_economicas[2] if len(actividades_economicas) >= 3 else None

        adicional["comercio_exterior"] = get_soup.obtener_valor("Actividad Comercio Exterior:", 'p')
        adicional["tipo_contabilidad"] = get_soup.obtener_valor("Sistema Contabilidad:", 'p')
        adicional["tipo_facturacion"] = get_soup.obtener_valor("Sistema Emisión de Comprobante:", 'p')

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




