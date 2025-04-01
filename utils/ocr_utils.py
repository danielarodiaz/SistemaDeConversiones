import re
from data.ocr_database import ocr_database

# 🔁 Mapeo de variantes a nombre base
remitente_map = {
    "GRUPO 7": ["GRUPO 7", "GRUPPO 7 SA", "GRUPO7"],
    "BESTSOX": ["BESTSOX", "BEST SOX SA", "BEST SOC", "BEST SOC SA"],
    "KENYAN": ["KENYAN", "KENIA"],
    "DISTRINANDO": ["DISTRINANDO"],
    "KOKUEN": ["KOKUEN"],
    #Agregar más proveedores
}

def remitente_es_excepcion(remitente_raw):
    for variantes in remitente_map.values():
        for variante in variantes:
            if variante in remitente_raw:
                return True
    return False

def calcular_ocr_code(destinatario, localidad, domicilio, remitente=""):
    destinatario_raw = str(destinatario).upper()
    domicilio_raw = str(domicilio).upper()
    localidad_raw = str(localidad).upper()
    remitente_raw = str(remitente).upper()

    # 1️⃣ Número de 6 dígitos en destinatario
    match = re.search(r"\d{6}", destinatario_raw)
    if match:
        return f"{match.group(0)}-1"
    
    # 2️⃣ Verificar si es remitente de excepción
    es_excepcion = remitente_es_excepcion(remitente_raw)

    # 3️⃣ MARATHON o BLANCO, pero ignorar si el remitente es de excepción
    if ("MARATHON" in destinatario_raw or "BLANCO" in destinatario_raw) and not es_excepcion:
        return "240001-1"

    # 4️⃣ Inferencia por provincia
    provincia = ""
    if "ROSARIO" in localidad_raw:
        provincia = "SFE"
    elif any(p in localidad_raw for p in ["SALTA", "JVG", "GUEMES", "TARTAGAL", "METAN"]):
        provincia = "SAL"
    elif any(p in localidad_raw for p in ["TUCUMAN","S M DE TUCUMAN","S.M TUCUMAN","TAFI VIEJO", "CONCEPCION", "YERBA", "AGUILARES", "MONTEROS"]):
        provincia = "TUC"

    # Buscar coincidencia en base provincial
    if provincia and provincia in ocr_database:
        for code, keywords in ocr_database[provincia].items():
            for keyword in keywords:
                if keyword in domicilio_raw:
                    return f"{code}-1"

    # Buscar en toda la base si no se encontró antes
    for prov_data in ocr_database.values():
        for code, keywords in prov_data.items():
            for keyword in keywords:
                if keyword in domicilio_raw:
                    return f"{code}-1"


    return "240001-1"

