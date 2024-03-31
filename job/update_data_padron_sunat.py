from apps.sunat.models import TempDireccionSunat
from django.db import connection
import datetime
import requests
import zipfile
import pandas as pd
from io import BytesIO

def update_data_padron_sunat():
    fecha_actual = datetime.datetime.now()
    fecha_formateada = fecha_actual.strftime('%Y%m')
    url = f"https://www.datosabiertos.gob.pe/sites/default/files/PadronRUC_{fecha_formateada}.zip"
    # Realizar la solicitud GET a la API
    response = requests.get(url)
    
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Crear un objeto ZipFile a partir de los datos recibidos
        with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
            # Extraer la lista de archivos en el zip
            lista_archivos = zip_file.namelist()
            # Seleccionar el primer archivo (suponiendo que es un archivo de texto)
            primer_archivo = lista_archivos[0]
            
            # Leer el archivo de texto seleccionado
            with zip_file.open(primer_archivo) as txt_file:
                # Decodificar los datos del archivo de texto
                datos_txt = txt_file.read().decode('ISO-8859-1')
                df = pd.read_csv(BytesIO(datos_txt.encode()), sep='|', dtype=str)
                #columns =['ruc', 'ubigeo', 'tipo_via', 'nombre_via', 'codigo_zona',
                #    'tipo_zona', 'numero', 'kilometro', 'interior', 'lote',
                #    'departamento_anexo', 'manzana', 'vacio']
                #df.columns =columns
                df = df[["RUC","UBIGEO","Departamento","Provincia","Distrito"]]
                df.rename(columns={
                    "RUC":"ruc",
                    "UBIGEO":"ubigeo",
                    "Departamento":"departamento",
                    "Provincia":"provincia",
                    "Distrito":"distrito"
                })
                df.dropna(subset = ['ruc'], inplace=True)
                df.drop_duplicates(subset=['ruc'],inplace=True)

                df = df.to_dict('records')
                TempDireccionSunat.objects.all().delete()
                BATCH_SIZE = 25000
                objects_to_create = [TempDireccionSunat(**record) for record in df]
                for i in range(0, len(objects_to_create), BATCH_SIZE):
                    batch = objects_to_create[i:i + BATCH_SIZE]
                    TempDireccionSunat.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                try:
                    with connection.cursor() as cursor:
                        # Llamar al Stored Procedure merge_cliente usando CALL
                        cursor.execute("CALL temporales.merge_direccion_sunat()", [])
                        # Después de la ejecución, recuperar el valor de result usando una consulta
                        #cursor.execute("SELECT p_result")
                        #result = cursor.fetchone()[0]
                        return True, "OK"

                except Exception as e:
                    print(f"Error en sp merge_cliente: {e}")
                    return False, str(e)
    else:
        return False,False

# URL de la API
#url_api = "https://www.datosabiertos.gob.pe/sites/default/files/PadronRUC_202403.zip"
#df = update_data_padron_sunat(url_api)
#print(df.columns)