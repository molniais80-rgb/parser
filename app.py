logging.basicConfig(level=logging.DEBUG)
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# Ваш токен
BOT_TOKEN = "8651733678:AAHir2wOkalFpb7bjYUOCHfAwCMJrfxdzM"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Я работаю на сервере!")

async def main():
    print(">>> ПОПЫТКА ЗАПУСТИТЬ БОТА...", flush=True)
    print(">>> ТЕСТОВЫЙ БОТ УСПЕШНО ЗАПУЩЕН И ЖДЕТ СООБЩЕНИЙ!", flush=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())