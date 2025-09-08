from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from convert import user_amount_conversion


conversion_router = Router()  # роутер для этого модуля

# --- FSM шаги ---
class ConversionForm(StatesGroup):
    choosing_currency = State()
    choosing_city = State()
    waiting_for_amount = State()


# Список валют
conversion = [
    "USD -> PL", "PL -> USD", "EUR -> PL", "PL -> EUR"
]

# Список городов
CITIES = [
    "belostok", "bydgoszcz", "gdansk", "katowice", "krakow", "lodz",
    "lublin", "poznan", "rzeszow", "szczecin", "warszawa", "wroclaw"
]

# --- Кнопки валют ---
async def choice_of_conversion(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=valuta.capitalize(), callback_data=f"currency:{valuta}")]
            for valuta in conversion
        ]
    )
    await message.answer("Выбери условия конвертации:", reply_markup=keyboard)
    await state.set_state(ConversionForm.choosing_currency)
    print("🟢 Кнопки валют отправлены")


# --- Кнопки городов ---
def show_table_city() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=city.capitalize(), callback_data=f"select_city1:{city}")]
            for city in CITIES
        ]
    )
    return keyboard


# --- Ловим выбор валюты ---
@conversion_router.callback_query(ConversionForm.choosing_currency, F.data.startswith("currency:"))
async def currency_callback(callback: types.CallbackQuery, state: FSMContext):
    conversion_option = callback.data.split(":")[1]
    await state.update_data(currency=conversion_option)  # сохраняем валюту
    await callback.answer()
    print(f"✅ Пользователь выбрал валюту: {conversion_option}")

    # показываем города
    keyboard = show_table_city()
    await callback.message.edit_text(
        f"Вы выбрали {conversion_option}. Теперь выберите город:",
        reply_markup=keyboard
    )
    await state.set_state(ConversionForm.choosing_city)


# --- Ловим выбор города ---
@conversion_router.callback_query(ConversionForm.choosing_city, F.data.startswith("select_city1:"))
async def city_callback(callback: types.CallbackQuery, state: FSMContext):
    city_conversion = callback.data.split(":")[1]
    await state.update_data(city=city_conversion)  # сохраняем город
    await callback.answer()
    print(f"🏙 Пользователь выбрал город: {city_conversion}")

    await callback.message.edit_text(
        "Теперь напишите сумму, которую хотите перевести ->"
    )
    await state.set_state(ConversionForm.waiting_for_amount)


# --- Ловим число ---
@conversion_router.message(ConversionForm.waiting_for_amount, F.text.regexp(r"^\d+(\.\d+)?$"))
async def process_amount(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    amount = float(message.text)
    currency = user_data.get("currency")
    city = user_data.get("city")

    await message.answer(
        f"📊 Вы выбрали:\n"
        f"Валюта: {currency}\n"
        f"Город: {city}\n"
        f"Сумма: {amount}"
    )

    # --------- функция для конвертации --------
    result, well = await user_amount_conversion(currency, city, amount)
    await message.answer(f"Перевод по курсу: {well}\nРезультат: {result}")

    await state.clear()  # очищаем FSM (новый диалог можно начать заново)


# --- Если введено не число ---
@conversion_router.message(ConversionForm.waiting_for_amount)
async def wrong_input(message: types.Message):
    await message.answer("❌ Нужно ввести число. Попробуй ещё раз:")