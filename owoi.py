
import os
import asyncio
import logging
import sys
import time
import re
import random
import aiohttp

import json

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timedelta
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InputFile
import sqlite3


# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TELEGRAM_BOT_TOKEN = '6997767656:AAF6arfo9vFhaBF3zQac8R9Tw8cdQEeNR1o'
ADMIN_CHAT_ID = '6448112643'

# Dispatcher initialization
dp = Dispatcher()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Initialize the SQLite database
conn = sqlite3.connect('bot_data.db')
cursor = conn.cursor()

# Function to check if a column exists in a table
def column_exists(table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    return column_name in columns

# Add new column 'timestamp' if it doesn't exist
def add_column_if_not_exists(table_name, column_name, column_type):
    if not column_exists(table_name, column_name):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        conn.commit()

# Create tables if they do not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        user_id INTEGER PRIMARY KEY,
        data TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ad_requests (
        requester_id TEXT PRIMARY KEY,
        data TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ad_contents (
        content_id TEXT PRIMARY KEY,
        data TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS advertiza (
        user_id TEXT PRIMARY KEY,
        data TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS ad_request_messages (
        message_id TEXT PRIMARY KEY,
        data TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        data TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS verified_users (
        user_id INTEGER PRIMARY KEY,
        data TEXT
    )
''')

# Add the new column to the tables

add_column_if_not_exists('ad_contents', 'user_id', 'TEXT')
add_column_if_not_exists('ad_contents', 'timestamp', 'TEXT')
add_column_if_not_exists('user_data', 'timestamp', 'TEXT')
add_column_if_not_exists('verified_users', 'timestamp', 'TEXT')
add_column_if_not_exists('advertiza', 'timestamp', 'TEXT')
add_column_if_not_exists('ad_requests', 'user_id', 'TEXT')
add_column_if_not_exists('ad_requests', 'timestamp', 'TEXT')

conn.commit()

# In-memory data structures
user_data = {}
ad_requests = {}
ad_contents = {}
advertiza = {}
ad_request_messages = {}
payments = {}
verified_users = {}
verif_reqs = {}

def save_data(table, key, data):
    data_to_save = data.copy()  # Create a copy of the data dictionary
    if 'verification_step' in data_to_save:
        del data_to_save['verification_step']  # Remove the verification_step key

    timestamp = datetime.now().isoformat()
    cursor.execute(f"INSERT OR REPLACE INTO {table} (user_id, data, timestamp) VALUES (?, ?, ?)", (key, json.dumps(data_to_save), timestamp))
    conn.commit()


def load_data(table, key):
    cursor.execute(f"SELECT data FROM {table} WHERE user_id = ?", (key,))
    row = cursor.fetchone()
    return json.loads(row[0]) if row else None


def delete_data(table, key):
    cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (key,))
    conn.commit()


def load_all_data():
    cursor.execute("SELECT user_id, data FROM user_data")
    for row in cursor.fetchall():
        user_data[row[0]] = json.loads(row[1])

    #cursor.execute("SELECT requester_id, data FROM ad_requests")
    cursor.execute("SELECT user_id, data FROM ad_requests")
    for row in cursor.fetchall():
        user_id, data = row
        ad_requests[user_id] = json.loads(data)
    return ad_requests

    cursor.execute("SELECT content_id, data FROM ad_contents")
    for row in cursor.fetchall():
        ad_contents[row[0]] = json.loads(row[1])

    cursor.execute("SELECT user_id, data FROM advertiza")
    for row in cursor.fetchall():
        advertiza[row[0]] = json.loads(row[1])

    cursor.execute("SELECT message_id, data FROM ad_request_messages")
    for row in cursor.fetchall():
        ad_request_messages[row[0]] = json.loads(row[1])

    cursor.execute("SELECT payment_id, data FROM payments")
    for row in cursor.fetchall():
        payments[row[0]] = json.loads(row[1])

    cursor.execute("SELECT user_id, data FROM verified_users")
    for row in cursor.fetchall():
        verified_users[row[0]] = json.loads(row[1])


load_all_data()


async def recieve_video(message: types.Message):
    okay = await message.reply("😍Glad you've finished adding the Advert to your new Video\n\n")
    await asyncio.sleep(4)
    await okay.delete()
    await asyncio.sleep(1)
    await message.reply("Please enter the video link:")
    user_data[message.from_user.id] = {'step': 'video_link'}

def calculate_price_with_markup(price):
    return price * 1.20  # Add 20% markup


# Function to generate a random unique ID of up to 8 digits
def generate_unique_id():
    return str(random.randint(10000000, 99999999))

async def send_welcome(message: types.Message):
    full_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    user_id = message.from_user.id

    if user_id in verified_users:
        await message.reply(f"Welcome Back {full_name}!"
                            f"\n\nWe are glad you are here with us again😍\n"
                            f"╰┈➤Press: /help ")
    else:
        caption = "Reach millions of potential customers on TikTok through us! \n\nWe connect advertisers with popular TikTok creators who have a large following ready to buy your products or services. \n\nType '/help' to learn more on how to get started!"
        photo_url = 'https://raw.githubusercontent.com/Lordsniffer22/fed/main/start.jpg'  # Replace with your photo URL
        await send_photo_from_url(user_id, photo_url, caption=caption)
async def send_help(message: types.Message):
    await message.reply("<b>This Bot now manages both TikTok content creators and Advertisers.</b>\n═══════════════════════════\n\n"
                        "<b>TikTokers</b>\n─────────────────\n\n"
                        "✨- To sign up, send /register to this chat and follow the prompts.\n\n"  
                        "✨- To submit your video where you have included the Advert, send /done to this chat and follow the prompts\n\n"                        
                        "<b>Advertisers</b>\n─────────────────\n\n"
                        "🗽- Advertisers Dont need to sign up. (You are flexible)\n\n"
                        "⊷▷Visit @adskity and look for a tiktoker you think will suit your marketing needs\n\n"
                        "⊷▷Press on 'Place AD' button to submit your request. We shall send you the Instructions through this bot.\n\n"
                        "<b>👉Confirm this:</b>\n─────────────────\nThe Adskit ID displayed on each Ad Space in the channel is also there on the Tiktoker's account if you visit his/her tiktok account.\n\n"
                        "<b><i>⚠️Note: Adskit (Tiktok spaces) Is not owned by ByteDance Ltd (TikTok).</i></b>\n\n",
                        parse_mode=ParseMode.HTML)
async def start_verification(message: types.Message):
    user_id = message.from_user.id

    if user_id in verified_users:
        await message.reply("You are already registered and verified with us.\n\nForgot Your Account ID? Look for it here: @adskity \n\nContact us for assistace: adskit1@gmail.com")
        return


    user_data[user_id] = {
        'verification_step': 'awaiting_link',
        'unique_id': generate_unique_id()  # Generate and store the unique ID
    }
    okay = await message.reply('You are now signing up as a TikToker!')
    await asyncio.sleep(3)
    await okay.delete()
    await asyncio.sleep(1)
    await message.reply("🤝Let's begin.\n\nSend me a link to Your tiktok account or to any of your videos.🤷‍♂️")

async def check_if_tiktok(message: types.Message):
    # Regular expression pattern to match TikTok URLs
    tiktok_pattern = r'(https?://)?(www\.)?(vm\.tiktok\.com/|tiktok\.com/@[\w.-]+/video/)[\w-]+'
    return re.search(tiktok_pattern, message.text) is not None

async def handle_cancel(message: types.Message):
    user_id = message.from_user.id
    if user_data.get(user_id, {}).get('step') == 'video_link':
        user_data[user_id]['step'] = None
        save_data('user_data', user_id, user_data[user_id])  # Save the updated data
        await message.reply("The current process has been cancelled. You can start again if you wish.")
    else:
        await message.reply("There is no ongoing process to cancel.")
async def cancel_user_reg(message: types.Message):
    if message.text.lower() == '/cancel':
        user_data[message.from_user.id]['verification_step'] = None
        save_data('user_data', message.from_user.id, user_data[message.from_user.id])
        await message.reply("Operation Terminated. You can start again anytime if you wish.")
        return True
    return False
async def cancel_done(message: types.Message):
    if message.text.lower() == '/cancel':
        user_data[message.from_user.id]['step'] = None
        save_data('user_data', message.from_user.id, user_data[message.from_user.id])
        await message.reply("Operation Terminated. You can start again anytime if you wish.")
        return True
    return False
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('step') == 'video_link')
async def process_video_link(message: types.Message):
    if await cancel_done(message):
        return
    if await check_if_tiktok(message):
        user_data[message.from_user.id]['video_link'] = message.text
        user_data[message.from_user.id]['step'] = 'payment_address'
        await message.reply("Please enter your payment address\n\n"
                            "It can be a phone number, Binance/Payeer ID or Chipper Cash tag")
    else:
        await message.reply("Please provide a valid TikTok link. \n\nSend /cancel to quit")

@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('step') == 'payment_address')
async def process_payment_address(message: types.Message):
    if await cancel_done(message):
        return
    user_data[message.from_user.id]['payment_address'] = message.text
    user_data[message.from_user.id]['step'] = 'order_id'
    await message.reply("What Order ID is this Video meant for?\n\nHint: Check the Ad Placement Request you recieved.")

@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('step') == 'order_id')
async def process_adskit_id(message: types.Message):
    user_id = message.from_user.id
    if await cancel_done(message):
        return
    user_data[message.from_user.id]['order_id'] = message.text
    video_link = user_data[message.from_user.id]['video_link']
    payment_address = user_data[message.from_user.id]['payment_address']
    order_id = user_data[message.from_user.id]['order_id']

    compiled_message = (
        f"Is this Correct?"
        f"\n───────────────────────\n"
        f"➤Video Link: {video_link}\n"
        f"➤Payment Address: {payment_address}\n"
        f"➤Order ID: {order_id}"
        f"\n\nBetter be sure of the payment info and order ID. If wrong press: /cancel"
    )
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Sure! 100%', callback_data=f"confirmed")]
    ])  # Some markup
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    confirma = await message.reply(compiled_message, reply_markup=builder.as_markup(), disable_web_page_preview=True, parse_mode=ParseMode.HTML)

    @dp.callback_query(lambda query: query.data == 'confirmed')
    async def handle_confirmation(query: types.CallbackQuery):
        user_id = query.from_user.id
        if user_id not in user_data:
            await query.answer("No data found to submit.")
            return

        video_link = user_data[user_id]['video_link']
        payment_address = user_data[user_id]['payment_address']

        order_id = user_data[user_id]['order_id']

        builder = InlineKeyboardBuilder()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Payment in Progress', callback_data=f"payment_process_{user_id}")]
        ])  # Some markup
        builder.attach(InlineKeyboardBuilder.from_markup(markup))
        compiled_message = (
            f"TikTok Video from @{query.from_user.username}:"
            f"\n─────────────────────────\n"
            f"➤Video Link: {video_link}\n"
            f"➤Payment Addr: {payment_address}\n"
            f"➤Order ID: {order_id}"
        )

        await bot.send_message(ADMIN_CHAT_ID, compiled_message, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await query.message.answer("Your information has been submitted for moderation.\nExpect to recieve your funds in less than 24 hours.")
        # Clear user data
        user_data.pop(user_id, None)
        await asyncio.sleep(3)

        await confirma.delete()

@dp.callback_query(lambda query: query.data.startswith('payment_process_'))
async def handle_payment_progress_callback(query: types.CallbackQuery):
    # Extract user_id from the callback data
    user_id = int(query.data.split('_')[2])
   # order_id = user_data[user_id]['order_id']
    await bot.send_message(user_id, f"We are processing your Payment. Expect it in less that 24 hours",
                           parse_mode=ParseMode.HTML)


#USER REGISTRATION SECTION

# Inside the handle_verification_link function
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_link')
async def handle_verification_link(message: types.Message):
    user_id = message.from_user.id
    if await cancel_user_reg(message):
        return
    if await check_if_tiktok(message):
        user_data[user_id]['link'] = message.text.strip()
        user_data[user_id]['verification_step'] = 'awaiting_profile_name'
        save_data('user_data', user_id, user_data[user_id])  # Save the entire dictionary
        await message.reply("🤔What's Your TikTok Account Name?\n\n╰┈➤Help Advertisers Know its You😎 ")
    else:
        await message.reply("Please provide a valid TikTok link. Either way, you can press /cancel to quit")

@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_profile_name')
async def handle_profile_name(message: types.Message):
    if await cancel_user_reg(message):
        return
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]['profile_name'] = message.text.strip()
    user_data[user_id]['verification_step'] = 'awaiting_followers'
    save_data('user_data', user_id, user_data[user_id])  # Save the entire dictionary

    await message.reply("How many followers do you have right now? \n\n-🛑 Wrong answers might lead to your account verification being neglected")



@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_followers')
async def handle_followers(message: types.Message):
    if await cancel_user_reg(message):
        return
    user_id = message.from_user.id
    user_data[user_id]['followers'] = message.text.strip()
    user_data[user_id]['verification_step'] = 'awaiting_location'
    save_data('user_data', user_id, user_data[user_id])  # Save the entire dictionary
    await message.reply("What country do your followers come from?\n\n╰┈➤Some Advertisers target specific Countries.")


@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_location')
async def handle_views(message: types.Message):
    user_id = message.from_user.id
    if await cancel_user_reg(message):
        return
    user_data[user_id]['location'] = message.text.strip()
    user_data[user_id]['verification_step'] = 'awaiting_price'
    save_data('user_data', user_id, user_data[user_id])  # Save the entire dictionary
    await message.reply("How much do you charge for an Advert?.\n\n⊚ Include Your Currency ( eg $5 or UGX 20,000, etc)\n\n╰┈➤A lower price brings more advertisers to you. Set wisely!")


@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_price')
async def handle_price(message: types.Message):
    if await cancel_user_reg(message):
        return
    user_id = message.from_user.id
    price_text = message.text.strip()

    # Extract digits from the message
    match = re.search(r'\d+', price_text)
    if match:
        original_price = float(match.group())
        new_price = calculate_price_with_markup(original_price)
        currency = re.sub(r'\d+', '', price_text).strip()  # Extract the currency text

        user_data[user_id]['price'] = f"{currency} {new_price}"
        user_data[user_id]['verification_step'] = None
        unique_id = user_data[user_id]['unique_id']  # Retrieve the unique ID
        save_data('user_data', user_id, user_data[user_id])  # Save the entire dictionary

    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Decline', callback_data=f"decline_link_{user_id}"),
    InlineKeyboardButton(text='Approve', callback_data=f"verify_link_{user_id}")]
    ])  # Some markup
    builder.attach(InlineKeyboardBuilder.from_markup(markup))


    reqx = await bot.send_message(ADMIN_CHAT_ID,
                           f"👮🏽‍♀️A TikTok Creator @{message.from_user.username}  Seeks Verification!\n"
                            f"─────────────────────────────\n\n"
                           f"TikTok Name: {user_data[user_id]['profile_name']}\n"
                           f"Followers: {user_data[user_id]['followers']}\n"
                           f"Location: {user_data[user_id]['location']}\n"
                           f"Price Per Ad: {user_data[user_id]['price']}\n\n"
                           f"Link: {user_data[user_id]['link']}\n"
                           f"➤Account ID: {unique_id}\n\n"
                           f"Please verify the link.", reply_markup=builder.as_markup())
    verif_reqs[user_id] = reqx.message_id
    # Prepare the "Send " button
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='See example', callback_data=f"check_the_sample_{user_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))
    okay = await message.reply('Saving your registration form...!')
    await asyncio.sleep(3)
    await okay.delete()
    await asyncio.sleep(1)
    await message.reply(f"Submitted Your Details for Verification. This usually takes 24 hours or less! Keep Alert🔊\n\n<i>💡Make sure you add your Adskit ID to your Bio Section on tiktok. It must stay visible, and should appear in the format below:</i>\n\n<code>Adskit ID: {unique_id}</code>", parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
@dp.callback_query(lambda query: query.data.startswith('check_the_sample_'))
async def handle_accept_ad_callback(query: types.CallbackQuery):
    parts = query.data.split('_')
    requester_id = int(parts[3])

    await asyncio.sleep(3)
    # Send the photo from URL with caption "Lorem ipsum"
    caption = ""
    photo_url = 'https://raw.githubusercontent.com/Lordsniffer22/fed/main/example2.jpg'  # Replace with your photo URL
    await send_photo_from_url(requester_id, photo_url, caption=caption)

#  Approve user registration
@dp.callback_query(lambda query: query.data.startswith('verify_link_'))
async def handle_verify_link_callback(query: types.CallbackQuery):
    # Extract user_id from the callback data
    user_id = int(query.data.split('_')[2])
    requester_id = int(query.data.split('_')[2])

    builder2 = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Place AD', callback_data=f"place_ad_{user_id}")]
    ])  # Some markup
    builder2.attach(InlineKeyboardBuilder.from_markup(markup))

    unique_id = user_data[user_id]['unique_id']

    # Notify the user that their link has been verified
    await bot.send_message(user_id, f"Your Account has been Approved 🎉\n\n<b>What Next:</b>\n✨Advertising companies will glance at your TikTok account.  Focus on making it more appealing 🤗 \n\nKeep an eye @adskity\n\n✅<b>Your Adskit ID:</b> <code>{unique_id}</code>",
                           parse_mode=ParseMode.HTML)
    verified_users[user_id] = user_data[user_id]  # Add user to verified users
    save_data('verified_users', user_id, user_data[user_id])
    save_data('ad_requests', requester_id, user_data[user_id])
    await query.answer('User has been verified Successfully!')

    # Send a message to the channel notifying about the verified link
    channel_id = '-1002061815083'  # Replace with your channel ID
    profile_link = user_data[user_id]['link']
    # Create the clickable hyperlink
    profile_link_html = f"<a href='{profile_link}'>CLICK</a>"

    await bot.send_message(channel_id,
                           f"<b>  🗣 New Ad space </b>👀\n═════════════════\n➤<b>Platform:</b> -TikTok\n➤<b>Username:</b> -{user_data[user_id]['profile_name']}\n➤<b>Followers:</b> #{user_data[user_id]['followers']}\n➤<b>Location:</b> -{user_data[user_id]['location']}\n\n🛒 Price Per Ad💰:\n─────────────\n╰┈➤{user_data[user_id]['price']}\n\n🥳 Profile link: {profile_link_html}\n\n<b>⊛Adskit ID:</b> <code>{unique_id}</code>",
                           disable_web_page_preview=True,
                           parse_mode=ParseMode.HTML,  # Set parse_mode to HTML
                           reply_markup=builder2.as_markup())


    await bot.send_message(ADMIN_CHAT_ID,f"[■■■■ Verified] 100% ✅")
    # Delete the previous ad request message
    print(verif_reqs)
    if user_id in verif_reqs:
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=user_id, message_id=verif_reqs[user_id])
        del verif_reqs[user_id]
@dp.callback_query(lambda query: query.data.startswith('place_ad_'))
async def handle_place_ad_callback(query: types.CallbackQuery):
    # Extract user_id from the callback data
    user_id = int(query.data.split('_')[2])
    requester_id = query.from_user.id


    # Check if the user has already requested to place an ad for this post
    if requester_id in ad_requests and user_id in ad_requests[requester_id]:
        await query.answer("You already requested to place an ad on this one.")
        return

    # Register the ad request
    if requester_id not in ad_requests:
        ad_requests[requester_id] = set()
    ad_requests[requester_id].add(user_id)

    ## Prepare the "Tell Him" button
    #builder = InlineKeyboardBuilder()
    #markup = InlineKeyboardMarkup(inline_keyboard=[
     #   [InlineKeyboardButton(text='Send Procedures', callback_data=f"tell_him_{requester_id}")]
    #])
    #builder.attach(InlineKeyboardBuilder.from_markup(markup))

    # Notify the admin about the ad request
    await bot.send_message(ADMIN_CHAT_ID,
                           f"A user wants to place an ad on {user_data[user_id]['profile_name']}'s TikTok profile.\n\n"
                           f"I just sent him the instructions in about 10 seconds",
                           )
    await query.answer("✅Request submitted. Check the Bot to complete the AD placement process😀")
    # Notify the profile owner about the ad request
    await bot.send_message(user_id,
                           "🎊Good News!😀\n\nAn advertiser just glanced at your  TikTok Ad Space🎉\n\n💐We will let you know if he requests to advertise with you ✨")
    # Send instructions to the requester
    await asyncio.sleep(3)

    instructions = ("Advert Placement Guide🤓\n══════════════════\n\n"
                    "Prepare and send us your Advert in any of these formats:\n"
                    "-Text only\n"
                    "-Picture with caption.\n"
                    "-Video with Caption\n\n"
                    "🛑Please Make sure your texts or Video/Photo caption start with #Adcontent as the trigger."
                    )

    await bot.send_message(requester_id, instructions)



async def send_photo_from_url(chat_id: int, photo_url: str, caption: str):
    await bot.send_photo(chat_id, photo=photo_url, caption=caption)

# New handler for photos with #Adcontent in the caption
@dp.message(lambda message: message.photo and "#Adcontent" in message.caption)
async def handle_ad_photo(message: types.Message):
    requester_id = message.from_user.id
    advertiza[requester_id] = {
        'order_id': generate_unique_id(), # Generate and store the unique ID
        'photo_ids': [photo.file_id for photo in message.photo]  #Store the photo IDs
    }
    order_id = advertiza[requester_id]['order_id']
    save_data('advertiza', requester_id, advertiza[requester_id])


    if requester_id not in ad_requests:
        await message.reply("You have not requested to place an ad yet. Please click the 'Place AD' button in the channel.")
        return

    # Extract the ad content from the caption
    ad_content = message.caption.replace("#Adcontent", "").strip()


    # Store the ad content in ad_contents
    ad_contents[requester_id] = {'ad_content': ad_content}
    save_data('ad_contents', requester_id, ad_contents[requester_id])  # Save ad_contents to database
    #save_data('ad_requests', requester_id, advertiza[requester_id])

    # Prepare the "Send to Tiktoker" button
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Send to Tiktoker', callback_data=f"sendp_to_tiktoker_{requester_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))


    # Forward the photo to the admin along with the caption
    await bot.send_photo(
        ADMIN_CHAT_ID,
        photo=message.photo[-1].file_id,  # The highest resolution photo
        caption=f"Ad Content from from Advertiser @{message.from_user.username}:\n\n{ad_content}\n\n<b>Order ID:</b> <code>{order_id}</code>",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML)

    await message.reply(f"Your Ad has been submitted.\n\n<b>Your order ID is:</b> <code>{order_id}</code> \n\nThis order automatically cancels if the escrow team doesnt recieve a payment from you within 2 hours.", parse_mode=ParseMode.HTML)
    await asyncio.sleep(18)
    # Prepare the "Send " button
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='How to Send Proof?', callback_data=f"how_to_prove_{requester_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))
    await message.answer("⭐️Your Advert has been confirmed!\n───────────────────────\n\n"
                    "Make a payment that the TikToker set on <a href='t.me/adskity'>TikTok spaces</a>Channel.\n\n"
                    "Payment Methods:\n───────────────────────\n\n"
                    "<b>💰Binance ID:</b> <code>772986361</code>\n\n"
                    f"⚡<b>Momo Payments:</b> <a href='t.me/AdskitBot/Payment'>Click2Pay</a>\n\n"
                    "✅Other Fiat Currencies coming soon..\n\n"
                    "Immediately Report to us at adskity@gmail.com if you find issues with the ADs you paid for.", disable_web_page_preview=True, reply_markup=builder.as_markup())

@dp.callback_query(lambda query: query.data.startswith('how_to_prove_'))
async def handle_accept_ad_callback(query: types.CallbackQuery):
    parts = query.data.split('_')
    requester_id = int(parts[3])

    await asyncio.sleep(3)
    # Send the photo from URL with caption "Lorem ipsum"
    photo_url = 'https://raw.githubusercontent.com/Lordsniffer22/fed/main/example.jpg'  # Replace with your photo URL
    await send_photo_from_url(requester_id, photo_url, "🤡 Follow that format.\n\nNote: Order ID must be attached too.")

    # Acknowledge the user's action
    await query.answer("Ad request accepted✅.")



@dp.message(lambda message: message.photo and "#paid" in message.caption)
async def handle_ad_photo(message: types.Message):
    requester_id = message.from_user.id
   # if requester_id not in ad_requests:
    #    await message.reply("You have not requested to place an ad yet. Please click the 'Place AD' button in the channel.")
    #    return

    # Extract the ad content from the caption
    addeitionals = message.caption.replace("#paid", "").strip()

    # Store the ad content
    payments[requester_id] = addeitionals

    # Forward the photo to the admin along with the caption
    await bot.send_photo(
        ADMIN_CHAT_ID,
        photo=message.photo[-1].file_id,  # The highest resolution photo
        caption=f"Proof of payment from: @{message.from_user.username}:\n\n{addeitionals}\n",
        parse_mode=ParseMode.HTML)
    await asyncio.sleep(10)
    await message.reply(f"Recieved your proof of payment. \n\nThe escrow department is reviewing it. We shall inform the tiktoker to publish the Advert as soon as the review is done.", parse_mode=ParseMode.HTML)


@dp.message(lambda message: message.text and message.text.startswith('#Adcontent'))
async def handle_ad_content(message: types.Message):
    requester_id = message.from_user.id

    # Generate and store the unique ID in advertiza
    advertiza[requester_id] = {
        'order_id': generate_unique_id()
    }
    order_id = advertiza[requester_id]['order_id']
    save_data('advertiza', requester_id, advertiza[requester_id])  # Save advertiza to database

    ad_content = message.text[len('#Adcontent'):].strip()

    if requester_id not in ad_requests:
        await message.reply(
            "You have not requested to place an ad yet. Please click the 'Place AD' button in the channel.")
        return

    # Store the ad content in ad_contents
    ad_contents[requester_id] = {'ad_content': ad_content}
    save_data('ad_contents', requester_id, ad_contents[requester_id])  # Save ad_contents to database
    #save_data('ad_requests', requester_id, ad_contents[requester_id])  # Save ad_contents to database


    # Prepare the "Send to Tiktoker" button
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Send to Tiktoker', callback_data=f"send_to_tiktoker_{requester_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    # Notify the admin with the ad content
    await bot.send_message(ADMIN_CHAT_ID,
                           f"Ad content from Advertiser @{message.from_user.username}:\n\n{ad_content}\n\n\n\n<b>Order ID:</b> <code>{order_id}</code>",
                           parse_mode=ParseMode.HTML,
                           reply_markup=builder.as_markup())
    await message.reply(f"Your Ad has been submitted. \n\nYour order ID is: <code>{order_id}</code> \n\nThis order automatically cancels if the escrow team doesnt recieve a payment from you.", parse_mode=ParseMode.HTML)
    await asyncio.sleep(18)
    # Prepare the "Send " button
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='How to Send Proof?', callback_data=f"how_to_prove_{requester_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))
    await message.answer("⭐️Your Advert has been confirmed!\n───────────────────────\n\n"
                    "Make a payment that the TikToker set on <a href='t.me/adskity'>TikTok spaces</a>Channel.\n\n"
                    "Payment Methods:\n───────────────────────\n\n"
                    "<b>💰Binance ID:</b> <code>772986361</code>\n\n"
                    f"⚡<b>Momo Payments:</b> <a href='t.me/AdskitBot/Payment'>Click2Pay</a>\n\n"
                    "✅Other Fiat Currencies coming soon..\n\n"
                    "Immediately Report to us at adskity@gmail.com if you find issues with the ADs you paid for.", disable_web_page_preview=True, reply_markup=builder.as_markup())

@dp.callback_query(lambda query: query.data.startswith('sendp_to_tiktoker_'))
async def handle_send_to_tiktoker_callback(query: types.CallbackQuery):
    # Extract requester_id from the callback data
    requester_id = int(query.data.split('_')[3])

    print(f"Handling callback for requester_id: {requester_id}")
    print(f"Current ad_requests: {ad_requests}")

    # Check if requester_id is in ad_requests
    if requester_id not in ad_requests:
        await query.answer("Could not find the associated TikTok profile owner.")
        return

    # Retrieve user_id from ad_requests
    user_data = ad_requests[requester_id]
    user_id = next(iter(user_data), None)  # Get the first (and possibly only) key

    order_id = advertiza.get(requester_id, {}).get('order_id', "No order ID")

    if not user_id:
        await query.answer("Could not find the associated TikTok profile owner.")
        return

    # Ensure that the requester_id has the 'photo_ids' key
    if requester_id not in advertiza or 'photo_ids' not in advertiza[requester_id]:
        await query.answer("No photo found for this ad request.")
        return

    # Retrieve the photo IDs from the stored data
    photo_ids = advertiza[requester_id]['photo_ids']

    # Check if photo IDs are retrieved successfully
    if not photo_ids:
        await query.answer("No photo IDs found for this ad request.")
        return

    try:
        # Retrieve and format the ad content
        raw_ad_content = ad_contents.get(requester_id, {}).get('ad_content', "No ad content provided.")
        ad_content = (
            f"⭐️💰<b>Ad placement Request.</b>💰\n"
            "──────────────────────────\n"
            "<i>- We request that you include this Advert in your next Tiktok video:</i>\n\n"
            "<b>Ad Content:</b>\n\n"
            f"<code>{raw_ad_content}</code>\n"
            "──────────────────────────\n"
            f"<b>Order ID: </b><code>{order_id}</code>")
        photo_id = photo_ids[-1]  # Use the highest resolution photo

        builder = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Decline❌',
                                  callback_data=f"decline_ad_{requester_id}_{user_id}_{query.message.message_id}"),
             InlineKeyboardButton(text='Accept✅', callback_data=f"accept_ad_{requester_id}_{user_id}")]
        ])

        ad_request_message = await bot.send_photo(user_id, photo=photo_id, caption=ad_content, parse_mode=ParseMode.HTML, reply_markup=builder)
        ad_request_messages[user_id] = ad_request_message.message_id  # Store the message ID

        # Acknowledge the user's action
        await query.answer("Ad content sent to the TikTok profile owner.")
    except Exception as e:
        print(f"Error sending photo: {e}")



@dp.callback_query(lambda query: query.data.startswith('send_to_tiktoker_'))
async def handle_send_to_tiktoker_callback(query: types.CallbackQuery):
    # Extract requester_id from the callback data
    requester_id = int(query.data.split('_')[3])
    user_id = next((u for u in ad_requests[requester_id]), None)
    order_id = advertiza[requester_id]['order_id']
    if not user_id:
        await query.answer("Could not find the associated TikTok profile owner.")
        return


    # Retrieve the ad content
    ad_data = ad_contents.get(requester_id, {})
    ad_content = ad_data.get('ad_content', "No ad content provided.")

    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Decline❌', callback_data=f"decline_ad_{requester_id}_{user_id}_{query.message.message_id}"),
        InlineKeyboardButton(text='Accept✅', callback_data=f"accept_ad_{requester_id}_{user_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    ad_request_message = await bot.send_message(user_id, (
            f"⭐️💰*Ad placement Request.*💰\n"
            "──────────────────────────\n"
            "<i>- We request that you include this Advert in your next Tiktok video:</i>\n\n"
            "<b>Ad Content:</b>\n\n"
            f"<code>{ad_content}</code>\n"
            "──────────────────────────\n"
            f"<b>Order ID: </b><code>{order_id}</code>"), parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
    ad_request_messages[user_id] = ad_request_message.message_id  # Store the message ID

    # Acknowledge the admin's action
    await query.answer("Ad content sent to the TikTok profile owner.")


@dp.callback_query(lambda query: query.data.startswith('accept_ad_'))
async def handle_accept_ad_callback(query: types.CallbackQuery):
    parts = query.data.split('_')
    requester_id = int(parts[2])
    user_id = int(parts[3])

    await asyncio.sleep(3)
    await bot.send_message(user_id, "🤩 Good Job!")
    await asyncio.sleep(4)

    await bot.send_message(user_id, f'<strong>💰How to get paid</strong>\n══════════════════════════\n\n-->Organise the video & include that Advert, then Send this command: /done to this chat.\n\n'
                                    f'✨You will then be asked to provide a few things like the link to the video, order ID for the Ad request the video is addressing.\n\n'
                                    f'🌟Accepted Payment Methods \n'
                                    f'──────────────────────\n'
                                    f'👉Mobile Money\n'
                                    f'👉Binance(international)\n'
                                    f'👉Payeer(international)\n'
                                    f'👉Chipper Cash📱\n\n'
                                    f'🌟 If Binance, say for example "Binance ID: 868665". Do the same for others.\n\n'
                                    f'The review team will have to check the video and if confirmed, be ready to see payment in a few hours\n\n'
                                    f'<b><u>Attention:</u></b> \n<i>Deleting the Video Afterwards will lead to your account getting banned.</i>', parse_mode=ParseMode.HTML)

    # Acknowledge the user's action
    await query.answer("Ad request accepted✅.")

@dp.callback_query(lambda query: query.data.startswith('decline_ad_'))
async def handle_decline_ad_callback(query: types.CallbackQuery):
    parts = query.data.split('_')
    requester_id = int(parts[2])
    user_id = int(parts[3])
    message_id = int(parts[4])  # Extract message_id from the callback data
    order_id = advertiza[requester_id]['order_id']


    # Delete the previous ad request message
    if user_id in ad_request_messages:
        await asyncio.sleep(3)
        await bot.delete_message(chat_id=user_id, message_id=ad_request_messages[user_id])
        del ad_request_messages[user_id]

    await bot.send_message(user_id, "You have declined the ad request. You have lost cash in just a click😢.")
    await bot.send_message(ADMIN_CHAT_ID, f"Order ID <code>{order_id}</code> has been declined by the tiktoker", parse_mode=ParseMode.HTML)
    # Acknowledge the user's action
    await query.answer("Ad declined❌.")

@dp.message()
async def msg(message: types.Message):
    cmd = message.text.lower()
    if cmd == '/start':
        await send_welcome(message)
    elif cmd == '/register':
        await start_verification(message)
    elif cmd == '/help':
        await send_help(message)
    elif cmd == '/done':
        await recieve_video(message)

    # Cancellation command handler
    elif cmd == '/cancel':
        await handle_cancel(message)
async def main() -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Listening...')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
