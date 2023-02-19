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
from telegram import *
from telegram.bot import Bot
from telegram.ext import *
# from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
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


def start(update, context):
    update.message.reply_text("Hi! I'm your Telegram bot. I'll collect messages and links from this group.")


def collect_message(update , context):
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
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    run_bot()
