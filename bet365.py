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


# Função para obter o dataframe a partir da página
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


# Função para recarregar a página
def refresh_page():
    print('Pagina atualizada')
    driver.get("https://www.bet365.com/#/IP/B1")


# Função para enviar uma mensagem para o Telegram
def send_telegram_message(bot, chat_id, message):
    bot.sendMessage(chat_id, message)


add_printer(1)

# Configurar o token do seu bot do Telegram

# Dados usuario
telegram_token = '6245366890:AAE0O3-Xdrvw5BnTgitnOcwnj81mjVk-kpI'
chat_id = '-1001964302283'
chat_id_private = '5497673724'

# Dados tecnico
# telegram_token = '6528253723:AAGCoqDVA4XnInPhRZGYJkZsrBSPP5Ra-Tw'
# chat_id = '1431057250'

# Inicializar o cliente Telepot
bot = telepot.Bot(telegram_token)

# Cache com expiração de 60 minutos
equipe_combinacoes_cache = TTLCache(maxsize=1000, ttl=3600)

driver = Driver(uc=True)
driver.get("https://www.bet365.com/#/IP/B1")

df = obter_dataframe()
try:
    df.loc[df.aa_classList.str.contains('iip-IntroductoryPopup_Cross', regex=False, na=False)].se_click.iloc[0]()
except Exception as e:
    refresh_page()
    df = obter_dataframe()
    df.loc[df.aa_classList.str.contains('iip-IntroductoryPopup_Cross', regex=False, na=False)].se_click.iloc[0]()
    time.sleep(1)
    df.loc[df.aa_classList.str.contains(
        'ccm-CookieConsentPopup_Accept', regex=False, na=False)].se_click.iloc[0]()

time.sleep(1)
df.loc[df.aa_classList.str.contains(
    'ccm-CookieConsentPopup_Accept', regex=False, na=False)].se_click.iloc[0]()

# Agendar a função de recarregar a página a cada 30 minutos
schedule.every(5).minutes.do(refresh_page)

times_red = pd.DataFrame(
    columns=['Equipe 1', 'Equipe 2', 'Placar 1', 'Placar 2', 'Id mensagem', 'Texto', 'Vantagem'])

