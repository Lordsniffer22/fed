import logging
import sys
import asyncio
from aiogram import Bot, Dispatcher, html, F, Router, types
import os
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pytube import YouTube
import requests
import aiofiles
import time


load_dotenv()
TOKEN = os.getenv('TOKEN')
dp = Dispatcher()


async def download_and_convert_to_mp3(video_url):
    yt = YouTube(video_url)
    video_title = yt.title
    stream = yt.streams.filter(only_audio=True).first()
    #stream = yt.streams.filter(res="360p").first()
    if stream:
        file_path = stream.download()
        mp3_file = f"{video_title}.mp3"
        time.sleep(5)
        os.rename(file_path, mp3_file)
        return mp3_file
    else:
        return None

async def send_mp3_file(message: types.Message, video_url: str):
    mp3_file = await download_and_convert_to_mp3(video_url)
    chat_id = message.chat.id
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"

    # Open the file in binary mode and send it as a document using the requests library
    with open(mp3_file, "rb") as file:
        files = {"document": file}
        params = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=params)

    if response.status_code == 200:
        print("File sent successfully!")
    else:
        print(f"Failed to send file. Error: {response.text}")

async def check_youtube(message: types.Message):
    return message.text.startswith('https://www.youtube.com/') or message.text.startswith('https://youtu.be/')



@dp.message()
async def handle_message(message: types.Message) -> None:
    is_yt_link = await check_youtube(message)

    if is_yt_link:
        builder = InlineKeyboardBuilder()
        markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='MP3', callback_data='rm_usa'),
        InlineKeyboardButton(text='Video', callback_data='rm_brazil')]
    ])  # Some markup
        builder.attach(InlineKeyboardBuilder.from_markup(markup))
        await message.answer("Choose a format:", reply_markup=builder.as_markup())
        await send_mp3_file(message, message.text)
    if message.text.strip() == '/admin':
        await message.answer('You are admin Ted Hackwell @hackwell101')
    elif not is_yt_link:
        await message.answer("Only Youtube Links are accepted. Try again later!")
        pass
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Listening..')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
