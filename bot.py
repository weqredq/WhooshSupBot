import asyncio, sys, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.environ.get('TOKEN', '8743381866:AAFkIbLJeOpKj69NQZUQ7tbKgCK_aTRy5NU')
ADMIN_IDS = [5214499041, 1325271591]

last_user_id = None
banned_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in banned_users: return
    await update.message.reply_text("💬 **Поддержка Whoosh**\n\n📝 Напишите ваш вопрос — мы ответим в ближайшее время!", parse_mode='Markdown')

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_user_id
    user = update.effective_user
    if user.id in banned_users: return

    for admin_id in ADMIN_IDS:
        keyboard = [[InlineKeyboardButton("✉️ Ответить", callback_data=f"reply_{user.id}")]]
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"📨 **Новое сообщение**\n👤 От: @{user.username or user.first_name}\n🆔 ID: `{user.id}`\n\n💬 {update.message.text}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    last_user_id = user.id
    await update.message.reply_text("✅ Отправлено. Ответим в ближайшее время!")

async def reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id not in ADMIN_IDS: await query.answer("❌ Вы не админ!"); return

    user_id = int(query.data.replace("reply_", ""))
    context.user_data['reply_to'] = user_id
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"📝 Введите ответ для пользователя `{user_id}`:", parse_mode='Markdown')

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        await update.message.reply_text(f"🚫 Пользователь `{target_id}` заблокирован.", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Используй: `/ban ID`")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    try:
        target_id = int(context.args[0])
        banned_users.discard(target_id)
        await update.message.reply_text(f"✅ Пользователь `{target_id}` разблокирован.", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Используй: `/unban ID`")

async def banlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if banned_users:
        ban_list = "\n".join([f"• `{uid}`" for uid in banned_users])
        await update.message.reply_text(f"📋 **Заблокированные:**\n{ban_list}", parse_mode='Markdown')
    else:
        await update.message.reply_text("📋 Список пуст.")

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_user_id
    admin_id = update.effective_user.id
    if admin_id not in ADMIN_IDS: return

    target_id = context.user_data.get('reply_to')
    if not target_id:
        if last_user_id:
            target_id = last_user_id
        else:
            await update.message.reply_text("❌ Некому отвечать. Дождитесь сообщения или нажмите **✉️ Ответить**.")
            return

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"💬 **Ответ от поддержки:**\n\n{update.message.text}",
            parse_mode='Markdown'
        )
        await update.message.reply_text("✅ Ответ отправлен!")
        context.user_data['reply_to'] = None
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try: asyncio.get_running_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("banlist", banlist_command))
    app.add_handler(CallbackQueryHandler(reply_callback, pattern='^reply_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_IDS), handle_admin_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    print("✅ Бот поддержки запущен!")
    app.run_polling()

if __name__ == "__main__": main()