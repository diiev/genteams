from aiogram.fsm.state import State, StatesGroup 
from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton

from aiogram import types 
from aiogram import  Dispatcher
from aiogram.fsm.context import FSMContext
from database import db_show_players, db_get_stats, db_update_atrr, db_get_update_players
from utils.util import cancel_button, main_menu_keyboard, back_button, generate_pagination_keyboard
# Редактирование 
#######################################
class EditPlayerStates(StatesGroup):
    SELECT_PLAYER = State()
    SELECT_ATTRIBUTE = State()
    ENTER_NEW_VALUE = State()


dp = Dispatcher()
###################
# Обработчик команды редактирования игрока
PAGE_SIZE = 6



@dp.callback_query(lambda c: c.data == "edit_player")
async def edit_player_start(callback_query: types.CallbackQuery, state: FSMContext):
    players = db_show_players(callback_query)
    # msg = None
    # if type(callback_query) == types.CallbackQuery:
    #     msg = callback_query.message
    # else:
    #     msg = callback_query

    if not players:
        await callback_query.message.answer("У вас нет игроков для редактирования.")
        return
    
    await callback_query.message.answer(
        "Выберите игрока для редактирования:",
        reply_markup=generate_pagination_keyboard(players = players, page = 0, callback="edit_select", callback_page="edit_page")
    )
    await state.set_state(EditPlayerStates.SELECT_PLAYER)

@dp.callback_query(lambda c: c.data.startswith("edit_page_"))
async def edit_player_pagination(callback_query: types.CallbackQuery, state: FSMContext):
    page = int(callback_query.data.split("_")[2])
    players = db_show_players(callback_query)
    
    await callback_query.message.edit_reply_markup(reply_markup=generate_pagination_keyboard(players = players, page = page, callback="edit_select", callback_page="edit_page"))

############################################
# Обработчик отмены
@dp.callback_query(lambda c: c.data == "edit_cancel")
async def edit_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text(
        "Главное меню",
        reply_markup=main_menu_keyboard()
    )
    await callback_query.answer()

# Обработчик выбора игрока
@dp.callback_query(EditPlayerStates.SELECT_PLAYER, lambda c: c.data.startwidth("edit_select_"))
async def select_player_to_edit(callback_query: types.CallbackQuery, state: FSMContext):
    player_name = callback_query.data.replace("edit_select_", "")
    await state.update_data(player_name=player_name)
    
    
    stats = db_get_stats(player_name, callback_query.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Имя: {player_name}", callback_data="edit_name")],
        [InlineKeyboardButton(text=f"Скорость: {stats[0]}", callback_data="edit_speed")],
        [InlineKeyboardButton(text=f"Выносливость: {stats[1]}", callback_data="edit_stamina")],
        [InlineKeyboardButton(text=f"Сила удара: {stats[2]}", callback_data="edit_shot_power")],
        [InlineKeyboardButton(text=f"Точность удара: {stats[3]}", callback_data="edit_shot_accuracy")],
        [InlineKeyboardButton(text=f"Точность пасов: {stats[4]}", callback_data="edit_pass_accuracy")],
        [InlineKeyboardButton(text=f"Командная игра: {stats[5]}", callback_data="edit_teamwork")],
        [InlineKeyboardButton(text=f"Защита: {stats[6]}", callback_data="edit_defense")],
        [InlineKeyboardButton(text=f"Принятие мяча: {stats[7]}", callback_data="edit_enterball")],
        [InlineKeyboardButton(text=f"Дриблинг: {stats[8]}", callback_data="edit_dribbling")],
        back_button("edit_player"),
        cancel_button()
    ])
    
    await callback_query.message.edit_text(
        f"Текущие характеристики игрока {player_name}:\n"
        f"Выберите характеристику для изменения:",
        reply_markup=keyboard
    )
    await state.set_state(EditPlayerStates.SELECT_ATTRIBUTE)

# Обработчик выбора характеристики
@dp.callback_query(EditPlayerStates.SELECT_ATTRIBUTE)
async def select_attribute_to_edit(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "edit_cancel":
        await edit_cancel(callback_query, state)
        return
        
    attribute_map = {
        "edit_name": ("Имя", "name"),
        "edit_speed": ("Скорость", "speed"),
        "edit_stamina": ("Выносливость", "stamina"),
        "edit_shot_power": ("Сила удара", "shot_power"),
        "edit_shot_accuracy": ("Точность удара", "shot_accuracy"),
        "edit_pass_accuracy": ("Точность пасов", "pass_accuracy"),
        "edit_teamwork": ("Командная игра", "teamwork"),
        "edit_defense": ("Защита", "defense"),
        "edit_enterball": ("Принятие мяча", "enterball"),
        "edit_dribbling": ("Дриблинг", "dribbling")
    }
    
    attribute_data = attribute_map.get(callback_query.data)
    if not attribute_data:
        await callback_query.answer("Неизвестная характеристика")
        return
    display_name, db_field = attribute_data
    await state.update_data(attribute=db_field, attribute_display=display_name)
    data = await state.get_data()
    player_name = data["player_name"]  
    if attribute_data[0] == "Имя":
        await callback_query.message.answer(
        f"Введите новое имя игрока:")
    else:
        await callback_query.message.answer(
            f"Текущее значение {display_name} игрока {player_name}\n"
            f"Введите новое значение (0-99) или нажмите /cancel для отмены:"
        )
    await state.set_state(EditPlayerStates.ENTER_NEW_VALUE)

# Обработчик ввода нового значения
@dp.message(EditPlayerStates.ENTER_NEW_VALUE)
async def enter_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    player_name = data["player_name"]
    attribute = data["attribute"]
    attribute_display = data["attribute_display"]
    user_id = message.from_user.id
    if message.text == "/cancel":
        await state.clear()
        await message.answer(
            "Редактирование отменено.",
            reply_markup=main_menu_keyboard()
        )
        return
    if data["attribute"] != "name":
        if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
            await message.answer("Пожалуйста, введите число от 0 до 99 или /cancel для отмены.")
            return
    
       
        new_value = int(message.text)
        db_update_atrr(attribute, new_value, player_name, user_id)
        player = db_get_update_players(player_name, user_id)
        await message.answer(
            f"✅ {attribute_display.capitalize()} игрока {player_name} изменена на {new_value}.\n"
            f"Новый общий рейтинг: {player[1]}", reply_markup= main_menu_keyboard()

            
        )
    else:
        new_value = message.text
        db_update_atrr(attribute, new_value, player_name, user_id)
        await message.answer(
            f"✅ {attribute_display.capitalize()} игрока {player_name} изменена на {new_value}.\n", reply_markup= main_menu_keyboard())

   
    await state.clear()



