from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time
import sys


def acessar_web(dados):
    servico = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servico)
    driver.get("https://pmjaboticabal.smarapd.com.br/rh/#/recursoshumanos/lancamentofixo")
    driver.maximize_window()
    print("Acessando sistema SMARPD")

    # Auxiliares
    def clicar_em_botao(xpath):
        botao = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        botao.click()

    # Script
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

            confirmar = "/html/body/div[3]/div/div/form/div/div[4]/div/button"
            clicar_em_botao(confirmar)

            print("Login realizado com sucesso.")
        except TimeoutException:
            print(f"Não foi possível realizar o login (ERRO: {TimeoutException}")

    def selecionar_unidade_gestora():
        try:
            confirmar = "/html/body/div[4]/div/form/div[3]/div/button"
            clicar_em_botao(confirmar)
        except TimeoutException:
            print(f"Não foi possível selecionar a unidade gestora (ERRO: {TimeoutException}")

    def incluir_registro():
        incluir = "/html/body/div[4]/div/div[1]/div/access-control/div/div/a[2]"
        clicar_em_botao(incluir)

        def preencher_formulario():
            def preencher_dados():
                registro_funcional = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[1]/div[1]/ddados-item/ddados-suggestion/div/ng-form/div/div/div[1]/ng-form/div/div/div/input"))
                )
                registro_funcional.send_keys(dados["matricula"])
                time.sleep(1)
                registro_funcional.send_keys(Keys.ENTER)

                verba = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[1]/div[2]/ddados-item/ddados-suggestion/div/ng-form/div/div/div[1]/ng-form/div/div/div/input"))
                )
                def selecionar_valor_verba(status):
                    match status:
                        case "I":
                            return "108"
                        case "II":
                            return "1120"
                        case "III":
                            return "109"
                        case "IV":
                            return "110"
                        case "V":
                            return "111"
                        case _:  # The wildcard '_' acts as a default case
                            print("ERRO: Verba Desconhecida, encerrando sistema.")
                            sys.exit(1)
                verba.send_keys(selecionar_valor_verba(dados.get("inciso")))
                time.sleep(1)
                verba.send_keys(Keys.ENTER)

            preencher_dados()

        preencher_formulario()

    realizar_login()
    selecionar_unidade_gestora()
    incluir_registro()

    time.sleep(10)
    print("Encerrando sistema WEB")
    driver.quit()
