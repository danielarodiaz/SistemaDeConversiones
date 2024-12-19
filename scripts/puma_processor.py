import pandas as pd
import re
import os


def process_csv_to_transformed_file(input_path, output_path):
    """
    Procesa un archivo CSV para transformar las columnas y genera un archivo delimitado por '|'.

    :param input_path: Ruta del archivo CSV original.
    :param output_path: Ruta donde se guardará el archivo transformado.
    """
    # Constantes
    CAB = "ZCOC1_"
    COD_PROVEEDOR = "UNISO"
    ALMACEN = "240001"
    DESCUENTO = "11,445"

    # Extraer la fecha del nombre del archivo
    file_name = os.path.basename(input_path)
    match = re.search(r"detalle_fact_(\d{6})\d{6}", file_name)
    if match:
        fecha = (
            match.group(1)[-2:] + match.group(1)[2:4] + match.group(1)[:2]
        )  # Reorganizar como 211124
    else:
        raise ValueError("El nombre del archivo no contiene una fecha válida.")

    # Leer el CSV original con validación de columnas
    try:
        df = pd.read_csv(input_path, sep=";", header=None, dtype=str)
    except Exception as e:
        raise ValueError(f"Error al leer el archivo CSV: {e}")

    # Validar número de columnas
    expected_columns = [7, 8, 11, 12, 15]
    missing_columns = [col for col in expected_columns if col >= len(df.columns)]
    if missing_columns:
        raise ValueError(
            f"El archivo CSV no tiene las columnas esperadas. Faltan: {missing_columns}"
        )
    
    # Limpieza de datos: eliminar espacios de las columnas relevantes
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Filtrar filas inválidas según las reglas de validación
    def is_valid_row(row):
        # Validar REFERENCIA-INTERNA (REM) tiene el formato NNNN-NNNNNNNN
        if not re.match(r"^\d{4}-\d{8}$", row[12]):
            return False

        # Validar CODIGO BARRAS es un número de 13 dígitos
        if not row[7].isdigit() or len(row[7]) != 13:
            return False

        # Validar CANTIDAD es un número entero
        if not row[15].isdigit():
            return False

        # Validar PRECIO tiene formato válido (puede contener punto decimal)
        if not re.match(r"^\d+(\.\d+)?$", row[8]):
            return False

        return True
    
    # Aplicar validación fila por fila
    valid_rows = df.apply(is_valid_row, axis=1)
    df = df[valid_rows]



    # Transformar las columnas necesarias
    df_transformado = pd.DataFrame(
        {
            "CAB": [CAB] * len(df),
            "REFERENCIA INTERNA": df[12],  # Columna 13 (índice 12)
            "FECHA": [fecha] * len(df),
            "COD PROVEEDOR": [COD_PROVEEDOR] * len(df),
            "CODIGO BARRAS": df[7].str.zfill(13),  # EAN de 13 dígitos
            "CANTIDAD": df[15],  # Columna 16 (índice 15)
            "PRECIO": df[8].str.replace(".", ",", regex=False),  # Columna 9 (índice 8)
            "ALMACEN": [ALMACEN] * len(df),
            "ESTABLECIMIENTO": df[11].apply(
                lambda x: "002" if x.strip().upper() == "MARATHON S.R.L." else "001"
            ),  # Columna 12
            "DESCUENTO": [DESCUENTO] * len(df),
        }
    )
   

    # Exportar el archivo transformado
    df_transformado.to_csv(output_path, sep="|", index=False, header=True)
