from aiogram import  Dispatcher
from aiogram import types 
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Dict
from database import db_show_players
from utils.util import main_menu_keyboard, _build_pagination_kb


dp = Dispatcher()
# Показ игроков

@dp.callback_query(lambda c: c.data == "players")
async def handle_players(callback_query: types.CallbackQuery):
    # Обрабатываем пагинацию (формат "players:page_num")
    data_parts = callback_query.data.split(":")
    current_page = int(data_parts[1]) if len(data_parts) > 1 else 1
    items_per_page = 8
    
    # Получаем всех игроков
    all_players = db_show_players(callback_query)
    
    if not all_players:
        await callback_query.message.answer(
            "У вас пока нет игроков.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # Рассчитываем пагинацию
    total_players = len(all_players)
    total_pages = (total_players + items_per_page - 1) // items_per_page
    current_page = max(1, min(current_page, total_pages))  # Защита от выхода за границы
    
    # Получаем игроков для текущей страницы
    start_idx = (current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_players = all_players[start_idx:end_idx]
    
    # Формируем сообщение
    response = [f"Список игроков (страница {current_page}/{total_pages}):\nВсего игроков: {total_players}\n"]
    response.extend(
        f"{idx + start_idx + 1}. {player[1]} - Рейтинг: {player[2]}"
        for idx, player in enumerate(page_players)
    )
    
    # Создаем клавиатуру пагинации
    pagination_kb = _build_pagination_kb(current_page, total_pages)
    
    # Отправляем/редактируем сообщение
    if callback_query.data == "players":  # Первый запрос
        await callback_query.message.answer("\n".join(response), reply_markup=pagination_kb)
    else:  # Перелистывание страниц
        await callback_query.message.edit_text("\n".join(response), reply_markup=pagination_kb)



