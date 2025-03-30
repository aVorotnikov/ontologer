#!/usr/bin/python3

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_keyboard(buttons):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=text)] for text in buttons], resize_keyboard=True)
