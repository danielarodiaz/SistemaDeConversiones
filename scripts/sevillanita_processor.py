import pandas as pd
import os
import re

def process_csv_to_transformed_sevillanita(input_path, output_path):
    try:
        with open(input_path, 'r', encoding="utf-8") as f:
            first_line = f.readline()
            delimiter = ";" if ";" in first_line else ","

        data = pd.read_csv(input_path, dtype=str, delimiter=delimiter)
        data.columns = [col.strip() for col in data.columns]
        
        # Mapeo de nombres de columnas con variantes
        column_mapping = {
            "Importe Flete": ["Importe Flete", "Inporte Flete", "ImporteFlete"],
            "Importe Seguro": ["Importe Seguro", "Inporte Seguro", "ImporteSeguro"],
            # Agregás más si encontrás otros casos
        }

        # Renombrar columnas si tienen errores comunes
        for standard_name, alternatives in column_mapping.items():
            for alt in alternatives:
                if alt in data.columns:
                    data.rename(columns={alt: standard_name}, inplace=True)
                    break

        if "F.Emis." not in data.columns:
            raise ValueError("No se encontró la columna 'F.Emis.' en el archivo CSV.")

        cabecera_marathon = []
        cabecera_otros = []
        detalle_marathon = []
        detalle_otros = []
        docnum_marathon = 1
        docnum_otros = 1

        for _, row in data.iterrows():
            try:
                if row["F.Emis."].strip() == "0" or row["Pref"].strip() == "0":
                    continue
                if len(row["Nro.Guia"].strip()) <= 2:
                    continue

                fecha_emision = row["F.Emis."].strip()
                if len(fecha_emision) != 8:
                    continue
                fecha_emision = f"{fecha_emision[4:8]}{fecha_emision[2:4]}{fecha_emision[0:2]}"

                pti_code = row["Pref"].strip().zfill(5)
                letter = "A"
                fol_num_from = row["Nro.Guia"].strip().zfill(8)
                num_at_card = f"{letter}{pti_code}{fol_num_from}"

                remitente = row.get("Remitente", "").strip()
                destinatario = row.get("Destinatario", "").strip()
                belongs_to_marathon = "MARATHON SRL" in [remitente, destinatario]
                
                # 🧠 DocNum local
                docnum_local = docnum_marathon if belongs_to_marathon else docnum_otros

                cabecera_row = {
                    "DocNum": docnum_local,
                    "DocEntry": docnum_local,
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
                    "Series": "14",
                }

                # OCRCODE
                destinatario_raw = destinatario.upper()
                if "MARATHON" in destinatario_raw or "BLANCO" in destinatario_raw:
                    ocr_code = "240001-1"
                else:
                    match = re.search(r"\d{6}", destinatario_raw)
                    if match:
                        solo_num = match.group(0)
                        ocr_code = f"{solo_num}-1"
                    else:
                        ocr_code = "000000-1"
                ocr_code2 = ocr_code[:-1] + "2"
                
                # DETALLE
                detalle_fila = []
                for line_num in range(4):
                    item_code = 100 + line_num
                    dscription = {
                        100: "FLETE DE TERCEROS",
                        101: "FLETES - SEGURO",
                        102: "FLETES - KILOS",
                        103: "FLETES - CAJAS"
                    }.get(item_code, "FLETE")

                    quantity = 1
                    if item_code == 102:
                        quantity = int(row.get("Kilos", "0"))
                    elif item_code == 103:
                        quantity = int(row.get("Bultos", "0"))

                    price = 0.0
                    if item_code == 100:
                        price = float(row.get("Importe Flete", "0").replace(",", "."))
                    elif item_code == 101:
                        price = float(row.get("Importe Seguro", "0").replace(",", "."))

                    detalle_row = {
                        "DocNum": docnum_local,
                        "LineNum": line_num,
                        "ItemCode": str(item_code),
                        "Dscription": dscription,
                        "Quantity": quantity,
                        "Price": price,
                        "TaxCode": "IVA_21",
                        "TaxOnly": "N",
                        "AcctCode": "5.2.020.05.001",
                        "OcrCode": ocr_code,
                        "OcrCode2": ocr_code2
                    }

                    detalle_fila.append(detalle_row)

                if belongs_to_marathon:
                    cabecera_marathon.append(cabecera_row)
                    detalle_marathon.extend(detalle_fila)
                    docnum_marathon += 1
                else:
                    cabecera_otros.append(cabecera_row)
                    detalle_otros.extend(detalle_fila)
                    docnum_otros += 1

            except Exception as e:
                print(f"Error procesando fila: {e}")

        def save_csv(file_path, data_list, header1, header2):
            if data_list:
                df = pd.DataFrame(data_list)
                with open(file_path, "w", encoding="utf-8", newline="") as f:
                    f.write(";".join(header1) + "\n")
                    f.write(";".join(header2) + "\n")
                    df.to_csv(f, index=False, sep=";", header=False)
                os.chmod(file_path, 0o777)
                print(f"Archivo generado: {file_path}")

        # ENCABEZADOS
        header_line_1_cab = ["DocNum", "DocEntry", "DocType", "DocDate", "TaxDate", "DocDueDate",
                             "CardCode", "NumAtCard", "DocCurrency", "JournalMemo", "Comments",
                             "PointOfIssueCode", "Letter", "FolioNumberFrom", "FolioNumberTo", "Series"]
        header_line_2_cab = ["DocNum", "DocEntry", "DocType", "DocDate", "TaxDate", "DocDueDate",
                             "CardCode", "NumAtCard", "DocCur", "JournalMemo", "Comments",
                             "PTICode", "Letter", "FolNumFrom", "FolNumTo", "Series"]

        header_line_1_det = ["ParentKey", "LineNum", "ItemCode", "ItemDescription", "Quantity", "Price",
                             "TaxCode", "TaxOnly", "AccountCode", "OcrCode", "OcrCode2"]
        header_line_2_det = ["DocNum", "LineNum", "ItemCode", "Dscription", "Quantity", "Price",
                             "TaxCode", "TaxOnly", "AcctCode", "OcrCode", "OcrCode2"]

        # Rutas
        cab_mar_path = output_path.replace(".csv", "_CABECERA_marathon.csv")
        cab_otr_path = output_path.replace(".csv", "_CABECERA_blanco.csv")
        det_mar_path = output_path.replace(".csv", "_DETALLE_marathon.csv")
        det_otr_path = output_path.replace(".csv", "_DETALLE_blanco.csv")

        # Guardar archivos
        save_csv(cab_mar_path, cabecera_marathon, header_line_1_cab, header_line_2_cab)
        save_csv(cab_otr_path, cabecera_otros, header_line_1_cab, header_line_2_cab)
        save_csv(det_mar_path, detalle_marathon, header_line_1_det, header_line_2_det)
        save_csv(det_otr_path, detalle_otros, header_line_1_det, header_line_2_det)

        return cab_mar_path, cab_otr_path, det_mar_path, det_otr_path

    except Exception as e:
        raise RuntimeError(f"Error al procesar el archivo: {e}")
