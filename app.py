import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from TelegramGifts import TelegramGifts

BOT_TOKEN = "8651733678:AAEkKpXTqTLF8gAx5t3rEbYD8zTHgG6ig3E"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=8651733678:AAEkKpXTqTLF8gAx5t3rEbYD8zTHgG6ig3E)
dp = Dispatcher()

gifts_db = None

def get_start_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Парсинг NFT", callback_data="start_parsing")
    return builder.as_markup()

def build_collections_keyboard(collections: list[str], page: int = 0, per_page: int = 8):
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_items = collections[start:end]

    for c in page_items:
        cb = f"coll_{c}"
        if len(cb.encode('utf-8')) > 64:
            cb = f"coll_{c[:50]}"
        builder.button(text=c, callback_data=cb)

    if page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"page_{page - 1}")
    if end < len(collections):
        builder.button(text="Вперёд ➡️", callback_data=f"page_{page + 1}")

    builder.adjust(2)
    return builder.as_markup()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 👋\n\n"
        "Я бот для поиска коллекционных NFT-подарков.\n"
        "Нажми на кнопку ниже, чтобы начать.",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(F.data == "start_parsing")
async def process_start_parsing(callback: CallbackQuery):
    global gifts_db
    
    if gifts_db is None:
        await callback.message.edit_text("⏳ Первый запуск: скачиваю базу данных. Это займет 1-2 минуты...")
        await callback.answer()
        
        print(">>> НАЧИНАЮ СКАЧИВАТЬ БАЗУ TELEGRAMGIFTS...", flush=True)
        try:
            gifts_db = await asyncio.to_thread(TelegramGifts, cache_mode="http", asset_mode="lazy")
            print(">>> БАЗА УСПЕШНО СКАЧАНА!", flush=True)
        except Exception as e:
            print(f">>> ОШИБКА СКАЧИВАНИЯ: {e}", flush=True)
            await callback.message.edit_text("😔 Ошибка: не удалось скачать базу данных.")
            return

    await callback.message.edit_text("⏳ Формирую список коллекций...")
    
    try:
        regular_gifts = gifts_db.get_regular_gifts()
        collections = sorted([gift.full_name for gift in regular_gifts])
    except Exception as e:
        logging.error(f"Ошибка при получении списка: {e}")
        await callback.message.edit_text("😔 Ошибка при обработке базы подарков.")
        return

    await callback.message.edit_text(
        f"📚 Доступно коллекций: <b>{len(collections)}</b>\n\n"
        "Выберите коллекционный подарок:",
        reply_markup=build_collections_keyboard(collections, page=0),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("page_"))
async def process_page_navigation(callback: CallbackQuery):
    page = int(callback.data.replace("page_", ""))
    regular_gifts = gifts_db.get_regular_gifts()
    collections = sorted([gift.full_name for gift in regular_gifts])
    
    await callback.message.edit_reply_markup(
        reply_markup=build_collections_keyboard(collections, page=page)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("coll_"))
async def process_collection_selection(callback: CallbackQuery):
    collection_name = callback.data.replace("coll_", "", 1)
    
    await callback.message.edit_text(f"🔎 Ищу данные по коллекции «{collection_name}»...")
    await callback.answer()

    try:
        info = gifts_db.get_gift(collection_name)
    except Exception as e:
        info = None

    if not info:
        await callback.message.edit_text(f"К сожалению, данные не найдены.")
        return

    price_ton = "Нет данных"
    if 'prices' in info and info['prices'].get('tgmrkt_price_ton'):
        price_ton = f"{info['prices']['tgmrkt_price_ton']} TON"

    slug = collection_name.replace(" ", "-")
    link = f"https://t.me/nft/{slug}"

    text = (
        f"✅ <b>{info['full_name']}</b>\n\n"
        f"💰 Мин. цена: <b>{price_ton}</b>\n"
        f"🔗 <a href='{link}'>Посмотреть на маркетплейсе</a>"
    )

    await callback.message.edit_text(text, parse_mode="HTML", disable_web_page_preview=True)

async def main():
    print(">>> СБРАСЫВАЮ СТАРЫЕ ВЕБХУКИ...", flush=True)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print(">>> БОТ УСПЕШНО ЗАПУЩЕН И ЖДЕТ СООБЩЕНИЙ!", flush=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
