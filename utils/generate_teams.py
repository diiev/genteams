from aiogram import types 
from aiogram import  Dispatcher
from utils.util import team_size_keyboard, generate_pagination_keyboard, generate_team_options_keyboard, main_menu_keyboard
from database import db_show_players, db_set_plays_today, db_get_players_today, db_reset_plays_today
from aiogram.fsm.state import State, StatesGroup 
from aiogram.fsm.context import FSMContext

dp = Dispatcher ()

class TeamSelection(StatesGroup):
    selecting_players = State()  # Состояние выбора игроков


@dp.callback_query(lambda c: c.data == "genteams")
async def genteams (callback_query: types.CallbackQuery):
    await callback_query.message.answer("Выберите размер игры:", reply_markup=team_size_keyboard())



@dp.callback_query(lambda c: c.data.startwidth("team_"))
async def handle_team_size(callback_query: types.CallbackQuery,  state: FSMContext):
    team_size_str = callback_query.data.split("_")[1]  # "5x5", "6x6" и т.д.
    team_size = int(team_size_str.split("x")[0])
    await state.set_state(TeamSelection.selecting_players)  # Устанавливаем состояние
    await state.update_data(
    team_size=team_size_str,
    selected_players=[],  # Очищаем предыдущий выбор
    current_page = 0
    )
    
    players = db_show_players(callback_query)
    db_reset_plays_today(callback_query.from_user.id)
    if len(players) < team_size * 2:
        await callback_query.message.answer(f"Недостаочно игроков, для игры на {team_size_str}\nВыберите другой размер игры или добавьте игроков в главном меню", reply_markup=team_size_keyboard())
    else:
        await callback_query.message.answer(f'Выберите игроков, которые будут играть сегодня (нужно {team_size * 2} чел.): ', 
        reply_markup=generate_pagination_keyboard(players=players, 
        page=0, 
        callback=f"select_player_{team_size}", 
        callback_page="s_edit_page"))

   
    await callback_query.answer()  # Подтверждаем нажатие


@dp.callback_query(lambda c: c.data.startswith("select_player_"))
async def select_players_today(
    callback_query: types.CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()
    
    # Восстанавливаем состояние, если оно сброшено
    if not data:
        await callback_query.message.answer("❌ Сессия была сброшена. Начните заново.")
        return
    
    # Инициализация списка, если его нет
    data.setdefault("selected_players", [])
    
    # Разбираем callback_data
    try:
        _, _, team_size_str, player_name = callback_query.data.split("_")
        team_size = int(team_size_str.split("x")[0])
    except (ValueError, IndexError):
        await callback_query.answer("⚠️ Ошибка формата данных", show_alert=True)
        return

    max_players = team_size * 2

    # Проверка дубликата
    if player_name in data["selected_players"]:
        data['selected_players'].remove(player_name)
        await callback_query.answer("❌ Игрок отменен!")
        remaining = max_players - len(data["selected_players"])
        # Обновляем сообщение при отмене игрока
        try:
            if "selection_message_id" in data:
                await callback_query.bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=data["selection_message_id"],
                    text=f"✅ Выбрано: {len(data['selected_players'])}/{max_players}\nОсталось: {remaining}"
                )
            else:
                msg = await callback_query.message.answer(
                    f"Выбрано игроков: {len(data['selected_players'])}/{max_players}\nОсталось: {remaining}"
                )
                await state.update_data(selection_message_id=msg.message_id)
        except Exception as e:
            msg = await callback_query.message.answer(
                f"Выбрано игроков: {len(data['selected_players'])}/{max_players}\nОсталось: {remaining}"
            )
            await state.update_data(selection_message_id=msg.message_id)
        
        await state.update_data(selected_players=data["selected_players"])
        return

    # Проверка лимита
    if len(data["selected_players"]) >= max_players:
        await callback_query.answer("🚫 Лимит достигнут!", show_alert=True)
        return

    # Обновляем данные
    data["selected_players"].append(player_name)
    await state.update_data(selected_players=data["selected_players"])

    remaining = max_players - len(data["selected_players"])

    # Восстанавливаем/обновляем сообщение
    try:
        if "selection_message_id" in data:
            await callback_query.bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=data["selection_message_id"],
                text=f"✅ Выбрано: {len(data['selected_players'])}/{max_players}\nОсталось: {remaining}"
            )
        else:
            msg = await callback_query.message.answer(
                f"Выбрано игроков: {len(data['selected_players'])}/{max_players}\nОсталось: {remaining}"
            )
            await state.update_data(selection_message_id=msg.message_id)
    except Exception as e:
        # Если сообщение было удалено - создаем новое
        msg = await callback_query.message.answer(
            f"Выбрано игроков: {len(data['selected_players'])}/{max_players}\nОсталось: {remaining}"
        )
        await state.update_data(selection_message_id=msg.message_id)

    await callback_query.answer(f"Добавлен игрок: {player_name}")
    db_set_plays_today(player_name, callback_query.from_user.id)

    # Если все игроки выбраны
    if remaining == 0:
        await callback_query.message.answer(
            "Все игроки выбраны! Генерируем команды...",
            reply_markup=generate_team_options_keyboard()  # Ваша клавиатура с вариантами
        )




