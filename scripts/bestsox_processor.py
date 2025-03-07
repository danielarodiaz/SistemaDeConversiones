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
         
        transformed_data = []
        for sheet_name, data in sheets.items():
            print(f"Procesando pestaña: {sheet_name}")
            print(f"Datos iniciales: {data.head()}")  # Ver los primeros datos de la pestaña

            for _, row in data.iterrows():
                try:

                    fecha = row['Fecha']
                    if isinstance(fecha, pd.Timestamp):  # Si es un objeto datetime
                        fecha_str = fecha.strftime("%d%m%y")  # Convertir al formato DDMMYY
                    else:
                        print(f"Formato inesperado de Fecha: {fecha}")
                        continue

                    referencia = str(row['Remito']).strip()  # Eliminar espacios en blanco
                    if not (referencia.startswith("R") and len(referencia) == 13):
                        print(f"Referencia inválida: {referencia}")
                        continue

                    codigo_barras = str(row['EAN']).strip()  # Eliminar espacios en blanco
                    if len(codigo_barras) != 13:
                        print(f"Código de barras inválido: {codigo_barras}")
                        continue

                    almacen = str(row['Suc']).strip()
                    match = re.match(r"^\d{5,6}", almacen)  # Extraer los primeros dígitos
                    if match:
                        almacen = match.group(0)
                        if len(almacen) == 5:
                            almacen = f"0{almacen}"  # Agregar un 0 si tiene 5 dígitos
                    else:
                        print(f"Almacén inválido: {almacen}")
                        continue

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
                        "FECHA": fecha_str, 
                        "COD PROVEEDOR": "BESTS",
                        "CODIGO BARRAS": codigo_barras,
                        "CANTIDAD": int(cantidad),
                        "PRECIO": str(float(precio)).replace('.', ','),
                        "ALMACEN": almacen,
                        "ESTABLECIMIENTO": establecimiento,
                        "DESCUENTO": 12
                    }
                    transformed_data.append(transformed_row)
                except Exception as e:
                    print(f"Error procesando fila: {e}")
      
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
