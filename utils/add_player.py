from aiogram.fsm.state import State, StatesGroup
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher 
from database import db_add_player, db_show_players
from utils.util import main_menu_keyboard


dp = Dispatcher()
# Состояния для FSM
class AddPlayerStates(StatesGroup):
    NAME = State()
    SPEED = State()
    STAMINA = State()
    SHOT_POWER = State()
    SHOT_ACCURACY = State()
    PASS_ACCURACY = State()
    TEAMWORK = State()
    DEFENSE = State()
    DRIBBLING = State()
    ENTER_BALL = State()


async def cmd_add_player(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите имя игрока:")
    await state.set_state(AddPlayerStates.NAME) 


# Обработчик для ввода имени
@dp.message(AddPlayerStates.NAME)
async def process_name(message: types.Message, state: FSMContext):
    existing_players = [name[1] for name in db_show_players(message)]
    player_name = message.text.strip()
     # Проверяем, существует ли уже такое имя
    if player_name in existing_players:
        await message.answer("Игрок с таким именем уже существует! Введите другое имя:")
        return
    await state.update_data(name=message.text)
    await message.answer("Введите скорость игрока (0-100):")
    await state.set_state(AddPlayerStates.SPEED)

# Обработчик для ввода скорости
@dp.message(AddPlayerStates.SPEED)
async def process_speed(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(speed=int(message.text))
    await message.answer("Введите выносливость игрока (0-99):")
    await state.set_state(AddPlayerStates.STAMINA)

# Обработчик для ввода выносливости
@dp.message(AddPlayerStates.STAMINA)
async def process_stamina(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(stamina=int(message.text))
    await message.answer("Введите силу удара игрока (0-99):")
    await state.set_state(AddPlayerStates.SHOT_POWER)

# Обработчик для ввода силы удара
@dp.message(AddPlayerStates.SHOT_POWER)
async def process_shot_power(message: types.Message, state: FSMContext):
   
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(shot_power=int(message.text))
    await message.answer("Введите точность удара игрока (0-99):")
    await state.set_state(AddPlayerStates.SHOT_ACCURACY)

# Обработчик для ввода точности удара
@dp.message(AddPlayerStates.SHOT_ACCURACY)
async def process_shot_accuracy(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(shot_accuracy=int(message.text))
    await message.answer("Введите точность пасов игрока (0-99):")
    await state.set_state(AddPlayerStates.PASS_ACCURACY)

# Обработчик для ввода точности пасов
@dp.message(AddPlayerStates.PASS_ACCURACY)
async def process_pass_accuracy(message: types.Message, state: FSMContext):
    
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(pass_accuracy=int(message.text))
    await message.answer("Введите командную игру игрока (0-99):")
    await state.set_state(AddPlayerStates.TEAMWORK)

# Обработчик для ввода командной игры
@dp.message(AddPlayerStates.TEAMWORK)
async def process_teamwork(message: types.Message, state: FSMContext):
   
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(teamwork=int(message.text))
    await message.answer("Введите защиту игрока (0-99):")
    await state.set_state(AddPlayerStates.DEFENSE)

# Обработчик для ввода защиты
@dp.message(AddPlayerStates.DEFENSE)
async def process_defense(message: types.Message, state: FSMContext):
 
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(defense=int(message.text))
    await message.answer("Введите уровень принятия мяча игрока (0-99):")
    await state.set_state(AddPlayerStates.ENTER_BALL)

# Обработчик для ввода принятия мяча
@dp.message(AddPlayerStates.ENTER_BALL)
async def process_enterball(message: types.Message, state: FSMContext):
 
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return
    await state.update_data(enterball=int(message.text))
    await message.answer("Введите дриблинг игрока (0-99):")
    await state.set_state(AddPlayerStates.DRIBBLING)

# Обработчик для ввода дриблинга
@dp.message(AddPlayerStates.DRIBBLING)
async def process_dribbling(message: types.Message, state: FSMContext):
    
    if not message.text.isdigit() or not (0 <= int(message.text) <= 99):
        await message.answer("Пожалуйста, введите число от 0 до 99.")
        return

    # Сохраняем дриблинг и завершаем сбор данных
    await state.update_data(dribbling=int(message.text))
    data = await state.get_data()

    # Вычисляем общий рейтинг
    total =  (
        data["speed"] + data["stamina"] + data["shot_power"] +
        data["shot_accuracy"] + data["pass_accuracy"] +
        data["teamwork"] + data["defense"] + data['enterball'] + data["dribbling"]
    ) 
    total = int(total / 9)
    db_add_player(message, data, total)
    await message.answer(f"Игрок {data['name']} успешно добавлен с общим рейтингом {total}!", reply_markup=main_menu_keyboard())
    await state.clear()
