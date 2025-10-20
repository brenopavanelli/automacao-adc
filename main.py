from docx import Document
from datetime import datetime
from pathlib import Path

# === 1. Função para gerar a data de hoje formatada ===
def data_hoje_formatada():
    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    hoje = datetime.now()
    return f"{hoje.day} de {meses[hoje.month]} de {hoje.year}"

# === 2. Coleta de dados pelo terminal ===
fis = input("Digite o número da folha de deferimento (FIS): ")
nome = input("Digite o nome do requerente (NOME): ")
matricula = input("Digite a matrícula (MATRICULA): ")
cargo = input("Digite o cargo (CARGO): ")
inciso = input("Digite o inciso (INCISO): ")
grupo = input("Digite o grupo (GRUPO): ")
numero_processo = input("Digite o número do processo (NUMERO_PROCESSO): ")
data_deferimento = input("Digite a data de deferimento (DATA_DEFERIMENTO): ")
competencia = input("Digite a competência (COMPETENCIA): ")

hoje = data_hoje_formatada()

# === 3. Mapeamento dos placeholders e valores ===
substituicoes = {
    "{{FIS}}": fis,
    "{{NOME}}": nome,
    "{{MATRICULA}}": matricula,
    "{{CARGO}}": cargo,
    "{{INCISO}}": inciso,
    "{{GRUPO}}": grupo,
    "{{NUMERO_PROCESSO}}": numero_processo,
    "{{DATA_DEFERIMENTO}}": data_deferimento,
    "{{COMP}}": competencia,
    "{{HOJE}}": hoje
}

# === Define o diretório base (onde está o main.py) ===
BASE_DIR = Path(__file__).resolve().parent

# === Caminhos dos modelos de entrada ===
modelo_informacoes = BASE_DIR / "modelos" / "entrada" / "modelo-folha-info.docx"
modelo_portaria = BASE_DIR / "modelos" / "entrada" / "modelo-folha-portaria.docx"

# === Diretório de saída ===
saida_dir = BASE_DIR / "modelos" / "saida"
saida_dir.mkdir(parents=True, exist_ok=True)  # cria a pasta caso não exista

# === Caminhos dos arquivos de saída ===
saida_informacoes = saida_dir / f"Adicional por Conclusão de Curso - {nome}.docx"
saida_portaria = saida_dir / f"Adicional Conclusão de Curso - {nome}.docx"


# === 5. Função de substituição ===
def substituir_texto(paragrafo, mapa):
    for chave, valor in mapa.items():
        if chave in paragrafo.text:
            for run in paragrafo.runs:
                if chave in run.text:
                    run.text = run.text.replace(chave, valor)

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

# === 6. Gera ambos os documentos ===
aplicar_substituicoes(modelo_informacoes, saida_informacoes, substituicoes)
aplicar_substituicoes(modelo_portaria, saida_portaria, substituicoes)

# === 7. Exibe confirmação ===
print("\n✅ Documentos gerados com sucesso!")
print(f"📄 {saida_informacoes}")
print(f"📄 {saida_portaria}")
