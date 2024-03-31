from apps.sunat.models import TempDireccionSunat
from django.db import connection
import datetime
import requests
import zipfile, os
import pandas as pd
from io import BytesIO

def update_data_padron_sunat():
    fecha_actual = datetime.datetime.now()
    fecha_formateada = fecha_actual.strftime('%Y%m')
    url = f"https://www.datosabiertos.gob.pe/sites/default/files/PadronRUC_{fecha_formateada}.zip"
    local_zip_path = f"PadronRUC_{fecha_formateada}.zip"
    TempDireccionSunat.objects.all().delete()
    # Realizar la solicitud GET a la API
    response = requests.get(url, stream=True)  # Usar stream=True para leer el contenido de manera incremental
    
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))  # Tamaño total del archivo
        downloaded_size = 0
        print("Descargando archivo ZIP...")
        # Guardar el archivo ZIP localmente
        with open(local_zip_path, 'wb') as local_file:
            for chunk in response.iter_content(chunk_size=8192):
                local_file.write(chunk)
                downloaded_size += len(chunk)
                percent = downloaded_size * 100 / total_size
                print(f"Progreso de descarga: {percent:.2f}%")
        print("Archivo ZIP descargado correctamente.")

        downloaded_size = 0
        
        # Leer el archivo ZIP y procesar los datos
        try:
            with zipfile.ZipFile(local_zip_path, 'r') as zip_file:
                primer_archivo = zip_file.namelist()[0]
                with zip_file.open(primer_archivo) as txt_file:
                    # Especificar la codificación ISO-8859-1 al abrir el archivo
                    datos_txt = txt_file.read().decode('ISO-8859-1')
                    # Leer el archivo CSV en trozos con chunksize
                    chunksize = 100000  # Tamaño del trozo
                    df_chunks = pd.read_csv(BytesIO(datos_txt.encode()), sep=',', dtype=str, chunksize=chunksize)
                    for chunk in df_chunks:
                        df = chunk[["RUC","UBIGEO","Departamento","Provincia","Distrito"]]
                        df = df.rename(columns={
                            "RUC":"ruc",
                            "UBIGEO":"ubigeo",
                            "Departamento":"departamento",
                            "Provincia":"provincia",
                            "Distrito":"distrito"
                        })
                        df = df.dropna(subset=['ruc'])
                        df = df.drop_duplicates(subset=['ruc'])

                        # Insertar en la base de datos Django
                        
                        BATCH_SIZE = 8000
                        objects_to_create = [TempDireccionSunat(**record) for record in df.to_dict('records')]
                        for i in range(0, len(objects_to_create), BATCH_SIZE):
                            batch = objects_to_create[i:i + BATCH_SIZE]
                            TempDireccionSunat.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                            
                            # Actualizar el progreso
                            downloaded_size += len(batch)
                            percent = downloaded_size * 100 / total_size
                            print(f"Progreso: {percent:.2f}%")
                    
                    try:
                        with connection.cursor() as cursor:
                            # Llamar al Stored Procedure merge_cliente usando CALL
                            cursor.execute("CALL temporales.merge_direccion_sunat()", [])
                            return True, "OK"
                    except Exception as e:
                        print(f"Error en sp merge_cliente: {e}")
                        return False, str(e)
        except Exception as e:
            print(f"Error al abrir el archivo ZIP: {e}")
            return False, str(e)
        finally:
            # Eliminar el archivo ZIP local después de su uso
            os.remove(local_zip_path)
    else:
        return False, False

