import asyncio, sys, os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TOKEN', '8743381866:AAFkIbLJeOpKj69NQZUQ7tbKgCK_aTRy5NU')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '5214499041'))

last_user_id = None
banned_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        return
    await update.message.reply_text(
        "💬 **Поддержка Whoosh**\n\n"
        "📝 Напишите ваш вопрос — мы ответим в ближайшее время!\n"
        "🕐 Обычно отвечаем в течение 15 минут.",
        parse_mode='Markdown'
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_user_id
    user = update.effective_user

    if user.id in banned_users:
        return

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📨 **Новое сообщение**\n"
             f"👤 От: @{user.username or user.first_name}\n"
             f"🆔 ID: `{user.id}`\n\n"
             f"💬 {update.message.text}",
        parse_mode='Markdown'
    )
    last_user_id = user.id
    await update.message.reply_text("✅ **Спасибо!** Ваше сообщение отправлено.\nМы ответим в ближайшее время 💨")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        await update.message.reply_text(f"🚫 Пользователь `{target_id}` заблокирован.", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Используй: `/ban ID`")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    try:
        target_id = int(context.args[0])
        banned_users.discard(target_id)
        await update.message.reply_text(f"✅ Пользователь `{target_id}` разблокирован.", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Используй: `/unban ID`")

async def banlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if banned_users:
        ban_list = "\n".join([f"• `{uid}`" for uid in banned_users])
        await update.message.reply_text(f"📋 **Заблокированные:**\n{ban_list}", parse_mode='Markdown')
    else:
        await update.message.reply_text("📋 Список пуст.")

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_user_id

    if update.effective_user.id != ADMIN_ID:
        return

    if not last_user_id:
        await update.message.reply_text("❌ Нет активного пользователя для ответа.\nДождитесь сообщения.")
        return

    try:
        await context.bot.send_message(
            chat_id=last_user_id,
            text=f"💬 **Ответ от поддержки:**\n\n{update.message.text}",
            parse_mode='Markdown'
        )
        await update.message.reply_text("✅ **Ответ отправлен!**")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    app.add_handler(CommandHandler("banlist", banlist_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_ID), handle_admin_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))
    print("✅ Бот поддержки запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()