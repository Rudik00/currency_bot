from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import json
import os

table_output_router = Router()  # роутер для этого модуля

# Список городов для кнопок
CITIES = [
    "belostok", "bydgoszcz", "gdansk", "katowice", "krakow", "lodz",
    "lublin", "poznan", "rzeszow", "szczecin", "warszawa", "wroclaw"
]

# Функция для создания и отправки кнопок
async def show_table_for_city(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=city.capitalize(), callback_data=f"select_city:{city}")]
            for city in CITIES
        ]
    )
    await message.answer("Выбери город:", reply_markup=keyboard)
    print("🟢 Кнопки отправлены")  # Для отладки

# Обработчик нажатий на кнопки
@table_output_router.callback_query(F.data.startswith("select_city:"))
async def city_callback(callback: types.CallbackQuery):
    city = callback.data.split(":")[1]
    await callback.answer()  # убрать "часики"
    await callback.message.delete()
    await callback.message.answer(f"Вы выбрали город: {city.capitalize()}")
    print(f"✅ Пользователь выбрал: {city}")  # Для отладки

    max_length = 4096

    filepath = f"cities/{city}.json"
    if not os.path.exists(filepath):
        await callback.message.answer(f"Файл данных для города {city.title()} не найден.")
        return

    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)


    if city not in data:
        await callback.message.answer(f"Данные по городу {city.title()} отсутствуют.")
        return

    table = f"<b>Курсы обмена – {city.title()}:</b>\n\n"
    for address, values in data[city].items():
        usd_buy, usd_sell, eur_buy, eur_sell = values
        table += (
            f"<b>{address}</b>\n"
            f"USD: покупка {usd_buy}, продажа {usd_sell}\n"
            f"EUR: покупка {eur_buy}, продажа {eur_sell}\n\n"
        )
    MAX_LENGTH = 4096
    if len(table) <= MAX_LENGTH:
        await callback.message.answer(table, parse_mode="HTML")    
    else:
        table1 = f"<b>Курсы обмена – {city.title()}:</b>\n\n"
        table2 = f"<b>Продолжение курсы обмена – {city.title()}:</b>\n\n"
        print(f"⚠️ Сообщение превышает лимит ({len(table)} символов), будет разбито.")
        for address, values in data[city].items():
            if len(table1) <= MAX_LENGTH:
                usd_buy, usd_sell, eur_buy, eur_sell = values
                table1 += (
                    f"<b>{address}</b>\n"
                    f"USD: покупка {usd_buy}, продажа {usd_sell}\n"
                    f"EUR: покупка {eur_buy}, продажа {eur_sell}\n\n"
                )
            else:
                usd_buy, usd_sell, eur_buy, eur_sell = values
                table2 += (
                    f"<b>{address}</b>\n"
                    f"USD: покупка {usd_buy}, продажа {usd_sell}\n"
                    f"EUR: покупка {eur_buy}, продажа {eur_sell}\n\n"
                )

        await callback.message.answer(table1, parse_mode="HTML")
        await callback.message.answer(table2, parse_mode="HTML")






