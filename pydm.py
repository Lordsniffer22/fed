import logging
import sys
import asyncio
from aiogram import Bot, Dispatcher, html, F, Router, types
import os
import re
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pytube import YouTube
import requests
import time


load_dotenv()
TOKEN = os.getenv('TOKEN')
dp = Dispatcher()
user_video_urls = {}

async def download_and_convert_to_mp3(video_url):
    yt = YouTube(video_url)
    video_title = yt.title
    stream = yt.streams.filter(only_audio=True).first()
    #stream = yt.streams.filter(res="360p").first()
    if stream:
        file_path = stream.download()
        mp3_file = f"{video_title}.mp3"
        time.sleep(15)
        os.rename(file_path, mp3_file)
        return mp3_file
    else:
        return None
async def send_mp3_file(message: types.Message, video_url: str):
    mp3_file = await download_and_convert_to_mp3(video_url)
    chat_id = message.chat.id
    url = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
    tyto = mp3_file
    caption = f"Audio: {tyto}\n\nBot: @TubyDoo_bot"  # Modify this caption as needed
    progress_message = await message.answer('Fetching the MP3 File\n[■■■□□□□□□□] 30%')
    time.sleep(2)
    progress_message2 = await progress_message.edit_text('Processing the file\n[■■■■■□□□□□] 50%')
    time.sleep(2)
    progress_message3 = await progress_message2.edit_text('Uploading...\n[■■■■■■■□□□] 70%')
    time.sleep(2)
    await progress_message3.edit_text('[■■■■■■■■■■] 100% ✅')
    # Open the file in binary mode and send it as a document using the requests library
    with open(mp3_file, "rb") as file:
        files = {"audio": file}
        params = {"chat_id": chat_id, "caption": caption}
        response = requests.post(url, files=files, data=params)

    if response.status_code == 200:
        print("File sent successfully!")
        time.sleep(15)
        await message.delete()
        #await progress_message.delete()
        os.system("sudo rm -rf *.mp3")
    else:
        os.system("sudo rm -rf *.mp3")
        print(f"Failed to send file. Error: {response.text}")
async def download_in_video_only(video_url):
    yt = YouTube(video_url)
    video_title = yt.title
    stream = yt.streams.filter(res="360p").first()
    if stream:
        file_path = stream.download()
        mp4_file = f"{video_title}.mp4"
        time.sleep(3)
        os.rename(file_path, mp4_file)
        return mp4_file
    else:
        return None
async def send_mp4_video_or_document(message: types.Message, video_url: str):
    mp4_file = await download_in_video_only(video_url)
    chat_id = message.chat.id
    tyto = mp4_file
    caption = f"Video: {tyto}\n\nBot: @TubyDoo_bot"  # Modify this caption as needed

    # Check the size of the video file
    file_size = os.path.getsize(mp4_file)
    if file_size > 50 * 1024 * 1024:  # 50MB in bytes
            await message.answer('Am sorry, Telegram servers didnt allow me \nshare that video because its greater that 50mb. \nBut the admins are working on a better fix. \n\nTry other video links too')
            os.system("sudo rm -rf *.mp4")
    else:
        url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"# Modify this caption as needed
        progress_message = await message.answer('Fetching the Video\n[■■■□□□□□□□] 30%')
        time.sleep(2)
        progress_message2 = await progress_message.edit_text('Processing the Video\n[■■■■■□□□□□] 50%')
        time.sleep(2)
        progress_message3 = await progress_message2.edit_text('Uploading...\n[■■■■■■■□□□] 70%')
        time.sleep(2)
        await progress_message3.edit_text('[■■■■■■■■■■] 100% ✅')
        # Open the file in binary mode and send it as a document using the requests library
        with open(mp4_file, "rb") as file:
            files = {"video": file}
            params = {"chat_id": chat_id, "caption": caption}
            response = requests.post(url, files=files, data=params)

        if response.status_code == 200:
            print("File sent successfully!")
            time.sleep(15)
            await message.delete()
           # await progress_message.delete()
            os.system("sudo rm -rf *.mp4")
        else:
            os.system("sudo rm -rf *.mp3")
            print(f"Failed to send file. Error: {response.text}")


async def check_youtube(message: types.Message):
    return message.text.startswith('https://www.youtube.com/') or message.text.startswith('https://youtu.be/')

async def check_if_youtube(message: types.Message):
    # Regular expression pattern to match YouTube URLs
    youtube_pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+(&\S+)?'
    return re.search(youtube_pattern, message.text) is not None
@dp.message()
async def handle_message(message: types.Message) -> None:
    is_yt_link = await check_youtube(message)
    re_yt_link = await check_if_youtube(message)

    if is_yt_link:
        user_video_urls[message.chat.id] = message.text
        time.sleep(2)
        await message.delete()
        builder = InlineKeyboardBuilder()
        markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='MP3', callback_data='get_mp3'),
        InlineKeyboardButton(text='Video', callback_data='get_video')]
    ])  # Some markup
        builder.attach(InlineKeyboardBuilder.from_markup(markup))
        await message.answer("Choose a format:\n══════════════════\nYoutube Video Downloader\nBot: @tubyDoo_bot ", reply_markup=builder.as_markup())

        #await send_mp3_file(message, message.text)
    if message.text.strip() == '/start':
        await message.answer('Hello, just forwad me a video link here or any message that has a youtube video . \n\nJoin our Community: \n--> @udpcustom')
    elif re_yt_link:
        user_video_urls[message.chat.id] = message.text
        time.sleep(2)
        await message.delete()
        builder = InlineKeyboardBuilder()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Get MP3', callback_data='get_mp3'),
             InlineKeyboardButton(text='Get Video', callback_data='get_video')]
        ])  # Some markup
        builder.attach(InlineKeyboardBuilder.from_markup(markup))
        await message.answer("Choose a format:\n══════════════════\nYoutube Video Downloader\nBot: @tubyDoo_bot", reply_markup=builder.as_markup())
        # await send_mp3_file(message, message.text)
        pass
# Handler for inline keyboard button clicks
@dp.callback_query(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    option = callback_query.data
    user_id = callback_query.from_user.id
    # Get the video URL for the user
    video_url = user_video_urls.get(user_id)

    # Call different functions based on the button clicked
    if option == 'get_mp3':
        if video_url:
            await send_mp3_file(callback_query.message, video_url)
        else:
            await callback_query.answer("Video URL not found. Please send a YouTube link first.")
    elif option == 'get_video':
        if video_url:
            await send_mp4_video_or_document(callback_query.message, video_url)
        else:
            await callback_query.answer("Video URL not found. Please send a YouTube link first.")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Listening..')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
