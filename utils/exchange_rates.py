import requests


def get_value(content, currency: str):
    """Получить значение определенной валюты из курсов обмена ЦБ РФ."""
    return round(content["Valute"][currency]["Value"], 2)

def get_exchange():
    # Запросить курсы обмена у ЦБ РФ
    response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
    if response.status_code == 200:
        content = response.json()
        # Извлечение даты из ответа
        date_exchange = content["Timestamp"][0:10]

        # Получить курсы обмена для USD, EUR, GBP и JPY
        exchanges: dict = {'USD': get_value(content, 'USD'), 'EUR': get_value(content, 'EUR'),
                               'GBP': get_value(content, 'GBP'), 'JPY': get_value(content, 'JPY')}

    return (f'📈 Официальный курс ЦБ РФ за {date_exchange} 📉\n\n'
                                                     f'🇺🇸 Доллар США (USD): {exchanges["USD"]}\n'
                                                     f'🇪🇺 Евро (EUR): {exchanges["EUR"]}\n'
                                                     f'🇬🇧 Фунт стерлингов Великобритании (GBP): {exchanges["GBP"]}\n'
                                                     f'🇯🇵 Японская иена (JPY): {exchanges["JPY"]}')