@dp.callback_query(lambda c: c.data.startswith("s_edit_page_"))
async def select_player_pagination(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    team_size_str = data["team_size"]  # Получаем сохраненный размер команды
    page = int(callback_query.data.split("_")[3])
    await state.update_data(current_page=page)  # Обновляем текущую страницу
    players = db_show_players(callback_query)
    await callback_query.message.edit_reply_markup(
        reply_markup=generate_pagination_keyboard(
            players=players,
            page=page,
            callback=f"select_player_{team_size_str}", # Передаем team_size_str
            callback_page="s_edit_page"
        )
    )
    await callback_query.answer()




import random
from typing import List, Tuple
def get_player_stats(player: Tuple) -> dict:
    """Извлекает характеристики игрока из кортежа"""
    return {
        'speed': player[3],
        'stamina': player[4],
        'shot_power': player[5],
        'shot_accuracy': player[6],
        'pass_accuracy': player[7],
        'teamwork': player[8],
        'defense': player[9],
        'dribbling': player[10],
        'enterball': player[13]
    } 

def calculate_total_rating(player: Tuple) -> int:
    # """Вычисляет общий рейтинг игрока"""
    # stats = get_player_stats(player)
    # print(stats)
    # print(sum(stats.values()))
    # return sum(stats.values())
    return player[-2]


def balance_teams(players: List[Tuple], team_size: int, max_attempts: int = 100) -> Tuple[List, List]:
    """
    Балансирует команды по общему рейтингу с ограничением на разницу рейтингов
    и возможностью перетасовки при повторных вызовах.
    
    Args:
        players: [(id, user_id, name, speed, stamina, ...), ...]
        team_size: количество игроков в команде
        max_attempts: максимальное количество попыток балансировки
        
    Returns:
        Кортеж из двух команд (team1, team2)
    """
    if len(players) < 2 * team_size:
        raise ValueError("Недостаточно игроков для формирования команд")
    
    # Сортируем по убыванию общего рейтинга для начального распределения
    sorted_players = sorted(players, key=calculate_total_rating, reverse=True)
    
    best_team1 = []
    best_team2 = []
    min_diff = float('inf')
    
    for attempt in range(max_attempts):
        # Перемешиваем игроков для разных попыток (кроме первой)
        if attempt > 0:
            random.shuffle(sorted_players)
        
        team1 = []
        team2 = []
        
        # Распределяем игроков змейкой
        for i, player in enumerate(sorted_players[:2*team_size]):
            if i % 2 == 0:
                team1.append(player)
            else:
                team2.append(player)
        
        # Вычисляем общий рейтинг команд
        rating1 = sum(calculate_total_rating(p) for p in team1[:team_size]) / len(team1)
        rating2 = sum(calculate_total_rating(p) for p in team2[:team_size]) / len(team2)
        diff = abs(rating1 - rating2)
        
        # Если разница удовлетворительная, возвращаем сразу
        if diff <= 1.5:
            return team1[:team_size], team2[:team_size]
        
        # Сохраняем лучший вариант
        if diff < min_diff:
            min_diff = diff
            best_team1, best_team2 = team1[:team_size], team2[:team_size]
    
    # Если не нашли идеальный вариант, возвращаем лучший из найденных
    return best_team1, best_team2


def random_teams(players: List[Tuple], team_size: int) -> Tuple[List, List]:
    """Случайное распределение игроков"""
    shuffled = random.sample(players, len(players))
    return shuffled[:team_size], shuffled[team_size:team_size*2]

def generate_teams_response(team1: List[Tuple], team2: List[Tuple]) -> str:
    """Формирует красивое сообщение с командами"""
    def calculate_team_stats(team):
        stats = {
            'total': sum(calculate_total_rating(p) for p in team) / len(team),
            'names': [p[2] for p in team]  # Имена игроков
        }
        # Добавляем все характеристики
        stats.update({k: sum(get_player_stats(p)[k] for p in team) / len(team)
                    for k in get_player_stats(team[0])})
        return stats
    
    stats1 = calculate_team_stats(team1)
    stats2 = calculate_team_stats(team2)
    
    response = (
        f"⚽ <b>Команда 1</b> (Общий рейтинг: {stats1['total']:.1f})\n"
        f"🏃 Скорость: {stats1['speed']:.2f} | 🏋️‍♂️ Выносливость: {stats1['stamina']:.1f}\n"
        f"💪 Сила удара: {stats1['shot_power']:.2f} | 🎯 Точность удара: {stats1['shot_accuracy']:.1f}\n"
        f"📡 Точность пасов: {stats1['pass_accuracy']:.1f} | 🤝 Командная игра: {stats1['teamwork']:.1f}\n"
        f"🛡️ Защита: {stats1['defense']:.1f} | 🏃‍♂️ Дриблинг: {stats1['dribbling']:.1f}\n"
        f"🤾🏿‍♂️ Принятие мяча: {stats1['enterball']:.1f}\n"
        "Состав:\n" + "\n".join([f"• {name}" for name in stats1['names']]) + "\n\n"
        
        f"⚽ <b>Команда 2</b> (Общий рейтинг: {stats2['total']:.1f})\n"
        f"🏃 Скорость: {stats2['speed']:.1f} | 🏋️‍♂️ Выносливость: {stats2['stamina']:.1f}\n"
        f"💪 Сила удара: {stats2['shot_power']:.1f} | 🎯 Точность удара: {stats2['shot_accuracy']:.1f}\n"
        f"📡 Точность пасов: {stats2['pass_accuracy']:.1f} | 🤝 Командная игра: {stats2['teamwork']:.1f}\n"
        f"🛡️ Защита: {stats2['defense']:.1f} | 🏃‍♂️ Дриблинг: {stats2['dribbling']:.1f}\n"
        f"🤾🏿‍♂️ Принятие мяча: {stats2['enterball']:.1f}\n"
        "Состав:\n" + "\n".join([f"• {name}" for name in stats2['names']])
    )
    
    return response




@dp.callback_query(lambda c: c.data.startswith("generate_"))
async def handle_generation(callback_query: types.CallbackQuery):
    selected_players = db_get_players_today(callback_query.from_user.id)
    if callback_query.data == "generate_balanced":
        team1, team2 = balance_teams(selected_players, len(selected_players)//2)
    else:
        team1, team2 = random_teams(selected_players, len(selected_players)//2)
    
    await callback_query.message.answer(
        generate_teams_response(team1, team2),
        reply_markup=generate_team_options_keyboard()
    )