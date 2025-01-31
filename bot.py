import asyncio
import uuid

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from downloader import NginxAPIDownloader
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
import config


async def handle_document(message: types.Message, downloader: NginxAPIDownloader):
    try:
        try:
            file_name = uuid.uuid4().hex + '.txt'
            print(file_name)
            await downloader.download(message.document, file_name)
            with open(file_name, 'r', encoding='utf-8') as f:
                content = f.read()
            await message.reply(f'Документ прочитан, он имеет {len(content)} символов')
            # os.remove(downloaded_file)
        except Exception as e:
            print(f'error while downloading: {e}')
    except Exception as e:
        print(e)
        await message.reply(f'Возникла ошибка')


async def main():
    session = AiohttpSession(api=TelegramAPIServer.from_base(config.TELEGRAM_API_URL, is_local=True))
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML,
                                                                   link_preview_is_disabled=True), session=session)
    storage = MemoryStorage()
    nginx_downloader = NginxAPIDownloader(bot=bot, url=config.NGINX_API_URL)

    dp = Dispatcher(storage=storage, downloader=nginx_downloader)
    dp.message.register(handle_document, F.content_type == 'document')

    try:
        await bot.delete_webhook(True)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