while True:
    try:
        if driver.find_element(By.CLASS_NAME, "ovm-Fixture_Container"):
            df3 = obter_dataframe(query='div.ovm-Fixture_Container')
        else:

            df3 = pd.DataFrame()

        df_final = df3.loc[df3.aa_innerText.str.split('\n').str[2:].apply(
            lambda x: True if re.match(r'^[\d:]+Ç\d+Ç\d+Ç\d+Ç[\d.]+Ç[\d.]', 'Ç'.join(x)) else False)
        ].aa_innerText.str.split(
            '\n').apply(pd.Series).reset_index(drop=True)

        df_final_end = df3.loc[df3.aa_innerText.str.split('\n').str[2:].apply(
            lambda x: True if re.match(r'^90:00', 'Ç'.join(x)) else False)
        ].aa_innerText.str.split(
            '\n').apply(pd.Series).reset_index(drop=True)

        df_dados = pd.DataFrame(
            columns=['Equipe 1', 'Equipe 2', 'Tempo', '-', 'Placar 1', 'Placar 2', 'Odds 1', 'Odds 2', 'Odds 3'])

        for i in range(len(df_final)):
            # Condição 1: Verifique se o nome das equipes não termina com "Esports"
            # Condição 2: Verifique se o tempo é 78:00 ou mais
            # Condição 3: Calcule a diferença entre os placares e verifique se é 2 ou -2
            # Condição 4: Verifique se o menor valor entre as três Odds é maior ou igual a 1008,0
            # Condição 4: Verifique se o menor valor entre as três Odds dividido pélo maior valor é
            # menor ou igual a 0,0153731343283582
            if (
                    not df_final[0][i].endswith('Esports') and
                    not df_final[1][i].endswith('Esports') and
                    int(df_final[2][i].split(':')[0]) >= 78 and
                    int(abs(int(df_final[4][i]) - int(df_final[5][i]))) == 2 and
                    min(float(df_final[6][i]), float(df_final[7][i]), float(df_final[8][i])) >= 1.008 and
                    (min(float(df_final[6][i]), float(df_final[7][i]), float(df_final[8][i])) /
                    max(float(df_final[6][i]), float(df_final[7][i]), float(df_final[8][i])) <= 0.0153731343283582)
            ):
                equipe_combinacao = f'{df_final[0][i]} vs {df_final[1][i]}'

                # Verifique se a combinação já está no cache

                if equipe_combinacao not in equipe_combinacoes_cache:
                    jogos = df_final.loc[[i]]
                    jogos.columns = ['Equipe 1', 'Equipe 2', 'Tempo', '-', 'Placar 1', 'Placar 2', 'Odds 1', 'Odds 2',
                                     'Odds 3']

                    df_dados = pd.concat([df_dados, jogos], axis=0)

                    # Adicione a combinação ao cache com expiração de 60 minutos
                    equipe_combinacoes_cache[equipe_combinacao] = True

        if not df_dados.empty:
            for i in range(len(df_dados)):
                message = f'Partida {i + 1}:\n'
                message += f'Equipe 1: {df_dados.iloc[i, 0]}\n' \
                           f'Equipe 2: {df_dados.iloc[i, 1]}\n' \
                           f'Tempo: {df_dados.iloc[i, 2]}\n' \
                           f'Placar 1: {df_dados.iloc[i, 4]}\n' \
                           f'Placar 2: {df_dados.iloc[i, 5]}\n' \
                           f'Odds 1: {df_dados.iloc[i, 6]}\n' \
                           f'Odds 2: {df_dados.iloc[i, 7]}\n' \
                           f'Odds 3: {df_dados.iloc[i, 8]}\n\n'

                id_mensagem = bot.sendMessage(chat_id, message)

                if df_dados.iloc[i, 4] > df_dados.iloc[i, 5]:
                    time_vantagem = 'Equipe 1'

                if df_dados.iloc[i, 5] > df_dados.iloc[i, 4]:
                    time_vantagem = 'Equipe 2'
                else:
                    time_vantagem = 'Nenhum'

                nova_linha = pd.DataFrame([[df_dados.iloc[i, 0], df_dados.iloc[i, 1], df_dados.iloc[i, 4],
                                            df_dados.iloc[i, 5], id_mensagem, message, time_vantagem]])
                nova_linha.columns = ['Equipe 1', 'Equipe 2', 'Placar 1', 'Placar 2', 'Id mensagem', 'Texto',
                                      'Vantagem']
                if not nova_linha.empty:
                    for i in range(len(nova_linha)):
                        if not nova_linha['Equipe 1'][i] in times_red['Equipe 1']:
                            times_red = pd.concat([times_red, nova_linha], axis=0)
                times_red.columns = ['Equipe 1', 'Equipe 2', 'Placar 1', 'Placar 2', 'Id mensagem', 'Texto', 'Vantagem']

        if not df_final_end.empty:
            for i in range(len(df_final_end)):

                equipe1_contem = df_final_end[0][i] in times_red['Equipe 1'].values
                equipe2_contem = df_final_end[1][i] in times_red['Equipe 2'].values

                if not times_red.empty:
                    try:
                        equipe1_a_procurar = df_final_end[0][i]
                        linha_correspondente = times_red[times_red['Equipe 1'] == equipe1_a_procurar]
                        valor_correspondente = linha_correspondente.iloc[0, 6]

                        equipe1_vantagem = valor_correspondente == 'Equipe 1' and int(df_final_end[4][i]) <= int(
                            df_final_end[5][i])

                        equipe2_vantagem = valor_correspondente == 'Equipe 2' and int(df_final_end[5][i]) <= int(
                            df_final_end[4][i])
                    except:
                        equipe1_vantagem = False
                        equipe2_vantagem = False
                else:
                    equipe1_vantagem = False
                    equipe2_vantagem = False

                if equipe1_contem and equipe2_contem and (equipe1_vantagem or equipe2_vantagem):
                    bot.editMessageText((int(chat_id),
                                         times_red.loc[
                                             times_red['Equipe 1'] == df_final_end[0][i], 'Id mensagem'].values[0][
                                             'message_id']),
                                        times_red.loc[times_red['Equipe 1'] == df_final_end[0][i], 'Texto'].values[
                                            0] + 'red❌')
                    times_red = times_red[
                        ~((times_red['Equipe 1'] == df_final_end[0][i]) & (
                                times_red['Equipe 2'] == df_final_end[1][i]))]

        # Verificar se há tarefas agendadas
        schedule.run_pending()

        # Coloque um atraso entre as verificações
        # print('------df_dados:-----')
        # print(df_dados)
        # print('------df_final_end:-----')
        # print(df_final_end)
        # print('------times_red:-----')
        # print(times_red)

        time.sleep(3.1)

    except Exception as e:
        refresh_page()
        print(e)
        error_message = f"Ocorreu um erro: {str(e)}"
        send_telegram_message(bot, 5497673724, error_message)
