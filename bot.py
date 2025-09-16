import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.types import BotCommand
from config import BOT_TOKEN
from utils.util import main_menu_keyboard
from utils.generate_teams import *
from utils.add_player import *
from utils.show_players import *
from database import create_table
from utils.delete_player import *
from utils.edit_player import *

TOKEN = BOT_TOKEN



dp = Dispatcher()
create_table()

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await message.answer(
        "Привет! Я бот для генерации футбольной команды!", reply_markup=main_menu_keyboard() )  
    
@dp.message(Command("menu"))
async def command_menu_handler(message: types.Message) -> None:
    await message.answer("Главное меню",reply_markup=main_menu_keyboard())  

@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data
    message = callback_query
    current_state = await state.get_state()
    if action == "add_player":
        dp.message.register(process_name, AddPlayerStates.NAME)
        dp.message.register(process_speed, AddPlayerStates.SPEED)
        dp.message.register(process_stamina, AddPlayerStates.STAMINA)
        dp.message.register(process_shot_power, AddPlayerStates.SHOT_POWER)
        dp.message.register(process_shot_accuracy, AddPlayerStates.SHOT_ACCURACY)
        dp.message.register(process_pass_accuracy, AddPlayerStates.PASS_ACCURACY)
        dp.message.register(process_teamwork, AddPlayerStates.TEAMWORK)
        dp.message.register(process_defense, AddPlayerStates.DEFENSE)
        dp.message.register(process_enterball, AddPlayerStates.ENTER_BALL)
        dp.message.register(process_dribbling, AddPlayerStates.DRIBBLING)
        await cmd_add_player(message, state)
    elif action == "menu":
        await state.clear()
        await callback_query.message.answer("Главное меню", reply_markup=main_menu_keyboard())
    elif action.startswith("players:") or action == "players":
        await handle_players(message)
    elif action == "generate_teams":
        await genteams(message)
    elif action.startswith("generate_"):
        await handle_generation(message)
    elif action == "edit_player":
        await state.clear()
        await edit_player_start(message, state)
    elif action.startswith("edit_select_"):
        await state.clear()
        await select_player_to_edit(message, state)
    elif action.startswith("edit_page_"):
        await edit_player_pagination(message, state)
    elif action.startswith("s_edit_page_"):
        await select_player_pagination(message, state)
    elif current_state == EditPlayerStates.SELECT_ATTRIBUTE:
        dp.message.register(enter_new_value, EditPlayerStates.ENTER_NEW_VALUE)
        await  select_attribute_to_edit(message, state) 
    elif action.startswith("team_"):
        await handle_team_size(message, state)
    elif action.startswith('select_player_'):
        await select_players_today(message, state)
    elif action == "edit_cancel":
        await edit_cancel(message, state)
    elif action == "delete_player":
        await state.clear()
        dp.message.register(process_player_delete)
        await delete_player(message)
    await callback_query.answer()
    
async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await bot.set_my_commands(
    [BotCommand(command='start', description='Запуск бота'),
    BotCommand(command='menu', description='Главное меню')])
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())