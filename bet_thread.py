import re
from seleniumbase import Driver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from a_selenium2df import get_df
from PrettyColorPrinter import add_printer
import telepot
import time
from cachetools import TTLCache
import schedule
import threading  # Importe a biblioteca threading


def obter_dataframe(query='*'):
    df = pd.DataFrame()
    while df.empty:
        df = get_df(
            driver,
            By,
            WebDriverWait,
            expected_conditions,
            queryselector=query,
            with_methods=True,
        )
    return df


driver = Driver(uc=True)
driver.get("https://www.bet365.com/#/IP/B1")

df = obter_dataframe()
df.loc[df.aa_classList.str.contains('iip-IntroductoryPopup_Cross', regex=False, na=False)].se_click.iloc[0]()
time.sleep(1)
df.loc[df.aa_classList.str.contains(
    'ccm-CookieConsentPopup_Accept', regex=False, na=False)].se_click.iloc[0]()

while True:
    try:
        # Verifique se a div com ID 'ovm-Fixture_Container' está presente na página
        fixture_container = driver.find_element(By.CLASS_NAME, "ovm-Fixture_Container")
        print("A div 'ovm-Fixture_Container' existe na página")
    except Exception as e:
        print("A div 'ovm-Fixture_Container' não existe na página")

    # Adicione um intervalo de tempo antes de verificar novamente
    time.sleep(30)  # Verificar a cada 60 segundos
