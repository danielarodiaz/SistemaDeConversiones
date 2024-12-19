import csv
import re

# Función para procesar el archivo .txt y crear el archivo .csv
def process_txt_to_csv(txt_file_path, csv_file_path):
    # Abrir el archivo CSV en modo escritura
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='|')

        # Escribir el encabezado
        writer.writerow(["CAB", "REFERENCIA INTERNA", "FECHA", "COD PROVEEDOR", "CODIGO BARRAS", "CANTIDAD", "PRECIO", "ALMACEN", "ESTABLECIMIENTO", "DESCUENTO"])
        
        referencia_actual = ""
        fecha_actual = ""
        establecimiento_actual = ""

        with open(txt_file_path, 'r', encoding='utf-8') as file_txt:
            for line in file_txt:
                referencia_match = re.search(r'\b\d{4}A\d{8}\b', line)
                if referencia_match:
                    referencia_actual = referencia_match.group(0).replace("A", "-")
                
                fecha_match = re.search(r'\b\d{4}-\d{2}-\d{2}\b', line[35:45])
                if fecha_match:
                    fecha = fecha_match.group(0)
                    fecha_actual = f"{fecha[8:10]}{fecha[5:7]}{fecha[2:4]}"  # Formato ddmmaa

                establecimiento_raw = line[191:198].strip()
                if establecimiento_raw == "1279300":
                    establecimiento_actual = "002"
                elif establecimiento_raw == "1279084":
                    establecimiento_actual = "001"

                cab = "ZCOC1_"
                cod_proveedor = "ALSAI"
                codigo_barras = line[74:88].strip()

                # Verificar si el código de barras es válido (si no es válido, eliminar la fila)
                if not codigo_barras.isdigit():
                    continue  # Omite esta fila y pasa a la siguiente

                cantidad_raw = line[31:37].strip()
                cantidad = cantidad_raw.split(',')[0]  # Solo parte entera

                # Verificar si la cantidad es igual a 0
                if int(cantidad) == 0:
                    continue  # Omite esta fila y pasa a la siguiente

                precio = line[44:53].strip()
                almacen = "240001"  # Valor vacío por defecto
                descuento = 12

                # Escribir la fila en el archivo CSV
                writer.writerow([
                    cab,
                    referencia_actual,
                    fecha_actual,
                    cod_proveedor,
                    codigo_barras,
                    cantidad,
                    precio,
                    almacen,
                    establecimiento_actual,
                    descuento
                ])