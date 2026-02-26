salario = float(input("Salario base: ").strip().replace(".", "").replace(",", "."))
data_deferimento = input("Data deferimento (DD/MM/AAAA): ")
inciso = input("Inciso: ")

def calcular_retroativo(salario_base, dia_do_deferimento, inciso):
    dia_do_deferimento = int(dia_do_deferimento[0:2])
    DIAS_POR_MES = 30

    def selecionar_valor_verba(inciso):
        match inciso:
            case "I":
                return 0.020
            case "II":
                return 0.025
            case "III":
                return 0.030
            case "IV":
                return 0.040
            case "V":
                return 0.050
            case _:
                raise ValueError("Verba desconhecida")

    valor_do_adicional = selecionar_valor_verba(inciso)

    dias_para_retroagir = DIAS_POR_MES - dia_do_deferimento + 1

    valor_do_retroativo = round(salario_base / DIAS_POR_MES * valor_do_adicional * dias_para_retroagir, 2)
    return valor_do_retroativo

print(calcular_retroativo(salario, data_deferimento, inciso))