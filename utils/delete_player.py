from aiogram import  Dispatcher
from aiogram import types 
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict
from database import db_show_players, db_delete_player
from utils.util import main_menu_keyboard, _build_pagination_kb

dp = Dispatcher()

# Обработчик удаления игрока
@dp.callback_query(lambda c: c.data == "delete_player")
async def delete_player(callback_query: types.CallbackQuery):
    players = db_show_players(callback_query)

    if not players: 
        await callback_query.message.answer("У вас нет зарегистрированных игроков.")
        return
    await callback_query.message.answer("Введите имя игрока который хотите удалить:", )


@dp.message(lambda message: message.text and not message.text.startswith("/") and (
    message.text.lower().startswith("delete ") or message.text in [player[1] for player in db_show_players(message)]
))
async def process_player_delete(message: types.Message):
    players = db_show_players(message)
    player_names = [player[1] for player in players]
    
    if message.text in player_names:
        db_delete_player(message)
        await message.answer(
            f"Игрок {message.text} удален.",
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(
            "Игрок не найден. Нажмите на список игроков, чтобы просмотреть игроков в базе:",
            reply_markup=main_menu_keyboard())
        
