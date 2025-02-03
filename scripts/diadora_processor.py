import pandas as pd

def process_xlsx_to_transformed_csv(input_path, output_path):
    """
    Procesa un archivo .xlsx y genera un archivo .csv transformado.
    :param input_path: Ruta del archivo .xlsx de entrada.
    :param output_path: Ruta donde se guardará el archivo .csv de salida.
    """
    try:
        print(f"Leyendo archivo de entrada: {input_path}")
        data = pd.read_excel(input_path)

        # Depuración: Mostrar columnas del archivo
        print("Columnas del archivo:", data.columns.tolist())

        # Limpiar nombres de columnas
        data.rename(columns=lambda x: x.strip(), inplace=True)

        # Validar columnas requeridas
        required_columns = ['Fecha', 'Remito', 'EAN', 'Cantidad', 'PreUni', 'Suc', 'Nombre']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise RuntimeError(f"Faltan columnas críticas en el archivo: {missing_columns}")

        # Transformar los datos según sea necesario
        transformed_data = []
        for _, row in data.iterrows():
            try:
                # Ejemplo de transformación (ajustar según necesidades)
                fecha = pd.to_datetime(row['Fecha'], dayfirst=True).strftime("%d%m%y")
                referencia = str(row['Remito']).strip()
                if not referencia or len(referencia) != 15:
                    continue

                codigo_barras = str(row['EAN']).strip()
                if len(codigo_barras) != 13:
                    continue

                cantidad = row['Cantidad']
                precio = str(float(row['PreUni'])).replace(".", ",")

                almacen = str(row['Suc']).strip()
                if len(almacen) == 5:
                    almacen = f"0{almacen}"
                elif len(almacen) > 6:
                    almacen = almacen[:6]

                establecimiento = "002" if "marathon" in str(row['Nombre']).lower() else "001"


                # Construcción de la fila transformada
                transformed_row = {
                    "CAB": "ZCOC1_",
                    "REFERENCIA INTERNA": referencia,
                    "FECHA": fecha,
                    "COD PROVEEDOR": "GSIET",
                    "CODIGO BARRAS": codigo_barras,
                    "CANTIDAD": int(cantidad),
                    "PRECIO": precio,
                    "ALMACEN": almacen,
                    "ESTABLECIMIENTO": establecimiento,
                    "DESCUENTO": 5,
                }
                transformed_data.append(transformed_row)
            except Exception as e:
                print(f"Error procesando fila: {e}")
                continue

        # Guardar el archivo .csv
        if transformed_data:
            transformed_df = pd.DataFrame(transformed_data)
            transformed_df.to_csv(output_path, index=False, sep="|", encoding="utf-8-sig")
            print(f"Archivo generado correctamente en: {output_path}")
        else:
            print("No se generaron datos válidos para exportar.")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        raise RuntimeError(f"Error al procesar el archivo: {e}")

