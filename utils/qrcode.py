import json
import hashlib
import asyncio
import aiohttp
from Crypto.Cipher import AES

# Адрес и эндпоинт для запросов к API
API_URL = "https://proverkacheka.com"
API_ENDPOINT = "/api/v1/check/get"

# Заголовки для HTTP запросов
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Referer": "https://proverkacheka.com/",
    "Origin": "https://proverkacheka.com",
}

# Функция для вычисления токена
def compute_token(qrraw: str, qr: str) -> str:
    base = qrraw + qr

    d = "0"
    for i in range(10000):
        h = hashlib.md5((base + (d := str(i))).encode()).hexdigest()
        if len(h.split("0")) - 1 > 4:
            break
    return "0." + d

# Асинхронная функция для получения зашифрованных данных по API
async def get_encrypted_data(qrraw: str, qr: str) -> bytes:
    form = aiohttp.FormData()
    form.add_field(name="qrraw", value=qrraw)
    form.add_field(name="qr", value=qr)
    form.add_field(name="token", value=compute_token(qrraw, qr))

    async with aiohttp.ClientSession(headers=HEADERS) as client:
        # Получаем куки
        await client.get(API_URL)

        # Отправляем POST запрос
        response = await client.post(API_URL + API_ENDPOINT, data=form, headers={"Cookie": "ENGID=1.1"})

        # Проверяем, получены ли зашифрованные данные
        if "+crypto" not in response.headers["Content-Type"]:
            raise ValueError("Invalid token")

        return await response.read()

# Функция для проверки QR кода
async def qrcheck(qrcode) -> None:
    # Исходные ключи для шифрования и дешифрования
    basekey = "38s91"
    decryptkey = "f65nm"

    qrraw = qrcode
    qr = "3"
    # Получаем зашифрованные данные
    crypted_json = await get_encrypted_data(qrraw, qr)

    # Разделяем зашифрованные данные и nonce
    crypted_data, nonce = crypted_json[:-12], crypted_json[-12:]

    # Генерируем ключ для дешифрования
    key = hashlib.sha256((basekey + decryptkey).encode()).digest()

    # Создаем объект шифрования
    cipher = AES.new(key=key, mode=AES.MODE_GCM, nonce=nonce)

    # Расшифровываем данные
    decrypted_data = cipher.decrypt(crypted_data)

    # Преобразуем данные в строку
    plain_text = decrypted_data.decode(errors="ignore")

    # Обрезаем лишние символы справа
    pt = plain_text[:plain_text.rfind("}") + 1]

    # Преобразуем строку в словарь JSON
    pt_dict = json.loads(pt)

    return pt_dict





'''
import json
import hashlib
import asyncio
import aiohttp
from Crypto.Cipher import AES

URL = "https://proverkacheka.com"
API = "/api/v1/check/get"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Referer": "https://proverkacheka.com/",
    "Origin": "https://proverkacheka.com",
}


def compute_token(qrraw: str, qr: str) -> str:
    base = qrraw + qr

    d = "0"
    for i in range(10000):
        h = hashlib.md5((base + (d := str(i))).encode()).hexdigest()
        if len(h.split("0")) - 1 > 4:
            break
    return "0." + d


async def get_crypted_json(qrraw: str, qr: str) -> bytes:
    form = aiohttp.FormData()
    form.add_field(name="qrraw", value=qrraw)
    form.add_field(name="qr", value=qr)
    form.add_field(name="token", value=compute_token(qrraw, qr))

    async with aiohttp.ClientSession(headers=headers) as client:
        # Получаем куки
        await client.get(URL)

        response = await client.post(URL + API, data=form, headers={"Cookie": "ENGID=1.1"})

        if "+crypto" not in response.headers["Content-Type"]:
            raise ValueError("Invalid token")

        return await response.read()


async def qrcheck(qrcode) -> None:
    basekey = "38s91"
    decryptkey = "f65nm"

    qrraw = qrcode

    #qrraw = "t=20201017T1923&s=1498.00&fn=9282440300669857&i=25151&fp=1186123459&n=1"
    qr = "3"
    crypted_json = await get_crypted_json(qrraw, qr)

    crypted_data, nonce = crypted_json[:-12], crypted_json[-12:]
    key = hashlib.sha256((basekey + decryptkey).encode()).digest()

    cipher = AES.new(key=key, mode=AES.MODE_GCM, nonce=nonce)
    decrypted_data = cipher.decrypt(crypted_data)

    # В plain_text присутствует какие-то лишние символы на конце, скорее всего паддинг для зашифровки. Не проверял.
    plain_text = decrypted_data.decode(errors="ignore")

    # Отрезаем лишние символы справа
    pt = plain_text[:plain_text.rfind("}") + 1]
    pt_dict = json.loads(pt)
    return pt_dict







    with open("decoded.json", "wt", encoding="utf-8") as fp:
        loaded = json.loads(pt)
        json.dump(loaded, fp, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    asyncio.run(qrcheck())
'''