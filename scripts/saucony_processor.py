import os
import pandas as pd

def process_xlsx_to_transformed_csv_saucony(input_path, output_folder):
    """
    Transforma las pestañas de un archivo .xlsx en archivos .csv separados con el formato especificado.
    
    :param input_path: Ruta del archivo .xlsx de entrada.
    :param output_folder: Carpeta donde se guardarán los archivos .csv.
    """
    try:
        # Leer todas las hojas del archivo .xlsx
        sheets = pd.read_excel(input_path, sheet_name=None)

        # Crear el directorio de salida si no existe
        os.makedirs(output_folder, exist_ok=True)

        for sheet_name, data in sheets.items():
            print(f"Procesando pestaña: {sheet_name}")
            
            transformed_data = []
            for _, row in data.iterrows():
                try:
                    # Procesar la columna Fecha
                    fecha_str = pd.to_datetime(row['Fecha'], dayfirst=True).strftime('%d%m%y')
                    
                    # Procesar la columna Remito
                    referencia = str(row['Remito']).zfill(4)
                    
                    # Procesar la columna EAN (código de barras)
                    codigo_barras = str(row['EAN']).strip()
                    
                    # Procesar la columna Cantidad
                    cantidad = int(row['Cantidad'])
                    
                    # Procesar la columna Costo
                    precio = str(float(row['Costo'])).replace('.', ',')
                    
                    # Procesar la columna Nombre para determinar Establecimiento
                    establecimiento = '002' if row['Nombre'] == 'MARATHON SRL' else '001'
                    
                    # Procesar la columna Suc para Almacen
                    almacen = str(row['Suc']).encode('latin1').decode('utf-8', 'ignore').strip().zfill(6)  # Remover caracteres no deseados y completar a 6 dígitos
                    
                    # Descuento fijo
                    descuento = 10
                    
                    # Construir la fila transformada
                    transformed_row = {
                        "CAB": "ZCOC1_",
                        "REFERENCIA INTERNA": referencia,
                        "FECHA": fecha_str,
                        "COD PROVEEDOR": "SUOLA",
                        "CODIGO BARRAS": codigo_barras,
                        "CANTIDAD": cantidad,
                        "PRECIO": precio,
                        "ALMACEN": almacen,
                        "ESTABLECIMIENTO": establecimiento,
                        "DESCUENTO": descuento,
                    }
                    transformed_data.append(transformed_row)
                except Exception as e:
                    print(f"Error procesando fila: {e}")

            # Guardar cada pestaña como un archivo .csv
            if transformed_data:
                output_file = os.path.join(output_folder, f"{sheet_name}.csv")
                transformed_df = pd.DataFrame(transformed_data)
                transformed_df.to_csv(output_file, index=False, sep='|', encoding='utf-8')
                print(f"Archivo generado: {output_file}")
            else:
                print(f"No hay datos válidos en la pestaña '{sheet_name}'")

    except Exception as e:
        raise RuntimeError(f"Error al procesar el archivo: {e}")
