import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random

logging.basicConfig(level=logging.DEBUG)

user_sessions = {}

# Generate a math question with additional types (addition, subtraction, multiplication, division)
def generate_question(level):
    if level == "easy":
        a, b = random.randint(1, 20), random.randint(1, 20)
        question = f"{a} + {b}"
        answer = a + b
        operation = "+"
    elif level == "medium":
        a, b = random.randint(10, 30), random.randint(2, 10)
        operation = random.choice(["×", "÷"])
        if operation == "×":
            question = f"{a} × {b}"
            answer = a * b
        else:
            b = random.randint(1, 10)
            question = f"{a} ÷ {b}"
            answer = a // b
    else:  # hard
        a, b = random.randint(50, 100), random.randint(10, 50)
        operation = random.choice(["+", "-", "×", "÷"])
        if operation == "+":
            question = f"{a} + {b}"
            answer = a + b
        elif operation == "-":
            question = f"{a} - {b}"
            answer = a - b
        elif operation == "×":
            question = f"{a} × {b}"
            answer = a * b
        else:  # division
            question = f"{a} ÷ {b}"
            answer = a // b

    options = {answer}
    while len(options) < 4:
        fake = random.randint(answer - 15, answer + 15)
        options.add(fake)
    return question, answer, list(options)

# Keyboard for setup menu
def get_main_menu(session):
    count = session["count"]
    level = session["level"]
    levels = ["easy", "medium", "hard"]
    level_buttons = [
        InlineKeyboardButton(f"{'🔘' if lvl == level else ''} {lvl.capitalize()}", callback_data=f"level_{lvl}")
        for lvl in levels
    ]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➖ 1", callback_data="sub_5"), InlineKeyboardButton(f"🎯 {count} Qs", callback_data="noop"), InlineKeyboardButton("➕ 5", callback_data="add_5")],
        level_buttons,
        [InlineKeyboardButton("▶️ Let's Start", callback_data="start_game")]
    ])

# /math command handler
@Client.on_message(filters.command("math"))
async def start_math_game(client, message: Message):
    user_id = message.from_user.id
    logging.debug(f"Starting math game for user {user_id}")
    
    user_sessions[user_id] = {
        "count": 5,
        "level": "easy",
        "score": 0,
        "current": 0,
        "game_over": False  # Track if the game is over
    }
    logging.debug(f"Session initialized: {user_sessions[user_id]}")
    
    await message.reply(
        "🎮 <b>Welcome to the Math Game!</b>\nChoose question count and difficulty level below:",
        reply_markup=get_main_menu(user_sessions[user_id])
    )

# Handle setup menu buttons
@Client.on_callback_query(filters.regex("^(add_5|sub_5|level_.*|start_game|noop)$"))
async def handle_setup_buttons(client, query: CallbackQuery):
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        return await query.answer("Session expired. Use /math to start again.", show_alert=True)

    data = query.data
    if data == "add_5":
        session["count"] += 5
        await query.answer("➕ +5 Questions")
    elif data == "sub_5" and session["count"] > 1:
        session["count"] -= 1
        await query.answer("➖ -1 Question")
    elif data.startswith("level_"):
        session["level"] = data.split("_")[1]
        await query.answer(f"✅ Level: {session['level'].capitalize()}")
    elif data == "start_game":
        await query.message.delete()
        return await send_next_question(client, query.message.chat.id, user_id)

    await query.message.edit(
        "🎮 <b>Welcome to the Math Game!</b>\nChoose question count and difficulty level below:",
        reply_markup=get_main_menu(session)
    )

# Send the next math question
async def send_next_question(client, chat_id, user_id):
    session = user_sessions.get(user_id)
    if not session or session["game_over"] or session["current"] >= session["count"]:
        session["game_over"] = True
        await client.send_message(
            chat_id,
            f"🏁 <b>Game Over!</b>\n✅ Score: {session['score']} / {session['count']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Play Again", callback_data="restart_game")]
            ])
        )
        return

    session["current"] += 1
    question, answer, options = generate_question(session["level"])
    session["answer"] = answer
    session["question"] = question

    random.shuffle(options)
    buttons = [
        [InlineKeyboardButton(str(opt), callback_data=f"answer_{opt}")]
        for opt in options
    ]
    buttons.append([InlineKeyboardButton("🛑 Stop", callback_data="stop_game")])

    text = f"❓ <b>Q{session['current']} of {session['count']}:</b>\n<code>{question}</code> = ?"
    await client.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(buttons))

# Handle answer selection
@Client.on_callback_query(filters.regex("^answer_"))
async def handle_answer(client, query: CallbackQuery):
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    if not session:
        return await query.answer("Session expired. Use /math to start again.", show_alert=True)

    if session["game_over"]:
        return await query.answer("Game over! You cannot answer anymore.", show_alert=True)

    selected = int(query.data.split("_")[1])
    correct = session["answer"]
    question = session["question"]

    if selected == correct:
        session["score"] += 1
        mark = "✅"
    else:
        mark = "❌"
        await query.answer(f"{mark} Wrong!\n{question} = {correct}", show_alert=True)
        return await send_next_question(client, query.message.chat.id, user_id)

    await query.answer()
    await send_next_question(client, query.message.chat.id, user_id)

# Stop game manually
@Client.on_callback_query(filters.regex("^stop_game$"))
async def stop_game(_, query: CallbackQuery):
    user_id = query.from_user.id
    session = user_sessions.pop(user_id, None)
    if session:
        score = session["score"]
        total = session["count"]
        await query.message.edit_text(f"🛑 Game stopped.\nFinal Score: {score} / {total}")

# Restart game from play again
@Client.on_callback_query(filters.regex("^restart_game$"))
async def restart_game(client, query: CallbackQuery):
    user_id = query.from_user.id
    old_session = user_sessions.get(user_id)

    if not old_session:
        return await query.answer("Session expired. Use /math to start again.", show_alert=True)

    user_sessions[user_id] = {
        "count": old_session["count"],
        "level": old_session["level"],
        "score": 0,
        "current": 0,
        "game_over": False
    }

    await query.message.delete()
    await send_next_question(client, query.message.chat.id, user_id)
