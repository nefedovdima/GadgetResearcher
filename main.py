import asyncio
import json
import logging
import sys
from os import getenv
import re

from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import CallbackQuery

from biggeek import fetch_biggeek
from nistone import fetch_nistone
from apple_market import fetch_apple_market
from apple_i_tochka import fetch_apple_i_tochka
from aiogram.fsm.storage.base import BaseStorage
from megafon import fetch_megafon
from store77 import fetch_store_77

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot token can be obtained via https://t.me/BotFather
TOKEN='8106823503:AAGRIrMz5uBP-h4arwLXRTabASAaThEhNR4'

# All handlers should be attached to the Router (or Dispatcher)

class FindProduct(StatesGroup):
    start = State()
    ask_name = State()
    ask_shop = State()
    biggeek = State()
    nistone = State()
    apple_i_tochka = State()
    all_shopes = State()
    found_item = State()
    apple_market = State()
    store_77 = State()
    megafon = State()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)

@form_router.message(lambda message: message.text == '/start')
async def command_start_handler(message: Message, state: FSMContext, prev_message_id=None) -> None:
    logger.info("Обработчик команды /start")
    if prev_message_id:
        try:
            await bot.delete_message(message.chat.id, prev_message_id)
        except Exception as e:
            logger.warning(f"Ошибка при удалении сообщения: {e}")
    await state.set_state(FindProduct.start)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Поиск товара', callback_data=str(FindProduct.ask_name))]
    ])
    await message.answer('Добро пожаловать!', reply_markup=kb)

@form_router.callback_query(lambda callback_query: callback_query.data == str(FindProduct.ask_name))
async def callback_query_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Обработчик callback запроса на поиск товара")
    await ask_name(callback_query.message.chat.id, state, callback_query.message.message_id)

async def ask_name(chatd_id, state: FSMContext, prev_message_id=None) -> None:
    logger.info("Переход в состояние ask_name")
    if prev_message_id:
        try:
            await bot.delete_message(chatd_id, prev_message_id)
        except Exception as e:
            logger.warning(f"Ошибка при удалении сообщения: {e}")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data=str(FindProduct.start))],
    ])
    await bot.send_message(
        chat_id=chatd_id,
        text='Введите название товара',
        reply_markup=kb,
    )
    await state.set_state(FindProduct.ask_name)

@form_router.callback_query(lambda callback_query: callback_query.data == str(FindProduct.start))
async def callback_query_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Возврат к начальному состоянию")
    await command_start_handler(callback_query.message, state, prev_message_id=callback_query.message.message_id)

@form_router.message(FindProduct.ask_name)
async def ask_name_handler(message: Message, state: FSMContext) -> None:
    logger.info(f"Получено имя товара: {message.text}")
    await state.update_data({'name': message.text})
    await state.set_state(FindProduct.ask_shop)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='biggeek', callback_data=str(FindProduct.biggeek))],
        [InlineKeyboardButton(text='nistone', callback_data=str(FindProduct.nistone))],
        [InlineKeyboardButton(text='apple_i_tochka', callback_data=str(FindProduct.apple_i_tochka))],
        [InlineKeyboardButton(text='apple_market', callback_data=str(FindProduct.apple_market))],
        [InlineKeyboardButton(text='megafon', callback_data=str(FindProduct.megafon))],
        [InlineKeyboardButton(text='store_77', callback_data=str(FindProduct.store_77))],
        [InlineKeyboardButton(text='all', callback_data=str(FindProduct.all_shopes))],
    ])
    await bot.send_message(
        chat_id=message.chat.id,
        text='Выберите магазин для поиска',
        reply_markup=kb,
    )

@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.biggeek))
async def find_biggeek(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска в магазине biggeek")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск')
    try:
        name = (await state.get_data())['name']
        result = fetch_biggeek(name)
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})
        await bot.send_message(callback_query.message.chat.id, 'Товар найден')
        await send_imagine(callback_query.message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при поиске в biggeek: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)

@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.nistone))
async def find_nistone(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска в магазине nistone")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск')
    try:
        name = (await state.get_data())['name']
        result = fetch_nistone(name)
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})
        await bot.send_message(callback_query.message.chat.id, 'Товар найден')
        await send_imagine(callback_query.message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при поиске в nistone: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)


