import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import uuid
from config import settings
from helpers.process_session import process_archive

bot = Bot(token=settings.TG_TOKEN)
dp = Dispatcher()
os.makedirs(settings.TEMP_DIR, exist_ok=True)


@dp.message(F.document)
async def handle_archive(message: Message):
    document = message.document
    original_name = document.file_name
    file = await bot.get_file(document.file_id)

    ext = os.path.splitext(original_name)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    save_path = os.path.join(settings.TEMP_DIR, unique_name)

    await bot.download_file(file.file_path, destination=save_path)

    await message.answer(f"✅ Архив сохранён как: `{unique_name}`", parse_mode='Markdown')

    result = await process_archive(unique_name)

    await message.reply(f"Обработка завершена, найдено: `{len(result)}` сессий", parse_mode='Markdown')

    for item in result:
        if item:
            alive = '**спам блок**' if item.spam_blocked else '**спам блок отсутствует**'
            renewed = '**обновлена**' if item.renewed_session else '**не обновлена**'
            await bot.send_message(
                message.chat.id,
                f"Сессия № `{item.session_phone}`\n{alive}\n{renewed}",
                parse_mode='Markdown'
            )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен!")
    asyncio.run(main())
