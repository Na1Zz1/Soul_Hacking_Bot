import os
import logging
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
MANAGER_ID = int(os.getenv("MANAGER_ID"))

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

PDF_FILES = {
    "mass": "massa.pdf",
    "weightloss": "weightloss.pdf"
}

# =========================
# 🔹 Логирование
# =========================
logging.basicConfig(level=logging.INFO)

# =========================
# 🔹 Функция удаления сообщений
# =========================
async def safe_delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.message.delete()
    except Exception:
        pass

# =========================
# 🔹 Главное меню
# =========================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎁 ПОЛУЧИТЬ ПРОБНЫЕ ПРОГРАММЫ", callback_data="trial_plan")],
        [InlineKeyboardButton("💪 Персональная программа тренировок", callback_data="buy_program")],
        [InlineKeyboardButton("🔒 Вход в закрытый Telegram-канал", callback_data="private_channel")],
        [InlineKeyboardButton("📩 Обратная связь", callback_data="feedback")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет, спортсмен! Добро пожаловать в официальный бот Soul Hacking Club.\n \n"
        "Здесь мы превращаем твое желание измениться в четкий и работающий план.\n \n"
        "🎯 Что ты получишь?\n"
        "• Персональные программы: Планы тренировок, идеально подстроенные под твои цели (масса, рельеф, сила, выносливость).\n"
        '• Доказательную базу: Не просто "делай так", а понятные объяснения по питанию, восстановлению и методикам.\n'
        "• Старт без риска: Получи пробную программу бесплатно, чтобы оценить наш подход.\n \n"
        "👇 Выбирай, с чего начать:",
        reply_markup=main_menu_keyboard()
    )

