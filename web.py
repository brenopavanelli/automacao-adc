from selenium import webdriver
from selenium.common import TimeoutException
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
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
    wait = WebDriverWait(driver, 20)

    driver.get("https://pmjaboticabal.smarapd.com.br/rh/#/recursoshumanos/lancamentofixo")
    driver.maximize_window()
    print("Acessando sistema SMARPD")

    # =========================
    # Auxiliares
    # =========================
    def esperar_pagina_estavel(timeout=20):
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def esperar_pequena_transicao(segundos=0.6):
        time.sleep(segundos)

    def esperar_overlay_sumir(timeout=10):
        """
        Tenta aguardar sumirem elementos comuns de bloqueio/overlay/loading.
        Se não existir nenhum desses seletores, apenas segue.
        """
        seletores = [
            ".blockUI",
            ".blockOverlay",
            ".loading",
            ".loading-mask",
            ".modal-backdrop",
            ".ui-widget-overlay",
            ".k-overlay",
            ".spinner",
            ".busy",
        ]

        for seletor in seletores:
            try:
                WebDriverWait(driver, 2).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, seletor))
                )
            except TimeoutException:
                pass
            except Exception:
                pass

        esperar_pequena_transicao(0.4)

    def localizar_presente(xpath: str, timeout: int = 20):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def localizar_visivel(xpath: str, timeout: int = 20):
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

    def localizar_clicavel(xpath: str, timeout: int = 20):
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

    def scroll_para_elemento(elemento):
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            elemento
        )
        esperar_pequena_transicao(0.3)

    def clicar_em_elemento(elemento):
        scroll_para_elemento(elemento)

        try:
            elemento.click()
            return
        except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException):
            pass

        try:
            driver.execute_script("arguments[0].click();", elemento)
            return
        except Exception:
            pass

        driver.execute_script("arguments[0].focus();", elemento)
        esperar_pequena_transicao(0.2)
        driver.execute_script("arguments[0].click();", elemento)

    def clicar_em_botao(xpath: str, timeout: int = 20):
        botao = localizar_clicavel(xpath, timeout)
        clicar_em_elemento(botao)

    def limpar_e_preencher_input(elemento, valor: str):
        scroll_para_elemento(elemento)
        clicar_em_elemento(elemento)

        try:
            elemento.send_keys(Keys.CONTROL, "a")
            elemento.send_keys(Keys.BACKSPACE)
        except Exception:
            pass

        try:
            elemento.clear()
        except Exception:
            pass

        try:
            driver.execute_script("arguments[0].value = '';", elemento)
        except Exception:
            pass

        esperar_pequena_transicao(0.2)
        elemento.send_keys(valor)

    def preencher_data(data_input: str, xpath: str):
        campo = localizar_visivel(xpath, 20)
        dd, mm, yyyy = data_input.split("/")

        scroll_para_elemento(campo)
        clicar_em_elemento(campo)

        try:
            campo.send_keys(Keys.CONTROL, "a")
            campo.send_keys(Keys.BACKSPACE)
        except Exception:
            pass

        campo.send_keys(dd)
        campo.send_keys(mm)
        campo.send_keys(yyyy)
        esperar_pequena_transicao(0.6)
        campo.send_keys(Keys.TAB)

    def preencher_suggestion(xpath: str, valor: str, timeout: int = 20):
        campo = localizar_visivel(xpath, timeout)
        limpar_e_preencher_input(campo, valor)
        esperar_pequena_transicao(1.0)
        campo.send_keys(Keys.ENTER)

    def preencher_decimal(xpath: str, valor):
        """
        Preenchimento robusto para campos monetários/decimais mascarados.
        """
        campo = localizar_visivel(xpath, 20)
        scroll_para_elemento(campo)

        wait.until(lambda d: campo.is_displayed() and campo.is_enabled())

        try:
            readonly = campo.get_attribute("readonly")
            disabled = campo.get_attribute("disabled")
            print(f"Campo valor -> readonly={readonly} | disabled={disabled}")
        except Exception:
            pass

        clicar_em_elemento(campo)
        esperar_pequena_transicao(0.2)

        valor_str = str(valor)

        # Tentativa 1: teclado
        try:
            campo.send_keys(Keys.CONTROL, "a")
            campo.send_keys(Keys.BACKSPACE)
            esperar_pequena_transicao(0.2)
            campo.send_keys(valor_str)
            esperar_pequena_transicao(0.3)
            campo.send_keys(Keys.TAB)
            return
        except Exception:
            pass

        # Tentativa 2: limpar + teclado
        try:
            limpar_e_preencher_input(campo, valor_str)
            esperar_pequena_transicao(0.3)
            campo.send_keys(Keys.TAB)
            return
        except Exception:
            pass

        # Tentativa 3: javascript + eventos
        driver.execute_script(
            """
            const el = arguments[0];
            const val = arguments[1];
            el.focus();
            el.value = '';
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.value = val;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.blur();
            """,
            campo,
            valor_str,
        )
        esperar_pequena_transicao(0.5)

    def avancar_para_proxima_etapa(xpath_botao_proximo: str, xpath_campo_destino: str):
        """
        Clica em Próximo e aguarda a nova etapa ficar realmente interagível.
        """
        botao = localizar_clicavel(xpath_botao_proximo, 20)
        clicar_em_elemento(botao)

        esperar_pagina_estavel()
        esperar_overlay_sumir()
        esperar_pequena_transicao(1.0)

        # Aguarda o campo da etapa seguinte existir, ficar visível e habilitado
        def campo_pronto(_driver):
            try:
                el = _driver.find_element(By.XPATH, xpath_campo_destino)
                return el.is_displayed() and el.is_enabled()
            except Exception:
                return False

        WebDriverWait(driver, 20).until(campo_pronto)
        esperar_pequena_transicao(0.5)

    # =========================
    # Script
    # =========================
    def realizar_login():
        print("Realizando login na página")
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

            esperar_pagina_estavel()
            esperar_overlay_sumir()
            print("Login realizado com sucesso.")

        except TimeoutException:
            print("Não foi possível realizar o login.")
            raise

    def selecionar_unidade_gestora():
        try:
            confirmar = "/html/body/div[4]/div/form/div[3]/div/button"
            clicar_em_botao(confirmar)
            esperar_pagina_estavel()
            esperar_overlay_sumir()
            print("Unidade gestora confirmada.")
        except TimeoutException:
            print("Não foi possível selecionar a unidade gestora.")
            raise

    def incluir_registro():
        incluir = "/html/body/div[4]/div/div[1]/div/access-control/div/div/a[2]"
        clicar_em_botao(incluir)
        esperar_pagina_estavel()
        esperar_overlay_sumir()

        def preencher_formulario():
            print("Preenchendo formulário da etapa 1...")

            # Registro funcional
            xpath_registro_funcional = "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[1]/div[1]/ddados-item/ddados-suggestion/div/ng-form/div/div/div[1]/ng-form/div/div/div/input"
            preencher_suggestion(xpath_registro_funcional, str(dados["matricula"]))

            # Verba
            xpath_verba = "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[1]/div[2]/ddados-item/ddados-suggestion/div/ng-form/div/div/div[1]/ng-form/div/div/div/input"
            codigo_verba = selecionar_codigo(dados.get("inciso"))
            preencher_suggestion(xpath_verba, str(codigo_verba))

            # Datas
            xpath_data_concessao = "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[5]/div[1]/fieldset/div/div[2]/div[1]/div[1]/ddados-item/ddados-date/div/ng-form/div/div/div/span/span/input"
            preencher_data(dados["data_deferimento"], xpath_data_concessao)

            DATA_VENCIMENTO_PADRAO = "31/12/2999"
            xpath_data_vencimento = "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[5]/div[1]/fieldset/div/div[2]/div[2]/div[2]/ddados-item/ddados-date/div/ng-form/div/div/div/span/span/input"
            preencher_data(DATA_VENCIMENTO_PADRAO, xpath_data_vencimento)

            # Observação
            xpath_observacao = "/html/body/div[4]/div/div/div/div/div[2]/section[1]/div/div/div/div/div/form/div[6]/div/ddados-item/ddados-textarea/div/ng-form/div/div/div/textarea[1]"
            observacao = localizar_visivel(xpath_observacao, 20)
            limpar_e_preencher_input(
                observacao,
                f"Conforme processo n.º {dados['numero_processo']}"
            )

            print("Avançando para etapa 2...")

            xpath_proximo = "/html/body/div[4]/div/div/div/div/div[3]/div/div[3]/button[1]"
            xpath_valor_lancamento = "/html/body/div[4]/div/div/div/div/div[2]/section[2]/div/div/div/div/div/form/div[1]/div[6]/ddados-item/ddados-decimal/div/ng-form/div/div/input"

            avancar_para_proxima_etapa(xpath_proximo, xpath_valor_lancamento)

            print("Preenchendo etapa 2...")

            valor = selecionar_aliquota(dados.get("inciso"))
            if valor is None:
                raise ValueError("Não foi possível determinar a alíquota para o inciso informado.")

            valor = valor * 1000
            preencher_decimal(xpath_valor_lancamento, valor)

            xpath_incluir_valor = "/html/body/div[4]/div/div/div/div/div[2]/section[2]/div/div/div/div/div/form/div[2]/div/button[3]"
            clicar_em_botao(xpath_incluir_valor)
            esperar_overlay_sumir()
            esperar_pequena_transicao(1.0)

            xpath_confirmar_final = "/html/body/div[4]/div/div/div/div/div[3]/div/div[2]/div/div/button"
            clicar_em_botao(xpath_confirmar_final)
            esperar_overlay_sumir()

            print("Lançamento incluído com sucesso.")

        preencher_formulario()

    try:
        realizar_login()
        selecionar_unidade_gestora()
        incluir_registro()
        print("Encerrando sistema WEB")
    finally:
        driver.quit()