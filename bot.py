import asyncio
import uuid

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from downloader import NginxAPIDownloader
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
import config


async def simple_handler(message: types.Message, downloader: NginxAPIDownloader):
    await message.answer("Скачиваю...")

    filepath = "file.pdf"
    await downloader.download(message.document, filepath)

    downloaded_file = types.FSInputFile(filepath)
    await message.answer_document(
        document=downloaded_file,
        caption="Файл успешно скачан!"
    )

    # await downloader.download(message.document, "file.txt")
    # await downloader.download(message.photo[0].file_id, "file.jpg")
    # ...


async def handle_document(message: types.Message, bot: Bot, downloader: NginxAPIDownloader):
    try:
        try:
            file_id = message.document.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            # file_name = uuid.uuid4().hex + '.txt'
            # downloaded_file = await bot.download_file(file_path=file_path)
            doc = await downloader.download(message.document, file_path)
            text = doc.getvalue().decode()
            """with open(downloaded_file, 'r', encoding='utf-8') as f:
                content = f.read()"""
            await message.reply(f'Документ прочитан, он имеет {len(text)} символов')
            # os.remove(downloaded_file)
        except Exception as e:
            print(f'error while downloading: {e}')
    except Exception as e:
        print(e)
        await message.reply(f'Возникла ошибка')


async def main():
    session = AiohttpSession(api=TelegramAPIServer.from_base(config.TELEGRAM_API_URL, is_local=True))
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML, session=session)
    storage = MemoryStorage()
    nginx_downloader = NginxAPIDownloader(bot=bot, url=config.NGINX_API_URL)

    dp = Dispatcher(storage=storage, downloader=nginx_downloader)
    dp.message.register(simple_handler)
    dp.message.register(handle_document, F.content_type == 'document')

    try:
        await bot.delete_webhook(True)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
