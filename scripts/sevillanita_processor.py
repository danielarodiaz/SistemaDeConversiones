import pandas as pd
import os

def process_csv_to_transformed_sevillanita(input_path, output_path):
    try:
        # Detectar automáticamente el delimitador
        with open(input_path, 'r', encoding="utf-8") as f:
            first_line = f.readline()
            delimiter = ";" if ";" in first_line else ","

        # Cargar el archivo CSV con el delimitador correcto
        data = pd.read_csv(input_path, dtype=str, delimiter=delimiter)

        # Limpiar los nombres de las columnas
        data.columns = [col.strip() for col in data.columns]

        # Verificar si la columna 'F.Emis.' realmente existe
        if "F.Emis." not in data.columns:
            raise ValueError("No se encontró la columna 'F.Emis.' en el archivo CSV. Verifique el encabezado.")

        transformed_data_marathon = []
        transformed_data_others = []

        for _, row in data.iterrows():
            try:
                # Omite filas con valores 0 en 'F.Emis.' o 'Pref'
                if row["F.Emis."].strip() == "0" or row["Pref"].strip() == "0":
                    continue

                # Omite filas con 'Nro.Guia' de 2 dígitos o menos
                if len(row["Nro.Guia"].strip()) <= 2:
                    continue

                # 🔹 CONVERTIR FECHA `DDMMYYYY` → `YYYYMMDD`
                fecha_emision = row["F.Emis."].strip()
                if len(fecha_emision) == 8:
                    fecha_emision = f"{fecha_emision[4:8]}{fecha_emision[2:4]}{fecha_emision[0:2]}"
                else:
                    print(f"Formato de fecha inválido en fila: {row['F.Emis.']}")
                    continue  # Omitir filas con formato incorrecto

                # Formatear NumAtCard
                pti_code = row["Pref"].strip().zfill(5)
                letter = "A"
                fol_num_from = row["Nro.Guia"].strip().zfill(8)
                num_at_card = f"{letter}{pti_code}{fol_num_from}"

                # Determinar a qué archivo pertenece según 'Remitente' o 'Destinatario'
                remitente = row["Remitente"].strip() if "Remitente" in data.columns else ""
                destinatario = row["Destinatario"].strip() if "Destinatario" in data.columns else ""
                belongs_to_marathon = "MARATHON SRL" in [remitente, destinatario]

                transformed_row = {
                    "DocType": "dDocument_Items",
                    "DocDate": fecha_emision,
                    "TaxDate": fecha_emision,
                    "DocDueDate": "",
                    "CardCode": "SEVIL",
                    "NumAtCard": num_at_card,
                    "DocCur": "ARS",
                    "JournalMemo": "Fact.proveedores - SEVIL",
                    "Comments": "",
                    "PTICode": pti_code,
                    "Letter": letter,
                    "FolNumFrom": fol_num_from,
                    "FolNumTo": fol_num_from,
                    "Series": "14"
                }

                # Agregar a la lista correspondiente
                if belongs_to_marathon:
                    transformed_data_marathon.append(transformed_row)
                else:
                    transformed_data_others.append(transformed_row)

            except Exception as e:
                print(f"Error procesando fila: {e}")

        # 🔹 AGREGAR NUMERACIÓN CONSECUTIVA POR ARCHIVO ANTES DE GUARDAR
        def add_consecutive_numbers(data_list):
            """ Agrega numeración consecutiva a cada archivo """
            for index, row in enumerate(data_list):
                row["DocNum"] = index + 1
                row["DocEntry"] = index + 1
            return data_list

        # Aplicar numeración a cada archivo
        transformed_data_marathon = add_consecutive_numbers(transformed_data_marathon)
        transformed_data_others = add_consecutive_numbers(transformed_data_others)
        
        # 🔹 Encabezados de las dos primeras líneas
        header_line_1 = ["DocNum", "DocEntry", "DocType", "DocDate", "TaxDate", "DocDueDate",
                         "CardCode", "NumAtCard", "DocCurrency", "JournalMemo", "Comments",
                         "PointOfIssueCode", "Letter", "FolioNumberFrom", "FolioNumberTo", "Series"]

        header_line_2 = ["DocNum", "DocEntry", "DocType", "DocDate", "TaxDate", "DocDueDate",
                         "CardCode", "NumAtCard", "DocCur", "JournalMemo", "Comments",
                         "PTICode", "Letter", "FolNumFrom", "FolNumTo", "Series"]

        # Convertir listas en DataFrames y guardarlas con las dos primeras líneas de encabezado
        def save_csv(file_path, data_list):
            if data_list:
                df = pd.DataFrame(data_list, columns=header_line_2)
                with open(file_path, "w", encoding="utf-8", newline="") as f:
                    f.write(";".join(header_line_1) + "\n")  # Primera línea personalizada
                    f.write(";".join(header_line_2) + "\n")  # Segunda línea (encabezado real)
                    df.to_csv(f, index=False, sep=";", header=False)  # Guardar sin encabezados de pandas
                os.chmod(file_path, 0o777)
                print(f"Archivo generado: {file_path}")
                
        # 🔹 Generar nombres de archivos con CABECERA_
        marathon_file = output_path.replace(".csv", "_marathon.csv")
        others_file = output_path.replace(".csv", "_blanco.csv")

        # Guardar ambos archivos
        save_csv(marathon_file, transformed_data_marathon)
        save_csv(others_file, transformed_data_others)
        
        return marathon_file, others_file  # Retornamos los nombres de los archivos generados

        # if not transformed_data_marathon and not transformed_data_others:
        #     print("No se generaron datos válidos.")

    except Exception as e:
        raise RuntimeError(f"Error al procesar el archivo: {e}")

