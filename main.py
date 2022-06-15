# -*- coding: utf-8 -*-

import re
import asyncio
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils import MyBot, Utils

mybot = MyBot()
bot, dp = mybot.get_bot()
utils = Utils("[\s\.,!\-]")

def register_handler(message):
    re_aliases = "|".join(mybot.get_aliases(message.from_user.mention))
    if len(mybot.get_aliases(message.from_user.mention)) > 0:
        dp.register_message_handler(tag, lambda message: len(re.findall(re_aliases, message.text, re.IGNORECASE)) > 0, state=BotState.on, content_types=[types.ContentType.TEXT])

class BotState(StatesGroup):
    on = State()
    off = State()

COMMANDS_MSG = {
    'start': 'Трепещать! Призыватель-инатор запущен!',
    'set_aliases': 'Заданы слова, на которые Вас призовут.',
    'get_aliases': 'Список Ваших призывательных слов: ',
    'add_aliases': 'Добавлены слова, на которые Вас призовут.',
    'leave_chat': 'Включён самоуничтожитель Призыватель-инатора',
    'stop': 'Призыватель-инатор остановлен',
}

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить призыватель-инатор!"),
        types.BotCommand("set_aliases", "Задать слова, на которые Вас призывать"),
        types.BotCommand("get_aliases", "Посмотреть слова, на которые Вас призывают"),
        types.BotCommand("add_aliases", "Добавить слова, на которые Вас призывать"),
        types.BotCommand("leave_chat", "Убрать призыватель-инатор из чата"),
        types.BotCommand("stop", "Выключить призыватель-инатор!")
    ])

@dp.message_handler(state='*', commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await BotState.on.set()
    await message.answer(COMMANDS_MSG['start'])
    await set_default_commands(dp)

@dp.message_handler(state='*', commands=['stop'])
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.finish()
    await BotState.off.set()
    await message.answer(COMMANDS_MSG['stop'])

@dp.message_handler(state='*', commands=['leave_chat'])
async def cmd_leave_chat(message: types.Message):
    await message.answer(COMMANDS_MSG['leave_chat'])
    await asyncio.sleep(1)
    await bot.leave_chat(message.chat.id)

@dp.message_handler(state='*', commands=['set_aliases'])
async def cmd_set_aliases(message: types.Message):
    mybot.set_aliases(message.from_user.mention, utils.get_words(message.get_args()))
    register_handler(message)
    await message.reply(COMMANDS_MSG['set_aliases'] + "\n" + COMMANDS_MSG['get_aliases'] + str(mybot.get_aliases(message.from_user.mention)))
    await asyncio.sleep(1)

@dp.message_handler(state='*', commands=['add_aliases'])
async def cmd_add_aliases(message: types.Message):
    mybot.add_aliases(message.from_user.mention, utils.get_words(message.get_args()))
    register_handler(message)
    await message.reply(COMMANDS_MSG['add_aliases'] + "\n" + COMMANDS_MSG['get_aliases'] + str(mybot.get_aliases(message.from_user.mention)))
    await asyncio.sleep(1)

@dp.message_handler(state='*', commands=['get_aliases'])
async def cmd_get_aliases(message: types.Message):
    await message.reply(COMMANDS_MSG['get_aliases'] + str(mybot.get_aliases(message.from_user.mention)))

@dp.message_handler(Text(contains="Призыватель-инатор"), state=BotState.on, content_types=[types.ContentType.TEXT])
async def tag(message: types.Message):
    tag_users = [k for k in mybot.get_aliases(None).keys() if len(re.findall("|".join(mybot.get_aliases(k)), message.text, re.IGNORECASE)) > 0]
    await message.reply(", ".join(tag_users) + " 👆")
    
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
