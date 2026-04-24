import asyncio, sys, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.environ.get('TOKEN', '8743381866:AAFkIbLJeOpKj69NQZUQ7tbKgCK_aTRy5NU')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '5214499041'))

user_queue = {}  # Хранит ID пользователей, ожидающих ответа: {message_id: user_id}
banned_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in banned_users: return
    await update.message.reply_text("💬 **Поддержка Whoosh**\n\n📝 Напишите ваш вопрос — мы ответим в ближайшее время!", parse_mode='Markdown')

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in banned_users: return
    
    keyboard = [[InlineKeyboardButton("✉️ Ответить", callback_data=f"reply_{user.id}")]]
    msg = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📨 **Новое сообщение**\n👤 От: @{user.username or user.first_name}\n🆔 ID: `{user.id}`\n\n💬 {update.message.text}",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    user_queue[msg.message_id] = user.id
    await update.message.reply_text("✅ Отправлено. Ответим в ближайшее время!")

async def reply_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID: await query.answer("❌ Вы не админ!"); return
    
    user_id = int(query.data.replace("reply_", ""))
    context.user_data['reply_to'] = user_id
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(f"📝 Введите ответ для пользователя `{user_id}`:", parse_mode='Markdown')

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_queue
    admin_id = update.effective_user.id
    if admin_id != ADMIN_ID: return
    
    text = update.message.text
    
    # Команды
    if text.startswith('/ban'):
        try: target_id = int(text.split()[1]); banned_users.add(target_id); await update.message.reply_text(f"🚫 Заблокирован `{target_id}`", parse_mode='Markdown')
        except: await update.message.reply_text("❌ Используй: `/ban ID`")
        return
    if text.startswith('/unban'):
        try: target_id = int(text.split()[1]); banned_users.discard(target_id); await update.message.reply_text(f"✅ Разблокирован `{target_id}`", parse_mode='Markdown')
        except: await update.message.reply_text("❌ Используй: `/unban ID`")
        return
    if text.startswith('/banlist'):
        if banned_users: await update.message.reply_text("📋 **Бан-лист:**\n" + "\n".join([f"• `{uid}`" for uid in banned_users]), parse_mode='Markdown')
        else: await update.message.reply_text("📋 Список пуст.")
        return
    
    # Ответ пользователю
    target_id = context.user_data.get('reply_to')
    if not target_id:
        # Пробуем найти последнего активного пользователя
        if user_queue:
            target_id = list(user_queue.values())[-1]
        else:
            await update.message.reply_text("❌ Некому отвечать. Нажми **✉️ Ответить** под сообщением.")
            return
    
    try:
        await context.bot.send_message(chat_id=target_id, text=f"💬 **Ответ от поддержки:**\n\n{update.message.text}", parse_mode='Markdown')
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
    app.add_handler(CommandHandler("ban", lambda u,c: handle_admin_message(u,c)))
    app.add_handler(CommandHandler("unban", lambda u,c: handle_admin_message(u,c)))
    app.add_handler(CommandHandler("banlist", lambda u,c: handle_admin_message(u,c)))
    app.add_handler(CallbackQueryHandler(reply_callback, pattern='^reply_'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_ID), handle_admin_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    print("✅ Бот поддержки запущен!")
    app.run_polling()

if __name__ == "__main__": main()