import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

TOKEN = "7711930364:AAEoVeW_M5JhhHCOx_234MU1zO4kgDMltSs"
OWNER_ID = 547994168
PRICE = 4

menu = [
    {
        "name": "Нежные сырнички",
        "description": "Сладкие, как твоя улыбка. Подаются с клубничкой и любовью.",
        "image": "https://i.imgur.com/ZdY2EGe.jpg"
    },
    {
        "name": "Тёплый борщ с заботой",
        "description": "Каждая ложка — как тёплое объятие.",
        "image": "https://i.imgur.com/Z2q5ZpM.jpg"
    },
    {
        "name": "Объятия в пюре",
        "description": "Картофельное пюре с котлеткой, мягкое, как наше утро вместе.",
        "image": "https://i.imgur.com/BY2sQLT.jpg"
    },
    {
        "name": "Любовные макарошки",
        "description": "Макароны с сыром и ноткой обожания. Настоящая еда для души.",
        "image": "https://i.imgur.com/pt6KQqw.jpg"
    },
    {
        "name": "Сладкий сюрприз",
        "description": "Десерт, как поцелуй — внезапный, сладкий и твой.",
        "image": "https://i.imgur.com/tKtUKhU.jpg"
    }
]

user_baskets = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{item['name']} — {PRICE} 💋", callback_data=f"add_{i}")]
        for i, item in enumerate(menu)
    ]
    await update.message.reply_text(
        "Добро пожаловать в «Домашний ресторан для любимой»! 💕\n\n"
        "Выбирай блюда, добавляй на поднос и отправляй заказ!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith("add_"):
        item_index = int(data.split("_")[1])
        user_baskets.setdefault(user_id, []).append(item_index)
        await query.reply_text(f"✔ Добавлено: {menu[item_index]['name']} ({PRICE} 💋)")

    elif data.startswith("remove_"):
        item_index = int(data.split("_")[1])
        if user_id in user_baskets and item_index in user_baskets[user_id]:
            user_baskets[user_id].remove(item_index)
            await query.reply_text(f"❌ Удалено: {menu[item_index]['name']}")
        else:
            await query.reply_text("Это блюдо не найдено в подносе.")

    elif data == "send_order":
        basket = user_baskets.get(user_id, [])
        if not basket:
            await query.reply_text("Твой поднос пуст 🥺")
            return

        summary = "🍽️ Твой заказ:\n"
        total = 0
        for i in basket:
            summary += f"- {menu[i]['name']} ({PRICE} 💋)\n"
            total += PRICE

        summary += f"\n♥️ Всего: {total} поцелуев"

        await context.bot.send_message(chat_id=OWNER_ID, text=f"📨 Новый заказ от @{query.from_user.username or query.from_user.first_name}:\n\n" + summary)
        await query.edit_message_text("❤️ Заказ отправлен! Жди с любовью!")
        user_baskets[user_id] = []

async def basket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    basket = user_baskets.get(user_id, [])
    if not basket:
        await update.message.reply_text("Твой поднос пуст 🥺")
        return

    text = "🚪 На подносе:\n"
    buttons = []
    for i in basket:
        item = menu[i]
        text += f"- {item['name']} ({PRICE} 💋)\n"
        buttons.append([InlineKeyboardButton(f"❌ {item['name']}", callback_data=f"remove_{i}")])

    buttons.append([InlineKeyboardButton("✉️ Отправить заказ", callback_data="send_order")])

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("basket", basket))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
