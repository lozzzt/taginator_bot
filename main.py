# -*- coding: utf-8 -*-

import re
import asyncio
from aiogram import executor, types
from aiogram.dispatcher.filters import Text
from utils import MyBot, RegexpUtils

mybot = MyBot()
bot, dp = mybot.get_bot()
utils = RegexpUtils(pattern = "[\s\.,!\-]")

def register_handler(message):
    re_aliases = "\\b" + "|\\b".join(mybot.get_aliases(message.from_user.mention))
    if len(mybot.get_aliases(message.from_user.mention)) > 0:
        dp.register_message_handler(tag, lambda message: len(re.findall(re_aliases, message.text, re.IGNORECASE)) > 0, content_types=[types.ContentType.TEXT])

COMMANDS_MSG = {
    'start': 'Трепещать! Призыватель-инатор запущен для Вас, ',
    'set_aliases': 'Заданы слова, на которые Вас призовут.',
    'set_aliases_error': 'Необходимо задать слова. Например: \n`/set_aliases@taginator_bot Имя Фамилия`',
    'reset_aliases': 'Сброшены слова, на которые Вас могли бы призвать.',
    'get_aliases': 'Список Ваших призывательных слов: ',
    'add_aliases': 'Добавлены слова, на которые Вас призовут.',
    'add_aliases_error': 'Необходимо задать слова. Например: \n`/add_aliases@taginator_bot Имя Фамилия`',
    'leave_chat': 'Включён самоуничтожитель Призыватель-инатора',
    'stop': 'Призыватель-инатор остановлен для Вас, '
}

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить призыватель-инатор для текущего пользователя!"),
        types.BotCommand("set_aliases", "Задать слова, на которые Вас призывать"),
        types.BotCommand("reset_aliases", "Сбросить все слова, на которые Вас призывать"),
        types.BotCommand("get_aliases", "Посмотреть слова, на которые Вас призывают"),
        types.BotCommand("add_aliases", "Добавить слова, на которые Вас призывать"),
        types.BotCommand("leave_chat", "Убрать призыватель-инатор из чата"),
        types.BotCommand("stop", "Выключить призыватель-инатор для текущего пользователя!")
    ])

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    mybot.register_user(message.from_user)
    await message.answer(COMMANDS_MSG['start'] + message.from_user.first_name + "!")
    await set_default_commands(dp)

@dp.message_handler(commands=['stop'])
async def cmd_stop(message: types.Message):
    mybot.unregister_user(message.from_user)
    await message.answer(COMMANDS_MSG['stop'] + message.from_user.first_name + "!")

@dp.message_handler(commands=['leave_chat'])
async def cmd_leave_chat(message: types.Message):
    await message.answer(COMMANDS_MSG['leave_chat'])
    await asyncio.sleep(1)
    await bot.leave_chat(message.chat.id)

@dp.message_handler(commands=['set_aliases'])
async def cmd_set_aliases(message: types.Message):
    if message.get_args():
        mybot.set_aliases(message.from_user.mention, utils.get_words(message.get_args()))
        register_handler(message)
        await message.reply(COMMANDS_MSG['set_aliases'] + "\n" + COMMANDS_MSG['get_aliases'] + str(mybot.get_aliases(message.from_user.mention)))
        await asyncio.sleep(1)
    else:
        await message.reply(COMMANDS_MSG['set_aliases_error'], parse_mode="Markdown")

@dp.message_handler(commands=['reset_aliases'])
async def cmd_reset_aliases(message: types.Message):
    mybot.set_aliases(message.from_user.mention, [])
    register_handler(message)
    await message.reply(COMMANDS_MSG['reset_aliases'])
    await asyncio.sleep(1)

@dp.message_handler(commands=['add_aliases'])
async def cmd_add_aliases(message: types.Message):
    if message.get_args():
        mybot.add_aliases(message.from_user.mention, utils.get_words(message.get_args()))
        register_handler(message)
        await message.reply(COMMANDS_MSG['add_aliases'] + "\n" + COMMANDS_MSG['get_aliases'] + str(mybot.get_aliases(message.from_user.mention)))
        await asyncio.sleep(1)
    else:
        await message.reply(COMMANDS_MSG['add_aliases_error'], parse_mode="Markdown")

@dp.message_handler(commands=['get_aliases'])
async def cmd_get_aliases(message: types.Message):
    await message.reply(COMMANDS_MSG['get_aliases'] + str(mybot.get_aliases(message.from_user.mention)))

@dp.message_handler(Text(equals="Призыватель-инатор"))
async def tag(message: types.Message):
    tag_users = [k for k in mybot.get_aliases(None).keys() if len(re.findall("\\b" + "|\\b".join(mybot.get_aliases(k)), message.text, re.IGNORECASE)) > 0]
    tag_users_on = [mybot.users.get(k).get('mention') for k in tag_users if (k in mybot.users.keys()) and (mybot.users.get(k) is not None)]
    if len(tag_users_on) > 0:
        await message.reply(", ".join(tag_users_on) + " 👆", parse_mode="Markdown")
    
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
