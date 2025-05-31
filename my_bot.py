from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# Твой Telegram Bot API токен
BOT_TOKEN = "7840656624:AAHGSvPGLLv3AVMOcmxl21ZPAyDr9LrKCjo"

# ID администратора (твое Telegram ID)
ADMIN_ID = 209559273

anon_users = {}
user_to_anon = {}
anon_counter = 1

# Старт — картинка + текст после картинки
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("/Users/geo/Downloads/Бот/welcome.jpg", "rb") as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo
        )

    # Отправляем текст отдельным сообщением
    await update.message.reply_text(
        "Отправь текст, фото или видео — и я анонимно передам это админу канала Дешёвый Дофамин (Насте) 😊"
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — начать\n"
        "/help — помощь\n"
        "Отправьте сообщение (текст, фото, видео) — оно будет передано анонимно."
    )

# Назначение анонимного ID
def get_anon_id(user_id):
    global anon_counter
    if user_id not in user_to_anon:
        anon_id = f"User#{anon_counter}"
        anon_users[anon_id] = user_id
        user_to_anon[user_id] = anon_id
        anon_counter += 1
    return user_to_anon[user_id]

# Обработка текста
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id == ADMIN_ID and context.user_data.get("reply_to_user"):
        target_user = context.user_data.pop("reply_to_user")
        await context.bot.send_message(chat_id=target_user, text=f"💬 Ответ от администратора:\n{update.message.text}")
        await update.message.reply_text("✅ Ответ отправлен!")
        return

    anon_id = get_anon_id(user_id)
    text = update.message.text

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ответить", callback_data=f"reply:{anon_id}")]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 Сообщение от {anon_id}:\n\n{text}",
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ Сообщение отправлено анонимно!")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id == ADMIN_ID and context.user_data.get("reply_to_user"):
        target_user = context.user_data.pop("reply_to_user")
        photo = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        await context.bot.send_photo(chat_id=target_user, photo=photo, caption=f"💬 Ответ от администратора:\n{caption}")
        await update.message.reply_text("✅ Ответ отправлен!")
        return

    anon_id = get_anon_id(user_id)
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or ""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ответить", callback_data=f"reply:{anon_id}")]
    ])

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"📷 Фото от {anon_id}:\n{caption}",
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ Фото отправлено анонимно!")

# Обработка видео
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id == ADMIN_ID and context.user_data.get("reply_to_user"):
        target_user = context.user_data.pop("reply_to_user")
        video = update.message.video.file_id
        caption = update.message.caption or ""
        await context.bot.send_video(chat_id=target_user, video=video, caption=f"💬 Ответ от администратора:\n{caption}")
        await update.message.reply_text("✅ Ответ отправлен!")
        return

    anon_id = get_anon_id(user_id)
    video = update.message.video.file_id
    caption = update.message.caption or ""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ответить", callback_data=f"reply:{anon_id}")]
    ])

    await context.bot.send_video(
        chat_id=ADMIN_ID,
        video=video,
        caption=f"🎥 Видео от {anon_id}:\n{caption}",
        reply_markup=keyboard
    )

    await update.message.reply_text("✅ Видео отправлено анонимно!")

# Обработка кнопки «Ответить»
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("reply:"):
        anon_id = data.split(":")[1]
        if anon_id in anon_users:
            context.user_data["reply_to_user"] = anon_users[anon_id]
            await query.message.reply_text("✏️ Напиши свой ответ — он будет отправлен пользователю.")
        else:
            await query.message.reply_text("❌ Пользователь не найден.")

# Инициализация
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))
app.add_handler(CallbackQueryHandler(button_callback))

print("✅ Бот запущен и готов принимать команды!")
app.run_polling()
