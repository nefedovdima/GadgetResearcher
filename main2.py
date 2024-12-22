import asyncio
import json
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import CallbackQuery

from biggeek import fetch_biggeek_products
from find_products_nistone import fetch_nistone_products

from aiogram.fsm.storage.base import BaseStorage

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
    all_shopes = State()
    found_item = State()

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
        result = fetch_biggeek_products(name)
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
        result = fetch_nistone_products(name)
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})
        await bot.send_message(callback_query.message.chat.id, 'Товар найден')
        await send_imagine(callback_query.message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при поиске в nistone: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)

@form_router.callback_query(FindProduct.ask_shop, lambda callback_query: callback_query.data == str(FindProduct.all_shopes))
async def find_all_shopes(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Начало поиска во всех магазинах")
    await bot.send_message(callback_query.message.chat.id, 'Идет поиск')
    try:
        name = (await state.get_data())['name']
        result_biggeek = fetch_biggeek_products(name)
        result_nistone = fetch_nistone_products(name)
        result = result_biggeek + result_nistone
        await state.set_state(FindProduct.found_item)
        await state.set_data({'result': json.dumps(result)})
        await bot.send_message(callback_query.message.chat.id, 'Товар найден')
        await send_imagine(callback_query.message.chat.id)
    except Exception as e:
        logger.error(f"Ошибка при поиске во всех магазинах: {e}")
        await bot.send_message(callback_query.message.chat.id, 'Товар не найден')
        await ask_name(callback_query.message.chat.id, state)

async def send_imagine(chat_id) -> None:
    logger.info("Отправка клавиатуры отображения")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Порядок возрастания цены', callback_data='x1')],
        [InlineKeyboardButton(text='Порядок возрастания цены 2', callback_data='x2')],
        [InlineKeyboardButton(text='Порядок возрастания цены 3', callback_data='x3')],
        [InlineKeyboardButton(text='Порядок возрастания цены 4', callback_data='x4')],
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
    result = json.loads((await state.get_data())['result'])
    result_str = ''
    for item in result:
        result_str += f"{item[0]} {item[1]}\n"
    await bot.send_message(callback_query.message.chat.id, result_str)
    await send_imagine(callback_query.message.chat.id)

@form_router.callback_query(lambda callback_query: callback_query.data == 'x2')
async def callback_query_handler(callback_query: CallbackQuery, state: FSMContext) -> None:
    logger.info("Обработка сортировки x2")
    result = sorted(json.loads((await state.get_data())['result']), key=lambda x: x[1])[:5]
    result_str = ''
    for item in result:
        result_str += f"{item[0]} {item[1]}\n"
    await bot.send_message(callback_query.message.chat.id, result_str)
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
