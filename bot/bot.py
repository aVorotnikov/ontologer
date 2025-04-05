#!/usr/bin/python3

from llm_connector import LlmConnector
from ontologies_connector import OntologiesConnector
from db_connector import DbConnector
from generate_task import generate_task, generate_task_text
from checker import check_answer
from bot_types import *

from keyboards import *
from states import *

import asyncio
import logging
import sys
from os import getenv
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


INFO_TEXT = '''
/name Сменить имя
/group Сменить группу
/assessment Начать контроль знаний
'''


BOT_TOKEN = getenv("BOT_TOKEN")
NEO4J_IP = getenv("NEO4J_IP")
if not NEO4J_IP:
    NEO4J_IP = "localhost"
NEO4J_PORT = getenv("NEO4J_PORT")
if NEO4J_PORT:
    NEO4J_PORT = int(NEO4J_PORT)
else:
    NEO4J_PORT = 7687
NEO4J_USER = getenv("NEO4J_USER")
if not NEO4J_USER:
    NEO4J_USER = "neo4j"
NEO4J_PWD = getenv("NEO4J_PWD")
if not NEO4J_PWD:
    NEO4J_PWD = "aaaaaa"
DB_NAME = getenv("DB_NAME")
if not DB_NAME:
    DB_NAME = "ontologer"
DB_USER = getenv("DB_USER")
if not DB_USER:
    DB_USER = "postgres"
DB_PWD = getenv("DB_PWD")
if not DB_PWD:
    DB_PWD = "aaaaaa"
DB_HOST = getenv("DB_HOST")
if not DB_HOST:
    DB_HOST = "localhost"
DB_PORT = getenv("DB_PORT")
if DB_PORT:
    DB_PORT = int(DB_PORT)
else:
    DB_PORT = 5432


llm = LlmConnector()

neo4j_uri = f"neo4j://{NEO4J_IP}:{NEO4J_PORT}"
neo4j_auth = (NEO4J_USER, NEO4J_PWD)
ontologies = OntologiesConnector(neo4j_uri, neo4j_auth)

db = DbConnector(DB_NAME, DB_USER, DB_PWD, DB_HOST, DB_PORT)

# Синхронизация базы данных и системы хранения онтологий
domains = ontologies.get_domains()
db.insert_domains(domains)


dp = Dispatcher()

tasks = dict()


async def proccess_login(message: Message, state: FSMContext):
    user = message.from_user
    if not user:
        await message.answer("Не могу определить имя пользователя")
        return False
    await state.update_data(login=user.username)
    users = db.get_student(user.username)
    if 0 == len(users):
        await state.set_state(Registration.name)
        await message.answer("Введите имя")
        return False
    elif 1 == len(users):
        await state.update_data(name=users[0][1])
        await state.update_data(group=users[0][2])
        await message.answer(f"Привет, {users[0][1]}!")
        return True
    else:
        await message.answer("Внутренняя ошибка")
        return False


async def get_data(message: Message, state: FSMContext):
    data = await state.get_data()
    if "login" not in data or "name" not in data or "group" not in data:
        if not await proccess_login(message, state):
            raise RuntimeError("User need login")
        return await state.get_data()
    return data


async def send_info(message: Message) -> None:
    await message.answer(INFO_TEXT)


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    if await proccess_login(message, state):
        await send_info(message)


@dp.message(Command('name'))
async def change_name(message: Message, state: FSMContext) -> None:
    await state.set_state(ChangeName.name)
    await message.answer("Введите имя")


@dp.message(ChangeName.name)
async def change_name_final(message: Message, state: FSMContext) -> None:
    data = await get_data(message, state)
    name = message.text
    db.insert_student(data["login"],name, data["group"])
    await proccess_login(message, state)
    await state.set_state(state=None)


@dp.message(Registration.name)
async def registration_set_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Registration.group)
    await message.answer("Выберите группу", reply_markup=create_keyboard(db.get_groups()))


@dp.message(Command('group'))
async def change_group(message: Message, state: FSMContext) -> None:
    await state.set_state(ChangeGroup.group)
    await message.answer("Выберите группу", reply_markup=create_keyboard(db.get_groups()))


@dp.message(ChangeGroup.group)
async def change_group_final(message: Message, state: FSMContext) -> None:
    data = await get_data(message, state)
    group = message.text
    db.insert_student(data["login"], data["name"], group)
    await proccess_login(message, state)
    await state.set_state(state=None)


@dp.message(Registration.group)
async def registration_set_group(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    group = message.text
    db.insert_student(data["login"], data["name"], group)
    await proccess_login(message, state)
    await state.set_state(state=None)


@dp.message(Command('assessment'))
async def start_assessment(message: Message, state: FSMContext) -> None:
    await state.set_state(Assessment.domain)
    await message.answer("Выберите предметную область", reply_markup=create_keyboard(domains))


@dp.message(Assessment.domain)
async def set_assessment_domain(message: Message, state: FSMContext) -> None:
    if message.text not in domains:
        await message.answer("Неизвестная предметная область. Повторите выбор", reply_markup=create_keyboard(domains))
        return
    await state.update_data(assessment_domain=message.text)
    await state.set_state(Assessment.type)
    await message.answer(
        "Выберите тип оценивания",
        reply_markup=create_keyboard([assessment_type_to_string(assessment_type) for assessment_type in AssessmentType]))


async def ask(message: Message, domain) -> None:
    task = generate_task(ontologies, domain)
    tasks[message.chat.id] = task
    await message.answer(generate_task_text(task))


@dp.message(Assessment.type)
async def set_assessment_type(message: Message, state: FSMContext) -> None:
    try:
        assessment_type = string_to_assessment_type(message.text)
    except ValueError:
        await message.answer(
            "Неизвестный тип. Повторите выбор",
            reply_markup=create_keyboard([assessment_type_to_string(assessment_type) for assessment_type in AssessmentType]))
        return
    await state.update_data(assessment_type=assessment_type)
    data = await get_data(message, state)
    domain = data["assessment_domain"]
    assessment_id=db.insert_assessment(data["login"], assessment_type, domain)
    await state.update_data(assessment_id=assessment_id)
    await state.set_state(Assessment.tasks)
    await message.answer(f"Начат контроль знаний \#`{assessment_id}`", parse_mode='MarkdownV2')
    await ask(message, domain)


@dp.message(Assessment.tasks)
async def get_answer(message: Message, state: FSMContext) -> None:
    data = await get_data(message, state)
    domain = data["assessment_domain"]
    if message.chat.id in tasks:
        task = tasks[message.chat.id]
        if not message.text:
            await message.answer("Сообщение не содержит текста")
        elif check_answer(ontologies, llm, domain, task.source, task.destination, message.text):
            await message.answer("Верно")
        else:
            await message.answer("Неверно")
    await ask(message, domain)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
