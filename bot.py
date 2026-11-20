import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
    ContextTypes,
)
​
TOKEN = "9183277996:AAFPXnn---n49zulXfTVW5tojP9tGl2G7NU"
CHANNEL_ID = -1003926830337
ADMIN_ID = 8608766730
PIX = "0b97805f-52e5-4512-8f40-fb7dc0cbb506"
​
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
​
pending = {}  # user_id -> user_chat_id
​
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_request = update.chat_join_request
    user = join_request.from_user
    user_id = user.id
    user_chat_id = join_request.user_chat_id
    pending[user_id] = user_chat_id
​
    keyboard = [
        [InlineKeyboardButton("📋 Copiar PIX", callback_data=f"copy_{user_id}")],
        [InlineKeyboardButton("✅ Já paguei", callback_data=f"paid_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
​
    texto = (
        "oii pra entrar nas minhas prévias, basta vc pagar apenas 1,50, aproveita hihi 💗\n\n"
        f"PIX: `{PIX}`\n\n"
        "Depois de pagar, clica em Já paguei."
    )
​
    try:
        await context.bot.send_message(
            chat_id=user_chat_id,
            text=texto,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Erro ao mandar mensagem: {e}")
​
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
​
    if data.startswith("copy_"):
        await query.message.reply_text(f"PIX pra copiar:\n`{PIX}`", parse_mode="Markdown")
        return
​
    if data.startswith("paid_"):
        user_id = int(data.split("_")[1])
        if user_id not in pending:
            await query.edit_message_text("Pedido não encontrado.")
            return
​
        admin_keyboard = [
            [InlineKeyboardButton("✅ Aceitar", callback_data=f"accept_{user_id}")],
            [InlineKeyboardButton("❌ Recusar", callback_data=f"decline_{user_id}")]
        ]
        admin_markup = InlineKeyboardMarkup(admin_keyboard)
​
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"💰 {query.from_user.full_name} diz que pagou!\nID: {user_id}\n\nAprovar entrada?",
                reply_markup=admin_markup
            )
            await query.edit_message_text("Avisado! Assim que eu confirmar, libero sua entrada.")
        except Exception as e:
            logger.error(f"Erro ao avisar admin: {e}")
            await query.edit_message_text("Erro ao avisar. Tenta de novo.")
        return
​
    if data.startswith("accept_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Só o admin pode fazer isso.", show_alert=True)
            return
        user_id = int(data.split("_")[1])
        try:
            await context.bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
            await query.edit_message_text(f"✅ Usuário {user_id} aprovado!")
            if user_id in pending:
                try:
                    await context.bot.send_message(
                        chat_id=pending[user_id],
                        text="✅ Pagamento confirmado! Você já foi liberado no canal de prévias."
                    )
                except:
                    pass
                del pending[user_id]
        except Exception as e:
            await query.edit_message_text(f"Erro ao aprovar: {e}")
        return
​
    if data.startswith("decline_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Só o admin pode fazer isso.", show_alert=True)
            return
        user_id = int(data.split("_")[1])
        try:
            await context.bot.decline_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
            await query.edit_message_text(f"❌ Usuário {user_id} recusado.")
            if user_id in pending:
                try:
                    await context.bot.send_message(
                        chat_id=pending[user_id],
                        text="Pedido recusado. Se pagou, manda mensagem de novo."
                    )
                except:
                    pass
                del pending[user_id]
        except Exception as e:
            await query.edit_message_text(f"Erro ao recusar: {e}")
​
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot rodando...")
    app.run_polling()
​
if __name__ == "__main__":
    main()
