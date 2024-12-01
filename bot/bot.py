#!/usr/bin/python3

from llm_connector import LlmConnector
from ontologies_connector import OntologiesConnector
from generate_task import generate_task, generate_task_text
from checker import check_answer

import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


DOMAIN = "Наивная теория множеств"


TOKEN = getenv("BOT_TOKEN")
llm = LlmConnector()
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
uri = f"neo4j://{NEO4J_IP}:{NEO4J_PORT}"
auth = (NEO4J_USER, NEO4J_PWD)
ontologies = OntologiesConnector(uri, auth)


dp = Dispatcher()

tasks = dict()


async def ask(message: Message) -> None:
    task = generate_task(ontologies, DOMAIN)
    tasks[message.chat.id] = task
    await message.answer(generate_task_text(task))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await ask(message)


@dp.message()
async def get_answer(message: Message) -> None:
    if message.chat.id in tasks:
        task = tasks[message.chat.id]
        if not message.text:
            await message.answer("Сообщение не содержит текста")
        else:
            if check_answer(ontologies, llm, DOMAIN, task.source, task.destination, message.text):
                await message.answer("Верно")
            else:
                await message.answer("Неверно")
    await ask(message)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