@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.apple_market))
async def find_apple_market(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска в магазине apple_market")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск')
    try:
        name = (await state.get_data())['name']
        result = fetch_apple_market(name)  # Ожидаем список кортежей, например: [("iPhone", 5), ("MacBook", 2)]

        if not result:
            raise ValueError("Товар не найден")

        # Вычисляем общее количество товаров
        total_items = len(result)

        # Формируем строку с результатами
        items_list = "\n".join([
            f"{index + 1}. {item[0]} - <b>{item[1]} шт.</b>" for index, item in enumerate(result)
        ])

        # Сохраняем результат в состояние
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})

        # Отправляем сообщение с общим количеством и списком товаров
        await bot.send_message(
            callback_query.message.chat.id,
            f"<b>Найдено товаров: {total_items}</b>\n",
            parse_mode="HTML"
        )

        await send_imagine(callback_query.message.chat.id)  # Предполагаем, что эта функция отображает изображения товаров

    except Exception as e:
        logger.error(f"Ошибка при поиске в apple_market: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)




@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.apple_i_tochka))
async def find_apple_i_tochka(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска в магазине apple_i_tochka")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск в магазине apple_i_tochka')
    try:
        name = (await state.get_data())['name']
        result = fetch_apple_i_tochka(name)
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})
        await bot.send_message(callback_query.message.chat.id, 'Товар найден')
        await send_imagine(callback_query.message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при поиске в apple_i_tochka: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)



@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.megafon))
async def find_megafon(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска в магазине megafon")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск в магазине megafon')
    try:
        name = (await state.get_data())['name']
        result = fetch_megafon(name)
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})
        await bot.send_message(callback_query.message.chat.id, 'Товар найден')
        await send_imagine(callback_query.message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при поиске в apple_i_tochka: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)



@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.store_77))
async def find_megafon(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска в магазине store_77")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск в магазине store_77')
    try:
        name = (await state.get_data())['name']
        result = fetch_store_77(name)
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})
        await bot.send_message(callback_query.message.chat.id, 'Товар найден')
        await send_imagine(callback_query.message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при поиске в apple_i_tochka: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)




@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.all_shopes))
async def find_all_shopes(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска во всех магазинах")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск')
    try:
        name = (await state.get_data())['name']
        
        # Получаем результаты из всех магазинов
        result_biggeek = fetch_biggeek(name)
        result_nistone = fetch_nistone(name)
        result_apple_i_tochka = fetch_apple_i_tochka(name)
        result_apple_market = fetch_apple_market(name)
        result_megafon = fetch_megafon(name)
        result_store_77 = fetch_store_77(name)

        # Считаем количество товаров в каждом магазине
        count_biggeek = len(result_biggeek)
        count_nistone = len(result_nistone)
        count_apple_i_tochka = len(result_apple_i_tochka)
        count_apple_market = len(result_apple_market)
        count_megafon = len(result_megafon)
        count_store_77 = len(result_store_77)

        # Суммируем общее количество товаров
        total_count = (
            count_biggeek + count_nistone + count_apple_i_tochka +
            count_apple_market + count_megafon + count_store_77
        )

        # Объединяем все данные для сохранения в состоянии
        combined_results = (
            result_biggeek + result_nistone + result_apple_i_tochka +
            result_apple_market + result_megafon + result_store_77
        )

        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(combined_results)})

        # Формируем сообщение с результатами
        result_message = (
            f"Общее количество товаров: <b>{total_count}</b>\n\n"
            f"BigGeek: <b>{count_biggeek}</b>\n"
            f"Nistone: <b>{count_nistone}</b>\n"
            f"Apple i-точка: <b>{count_apple_i_tochka}</b>\n"
            f"Apple Market: <b>{count_apple_market}</b>\n"
            f"Megafon: <b>{count_megafon}</b>\n"
            f"Store 77: <b>{count_store_77}</b>"
        )

        # Отправляем сообщение с результатами
        await bot.send_message(
            callback_query.message.chat.id,
            result_message,
            parse_mode="HTML"
        )
        await send_imagine(callback_query.message.chat.id)

    except Exception as e:
        logger.error(f"Ошибка при поиске во всех магазинах: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)



async def send_imagine(chat_id) -> None:
    logger.info("Отправка клавиатуры отображения")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вывести первые 10', callback_data='x1')],
        [InlineKeyboardButton(text='5 самых дешевых', callback_data='x2')],
        [InlineKeyboardButton(text='Самый дешевый', callback_data='x3')],
        [InlineKeyboardButton(text='Назад', callback_data=str(FindProduct.ask_name))],
    ])
    await bot.send_message(chat_id, 'Выведите желаемое отображение', reply_markup=kb)

