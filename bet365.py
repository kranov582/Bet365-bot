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
telegram_token = ''
chat_id = ''
chat_id_private = ''

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
# schedule.every(5).minutes.do(refresh_page)

times_red = pd.DataFrame(
    columns=['Equipe 1', 'Equipe 2', 'Placar 1', 'Placar 2', 'Id mensagem', 'Texto', 'Vantagem'])

data_verification = pd.DataFrame(
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
                    min(float(df_final[6][i]), float(df_final[7][i]), float(df_final[8][i])) >= 1.002
                    # (min(float(df_final[6][i]), float(df_final[7][i]), float(df_final[8][i])) /
                    # max(float(df_final[6][i]), float(df_final[7][i]), float(df_final[8][i])) <= 0.0153731343283582)
            ):
                equipe_combinacao = f'{df_final[0][i]} vs {df_final[1][i]}'

                jogos = df_final.loc[[i]]
                jogos.columns = ['Equipe 1', 'Equipe 2', 'Tempo', '-', 'Placar 1', 'Placar 2', 'Odds 1', 'Odds 2',
                                 'Odds 3']

                data_verification = pd.concat([data_verification, jogos], axis=0)
                data_verification = data_verification.drop_duplicates(
                    subset=['Equipe 1', 'Equipe 2', 'Placar 1', 'Placar 2']
                    , keep='first')

                # Verifique se a combinação já está no cache
                if equipe_combinacao not in equipe_combinacoes_cache:
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

        if not data_verification.empty:
            for i in range(len(data_verification)):

                equipe1_contem = data_verification.iloc[i, 0] in times_red['Equipe 1'].values
                equipe2_contem = data_verification.iloc[i, 1] in times_red['Equipe 2'].values

                equipe1_a_procurar = data_verification.iloc[i, 0]
                equipe2_a_procurar = data_verification.iloc[i, 1]
                linha_correspondente1 = data_verification[data_verification['Equipe 1'] == equipe1_a_procurar]
                linha_correspondente2 = data_verification[data_verification['Equipe 2'] == equipe2_a_procurar]
                # linha_correspondente1_times_red = times_red[times_red['Equipe 1'] == equipe1_a_procurar]
                # linha_correspondente2_times_red = times_red[times_red['Equipe 1'] == equipe1_a_procurar]

                if len(linha_correspondente1) > 1:
                    valor_correspondente1 = linha_correspondente1.iloc[-1, 2]
                    valor_correspondente1_old = linha_correspondente1.iloc[-2, 2]

                    valor_correspondente2 = linha_correspondente1.iloc[-1, 3]
                    valor_correspondente2_old = linha_correspondente1.iloc[-2, 3]
                else:
                    valor_correspondente1 = linha_correspondente1.iloc[0, 2]
                    valor_correspondente1_old = valor_correspondente1

                    valor_correspondente2 = linha_correspondente1.iloc[0, 3]
                    valor_correspondente2_old = valor_correspondente2

                equipe1_marcou = valor_correspondente1 > valor_correspondente1_old
                equipe2_marcou = valor_correspondente2 > valor_correspondente2_old

                new_line = pd.DataFrame({'Equipe 1': equipe1_a_procurar, 'Equipe 2': equipe2_a_procurar,
                                         'Placar 1 antigo': [valor_correspondente1],
                                         'Placar 2 antigo': [valor_correspondente2],
                                         'Placar 1 novo': [valor_correspondente1_old],
                                         'Placar 2 novo': [valor_correspondente2_old],
                                         'Equipe 1 marcou': equipe1_marcou, 'Equipe 2 marcou': equipe2_marcou})

                if equipe1_contem and equipe2_contem and (equipe1_marcou or equipe2_marcou):
                    bot.editMessageText((int(chat_id),
                                         times_red.loc[
                                             times_red['Equipe 1'] == data_verification.iloc[
                                                 i, 0], 'Id mensagem'].values[0][
                                             'message_id']),
                                        times_red.loc[
                                            times_red['Equipe 1'] == data_verification.iloc[i, 0], 'Texto'].values[
                                            0] + f'Novo placar : {valor_correspondente1} a {valor_correspondente2}')

                    data_verification = data_verification.drop_duplicates(
                        subset=['Equipe 1', 'Equipe 2']
                        , keep='last')

        # Verificar se há tarefas agendadas
        # schedule.run_pending()

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
