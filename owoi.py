
import os
import asyncio
import logging
import sys
import time
import re
import random

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from datetime import datetime, timedelta
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Load environment variables from .env file
load_dotenv()

# Telegram bot token
TELEGRAM_BOT_TOKEN = '6917061943:AAFQXY3j_bLYX_z30kpyfRYq4GuEHpCZ6Ys'
ADMIN_CHAT_ID = '6448112643'

# Dispatcher initialization
dp = Dispatcher()
bot = Bot(token=TELEGRAM_BOT_TOKEN)


user_data = {}
ad_requests = {}
ad_contents = {}
advertiza = {}
ad_request_messages = {}


async def recieve_video(message: types.Message):
    await message.reply("Please enter the video link:")
    user_data[message.from_user.id] = {'step': 'video_link'}


# Function to generate a random unique ID of up to 8 digits
def generate_unique_id():
    return str(random.randint(10000000, 99999999))

async def send_welcome(message: types.Message):
        await message.reply("Reach millions of potential customers on TikTok through us! \n\nWe connect advertisers with popular TikTok creators who have a large following ready to buy your products or services. \n\nType '/help' to learn how to register your TikTok account with Ad Spaces and get started!")
async def send_help(message: types.Message):
    await message.reply("This Bot now manages both the TikTok content creators and the Advertisers.\n═══════════════════════════\n\n"
                        "✨- To sign up as a tiktoker, send /verify to this chat and follow the prompts.\n\n"
                        "🗽-Advertisers Dont need to sign up. All you need is to keep an eye on @adskity to find the best tiktoker that will fit your advertising needs.\n\n"
                        "⚠️Note: Adskit (Tiktok spaces) Is not owned by ByteDance Ltd (TikTok).\n\n"
                        "Adskit (TikTok Spaces) Will never ask for your tiktok account login credentials or Passwords to your payment wallets!")
async def start_verification(message: types.Message):
    user_id = message.from_user.id

    user_data[user_id] = {
        'verification_step': 'awaiting_link',
        'unique_id': generate_unique_id()  # Generate and store the unique ID
    }
    await message.reply("🤝Let's begin.\n\nSend me a link to Your tiktok account or to any of your videos.🤷‍♂️")

async def check_if_tiktok(message: types.Message):
    # Regular expression pattern to match TikTok URLs
    tiktok_pattern = r'(https?://)?(www\.)?(vm\.tiktok\.com/|tiktok\.com/@[\w.-]+/video/)[\w-]+'
    return re.search(tiktok_pattern, message.text) is not None


@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('step') == 'video_link')
async def process_video_link(message: types.Message):
    if await check_if_tiktok(message):
        user_data[message.from_user.id]['video_link'] = message.text
        user_data[message.from_user.id]['step'] = 'payment_address'
        await message.reply("Please enter the payment address:")
    else:
        await message.reply("Please provide a valid TikTok link.")
    
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('step') == 'payment_address')
async def process_payment_address(message: types.Message):
    user_data[message.from_user.id]['payment_address'] = message.text
    user_data[message.from_user.id]['step'] = 'adskit_id'
    await message.reply("Please enter your Adskit ID:")

