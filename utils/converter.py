import requests
from bs4 import BeautifulSoup as bs


def convert_currency_xe(amount: float, src: str, dst: str):
    """
    Конвертирует сумму из одной валюты в другую, используя XE.com.

    Args:
        amount (float): Сумма для конвертации.
        src (str): Код исходной валюты.
        dst (str): Код целевой валюты.

    Returns:
        float: Обменный курс для конвертации суммы.
    """
    def get_digits(text):
        """
        Извлекает из строки только цифры и точки, преобразуя их в число.

        Args:
            text (str): Исходная строка.

        Returns:
            float: Число, представляющее только цифры и точки из исходной строки.
        """
        new_text = ""
        for c in text:
            if c.isdigit() or c == ".":
                new_text += c
        return float(new_text)

    # Формируем URL для запроса на XE.com
    url = f"https://www.xe.com/currencyconverter/convert/?Amount={amount}&From={src}&To={dst}"
    # Получаем содержимое страницы
    content = requests.get(url).content
    # Парсим HTML-контент
    soup = bs(content, "html.parser")
    # Находим HTML-элемент с обменным курсом
    exchange_rate_html = soup.find_all("p")[2]

    # Извлекаем обменный курс из HTML-элемента
    return get_digits(exchange_rate_html.text)