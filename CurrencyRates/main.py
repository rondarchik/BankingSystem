import os
import requests
import psycopg2
import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def create_exchanges(conn, cur, from_currency, to_currency):
    currency_name = get_currency_name(conn, cur, to_currency)

    insert_query = """
        INSERT INTO public."CurrencyRates" (from_currency_id, to_currency_id, rate, scale, date) 
            VALUES (%s, %s, %s, %s, %s);
    """

    if currency_name == 'RUB':
        cur.execute(insert_query, (from_currency, to_currency, 0, 100, datetime.datetime.now()))
    else:
        cur.execute(insert_query, (from_currency, to_currency, 0, 1, datetime.datetime.now()))

    conn.commit()


def get_currency_name(conn, cur, currency_id):
    get_target_currency = """
        SELECT currency_name FROM public."Currencies" WHERE id=%s;
    """

    cur.execute(get_target_currency, (currency_id, ))
    return cur.fetchone()[0]


def update_exchange_rate(conn, cur, from_currency, to_currency):
    url = "https://bankdabrabyt.by/export_courses.php"
    response = requests.get(url)
    data = BeautifulSoup(response.text, 'xml')
    last_date = data.find('time').text
    last_date = datetime.datetime.strptime(last_date, '%d.%m.%Y %H:%M')
    data = data.find('filial', {'name': 'Центральный офис'})

    update_query = """
        UPDATE public."CurrencyRates" SET rate=%s, date=%s
            WHERE from_currency_id=%s AND to_currency_id=%s;
    """

    from_currency_name = get_currency_name(conn, cur, from_currency)
    to_currency_name = get_currency_name(conn, cur, to_currency)

    if from_currency_name == 'BYN':
        rate = data.find('value', {'iso': f'{to_currency_name}'}).get('sale')
    elif to_currency_name == 'BYN':
        rate = data.find('value', {'iso': f'{from_currency_name}'}).get('buy')
    elif from_currency_name == 'USD':
        rate = data.find('value', {'iso': f'{from_currency_name}/{to_currency_name}'}).get('sale')
    elif to_currency_name == 'USD':
        rate = data.find('value', {'iso': f'{to_currency_name}/{from_currency_name}'}).get('buy')
    elif from_currency_name == 'EUR':
        rate = data.find('value', {'iso': f'{from_currency_name}/{to_currency_name}'}).get('sale')
    elif to_currency_name == 'EUR':
        rate = data.find('value', {'iso': f'{to_currency_name}/{from_currency_name}'}).get('buy')

    cur.execute(update_query, (rate, last_date, from_currency, to_currency))
    conn.commit()


def update_rates():
    conn = psycopg2.connect(
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PW"),
        host=os.getenv("POSTGRES_URL")
    )
    cur = conn.cursor()

    select_currencies_query = """
        SELECT id, currency_name FROM public."Currencies";
    """
    cur.execute(select_currencies_query)
    res = cur.fetchall()

    currencies = {}
    for item in res:
        currencies[item[1]] = item[0]

    currency_names = [str(res[i][1]) for i in range(len(res))]

    # вызывается только единожды
    # for cur1 in currency_names:
    #     for cur2 in currency_names:
    #         if cur1 != cur2:
    #             create_exchanges(conn, cur, currencies[cur1], currencies[cur2])

    for cur1 in currency_names:
        for cur2 in currency_names:
            if cur1 != cur2:
                update_exchange_rate(conn, cur, currencies[cur1], currencies[cur2])

    cur.close()
    conn.close()


if __name__ == '__main__':
    update_rates()

