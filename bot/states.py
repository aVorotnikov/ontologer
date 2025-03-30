#!/usr/bin/python3

from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    group = State()


class ChangeGroup(StatesGroup):
    group = State()


class ChangeName(StatesGroup):
    name = State()
