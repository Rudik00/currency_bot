from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
from conversion_request.saving import update_json_files
from table_output import table_output_router, show_table_for_city
from converter import conversion_router, choice_of_conversion
from table_output import table_output_router, show_table_for_city


import asyncio
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Добавь его в .env или Railway Variables")

router = Router()


# Бот с HTML-поддержкой
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(table_output_router)
dp.include_router(conversion_router)


# Хендлер команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я покажу тебе курс валют. Напиши /exchange_rate")


# Хендлер команды /exchange_rate
@dp.message(Command("exchange_rate"))
async def cmd_rates(message: Message):
    await show_table_for_city(message)


# Хендлер команды /conversion
@dp.message(Command("conversion"))
async def test_command(message: Message, state: FSMContext):
    await choice_of_conversion(message, state)


async def background_updater():
    while True:
        print("⏰ Фоновое обновление данных...")
        update_json_files()
        await asyncio.sleep(6 * 60 * 60)  # 6 часов


# Запуск
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(router)
    asyncio.create_task(background_updater())  # Запуск фонового обновления
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
