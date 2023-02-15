# import os
# import time
# import requests
# import openpyxl
# import pymongo
# import schedule
#
# # Set up MongoDB connection
# client = pymongo.MongoClient(
#     "mongodb+srv://pugalkmc:pugalkmc@cluster0.ey2yh.mongodb.net/mydb?retryWrites=true&w=majority")
# db = client.mydatabase
# collection = db.mycol
#
# collection.insert_one({"user": "me"})
#
# # Set up Telegram bot
# bot_token = "5123712096:AAFoWsAeO_sJyrsl0upMa-LUCeHE-k8AWYE"
# bot_chat_id = "1291659507"
# BASE_URL = f"https://api.telegram.org/bot{bot_token}/"
#
# # Set up list of members to collect messages from
# members = ["pugalkmc", "sarankmc"]
#
#
# # Define a function to collect messages
# def collect_messages():
#     import re
#     result = requests.get(BASE_URL + f"getUpdates?chat_id=1605512981").json()["result"]
#     for message in result:
#         if "text" in message["message"]:
#             text = message["message"]["text"]
#             message_id = message["message"]["message_id"]
#             url = f"https://t.me/harley_bot_support_group/{message_id}"
#             print(text)
#             if not collection.find_one({"url": f"https://t.me/harley_bot_support_group/{message_id}"}):
#                 collection.insert_one({
#                     "username": message["message"]["from"].get("username"),
#                     "text": text,
#                     "url": url,
#                     "timestamp": message["message"].get("date")
#                 })
#
#     messages = collection.find({})
#     wb = openpyxl.Workbook()
#     sheet = wb.active
#     sheet.append(["Username", "Link", "Date"])
#     for message in messages:
#         sheet.append([message["username"], message["url"], message["timestamp"]])
#     total_links = {}
#     for message in messages:
#         date = time.strftime("%Y-%m-%d", time.localtime(message["timestamp"]))
#         if date in total_links:
#             total_links[date] += 1
#         else:
#             total_links[date] = 1
#     for i, (date, count) in enumerate(total_links.items()):
#         sheet.cell(row=1, column=i + 4, value=date)
#         sheet.cell(row=2, column=i + 4, value=count)
#     wb.save("messages.xlsx")
#     file = open("messages.xlsx", "rb")
#     requests.post(BASE_URL + "sendDocument", data={"chat_id": bot_chat_id}, files={"document": file})
#
#     # result = requests.get(BASE_URL + f"getUpdates?chat_id=1605512981").json()["result"]
#     # print(result)
#     # for message in result:
#     #     if "message" in message and "from" in message["message"] and "username" in message["message"]["from"]:
#     #         if message["message"]["from"]["username"] in members:
#     #             print("here 1")
#     #             if "entities" in message["message"]:
#     #                 print("entitie sskf")
#     #                 for entity in message["message"]["entities"]:
#     #                     if entity["type"] == "url":
#     #                         print("entity")
#     #                         url = message["message"]["text"][entity["offset"]:entity["offset"] + entity["length"]]
#     #                         if not collection.find_one({"url": url}):
#     #                             collection.insert_one({"username": message["message"]["from"]["username"], "url": url,
#     #                                                    "timestamp": message["message"]["date"]})
#
#
# # Define a function to export the collected messages to a spreadsheet
# def export_to_spreadsheet():
#     messages = list(collection.find({}))
#     wb = openpyxl.Workbook()
#     sheet = wb.active
#     sheet.append(["Username", "Link", "Date"])
#     for message in messages:
#         sheet.append([message["username"], message["url"], message["timestamp"]])
#     total_links = {}
#     for message in messages:
#         date = time.strftime("%Y-%m-%d", time.localtime(message["timestamp"]))
#         if date in total_links:
#             total_links[date] += 1
#         else:
#             total_links[date] = 1
#     for i, (date, count) in enumerate(total_links.items()):
#         sheet.cell(row=1, column=i + 4, value=date)
#         sheet.cell(row=2, column=i + 4, value=count)
#     wb.save("messages.xlsx")
#     file = open("messages.xlsx", "rb")
#     requests.post(BASE_URL + "sendDocument", data={"chat_id": bot_chat_id}, files={"document": file})
#
#
# # Schedule the functions to run at specified intervals
# schedule.every().day.at("23:59").do(export_to_spreadsheet)
# schedule.every(1).seconds.do(collect_messages)
#
# # Run the scheduled functions
# while True:
#     schedule.run_pending()
#     time.sleep(1)


import os
import re
import time
from datetime import datetime, timedelta
import pytz
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up the MongoDB client and database
mongo_client = MongoClient(
    os.environ.get("mongodb+srv://pugalkmc:pugalkmc@cluster0.ey2yh.mongodb.net/mydb?retryWrites=true&w=majority"))
db = mongo_client["telegram_bot"]
collection = db["messages"]

