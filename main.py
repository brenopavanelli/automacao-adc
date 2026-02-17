from docx import Document
from datetime import datetime
from pathlib import Path
import json
import subprocess
import os

import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# A forma mais fácil (sem precisar baixar o driver manualmente)
servico = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=servico)


def testar_web():
    driver.get("https://pmjaboticabal.smarapd.com.br/rh/#/recursoshumanos/lancamentofixo")
    driver.maximize_window()
    print("Acessando sistema SMARPD")

    def realizar_login():
        print("Realizando o login na página")
        try:
            usuario = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            usuario.send_keys("bpsantos")
            print("Usuário preenchido")

            senha = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            senha.send_keys("Cavalo13!")
            print("Senha preenchida")

            confirmar = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[3]/div/div/form/div/div[4]/div/button"))
            )
            confirmar.click()

            print("Login realizado com sucesso.")
        except TimeoutException:
            print(f"Não foi possível realizar o login (ERRO: {TimeoutException}")

    def selecionar_unidade_gestora():
        try:
            confirmar = WebDriverWait(driver, 10).until (
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/form/div[3]/div/button"))
            )
            confirmar.click()
        except TimeoutException:
            print(f"Não foi possível selecionar a unidade gestora (ERRO: {TimeoutException}")


    realizar_login()
    selecionar_unidade_gestora()

    time.sleep(10)
    print("Encerrando sistema WEB")
    driver.quit()

testar_web()

'''

# === 1. Função para gerar a data de hoje formatada ===
def data_hoje_formatada():
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    hoje = datetime.now()
    return f"{hoje.day} de {meses[hoje.month]} de {hoje.year}"

def gera_competencia(meses_passados=0):
    hoje = datetime.now()
    competencia = f"{hoje.month-meses_passados}/{hoje.year}"
    if len(competencia) == 6:
        return f"0{competencia}"
    else:
        return competencia

def classificar_mes(data_str):
    try:
        dt = datetime.strptime(data_str.strip(), "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Data inválida. Use o formato dd/mm/aaaa e uma data real (ex.: 27/01/2026).")

    hoje = datetime.today()

    if (dt.year, dt.month) == (hoje.year, hoje.month):
        return "mes atual"
    else:
        return "mes passado"

hoje = data_hoje_formatada()

# === Define o diretório base (onde está o main.py) ===
BASE_DIR = Path(__file__).resolve().parent
config_path = BASE_DIR / "config.json"

fis = input("Digite o número da folha de deferimento: ")
matricula = input("Digite a matrícula: ")
nome = input("Digite o nome do requerente: ")
cargo = input("Digite o cargo: ")
numero_processo = input("Digite o número do processo: ")
data_deferimento = input("Digite a data de deferimento: ")
competencia = gera_competencia()
inciso = input("Digite o inciso: ")

substituicoes = {
    "{{FIS}}": fis,
    "{{NOME}}": nome,
    "{{MATRICULA}}": matricula,
    "{{CARGO}}": cargo,
    "{{NUMERO_PROCESSO}}": numero_processo,
    "{{DATA_DEFERIMENTO}}": data_deferimento,
    "{{COMP}}": competencia,
    "{{HOJE}}": hoje,
    "{{INCISO}}": inciso
}

if inciso == "I" or inciso == "II":
    modelo_portaria = BASE_DIR / "modelos" / "entrada" / "modelo-folha-portaria.docx"
else:
    modelo_portaria = BASE_DIR / "modelos" / "entrada" / "modelo-folha-portaria-com-grupo.docx"
    grupo = input("Digite o grupo: ")
    substituicoes["{{GRUPO}}"] = grupo

mes_do_deferimento = classificar_mes(data_deferimento)
if mes_do_deferimento == 'mes atual':
    modelo_informacoes = BASE_DIR / "modelos" / "entrada" / "modelo-folha-info2.docx"
else:
    modelo_informacoes = BASE_DIR / "modelos" / "entrada" / "modelo-folha-info-retroativo.docx"
    valor_do_retroativo = input("Digite o valor do retroativo a ser pago: ")
    substituicoes["{{COMPETENCIA_ANTERIOR}} "] = gera_competencia(1)
    substituicoes["{{VALOR}}"] = valor_do_retroativo

if not config_path.exists():
    raise FileNotFoundError("Arquivo config.json não encontrado! Crie um antes de executar.")

with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

# Paths de saída vindos do arquivo externo
saida_informacoes_dir = Path(config["saida_informacoes"])
saida_portaria_dir = Path(config["saida_portaria"])

# Garante que as pastas existem
saida_informacoes_dir.mkdir(parents=True, exist_ok=True)
saida_portaria_dir.mkdir(parents=True, exist_ok=True)

# Gera caminhos finais dos arquivos
saida_informacoes = saida_informacoes_dir / f"Adicional Conclusão de Curso - {nome}.docx"
saida_portaria = saida_portaria_dir / f"Adicional por Conclusão de Curso - {nome}.docx"


# === 5. Função de substituição ===
def substituir_texto(paragrafo, mapa):
    if not paragrafo.runs:
        return

    texto_original = "".join(run.text for run in paragrafo.runs)
    texto_novo = texto_original

    for chave, valor in mapa.items():
        texto_novo = texto_novo.replace(chave, str(valor))

    if texto_novo != texto_original:
        # coloca tudo no primeiro run e apaga o resto
        paragrafo.runs[0].text = texto_novo
        for run in paragrafo.runs[1:]:
            run.text = ""



def aplicar_substituicoes(caminho_modelo, caminho_saida, mapa):
    """Abre o modelo, substitui e salva o resultado."""
    doc = Document(caminho_modelo)

    # Substitui em parágrafos
    for paragrafo in doc.paragraphs:
        substituir_texto(paragrafo, mapa)

    # Substitui em tabelas (caso existam)
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for paragrafo in celula.paragraphs:
                    substituir_texto(paragrafo, mapa)

    # Salva o arquivo final
    doc.save(caminho_saida)


aplicar_substituicoes(modelo_informacoes, saida_informacoes, substituicoes)
aplicar_substituicoes(modelo_portaria, saida_portaria, substituicoes)

def abrir_no_libreoffice(caminho_arquivo):
    """
    Abre um arquivo usando o LibreOffice em uma nova janela.
    Compatível com Windows.
    """
    possiveis_caminhos = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]

    soffice = None
    for caminho in possiveis_caminhos:
        if os.path.exists(caminho):
            soffice = caminho
            break

    if soffice is None:
        raise FileNotFoundError("❌ LibreOffice não encontrado no sistema.")

    subprocess.Popen([soffice, caminho_arquivo])

abrir_no_libreoffice(str(saida_informacoes))
abrir_no_libreoffice(str(saida_portaria))


print("\n✅ Documentos gerados com sucesso!")
print(f"📄 {saida_informacoes}")
print(f"📄 {saida_portaria}")
'''