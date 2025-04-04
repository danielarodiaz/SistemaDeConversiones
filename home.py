from flask import Flask, render_template, request, redirect, flash, url_for, send_file
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from collections import defaultdict
from scripts import (
    process_txt_to_csv,
    process_csv_to_transformed_file,
    process_xlsx_to_csv,
    process_xlsx_to_transformed_csv,
    process_xlsx_to_transformed_csv_saucony,
    process_xlsx_to_transformed_csv_kdy,
    process_csv_to_transformed_sevillanita,
)  # Agregar otros procesadores aquí

app = Flask(__name__)
app.config.from_object("config")

# Diccionario de proveedores y funciones asociadas
PROVIDERS = {
    "topper": {
        "processor": process_txt_to_csv,  # Llama directamente a la función
        "title": "Topper - Conversor de TXT a CSV",
        "logo": "img/logo_topper.png",
        "label": "Subir archivo .txt",
        "file_type": ".txt",
    },
    "puma": {
        "processor": process_csv_to_transformed_file,
        "title": "Puma - Conversor de CSV a CSV",
        "logo": "img/logo_puma.png",
        "label": "Subir archivo .csv",
        "file_type": ".csv",
    },
    "bestsox": {
        "processor": process_xlsx_to_csv,
        "title": "BestSox - Conversor de XLSX a CSV",
        "logo": "img/logo_bestsox.png",
        "label": "Subir archivo .xlsx",
        "file_type": ".xlsx",
    },
    "diadora":{
        "processor": process_xlsx_to_transformed_csv,
        "title": "G7 Diadora - Conversor de XLSX a CSV",
        "logo": "img/logo_diadora.png",
        "label": "Subir archivo .xlsx",
        "file_type": ".xlsx",
    },
    "saucony":{
        "processor": process_xlsx_to_transformed_csv_saucony,
        "title": "Suola Saucony - Conversor de XLSX a CSV",
        "logo": "img/logo_saucony.png",
        "label": "Subir archivo .xlsx",
        "file_type": ".xlsx",
    },
    "kdy":{
        "processor": process_xlsx_to_transformed_csv_kdy,
        "title": "Kenyan KDY - Conversor de XLSX a CSV",
        "logo": "img/logo_kdy.png",
        "label": "Subir archivo .xlsx",
        "file_type": ".xlsx",
    },
    "sevillanita":{
        "processor": process_csv_to_transformed_sevillanita,
        "title": "Sevillanita - Conversor de CSV a CSV",
        "logo": "img/logo_sevillanita.png",
        "label": "Subir archivo .csv",
        "file_type": ".csv",  
    },
    # Agregar más proveedores aquí...
}


@app.route("/")
def index():
    """Página principal."""
    current_year = datetime.now().year
    return render_template("index.html", providers=PROVIDERS, current_year=current_year)

@app.route("/download/<filename>")
def download_file(filename):
    """Forza la descarga del archivo en el navegador del usuario."""
    file_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)

@app.route("/<provider>", methods=["GET", "POST"])
def handle_provider(provider):
    """Maneja la lógica de cada proveedor."""
    if provider not in PROVIDERS:
        flash("Proveedor no reconocido.")
        return redirect(url_for("index"))

    provider_config = PROVIDERS[provider]
    file_type = provider_config.get("file_type", ".txt")  # Por defecto, acepta '.txt'

    if request.method == "GET":
        # Renderizar plantilla del proveedor con datos dinámicos
        return render_template(
            "provider.html", provider=provider, config=provider_config
        )

    if request.method == "POST":
        # Subir y procesar archivo
        file = request.files.get("file")
        
        # Normalizar extensión a minúscula para evitar rechazos por .CSV vs .csv (type of file in general)
        file_name = secure_filename(file.filename)
        base, ext = os.path.splitext(file_name)
        file_name = base + ext.lower()  # convierte .CSV → .csv

        if not file or not file_name.endswith(file_type):
            flash(
                f"Formato de archivo inválido. Por favor, suba un archivo {file_type}"
            )
            return redirect(url_for("handle_provider", provider=provider))
        
        # Guardar archivo
        upload_folder = os.path.join(app.config["UPLOAD_FOLDER"], provider)
        os.makedirs(upload_folder, exist_ok=True)
        input_path = os.path.join(upload_folder, file_name)
        file.save(input_path)

        # Procesar archivo
        current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        output_file_name = f"{provider.upper()}_{current_time}.csv"
        output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_file_name)


        # Depuración: Verificar rutas
        print(f"Ruta de entrada: {input_path}")
        print(f"Ruta de salida: {output_path}")

        processor = provider_config["processor"]
        
         # 🔹 Si el proveedor es "sevillanita", manejar múltiples archivos
        if provider == "sevillanita":
            zip_file_path = processor(input_path, output_path)
            zip_file_name = os.path.basename(zip_file_path)

            # Detectar si se generaron archivos para MARATHON y/o BLANCO
            grupos_presentes = []
            if os.path.exists(output_path.replace(".csv", "_CABECERA_marathon.csv")):
                grupos_presentes.append("MARATHON")
            if os.path.exists(output_path.replace(".csv", "_CABECERA_blanco.csv")):
                grupos_presentes.append("BLANCO")

            # Construir mensaje compacto
            grupos_str = " & ".join(grupos_presentes) if grupos_presentes else "Sin grupo"
            msg = f"Guias de: {grupos_str} - Se descargará un ZIP automáticamente: <strong>{zip_file_name}</strong>"

            flash(msg, "success")
            return redirect(url_for("handle_provider", provider=provider, filename=zip_file_name))

        else:
            # Procesamiento normal para los otros proveedores
            processor(input_path, output_path)  # Ejecuta la función directamente
            flash(f"Archivo transformado y guardado como: <strong>{output_file_name}</strong>", "success")
            return redirect(url_for("handle_provider", provider=provider, filename=output_file_name))
            #return redirect(url_for('download_file', filename=output_file_name))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
