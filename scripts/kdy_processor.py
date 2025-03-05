import pandas as pd

def process_xlsx_to_transformed_csv_kdy(input_path, output_folder):
    try:
        data = pd.read_excel(input_path)
        
        transformed_data = []
        
        for _, row in data.iterrows():
            try:
                fecha_str = pd.to_datetime(row['Fecha'], dayfirst=True).strftime('%d%m%y')
                
                referencia = str(row['Remito']).strip().zfill(12)  # Asegura que tenga al menos 12 dígitos con ceros a la izquierda
                referencia_formateada = referencia[:4] + '-' + referencia[4:]  # Separa los primeros 4 dígitos con un guion

                codigo_barras = str(row['EAN']).strip().replace('/','-')
                
                cantidad = int(row['Cantidad'])
                
                precio = f"{float(row['PreUni']):.2f}".replace('.', ',') #El precio siempre tendra dos decimales
                
                establecimiento = '002' if row['Empresa'] == 'MARATHON S.R.L' else '001'
                
                almacen = str(row['Suc']).strip().zfill(6)
                
                transformed_row = {
                    "CAB": "ZCOC1_",
                    "REFERENCIA INTERNA": referencia_formateada,
                    "FECHA": fecha_str,
                    "COD PROVEEDOR": "KENYA",
                    "CODIGO BARRAS": codigo_barras,
                    "CANTIDAD": cantidad,
                    "PRECIO": precio,
                    "ALMACEN": almacen,
                    "ESTABLECIMIENTO": establecimiento,
                    "DESCUENTO": 10,
                }
                transformed_data.append(transformed_row)
            except Exception as e:
                print(f"Error procesando fila: {e}")
                
        if transformed_data:
            transformed_df = pd.DataFrame(transformed_data)
            transformed_df.to_csv(output_folder, index=False, sep="|", encoding="utf-8-sig")
            print(f"Archivo generado correctamente en: {output_folder}")
        else:
            print("No se generaron datos válidos para exportar.")
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        raise RuntimeError(f"Error al procesar el archivo: {e}")
        
        
                
                
                              
                
                
            
            