@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('step') == 'adskit_id')
async def process_adskit_id(message: types.Message):
    user_id = message.from_user.id
    user_data[message.from_user.id]['adskit_id'] = message.text
    video_link = user_data[message.from_user.id]['video_link']
    payment_address = user_data[message.from_user.id]['payment_address']
    adskit_id = user_data[message.from_user.id]['adskit_id']

    compiled_message = (
        f"Is this the Correct?\n\n"
        f"Video Link: {video_link}\n"
        f"Payment Address: {payment_address}\n"
        f"Adskit ID: {adskit_id}"
    )
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Sure!', callback_data=f"confirmed")]
    ])  # Some markup
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    await message.reply(compiled_message, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    @dp.callback_query(lambda query: query.data == 'confirmed')
    async def handle_confirmation(query: types.CallbackQuery):
        user_id = query.from_user.id
        if user_id not in user_data:
            await query.answer("No data found to submit.")
            return

        video_link = user_data[user_id]['video_link']
        payment_address = user_data[user_id]['payment_address']
        adskit_id = user_data[user_id]['adskit_id']

        compiled_message = (
            f"TikTok Video from @{query.from_user.username}:\n\n"
            f"Video Link: {video_link}\n"
            f"Momo Account: {payment_address}\n"
            f"Adskit ID: {adskit_id}"
        )

        await bot.send_message(ADMIN_CHAT_ID, compiled_message, parse_mode=ParseMode.HTML)
        await query.message.reply("Your information has been submitted to the admin.")
        # Clear user data
        user_data.pop(user_id, None)




# Inside the handle_verification_link function
@dp.message(lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_link')
async def handle_verification_link(message: types.Message):
    user_id = message.from_user.id
    if await check_if_tiktok(message):
        user_data[user_id]['link'] = message.text.strip()
        user_data[user_id]['verification_step'] = 'awaiting_profile_name'
        await message.reply("🤔What's Your TikTok Account Name?\n\n╰┈➤Help Advertisers Know its You😎 ")
    else:
        await message.reply("Please provide a valid TikTok link.")

@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_profile_name')
async def handle_profile_name(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['profile_name'] = message.text.strip()
    user_data[user_id]['verification_step'] = 'awaiting_followers'
    await message.reply("How many followers do you have right now? \n\n-🛑 Wrong answers might lead to your account verification being neglected")


@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_followers')
async def handle_followers(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['followers'] = message.text.strip()
    user_data[user_id]['verification_step'] = 'awaiting_location'
    await message.reply("What country do your followers come from?\n\n╰┈➤Some Advertisers target specific Countries.")


@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_location')
async def handle_views(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['location'] = message.text.strip()
    user_data[user_id]['verification_step'] = 'awaiting_price'
    await message.reply("How much do you charge for an Advert?.\n\n╰┈➤A lower price brings more advertisers to you. Set wisely!")


@dp.message(
    lambda message: user_data.get(message.from_user.id, {}).get('verification_step') == 'awaiting_price')
async def handle_price(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['price'] = message.text.strip()
    user_data[user_id]['verification_step'] = None
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Verify', callback_data=f"verify_link_{user_id}")]
    ])  # Some markup
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    # Notify the admin about the verification details
    await bot.send_message(ADMIN_CHAT_ID,
                           f"@{message.from_user.username} has sent a verification request with the following details:\n\n"
                           f"TikTok Name: {user_data[user_id]['profile_name']}\n"
                           f"Followers: {user_data[user_id]['followers']}\n"
                           f"Location: {user_data[user_id]['location']}\n"
                           f"Price Per Ad: {user_data[user_id]['price']}\n\n"
                           f"Link: {user_data[user_id]['link']}\n"
                           f"Please verify the link.", reply_markup=builder.as_markup())
    await message.reply("Your verification request has been sent. You will be notified once it's verified.")


@dp.callback_query(lambda query: query.data.startswith('verify_link_'))
async def handle_verify_link_callback(query: types.CallbackQuery):
    # Extract user_id from the callback data
    user_id = int(query.data.split('_')[2])

    builder2 = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Place AD', callback_data=f"place_ad_{user_id}")]
    ])  # Some markup
    builder2.attach(InlineKeyboardBuilder.from_markup(markup))

    unique_id = user_data[user_id]['unique_id']

    # Notify the user that their link has been verified
    await bot.send_message(user_id, f"Your Account has been Approved 🎉\n\n<b>What Next:</b>\n✨Advertising companies will glance at your TikTok account.  Focus on making it more appealing 🤗 \n\nKeep an eye @adskity\n\n✅<b>Your Adskit ID:</b> <code>{unique_id}</code>",
                           parse_mode=ParseMode.HTML)
    # Send a message to the channel notifying about the verified link
    channel_id = '-1002061815083'  # Replace with your channel ID
    profile_link = user_data[user_id]['link']
    # Create the clickable hyperlink
    profile_link_html = f"<a href='{profile_link}'>CLICK</a>"

    await bot.send_message(channel_id,
                           f"<b>  🗣 New Ad space </b>👀\n═════════════════\n➤<b>Platform:</b> -TikTok\n➤<b>Username:</b> -{user_data[user_id]['profile_name']}\n➤<b>Followers:</b> #{user_data[user_id]['followers']}\n➤<b>Location:</b> -{user_data[user_id]['location']}\n\n🛒 Price Per Ad💰: ${user_data[user_id]['price']}\n\n🥳 Profile link: {profile_link_html}\n\n<b>Adskit ID:</b> <code>{unique_id}</code>",
                           parse_mode=ParseMode.HTML,  # Set parse_mode to HTML
                           reply_markup=builder2.as_markup())
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

    # Prepare the "Tell Him" button
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Send Procedures', callback_data=f"tell_him_{requester_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    # Notify the admin about the ad request
    await bot.send_message(ADMIN_CHAT_ID,
                           f"A user wants to place an ad on {user_data[user_id]['profile_name']}'s TikTok profile.",
                           reply_markup=builder.as_markup())
    await query.answer("✅Request submitted. Check the Bot to complete the AD placement process😀")
    # Notify the profile owner about the ad request
    await bot.send_message(user_id,
                           "🎊Good News!😀\n\nAn advertiser just glanced at your  TikTok Ad Space🎉\n\n💐We will let you know if he requests to advertise with you ✨")
@dp.callback_query(lambda query: query.data.startswith('tell_him_'))
async def handle_tell_him_callback(query: types.CallbackQuery):
    # Extract requester_id from the callback data
    requester_id = int(query.data.split('_')[2])

    # Send instructions to the requester
    instructions = ("Advert Placement Guide🤓\n══════════════════\n\n"
                    "Prepare and send us your Advert in any of these formats:\n"
                    "-Text only\n"
                    "-Picture with caption.\n"
                    "-Video with Caption\n\n"
                    "🛑Please Make sure your texts or Video/Photo caption start with #Adcontent as the trigger."
                    )

    await bot.send_message(requester_id, instructions)

# New handler for photos with #Adcontent in the caption
@dp.message(lambda message: message.photo and "#Adcontent" in message.caption)
async def handle_ad_photo(message: types.Message):
    requester_id = message.from_user.id
    advertiza[requester_id] = {
        'order_id': generate_unique_id(), # Generate and store the unique ID
        'photo_ids': [photo.file_id for photo in message.photo]  #Store the photo IDs
    }
    order_id = advertiza[requester_id]['order_id']

    if requester_id not in ad_requests:
        await message.reply("You have not requested to place an ad yet. Please click the 'Place AD' button in the channel.")
        return

    # Extract the ad content from the caption
    ad_content = message.caption.replace("#Adcontent", "").strip()

    # Store the ad content
    ad_contents[requester_id] = ad_content


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

    await message.reply(f"Your Ad has been submitted. \n\nYour order ID is: <code>{order_id}</code> \n\nThis order automatically cancels if the escrow team doesnt recieve a payment from you.", parse_mode=ParseMode.HTML)
    await asyncio.sleep(18)
    await message.answer("Your Advert has been confirmed!\n\n"
                    "Make a payment that the TikToker set on Adspace.\n"
                    "--> Binance ID (For crypto only):\n"
                    "--> Flutterwave UGX payments: \n"
                    "✅Other Fiat Currencies coming soon..\n\n"
                    "Immediately Report to us at adskity@gmail.com if you find issues with the ADs you paid for.")

@dp.message(lambda message: message.text and message.text.startswith('#Adcontent') or message.photo)
async def handle_ad_content(message: types.Message):
    requester_id = message.from_user.id
    advertiza[requester_id] = {
        'order_id': generate_unique_id()  # Generate and store the unique ID
    }
    order_id = advertiza[requester_id]['order_id']
    ad_content = message.text[len('#Adcontent'):].strip()


    if requester_id not in ad_requests:
        await message.reply("You have not requested to place an ad yet. Please click the 'Place AD' button in the channel.")
        return

    # Store the ad content
    ad_contents[requester_id] = ad_content

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
    await message.answer("Your Advert has been confirmed!\n\n"
                    "Make a payment that the TikToker set on Adspace.\n"
                    "--> Binance ID (For crypto only):\n"
                    "--> Flutterwave UGX payments: \n"
                    "✅Other Fiat Currencies coming soon..\n\n"
                    "Immediately Report to us at adskity@gmail.com if you find issues with the ADs you paid for.")


@dp.callback_query(lambda query: query.data.startswith('sendp_to_tiktoker_'))
async def handle_send_to_tiktoker_callback(query: types.CallbackQuery):
    # Extract requester_id from the callback data
    requester_id = int(query.data.split('_')[3])
    user_id = next((u for u in ad_requests[requester_id]), None)

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
        raw_ad_content = ad_contents.get(requester_id, "No ad content provided.")
        ad_content = (
            f"⭐️💰*Ad placement Request.*💰\n"
            "──────────────────────────\n"
            "<i>- We request that you include this Advert in your next video:</i>\n\n"
            "<b>Ad Content:</b>\n\n"
            f"<code>{raw_ad_content}</code>\n"
            "──────────────────────────\n")
        photo_id = photo_ids[-1]  # Use the highest resolution photo

        builder = InlineKeyboardBuilder()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Decline❌',
                                  callback_data=f"decline_ad_{requester_id}_{user_id}_{query.message.message_id}"),
             InlineKeyboardButton(text='Accept✅', callback_data=f"accept_ad_{requester_id}_{user_id}")]
        ])
        builder.attach(InlineKeyboardBuilder.from_markup(markup))

        ad_request_message = await bot.send_photo(user_id, photo=photo_id, caption=ad_content, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
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


    if not user_id:
        await query.answer("Could not find the associated TikTok profile owner.")
        return

    # Send the ad content to the TikTok profile owner with Accept/Decline buttons
    ad_content = ad_contents.get(requester_id, "No ad content provided.")
    builder = InlineKeyboardBuilder()
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Decline❌', callback_data=f"decline_ad_{requester_id}_{user_id}_{query.message.message_id}"),
        InlineKeyboardButton(text='Accept✅', callback_data=f"accept_ad_{requester_id}_{user_id}")]
    ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))

    ad_request_message = await bot.send_message(user_id, f"⭐️💰*Ad placement Request.*💰\n══════════════════════════\n\nPlease prepare and make sure your next video contains the following Advert:\n\n╭──────────────────────────╮\n{ad_content}\n╰──────────────────────────╯", reply_markup=builder.as_markup())
    ad_request_messages[user_id] = ad_request_message.message_id  # Store the message ID

    # Acknowledge the admin's action
    await query.answer("Ad content sent to the TikTok profile owner.")


