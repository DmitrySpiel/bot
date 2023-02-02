import logging
from telegram import *
from telegram.ext import *
import flag
import json
import tempfile
import os
import numpy as np
import re
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def jsonSelect(name):
    file = open('countries.json', "r+")
    jfile = json.load(file)
    return jfile[name]

def propGet(country, prop):
    file = open('countries.json')
    jfile = json.load(file)
    return jfile[country][prop]

def jsonModify(country, prop, value):
    file = open('countries.json')
    jfile = json.load(file)
    jfile[country][prop] = value
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        json.dump(jfile, f)
        os.rename(f.name, "countries.json")

def jsonClear(country, prop):
    file = open('countries.json')
    jfile = json.load(file)
    jfile[country][prop] = ''
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        json.dump(jfile, f)
        os.rename(f.name, "countries.json")

def arrShape(array):
    honest_list = np.resize(array, (int(np.floor(len(array)/2)), 2)).tolist()

    if len(array)%2 != 0:
        honest_list.append(array[-1])
    return honest_list

def jsonAddProp(prop, val):
    file = open('countries.json', "r+")
    jfile = json.load(file)
    for i in jfile:
        if not prop in jfile[i]:
            jfile[i][prop] = ''
        elif val:
            jfile[i].pop(prop)
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
        json.dump(jfile, f)
        os.rename(f.name, "countries.json")

async def start(update: Update, context: CallbackContext):
    buttons = [
    [
        InlineKeyboardButton(flag.flag("EA") + " " + "Spain", callback_data='Spain'),
        InlineKeyboardButton(flag.flag("US") + " " + "USA", callback_data='USA')
    ],
    [
        InlineKeyboardButton(flag.flag("FR") + " " + "France", callback_data='France'),
        InlineKeyboardButton(flag.flag("AU") + " " + "Australia", callback_data='Australia')
    ],
    [
        InlineKeyboardButton(flag.flag("NZ") + " " + "New Zealand", callback_data='New Zealand'),
        InlineKeyboardButton(flag.flag("GB") + " " + "UK", callback_data='UK'),
    ],
    [InlineKeyboardButton(flag.flag("CA") + " " + "Canada", callback_data='Canada')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose:", reply_markup=reply_markup)

async def menu(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == 'start':
        buttons = [
        [
            InlineKeyboardButton(flag.flag("EA") + " " + "Spain", callback_data='Spain'),
            InlineKeyboardButton(flag.flag("US") + " " + "USA", callback_data='USA')
        ],
        [
            InlineKeyboardButton(flag.flag("FR") + " " + "France", callback_data='France'),
            InlineKeyboardButton(flag.flag("AU") + " " + "Australia", callback_data='Australia')
        ],
        [
            InlineKeyboardButton(flag.flag("NZ") + " " + "New Zealand", callback_data='New Zealand'),
            InlineKeyboardButton(flag.flag("GB") + " " + "UK", callback_data='UK'),
        ],
        [InlineKeyboardButton(flag.flag("CA") + " " + "Canada", callback_data='Canada')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="Choose:", reply_markup=reply_markup)
    


async def countryInit(update: Update, context:CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    print(data)
    countries = ["Spain", "USA", "France", "Australia", "New Zealand", "UK", "Canada"]

    dataList = data.split("/")
    if(len(dataList) == 1):
        print(query)
        print(dataList[0])
        props = jsonSelect(dataList[0])
        arr = []
        buttons = []
        for i in props: 
            arr.append(i)
        for i, button in enumerate(arr):
            buttons.append([InlineKeyboardButton(button, callback_data= data + "/" + arr[i])])
        buttons.append([InlineKeyboardButton(text="Add Property", switch_inline_query_current_chat="/update")])
        buttons.append([InlineKeyboardButton(text="Remove Property", switch_inline_query_current_chat="/remove")])
        buttons.append([InlineKeyboardButton(text="Back", callback_data='start')])
        arrShape(buttons)
        print(buttons)
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_text(text="Choose:", reply_markup=reply_markup)

    elif(len(dataList) == 2):
        props = jsonSelect(dataList[0])
        arr = []
        for i in props: 
            arr.append(i)
        prop = propGet(dataList[0], dataList[1])
        mark = True
        if prop == '':
            prop = "Do you want to edit it?"
            mark = False
        if mark: 
            reply_text = "Here comes"
            buttons = [
                [  
                    InlineKeyboardButton(text="Edit", switch_inline_query_current_chat=dataList[0] + "/" + dataList[1] + " " + prop),
                    InlineKeyboardButton(text="Remove", callback_data=dataList[0] + "/" + dataList[1] + '/Remove')
                ],
                
                [
                    InlineKeyboardButton(text="Back", callback_data=dataList[0])
                ]
            ]
        else:
            reply_text = "This attribute is empty"
            buttons = [
                [  
                    InlineKeyboardButton(text="Edit", switch_inline_query_current_chat=dataList[0] + "/" + dataList[1] + " ")
                ],
                [
                    InlineKeyboardButton(text="Back", callback_data=dataList[0])
                ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=prop, reply_markup=reply_markup)
    else:
        if dataList[2] == "ConfirmRemoval":
            jsonClear(dataList[0], dataList[1])
        elif dataList[2] == "Remove":
            buttons = [
                [  
                    InlineKeyboardButton(text="Yes", callback_data=dataList[0] + "/" + dataList[1] + "/" + "ConfirmRemoval"),
                    InlineKeyboardButton(text="No", callback_data=dataList[0] + "/" + dataList[1])
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.edit_message_text(text=f"Are you sure you want to remove the current value?", reply_markup=reply_markup)
            jsonClear(dataList[0], dataList[1])

async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    str = update.message.text
    strRes = str.split(" ")
    strRes.remove(strRes[0])
    if strRes[0] == '/update':
        jsonAddProp(strRes[1], False)
    elif strRes[0] == '/remove':
        jsonAddProp(strRes[1], True)
    else:
        strRes.remove(strRes[0])
        strFin = ' '.join(strRes)
        act = strRes[0].split("/")
        print(act)
        jsonModify(act[0], act[1], strFin)

if __name__ == '__main__':
    application = ApplicationBuilder().token('5932809332:AAEtEThaGZngAkbyqCyUgsJ8PA9uY8g8coQ').build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(menu, pattern="start"))
    application.add_handler(CallbackQueryHandler(countryInit))
    application.add_handler(MessageHandler(filters.TEXT, edit))

    application.run_polling()