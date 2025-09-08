from bs4 import BeautifulSoup

import requests
import os
import json


#в данном файле мы получаем html код с 12 страниц сайта на каждой странице отдельный город
#из всего достаём :
#                   адресс
#                   курс валют
#после чего это всё загружаем в словарь 
#который потом раскидываеться отдельными файлами в папку 
#название файла = название города

#структура словаря
# list_conversion = {
#     "city": {
#         "address": [values1, values2, values3, values4],
#     },
# }

def update_json_files():
    # Твой код для обновления .json
    print("Обновление JSON файлов...")
    
    urls = {
        "url1": ["https://zlata.ws/kantory/belostok/", "belostok"],#
        "url2": ["https://zlata.ws/kantory/bydgoszcz/", "bydgoszcz"],#
        "url3": ["https://zlata.ws/kantory/warszawa/", "warszawa"],#
        "url4": ["https://zlata.ws/kantory/wroclaw/", "wroclaw"],#
        "url5": ["https://zlata.ws/kantory/gdansk/", "gdansk"],#
        "url6": ["https://zlata.ws/kantory/rzeszow/", "rzeszow"],#
        "url7": ["https://zlata.ws/kantory/katowice/", "katowice"],#
        "url8": ["https://zlata.ws/kantory/krakow/", "krakow"],#
        "url9": ["https://zlata.ws/kantory/lodz/", "lodz"],#
        "url10": ["https://zlata.ws/kantory/lublin/", "lublin"],#
        "url11": ["https://zlata.ws/kantory/poznan/", "poznan"],#
        "url12": ["https://zlata.ws/kantory/szczecin/", "szczecin"],#
    }

    folder_path = "/Users/apple/currency_bot/conversion_request/saving_html_site/cities"
    list_conversion = {}
    output_folder = "cities"

    # Заголовки, чтобы не блокировали как бота
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # Выполняем GET-запросы
    for key, (url, city) in urls.items():
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html_content = response.text
        soup = BeautifulSoup(html_content, 'lxml')

        if city not in list_conversion:
            list_conversion[city] = {}

        # Найти все элементы с классом "нужный-класс"
        elements = soup.find("tbody")

        #small содержит адрес обменика и время обновления курса
        tr_all= elements.find_all("tr")

        for tr in tr_all:
            #small содержит адрес обменика и время обновления курса
            small = tr.find_all("small")
            #остовляем только пункты с курсом валют
            center_tds = tr.find_all("td", attrs={"align": "center"})
            #убираем лишние пункты, остовляем только доллар и евро
            del center_tds[0]
            del center_tds[4:]
            
            for num, values in enumerate(small):
                #остаёться дата последнего обновления курса валют
                # if num % 2 != 0:
                #     time = vales.get_text(separator=" ").strip()
                #оставляем только четные, в них содержиться адреес 
                if num % 2 == 0:
                    coins = []
                    address = values.get_text(separator=" ").strip()
                    
                    for coin in center_tds:
                        coin = coin.get_text(separator=" ").strip()
                        coins.append(coin)                    
                    
                list_conversion[city][address] = coins

    # создаём папку, если её нет
    os.makedirs(output_folder, exist_ok=True)

    #сохроняем каждый город отдельно
    for city, addresses in list_conversion.items():
        filename = f"{city.lower()}.json"
        filepath = os.path.join(output_folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({city: addresses}, f, ensure_ascii=False, indent=4)


    #создаём файл с лучшими курсами на каждый город

    #ниже будет перебираться словарь - list_conversion 
    #из него будет извлекаться лучший курс для перевода во все стороны
    #данные будет сохраняться в словарь - best_rate
    #после чего словарь будет сохронён в отдельный файл в главной папке

    #схема словаря
    #
    #best_rate = {
    #   city:{
    #       USD_PL: 09, PL_USD: 09, EUR_PL: 09, "PL_EUR: 09,
    #   }
    #}
    best_rate = {}


    for city, adress_and in list_conversion.items():
        best_rate[city] = {"USD_PL": 0, "PL_USD": 999, "EUR_PL": 0, "PL_EUR": 999}
        for adress, value in adress_and.items():
            if value[0] != "-" and best_rate[city]["USD_PL"] < float(value[0]): best_rate[city]["USD_PL"] = (float(value[0]))
            if value[1] != "-" and best_rate[city]["PL_USD"] > float(value[1]): best_rate[city]["PL_USD"] = (float(value[1]))
            if value[2] != "-" and best_rate[city]["EUR_PL"] < float(value[2]): best_rate[city]["EUR_PL"] = (float(value[2]))
            if value[3] != "-" and best_rate[city]["PL_EUR"] > float(value[3]): best_rate[city]["PL_EUR"] = (float(value[3]))


    file_path = "/Users/apple/currency_bot/best_rate/best_rate.json"

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(best_rate, f, ensure_ascii=False, indent=4)