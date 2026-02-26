from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
import os
from dotenv import load_dotenv

from tabela_verbas import selecionar_codigo
from tabela_verbas import selecionar_aliquota

load_dotenv()


def acessar_web(dados):
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico)

    driver.get("https://pmjaboticabal.smarapd.com.br/rh/#/recursoshumanos/lancamentofixo")
    driver.maximize_window()
    print("Acessando sistema SMARPD")

    # ===== Auxiliares =====
    def clicar_em_botao(xpath: str, timeout: int = 10):
        botao = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        botao.click()

    def encontrar(xpath: str, timeout: int = 10):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def preencher_data(data_input: str, xpath: str):
        campo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        dd, mm, yyyy = data_input.split("/")

        campo.click()
        campo.send_keys(Keys.CONTROL, "a", Keys.BACKSPACE)
        campo.send_keys(dd)
        campo.send_keys(mm)
        campo.send_keys(yyyy)
        time.sleep(1)
        campo.send_keys(Keys.ENTER)

    # ===== Script =====
    def realizar_login():
        print("Realizando o login na página")
        try:
            usuario_smar = os.getenv("SMAR_USER")
            senha_smar = os.getenv("SMAR_PASSWORD")

            if not usuario_smar or not senha_smar:
                raise ValueError("Credenciais não encontradas no .env (SMAR_USER / SMAR_PASSWORD)")

            usuario = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "userId"))
            )
            usuario.send_keys(usuario_smar)
            print("Usuário preenchido")

            senha = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            senha.send_keys(senha_smar)
            print("Senha preenchida")

            confirmar = "/html/body/div[3]/div/div/form/div/div[4]/div/button"
            clicar_em_botao(confirmar)

            print("Login realizado com sucesso.")
        except TimeoutException:
            print(f"Não foi possível realizar o login (ERRO: {TimeoutException})")
            raise  # propaga para o try/except do main.py

    def selecionar_unidade_gestora():
        try:
            confirmar = "/html/body/div[4]/div/form/div[3]/div/button"
            clicar_em_botao(confirmar)
        except TimeoutException:
            print(f"Não foi possível selecionar a unidade gestora (ERRO: {TimeoutException})")
            raise

    def incluir_registro():
        incluir = "/html/body/div[4]/div/div[1]/div/access-control/div/div/a[2]"
        clicar_em_botao(incluir)

        def preencher_formulario():
            # Registro funcional
            registro_funcional = encontrar(
                "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[1]/div[1]/ddados-item/ddados-suggestion/div/ng-form/div/div/div[1]/ng-form/div/div/div/input"
            )
            registro_funcional.send_keys(dados["matricula"])
            time.sleep(1)
            registro_funcional.send_keys(Keys.ENTER)

            # Verba (usa tabela_verbas.py)
            verba = encontrar(
                "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[1]/div[2]/ddados-item/ddados-suggestion/div/ng-form/div/div/div[1]/ng-form/div/div/div/input"
            )
            codigo_verba = selecionar_codigo(dados.get("inciso"))
            verba.send_keys(codigo_verba)
            time.sleep(1)
            verba.send_keys(Keys.ENTER)

            # Datas
            preencher_data(
                dados["data_deferimento"],
                "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[5]/div[1]/fieldset/div/div[2]/div[1]/div[1]/ddados-item/ddados-date/div/ng-form/div/div/div/span/span/input"
            )

            DATA_VENCIMENTO_PADRAO = "31/12/2999"
            preencher_data(
                DATA_VENCIMENTO_PADRAO,
                "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[5]/div[1]/fieldset/div/div[2]/div[2]/div[2]/ddados-item/ddados-date/div/ng-form/div/div/div/span/span/input"
            )

            # Observação (corrigido bug de aspas)
            observacao = encontrar(
                "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[6]/div/ddados-item/ddados-textarea/div/ng-form/div/div/div/textarea[1]"
            )
            observacao.send_keys(f"Conforme processo n.º {dados['numero_processo']}")
            time.sleep(1)

            # Próximo
            proximo = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div/div/div[3]/div/div[3]/button[1]"))
            )
            proximo.click()

            # Valor do lançamento (se existir no seu fluxo)
            valor_lancamento = encontrar(
                "/html/body/div[4]/div/div/div/div/div[2]/section[2]/div/div/div/div/div/form/div[1]/div[6]/ddados-item/ddados-decimal/div/ng-form/div/div/input"
            )

            valor = selecionar_aliquota(dados.get("inciso"))
            if valor is not None:
                valor_lancamento.send_keys(str(valor))

        preencher_formulario()

    try:
        realizar_login()
        selecionar_unidade_gestora()
        incluir_registro()

        print("Encerrando sistema WEB")
    finally:
        driver.quit()