# Set up the Google Sheets API client
scope = ["https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("omega-cosmos-290504-9567ce79765b.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Telegram Bot Data").sheet1

# Set up the Telegram bot
bot = Bot(token=os.environ.get("5123712096:AAFoWsAeO_sJyrsl0upMa-LUCeHE-k8AWYE"))


def start(update: Update, context):
    update.message.reply_text("Hi! I'm your Telegram bot. I'll collect messages and links from this group.")


def collect_message(update: Update, context):
    message = update.message
    username = message.from_user.username
    chat_id = message.chat_id
    if chat_id == -1001605512981 and username in ["pugalkmc", "sarankmc"]:
        collection.insert_one({"message": message, "link": "sample link", "timestamp": message.date})
        context.user_data["last_message_time"] = message.date.timestamp()


def save_to_spreadsheet():
    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    yesterday = now - timedelta(days=1)
    messages = collection.find({"timestamp": {"$gte": yesterday.timestamp(), "$lt": now.timestamp()}})
    links = set()
    for message in messages:
        links.add(message["link"])
    row = [now.strftime("%Y-%m-%d %H:%M:%S"), len(links)]
    sheet.append_row(row)
    print(f"Saved {len(links)} links to the spreadsheet.")


def run_bot():
    updater = Updater(token=os.environ.get("5123712096:AAFoWsAeO_sJyrsl0upMa-LUCeHE-k8AWYE"), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, collect_message))

    # Set up a job to run save_to_spreadsheet() every day at 11:59 PM IST
    job_queue = updater.job_queue
    job_queue.run_daily(save_to_spreadsheet, time(hour=18, minute=29, second=0), days=(0, 1, 2, 3, 4, 5, 6),
                        context=None)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    run_bot()

# import os
#
# import telepot
# import time
# import csv
# import pymongo
# from datetime import datetime, timedelta
#
# # Set up MongoDB
# client = pymongo.MongoClient('mongodb+srv://pugalkmc:pugalkmc@cluster0.ey2yh.mongodb.net/mydb?retryWrites=true&w=majority')
# db = client['telegram_bot']
# users_collection = db['users']
#
# # Set up Telegram bot
# bot = telepot.Bot('5123712096:AAFoWsAeO_sJyrsl0upMa-LUCeHE-k8AWYE')
#
# # Define list of usernames to send daily queue of work to
# usernames_to_send = ['pugalkmc', 'pugalkmc']
# usernam = 'ni'
# user1 = {'username': usernam}
# users_collection.insert_one(user1)
# print('wef')
#
#
# # Define function to handle incoming messages
# def handle_message(msg):
#     content_type, chat_type, chat_id = telepot.glance(msg)
#     if content_type == 'text' and msg['text'].startswith('/add_username'):
#         # Add new user to list of authorized users
#         username = msg['text'][len('/add_username '):]
#         user = {'username': username}
#         users_collection.insert_one(user)
#         bot.sendMessage(chat_id, f'Added {username} to list of authorized users.')
#     elif content_type == 'text' and chat_type == 'group':
#         # Collect messages and message links from authorized users
#         user = users_collection.find_one({'username': msg['from']['username']})
#         if user is not None:
#             message = {'text': msg['text'], 'link': None, 'user': user['_id']}
#             if 'entities' in msg:
#                 for entity in msg['entities']:
#                     if entity['type'] == 'url':
#                         message['link'] = msg['text'][entity['offset']:entity['offset'] + entity['length']]
#             db['messages'].insert_one(message)
#
#
# # Define function to send daily queue of work to authorized users
# def send_daily_queue():
#     # Get today's date
#     today = datetime.now().date()
#
#     # Get messages from yesterday from authorized users
#     yesterday = today - timedelta(days=1)
#     users = users_collection.find()
#     messages = []
#     for user in users:
#         user_messages = db['messages'].find({'user': user['_id'],
#                                              'date': {'$gte': datetime.combine(yesterday, datetime.min.time()),
#                                                       '$lt': datetime.combine(today, datetime.min.time())}})
#         for message in user_messages:
#             messages.append({'user': user['username'], 'text': message['text'], 'link': message['link']})
#
#     # Write messages to CSV file
#     filename = f'daily_queue_{yesterday}.csv'
#     with open(filename, 'w', newline='') as csvfile:
#         fieldnames = ['User', 'Text', 'Link']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         for message in messages:
#             writer.writerow({'User': message['user'], 'Text': message['text'], 'Link': message['link']})
#
#     # Send CSV file to authorized users
#     for username in usernames_to_send:
#         user = users_collection.find_one({'username': username})
#         if user is not None:
#             bot.sendDocument(user['_id'], open(filename, 'rb'))
#
#     # Delete CSV file
#     os.remove(filename)
#
#
# # Set up message handler and start bot
# bot.message_loop(handle_message)
# while True:
#     now = datetime.now().time()
#     if now.hour == 23 and now.minute == 59:
#         send_daily_queue()
#     time.sleep(1)
