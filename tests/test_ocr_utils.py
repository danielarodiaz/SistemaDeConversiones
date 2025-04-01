import pytest
from utils.ocr_utils import calcular_ocr_code

def test_numero_en_destinarario_tomar_ese_numero():
    result = calcular_ocr_code("200106ROSARIO 1","ROSARIO","PORTAL","DEPORTES ANTONIO BLANCO SA")
    assert result == "200106-1"

def test_remitente_especial_ignora_destinarario_revisa_provincia():
    result = calcular_ocr_code("MARATHON SRL","TAFI VIEJO","AV LEANDRO ALEM","GRUPPO 7 SA")
    assert result == "240601-1"
    
def test_destinatario_no_tiene_numero_ni_es_remitente_excepcional_ni_destinarario_bases_revisa_provincia():
    result = calcular_ocr_code("ROSARIO 1","ROSARIO","PORTAL","DEPORTES ANTONIO BLANCO SA")
    assert result == "200106-1"
    
def test_destinatario_no_tiene_numero_ni_es_remitente_excepcional_ni_destinarario_bases_ni_coincide_con_la_bd_de_sucursales():
    result = calcular_ocr_code("BARROS ROBERTO DANIEL","BERAZATEGUI","COLECTORA RUTA 2","MARATHON SRL")
    assert result == "240001-1"