@dp.callback_query(lambda query: query.data.startswith('accept_ad_'))
async def handle_accept_ad_callback(query: types.CallbackQuery):
    parts = query.data.split('_')
    requester_id = int(parts[2])
    user_id = int(parts[3])

    await bot.send_message(user_id, f'💰How to get paid;\n══════════════════════════\n\n-->Make sure you provide here the link to the video where you made this AD visible \n-->Also, attach your payment details/address to the same message.\n\nHOW TO SEND:\n═══════════\nType "/link" followed by the link to the video.\nExample:\n /link tiktok.com/kfkfjf.... \nPayment Address: XX123XXMS\n\nThe review team will have to check the video and if confirmed, be ready to see payment in a few hours\n\nAttention: Deleting the Video Afterwards will lead to your account getting banned')

    # Acknowledge the user's action
    await query.answer("Ad request accepted✅.")

@dp.callback_query(lambda query: query.data.startswith('decline_ad_'))
async def handle_decline_ad_callback(query: types.CallbackQuery):
    parts = query.data.split('_')
    requester_id = int(parts[2])
    user_id = int(parts[3])
    message_id = int(parts[4])  # Extract message_id from the callback data

    # Delete the previous ad request message
    if user_id in ad_request_messages:
        asyncio.sleep(3)
        await bot.delete_message(chat_id=user_id, message_id=ad_request_messages[user_id])
        del ad_request_messages[user_id]

    await bot.send_message(user_id, "You have declined the ad request. You have lost cash in just a click😢.")

    # Acknowledge the user's action
    await query.answer("Ad declined❌.")

@dp.message()
async def msg(message: types.Message):
    cmd = message.text
    if cmd.lower() == '/start':
        await send_welcome(message)
    elif cmd.lower() == '/verify':
        user_id = message.from_user.id
        # Clear user data
        user_data.pop(user_id, None)
        await start_verification(message)
    elif cmd.lower() == '/help':
        await send_help(message)
    elif cmd.lower() == '/done':
        await recieve_video(message)

async def main() -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Listening...')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
