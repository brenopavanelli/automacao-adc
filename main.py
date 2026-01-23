from docx import Document
from datetime import datetime
from pathlib import Path
import json
import subprocess
import os

# === 1. Função para gerar a data de hoje formatada ===
def data_hoje_formatada():
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    hoje = datetime.now()
    return f"{hoje.day} de {meses[hoje.month]} de {hoje.year}"

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
competencia = input("Digite a competência: ")
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


if not config_path.exists():
    raise FileNotFoundError("Arquivo config.json não encontrado! Crie um antes de executar.")

with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

# === Caminhos dos modelos de entrada ===
modelo_informacoes = BASE_DIR / "modelos" / "entrada" / "modelo-folha-info.docx"


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
