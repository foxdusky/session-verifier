import os
import zipfile
import json
import asyncio
import rarfile
import re
from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, AuthRestartError

from config import logger, settings, GET_RANDOM_PROXY
from schemes.processing_result import ProcessingResult


async def _process_session(phone: str, api_id: int, api_hash: str) -> ProcessingResult | None:
    proxy = GET_RANDOM_PROXY
    session_renewed = False
    spam_blocked = False
    old_session_path: str = os.path.join(settings.TEMP_DIR, phone + ".session")  # type: ignore
    new_session_name: str = os.path.join(settings.SESSION_DIR, phone)  # type: ignore

    if not os.path.exists(old_session_path):
        logger.info(f"[!] Нет session файла для {phone}, пропуск.")
        return None
    try:

        client1 = TelegramClient(old_session_path, api_id, api_hash)
        await client1.connect()

        if not await client1.is_user_authorized():
            logger.info(f"[!] Сессия {phone} невалидна.")
            await client1.disconnect()
            return None

        client2 = TelegramClient(new_session_name, api_id, api_hash)
        await client2.connect()
        if not client2.is_connected():
            logger.info(f"[❌] client2 не подключён для {phone}")
            await client2.disconnect()
            await client1.disconnect()
            return None

        try:
            sent = await client2.send_code_request(phone)
        except AuthRestartError:
            logger.info(f"[❌] Telegram требует перезапустить авторизацию для {phone}")
            await client2.disconnect()
            await client1.disconnect()
            return None

        logger.info(f"[📨] Отправлен код для {phone} — ждём сообщение от Telegram...")
        await asyncio.sleep(3)

        code = None
        async for msg in client1.iter_messages('Telegram', limit=10):
            match = re.search(r'\b\d{5}\b', msg.message)
            if match:
                code = match.group(0)
                logger.info(f"[✓] Код получен: {code}")
                break

        if not code:
            logger.info(f"[❌] Не удалось получить код для {phone}")
            await client2.disconnect()
            client2 = client1
        else:
            try:
                await client2.sign_in(phone=phone, code=code)
                logger.info(f"[🔐] Новая сессия создана для {phone}")
                session_renewed = True
            except PhoneCodeInvalidError:
                logger.info(f"[❌] Неверный код авторизации для {phone}")
                await client1.disconnect()
                await client2.disconnect()
                return None

        await client2.send_message('@SpamBot', '/start')
        await asyncio.sleep(3)

        async for msg in client2.iter_messages('@SpamBot', limit=1):
            text = msg.message.lower()
            if 'limited' in text or 'spam' in text:
                spam_blocked = True
        await client1.disconnect()
        await client2.disconnect()

    except Exception as e:
        logger.error(f"[Ошибка] {phone}: {e}")
    return ProcessingResult(session_phone=phone, spam_blocked=spam_blocked, renewed_session=session_renewed)


async def process_archive(archive_name: str) -> list[ProcessingResult | None]:
    archive_path = os.path.join(settings.TEMP_DIR, archive_name)
    tasks = []
    if archive_path.endswith('.rar'):
        with rarfile.RarFile(archive_path) as rf:
            rf.extractall(settings.TEMP_DIR)
    else:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(settings.TEMP_DIR)

    for filename in os.listdir(settings.TEMP_DIR):
        if not filename.endswith('.json'):
            continue

        json_path = os.path.join(settings.TEMP_DIR, filename)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        phone = data["phone"]
        api_id = data["app_id"]
        api_hash = data["app_hash"]

        tasks.append(_process_session(phone, api_id, api_hash))

    return await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(process_archive("test.zip"))
