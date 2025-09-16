from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types 
from database import db_show_players
# Функция для создания главного меню с inline-кнопками
def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить игрока", callback_data="add_player")],
        [InlineKeyboardButton(text="📋 Список игроков", callback_data="players")],
        [InlineKeyboardButton(text="👥 Сгенерировать команды", callback_data="generate_teams")],
        [InlineKeyboardButton(text="✏️ Редактировать игрока", callback_data="edit_player")],
        [InlineKeyboardButton(text="❌ Удалить игрока", callback_data="delete_player")],
    ])
    return keyboard



def back_button(callback):
    return [InlineKeyboardButton(text="🔙 Назад", callback_data=f"{callback}")]


def cancel_button():
    return [InlineKeyboardButton(text="❌ Отмена", callback_data="edit_cancel")]


def team_size_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="4x4", callback_data="team_4x4")],
        [InlineKeyboardButton(text="5x5", callback_data="team_5x5")],
        [InlineKeyboardButton(text="6x6", callback_data="team_6x6")],
        [InlineKeyboardButton(text="8x8", callback_data="team_8x8")]
    ])
    return keyboard



# Функция для балансировки команд
def balance_teams(players, team_size):
    players.sort(key=lambda x: x[1], reverse=True)  # Сортируем игроков по силе
    team1, team2 = [], []
    total1, total2 = 0, 0
    
    for player in players:
        if len(team1) < team_size and (total1 <= total2 or len(team2) >= team_size):
            team1.append(player)
            total1 += player[1]
        else:
            team2.append(player)
            total2 += player[1]
    
    return team1, team2



def generate_team_options_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⚖️ Сбалансированные", callback_data="generate_balanced")
    builder.button(text="🎲 Случайные", callback_data="generate_random")
    builder.button(text="↩️ Готово(возврат в меню)", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


def _build_pagination_kb(current_page: int, total_pages: int) -> types.InlineKeyboardMarkup:
    """Создает клавиатуру пагинации."""
    kb = []
    
    # Кнопки навигации
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="⬅️ Назад", 
                callback_data=f"players:{current_page - 1}"
            )
        )
    
    if current_page < total_pages:
        nav_buttons.append(
            types.InlineKeyboardButton(
                text="Вперед ➡️", 
                callback_data=f"players:{current_page + 1}"
            )
        )
    
    if nav_buttons:
        kb.append(nav_buttons)
    
    # Индикатор страницы (если больше 1 страницы)
    if total_pages > 1:
        kb.append([
            types.InlineKeyboardButton(
                text=f"Страница {current_page}/{total_pages}",
                callback_data="noop"  # Заглушка, ничего не делает
            )
        ])
    
    # Кнопка возврата в меню
    kb.append([
        types.InlineKeyboardButton(
            text="В главное меню",
            callback_data="menu"
        )
    ])
    
    return types.InlineKeyboardMarkup(inline_keyboard=kb)


def get_players_page(players, page=0, PAGE_SIZE = 6):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    return players[start:end]

def generate_pagination_keyboard(players, page=0,   PAGE_SIZE = 6, callback = "", callback_page = ""):
    total_pages = (len(players) - 1) // PAGE_SIZE + 1
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки игроков
    for p in get_players_page(players, page):
        builder.button(text=f"{p[1]} - {p[2]}", callback_data=f"{callback}_{p[1]}")

    # Добавляем кнопки пагинации
    if page > 0:
        builder.button(text="⬅️ Назад", callback_data=f"{callback_page}_{page-1}")
    if page < total_pages - 1:
        builder.button(text="Вперёд ➡️", callback_data=f"{callback_page}_{page+1}")

    # Добавляем кнопку отмены
    builder.button(text="❌ Отмена", callback_data="edit_cancel")

    builder.adjust(1)  # Автоматическое выравнивание кнопок
    return builder.as_markup()



async def player_pagination(callback_query: types.CallbackQuery, callback):
    page = int(callback_query.data.split("_")[2])
    players = db_show_players(callback_query)
    
    await callback_query.message.edit_reply_markup(reply_markup=generate_pagination_keyboard(players = players, page = page, callback=f"{callback}"))