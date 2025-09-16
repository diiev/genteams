import sqlite3

# Подключение к базе данных
conn = sqlite3.connect("players.db")
cursor = conn.cursor()


def create_table ():
    cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    speed INTEGER,
                    stamina INTEGER,
                    shot_power INTEGER,
                    shot_accuracy INTEGER,
                    pass_accuracy INTEGER,
                    teamwork INTEGER,
                    defense INTEGER,
                    dribbling INTEGER,
                    plays_today INTEGER,
                    total INTEGER)''')
conn.commit()


def db_add_player(message, data, total):
        # Сохраняем игрока в базу данных
    cursor.execute(
        "INSERT INTO players (user_id, name, speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, enterball, dribbling, total) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (message.from_user.id, data["name"], data["speed"], data["stamina"],
         data["shot_power"], data["shot_accuracy"], data["pass_accuracy"],
         data["teamwork"], data["defense"], data['enterball'], data["dribbling"], total)
    )
    conn.commit()



def db_show_players(callback_query):
    cursor.execute(
        "SELECT id, name, total FROM players WHERE user_id=?", (callback_query.from_user.id, )
    )
    conn.commit()   
    return cursor.fetchall()



def db_delete_player(message):
    cursor.execute("DELETE FROM players WHERE name=? AND user_id=?", (message.text, message.from_user.id))
    conn.commit()
 


def db_get_stats(player_name, user_id):
    cursor.execute(
        "SELECT speed, stamina, shot_power, shot_accuracy, pass_accuracy, teamwork, defense, enterball, dribbling "
        "FROM players WHERE name = ? AND user_id = ?",
        (player_name, user_id)
    )
    return cursor.fetchone()


def db_update_atrr(attribute, new_value, player_name, user_id):
    cursor.execute(
        f"UPDATE players SET {attribute} = ? WHERE name = ? AND user_id = ?",
        (new_value, player_name, user_id)
    ) 
     # Затем пересчитываем общий рейтинг для этого игрока
    cursor.execute(
        """
        UPDATE players 
        SET total = ROUND(
            (speed + stamina + shot_power + 
            shot_accuracy + pass_accuracy + 
            teamwork + defense + enterball + dribbling) / 9.0
        )
        WHERE name = ? AND user_id = ?
        """,
        (player_name, user_id)
    )
    conn.commit()


def db_get_update_players(player_name, user_id):
     # Получаем обновленные данные игрока
    cursor.execute(
        "SELECT name, total FROM players WHERE name = ? AND user_id = ?",
        (player_name, user_id)
    )  
    return cursor.fetchone()



def db_get_players_today(user_id):
     # Получаем игроков, которые будут играть сегодня
    cursor.execute("SELECT * FROM players WHERE user_id=? AND plays_today = 1", (user_id,))
    return cursor.fetchall()


def db_reset_plays_today(user_id):
    cursor.execute("""
            UPDATE players
            SET 
            plays_today = 0
            WHERE user_id = ?
            """, (user_id,))
    conn.commit()
    
def db_set_plays_today(player_name, user_id):
    cursor.execute("""
                   UPDATE players
                   SET 
                   plays_today = 1
                   WHERE name = ? AND user_id = ?
                   """, (player_name, user_id))
    conn.commit()


# def update_table():
#     cursor.execute('''ALTER TABLE players ADD COLUMN enterball INTEGER DEFAULT 0''')
#     conn.commit()

# def all():
#     cursor.execute("SELECT * FROM players")
#     return cursor.fetchall()