@form_router.callback_query(FindProduct.found_item, lambda callback_query: callback_query.data == str(FindProduct.ask_name))
async def callback_query_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Возврат к предыдущему состоянию")
    try:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    except Exception as e:
        logger.warning(f"Ошибка при удалении сообщения: {e}")
    await ask_name(callback_query.message.chat.id, state)



@form_router.callback_query(lambda callback_query: callback_query.data == 'x1')
async def callback_query_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Обработка сортировки x1")
    
    try:
        # Fetch and parse the data
        data = json.loads((await state.get_data())['result'])

        # Ensure all items are of a valid format
        result = [
            (item[0], float(item[1])) if isinstance(item[1], (int, float, str)) and str(item[1]).replace('.', '', 1).isdigit() else (item[0], 0)
            for item in data
        ]
    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"Ошибка обработки данных: {e}")
        await bot.send_message(
            callback_query.message.chat.id,
            "Ошибка при обработке данных. Убедитесь, что формат данных корректен.",
            parse_mode="HTML"
        )
        return

    # Формируем строку с результатами
    result_str = "\n".join([
        f"{index + 1}. {item[0]} - <b>{item[1]}</b> шт." for index, item in enumerate(result[:10])
    ])

    await bot.send_message(
        callback_query.message.chat.id,
        result_str,
        parse_mode="HTML"
    )
    await send_imagine(callback_query.message.chat.id)



@form_router.callback_query(lambda callback_query: callback_query.data == 'x2')
async def callback_query_handler_x2(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Обработка сортировки x2")
    
    try:
        # Получаем и парсим данные
        data = json.loads((await state.get_data())['result'])
        
        # Функция для извлечения числового значения
        def extract_numeric(value):
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Убираем все символы, кроме цифр, точек и запятых
                numeric_str = re.sub(r'[^\d.]', '', value.replace(',', '.'))
                return float(numeric_str) if numeric_str else float('inf')
            return float('inf')
        
        # Обрабатываем и сортируем данные
        result = sorted(
            [(item[0], extract_numeric(item[1])) for item in data],
            key=lambda x: x[1]
        )[:5]
    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"Ошибка обработки данных: {e}")
        await bot.send_message(
            callback_query.message.chat.id,
            "Ошибка при обработке данных. Убедитесь, что формат данных корректен.",
            parse_mode="HTML"
        )
        return

    # Формируем строку с результатами
    result_str = "\n".join([
        f"{index + 1}. {item[0]} - <b>{item[1]:,.2f}</b> шт." for index, item in enumerate(result)
    ])

    await bot.send_message(
        callback_query.message.chat.id,
        result_str,
        parse_mode="HTML"
    )
    await send_imagine(callback_query.message.chat.id)


@form_router.callback_query(lambda callback_query: callback_query.data == 'x3')
async def callback_query_handler_x3(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Обработка сортировки x3")
    
    try:
        # Получаем и парсим данные
        data = json.loads((await state.get_data())['result'])
        
        # Функция для извлечения числового значения
        def extract_numeric(value):
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Убираем все символы, кроме цифр и разделителей
                numeric_str = re.sub(r'[^\d.]', '', value.replace(',', '.'))
                return float(numeric_str) if numeric_str else float('inf')
            return float('inf')
        
        # Преобразуем и сортируем данные
        result = sorted(
            [(item[0], extract_numeric(item[1])) for item in data],
            key=lambda x: x[1]
        )[:1]
    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"Ошибка обработки данных: {e}")
        await bot.send_message(
            callback_query.message.chat.id,
            "Ошибка при обработке данных. Убедитесь, что формат данных корректен.",
            parse_mode="HTML"
        )
        return

    # Формируем строку с результатами
    result_str = "\n".join([
        f"{index + 1}. {item[0]} - <b>{item[1]:,.2f}</b> шт." for index, item in enumerate(result)
    ])

    await bot.send_message(
        callback_query.message.chat.id,
        result_str,
        parse_mode="HTML"
    )
    await send_imagine(callback_query.message.chat.id)





@form_router.message()
async def echo_handler(message: Message) -> None:
    logger.info(f"Эхо сообщение: {message.text}")
    await message.send_copy(chat_id=message.chat.id)

async def main() -> None:
    logger.info("Запуск бота")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logger.info("Инициализация бота")
    asyncio.run(main())
