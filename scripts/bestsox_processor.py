import os
import pandas as pd
import re  # Importar para manejar expresiones regulares

def process_xlsx_to_csv(input_path, output_folder):
    """
    Transforma las pestañas de un archivo .xlsx en archivos .csv separados.
    
    :param input_path: Ruta del archivo .xlsx de entrada.
    :param output_folder: Carpeta donde se guardarán los archivos .csv.
    """
    try:
        # Leer todas las hojas del archivo .xlsx
        sheets = pd.read_excel(input_path, sheet_name=None)

        # Crear el directorio de salida si no existe
        #os.makedirs(output_folder, exist_ok=True)
        
        #output_folder = os.path.dirname(input_path)  # Guarda en la misma carpeta del archivo de entrada
        
        # Obtener la carpeta de descargas del usuario actual
        #download_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        # Definir el nombre del archivo CSV de salida (con timestamp para evitar conflictos)
        #output_file = os.path.join(download_folder, "BESTSOX_Procesado.csv")
        
        
        transformed_data = []
        for sheet_name, data in sheets.items():
            print(f"Procesando pestaña: {sheet_name}")
            print(f"Datos iniciales: {data.head()}")  # Ver los primeros datos de la pestaña

            #transformed_data = []
            for _, row in data.iterrows():
                try:
                    # Procesar la columna Fecha
                    fecha = row['Fecha']
                    if isinstance(fecha, pd.Timestamp):  # Si es un objeto datetime
                        fecha_str = fecha.strftime("%d%m%y")  # Convertir al formato DDMMYY
                    else:
                        print(f"Formato inesperado de Fecha: {fecha}")
                        continue

                    # Procesar la columna Remito
                    referencia = str(row['Remito']).strip()  # Eliminar espacios en blanco
                    if not (referencia.startswith("R") and len(referencia) == 13):
                        print(f"Referencia inválida: {referencia}")
                        continue

                    # Procesar la columna EAN (código de barras)
                    codigo_barras = str(row['EAN']).strip()  # Eliminar espacios en blanco
                    if len(codigo_barras) != 13:
                        print(f"Código de barras inválido: {codigo_barras}")
                        continue

                    # Procesar la columna Almacén (Suc)
                    almacen = str(row['Suc']).strip()
                    match = re.match(r"^\d{5,6}", almacen)  # Extraer los primeros dígitos
                    if match:
                        almacen = match.group(0)
                        if len(almacen) == 5:
                            almacen = f"0{almacen}"  # Agregar un 0 si tiene 5 dígitos
                    else:
                        print(f"Almacén inválido: {almacen}")
                        continue

                    # Procesar otras columnas
                    cantidad = row['Cantidad']
                    if not isinstance(cantidad, (int, float)):
                        print(f"Cantidad inválida: {row['Cantidad']}")
                        continue

                    precio = row['PreUni']
                    if not isinstance(precio, (float, int)):
                        print(f"Precio inválido: {row['PreUni']}")
                        continue

                    establecimiento = "002" if row['Nombre'] == "MARATHON SRL" else "001"


                    # Construir la fila transformada
                    transformed_row = {
                        "CAB": "ZCOC1_",
                        "REFERENCIA INTERNA": referencia,
                        "FECHA": fecha_str,  # Usar la fecha procesada
                        "COD PROVEEDOR": "BESTS",
                        "CODIGO BARRAS": codigo_barras,
                        "CANTIDAD": int(cantidad),
                        "PRECIO": str(float(precio)).replace('.', ','), # Cambiar el punto por coma
                        "ALMACEN": almacen,
                        "ESTABLECIMIENTO": establecimiento,
                        "DESCUENTO": 12
                    }
                    transformed_data.append(transformed_row)
                except Exception as e:
                    print(f"Error procesando fila: {e}")

            # # Guardar cada pestaña como un archivo .csv
            # if transformed_data:
            #     output_file = os.path.join(output_folder, f"{sheet_name}.csv")
            #     transformed_df = pd.DataFrame(transformed_data)
            #     transformed_df.to_csv(output_file, index=False, sep="|", encoding='utf-8-sig')  # Separador personalizado
            #      # 🔹 Asignar permisos al archivo para asegurar que Flask pueda acceder
            #     os.chmod(output_file, 0o777)
            #     print(f"Archivo generado: {output_file}")
            # else:
            #     print(f"No hay datos válidos en la pestaña '{sheet_name}'")
            
            # Guardar todo en un solo archivo CSV
            if transformed_data:
                transformed_df = pd.DataFrame(transformed_data)
                transformed_df.to_csv(output_folder, index=False, sep="|", encoding='utf-8-sig')

            # 🔹 Asegurar permisos para que Flask pueda acceder
                os.chmod(output_folder, 0o777)

                print(f"Archivo generado: {output_folder}")
            else:
                print("No se generaron datos válidos")

    except Exception as e:
        raise RuntimeError(f"Error al procesar el archivo: {e}")
