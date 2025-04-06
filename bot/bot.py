#!/usr/bin/python3

from llm_connector import LlmConnector
from ontologies_connector import OntologiesConnector
from db_connector import DbConnector
from generate_task import generate_free_choice_task, generate_free_choice_task_text, generate_test_task, generate_test_task_text
from free_choice_checker import check_free_choice_answer
from test_checker import check_test_answer
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
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import aiogram.utils.formatting as formatting


INFO_TEXT = '''
/name Сменить имя
/group Сменить группу
/assessment Начать контроль знаний
/stat Получить статистику по заданиям
/dispute Оспорить результаты
'''


TASK_COUNT_IN_ASSESSMENT = 5


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


async def send_info(message: Message) -> None:
    await message.answer(INFO_TEXT, reply_markup=ReplyKeyboardRemove())


async def to_main_menu(message: Message, state: FSMContext):
    await state.set_state(state=None)
    await send_info(message)


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
    await to_main_menu(message, state)


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
    await to_main_menu(message, state)


@dp.message(Registration.group)
async def registration_set_group(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    group = message.text
    db.insert_student(data["login"], data["name"], group)
    await proccess_login(message, state)
    await to_main_menu(message, state)


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


async def free_choice_ask(message: Message, state: FSMContext, domain, number) -> None:
    task = generate_free_choice_task(ontologies, domain)
    task.start = datetime.now()
    task.number = number
    task.question = generate_free_choice_task_text(task)
    await state.update_data(task=task)
    await message.answer(task.question)


async def test_ask(message: Message, state: FSMContext, domain, number) -> None:
    task = generate_test_task(ontologies, domain)
    task.start = datetime.now()
    task.number = number
    task.question = generate_test_task_text(task)
    await state.update_data(task=task)
    await message.answer(task.question, reply_markup=create_keyboard(task.options))


@dp.message(Assessment.type)
async def set_assessment_type(message: Message, state: FSMContext) -> None:
    try:
        assessment_type = string_to_assessment_type(message.text)
    except ValueError:
        await message.answer(
            "Неизвестный тип. Повторите выбор",
            reply_markup=create_keyboard([assessment_type_to_string(assessment_type) for assessment_type in AssessmentType]))
        return
    data = await get_data(message, state)
    domain = data["assessment_domain"]
    assessment_id=db.insert_assessment(data["login"], assessment_type, domain)
    await state.update_data(assessment_id=assessment_id)
    await state.update_data(passed=0)
    if AssessmentType.FreeChoice == assessment_type:
        await state.set_state(Assessment.free_choice)
        await message.answer(
            f"Начат контроль знаний \#`{assessment_id}`",
            parse_mode='MarkdownV2',
            reply_markup=ReplyKeyboardRemove())
        await free_choice_ask(message, state, domain, 1)
    elif AssessmentType.Test == assessment_type:
        await state.set_state(Assessment.test)
        await message.answer(
            f"Начат контроль знаний \#`{assessment_id}`",
            parse_mode='MarkdownV2',
            reply_markup=ReplyKeyboardRemove())
        await test_ask(message, state, domain, 1)
    else:
        await message.answer(
            "Неизвестный тип. Повторите выбор",
            reply_markup=create_keyboard([assessment_type_to_string(assessment_type) for assessment_type in AssessmentType]))


@dp.message(Assessment.free_choice)
async def proccess_free_choice(message: Message, state: FSMContext) -> None:
    data = await get_data(message, state)
    task = data["task"]
    passed = False
    passed_number = data["passed"]
    if not message.text:
        await message.answer("Неверно")
    elif check_free_choice_answer(ontologies, llm, task.domain, task.source, task.destination, message.text):
        await message.answer("Верно")
        passed = True
        passed_number += 1
        await state.update_data(passed=passed_number)
    else:
        await message.answer("Неверно")

    assessment_id = data["assessment_id"]
    db.insert_task(
        assessment_id,
        task.number,
        task.question,
        task.start,
        passed,
        {"source": task.source, "destination": task.destination, "difficulty": task.difficulty})

    if task.number == TASK_COUNT_IN_ASSESSMENT:
        await message.answer(
            f"Окончен контроль знаний \#`{assessment_id}`\.\nЗачтено {passed_number} из {TASK_COUNT_IN_ASSESSMENT}",
            parse_mode='MarkdownV2')
        await to_main_menu(message, state)
        return
    await free_choice_ask(message, state, task.domain, task.number + 1)


@dp.message(Assessment.test)
async def proccess_test(message: Message, state: FSMContext) -> None:
    data = await get_data(message, state)
    task = data["task"]
    passed = False
    passed_number = data["passed"]
    if not message.text:
        await message.answer("Неверно")
    elif check_test_answer(ontologies, task.domain, task.source, task.relation, message.text):
        await message.answer("Верно")
        passed = True
        passed_number += 1
        await state.update_data(passed=passed_number)
    else:
        await message.answer("Неверно")

    assessment_id = data["assessment_id"]
    db.insert_task(
        assessment_id,
        task.number,
        task.question,
        task.start,
        passed,
        {"source": task.source, "relation": task.relation.value, "options": task.options})

    if task.number == TASK_COUNT_IN_ASSESSMENT:
        await message.answer(
            f"Окончен контроль знаний \#`{assessment_id}`\.\nЗачтено {passed_number} из {TASK_COUNT_IN_ASSESSMENT}",
            parse_mode='MarkdownV2',
            reply_markup=ReplyKeyboardRemove())
        await to_main_menu(message, state)
        return
    await test_ask(message, state, task.domain, task.number + 1)


@dp.message(Command('stat'))
async def get_stat(message: Message, state: FSMContext) -> None:
    data = await get_data(message, state)
    stat = db.get_stat(data["login"])
    if 0 == len(stat):
        await message.answer("Задания не найдены")
        return
    formatting_list = [formatting.Bold("Результаты")]
    passed = 0
    challenged = 0
    total = 0
    for stat_for_type in stat:
        formatting_list.append(formatting.as_marked_section(
            formatting.Underline(assessment_type_to_string(AssessmentType(stat_for_type[0]))),
            formatting.as_key_value("Зачтены", stat_for_type[1]),
            formatting.as_key_value("Оспорены", stat_for_type[2]),
            formatting.as_key_value("Всего", stat_for_type[3])
        ))
        passed += stat_for_type[1]
        challenged += stat_for_type[2]
        total += stat_for_type[3]
    formatting_list.append(formatting.as_marked_section(
        formatting.Underline("Всего"),
        formatting.as_key_value("Зачтены", passed),
        formatting.as_key_value("Оспорены", challenged),
        formatting.as_key_value("Всего", total)
    ))
    await message.answer(**formatting.as_list(*formatting_list).as_kwargs())


@dp.message(Command('dispute'))
async def dispute_ask_assessment(message: Message, state: FSMContext) -> None:
    data = await get_data(message, state)
    assessments = db.get_assessments(data["login"])
    if 0 == len(assessments):
        await message.answer("Не найдены контроли знаний")
        await to_main_menu(message, state)
        return
    text = "Выберите контроль знаний:\n"
    for assessment in assessments:
        text += f"`{assessment[0]}` начат {assessment[1].strftime('%F %X')}\n"
    await state.set_state(Contestation.assessment)
    await message.answer(
        text.replace('-', '\-').replace('.', '\.'),
        parse_mode='MarkdownV2',
        reply_markup=create_keyboard([str(record[0]) for record in assessments]))


@dp.message(Contestation.assessment)
async def dispute_ask_task(message: Message, state: FSMContext) -> None:
    assessment_id = message.text
    data = await get_data(message, state)
    tasks = db.get_tasks(assessment_id, data["login"])
    if 0 == len(tasks):
        await message.answer(f"Не найдены подходящие задания в {assessment_id}")
        await to_main_menu(message, state)
        return
    await state.update_data(assessment_id=assessment_id)
    text = "Выберите задание:\n"
    for task in tasks:
        text += f"`{task[0]}`) начато {task[1].strftime('%F %X')} закончено {task[2].strftime('%F %X')}\n"
    await state.set_state(Contestation.task)
    await message.answer(
        text.replace('-', '\-').replace('.', '\.').replace(')', '\)'),
        parse_mode='MarkdownV2',
        reply_markup=create_keyboard([str(record[0]) for record in tasks]))


@dp.message(Contestation.task)
async def dispute_final(message: Message, state: FSMContext) -> None:
    task_number = message.text
    data = await get_data(message, state)
    try:
        db.insert_contestation(data["assessment_id"], task_number, data["login"])
    except:
        await message.answer("Произошла ошибка")
        await to_main_menu(message, state)
        return
    await message.answer("Оспаривание зарегистрировано")
    await to_main_menu(message, state)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