# =========================
# 🔹 Пробный план
# =========================
async def trial_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_delete_message(update, context)
    keyboard = [
        [InlineKeyboardButton("💪 Набрать мышечную массу", callback_data="goal_massa")],
        [InlineKeyboardButton("🔥 Сбросить лишний вес", callback_data="goal_weightloss")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")]
    ]
    await update.callback_query.message.reply_text(
        "Выбери цель для пробной программы:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# 🔹 Выбор цели
# =========================
async def goal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_delete_message(update, context)
    query = update.callback_query
    goal = query.data.replace("goal_", "")
    context.user_data["goal"] = goal

    keyboard = [
        [InlineKeyboardButton("🔗 Перейти к каналу", url=f"https://t.me/{CHANNEL_ID[1:]}")],
        [InlineKeyboardButton("✅ Проверить подписку", callback_data="check_subscription")],
        [InlineKeyboardButton("⬅ Назад", callback_data="trial_plan")]
    ]
    await query.message.reply_text(
        f"Подпишись на наш канал, чтобы получить пробный план:\n{CHANNEL_ID}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# 🔹 Проверка подписки и выдача PDF
# =========================
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    goal = context.user_data.get("goal")

    caption = "✅ Твой план тренировок готов! 💪"  # всегда определена

    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            file_path = PDF_FILES.get(goal)
            if file_path and os.path.exists(file_path):
                # Сохраняем сообщение с кнопками для удаления
                buttons_message = query.message

                # Отправляем PDF с caption
                with open(file_path, "rb") as f:
                    await query.message.reply_document(InputFile(f, filename=os.path.basename(file_path)), caption=caption)

                # Удаляем старое сообщение с кнопками
                try:
                    await buttons_message.delete()
                except:
                    pass

                # Отправляем меню после выдачи PDF
                await query.message.reply_text(
                    "Выбери действие:",
                    reply_markup=main_menu_keyboard()
                )
            else:
                # Если файл не найден
                await query.message.reply_text("❌ Файл для этой цели не найден.", reply_markup=main_menu_keyboard())
        else:
            await query.message.reply_text("❌ Подпишись на канал, чтобы получить план.", reply_markup=main_menu_keyboard())
    except Exception as e:
        await query.message.reply_text(f"⚠️ Ошибка при проверке подписки: {e}", reply_markup=main_menu_keyboard())

# =========================
# 🔹 Персональная программа
# =========================
async def buy_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_delete_message(update, context)
    keyboard = [
        [InlineKeyboardButton("💳 Заказать персональную программу тренировок (450 руб.)", url="https://t.me/tribute/app?startapp=plQZ")],
        [InlineKeyboardButton("❓ Задать вопрос", callback_data="buy_feedback")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")]
    ]
    message_text = (
       "ПЕРСОНАЛЬНАЯ ПРОГРАММА ТРЕНИРОВОК🔥\n \n"

        "📄Получи полностью индивидуальный план, созданный под твои цели, уровень подготовки и условия — домашние или зал.\n \n"

        "📋 В ПРОГРАММЕ БУДЕТ УЧТЕНО:\n"
        "— вес, рост и пол,\n"
        "— цель (похудение/набор массы/рельеф),\n"
        "— травмы и ограничения,\n"
        "— частота тренировок в неделю,\n"
        "— оборудование (что есть у тебя дома / в зале),\n"
        "— опционально рекомендации по питанию и восстановлению.\n \n"

        "💸СТОИМОСТЬ ДОСТУПА: 4️⃣5️⃣0️⃣ руб\n"
        "❗️После оплаты ты получишь наш username в Telegram, куда нужно будет написать ответы на вопросы для составления программы."
    )
    await update.callback_query.message.reply_text(
        message_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# 🔹 Задать вопрос по персональной тренировке
# =========================

async def buy_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_delete_message(update, context)
    context.user_data["awaiting_buy_feedback"] = True

    keyboard = [
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")]
    ]

    await update.callback_query.message.reply_text(
        "✍️ Напиши свой вопрос по персональной программе. Мы ответим как можно быстрее.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# 🔹 Вход в закрытый канал
# =========================
async def private_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_delete_message(update, context)
    keyboard = [
        [InlineKeyboardButton("💳 Подписаться (100 руб.)", url="https://t.me/tribute/app?startapp=sE8y")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")]
    ]
    await update.callback_query.message.reply_text(
        '<b>ЗАКРЫТЫЙ КАНАЛ SOUL HACKING CLUB🔒\n \n⛔️ Получи доступ в приватное сообщество, где есть вся информация про:\n— программы и техники тренировок,\n— качественный набор/сушку, КБЖУ,\n— добавки и БАДы,\n — спортивные мифы,\n — мотивацию и дисциплину,\n — самореализацию и философию,\n— эксклюзивные материалы, которых нет в открытом доступе.\n \n💸СТОИМОСТЬ ДОСТУПА: 1️⃣0️⃣0️⃣ руб.\n❗️После оплаты ты получишь ссылку на канал, который откроет тебе доступ к закрытому контенту.</b>',
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# 🔹 Обратная связь
# =========================
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_delete_message(update, context)
    keyboard = [
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")]
    ]
    await update.callback_query.message.reply_text(
        "Можешь оставить отзыв или написать обращение. Время ответа около 15-30 минут. 💬",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data["awaiting_feedback"] = True

async def handle_feedback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        text = update.message.text

        if context.user_data.get("awaiting_feedback") or context.user_data.get("awaiting_buy_feedback"):
            await update.message.reply_text("✅ Спасибо! Сообщение отправлено.")
            await context.bot.send_message(
                MANAGER_ID,
                f"📩 Новое сообщение от {user.first_name} (@{user.username}):\n\n{text}"
        )
        context.user_data["awaiting_feedback"] = False
        context.user_data["awaiting_buy_feedback"] = False

# =========================
# 🔹 Кнопка Назад
# =========================
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_delete_message(update, context)
    await update.callback_query.message.reply_text(
        "Главное меню:",
        reply_markup=main_menu_keyboard()
    )

# =========================
# 🔹 MAIN
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(trial_plan, pattern="trial_plan"))
    app.add_handler(CallbackQueryHandler(goal_selection, pattern="goal_"))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    app.add_handler(CallbackQueryHandler(buy_program, pattern="buy_program"))
    app.add_handler(CallbackQueryHandler(private_channel, pattern="private_channel"))
    app.add_handler(CallbackQueryHandler(feedback, pattern="feedback"))
    app.add_handler(CallbackQueryHandler(buy_feedback, pattern="buy_feedback"))
    app.add_handler(CallbackQueryHandler(back_to_menu, pattern="back_to_menu"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_message))

    app.run_polling()

if __name__ == "__main__":
    main()
