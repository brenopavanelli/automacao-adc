VERBAS = {
    "I":   {"aliquota": 0.020, "codigo": "108"},
    "II":  {"aliquota": 0.025, "codigo": "1120"},
    "III": {"aliquota": 0.030, "codigo": "109"},
    "IV":  {"aliquota": 0.040, "codigo": "110"},
    "V":   {"aliquota": 0.050, "codigo": "111"},
}

def normalizar_inciso(inciso: str) -> str:
    if inciso is None:
        raise ValueError("Inciso não pode ser None")
    return str(inciso).strip().upper()

def verba_por_inciso(inciso: str) -> dict:
    inciso = normalizar_inciso(inciso)
    try:
        return VERBAS[inciso]
    except KeyError:
        raise ValueError(f"Verba desconhecida: {inciso!r}")

def selecionar_aliquota(inciso: str) -> float:
    return verba_por_inciso(inciso)["aliquota"]

def selecionar_codigo(inciso: str) -> str:
    return verba_por_inciso(inciso)["codigo"]