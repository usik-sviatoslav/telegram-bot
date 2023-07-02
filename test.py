import logging
import markups as nav
import bot_data as data
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters


# ----------------------------------------------------------------------------------------------------------------------
# Function
# ----------------------------------------------------------------------------------------------------------------------

async def start(update: Update, context: CallbackContext) -> None:
    logging.info('Command "/start" was triggered.')
    try:
        await update.message.delete()
        logging.info("❌ Message from user deleted ❌")
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")

    message_1 = await update.message.reply_text("Привіт! Давай розкажу що я взагалі вмію.\n")
    message_2 = await update.message.reply_text(
        "Операції:\n"
        "• Додавати витрати та доходи\n"
        "• Видаляти створені операції\n\n"
        "Категорії:\n"
        "• Дивитись список доступних категорій\n"
        "• Створювати та видаляти категорії\n\n"
        "Статистика:\n"
        "• Переглядати усі витрати за період\n"
        "• Переглядати усі доходи за період\n"
        "• Переглядати загальну статистику\n",
        reply_markup=nav.home
    )
    bot_message_command = context.bot_data.get("bot_message_command", [])
    bot_message_command.append(message_1.message_id)
    bot_message_command.append(message_2.message_id)
    context.bot_data["bot_message_command"] = bot_message_command


async def home(update: Update, context: CallbackContext) -> None:
    logging.info('Command "/home" was triggered.')
    try:
        await update.message.delete()
        logging.info("❌ Message from user deleted ❌")
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")

    bot_message = context.bot_data.get("bot_message", [])
    bot_message_command = context.bot_data.get("bot_message_command", [])

    m_id = await update.message.reply_text("Оберіть опцію", reply_markup=nav.home)
    bot_message_command.append(m_id.message_id)

    try:
        for message_id in reversed(bot_message):
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
            bot_message.pop()

        for message_id in bot_message_command[:-1]:
            if message_id == 0:
                bot_message_command.pop(0)
            else:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                bot_message_command.pop(0)
                context.bot_data["bot_message_command"] = [bot_message_command[-1]]
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")

    logging.info("Clear ✔️")


async def message_from_user(update: Update, context: CallbackContext, *args) -> None:
    bot_message_command = context.bot_data.get("bot_message_command", [])
    bot_message = context.bot_data.get("bot_message", [])

    # Видаляємо повідомлення від користувача
    try:
        await update.message.delete()
        logging.info("❌ Message from user deleted ❌")
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")

    # Перевірка чи є введений текст викликає KeyboardButton
    message = update.message.text
    if message == "Меню" \
            or message == "Переглянути доходи" \
            or message == "Переглянути витрати" \
            or message == "Статистика" \
            or message == "Переглянути категорії" \
            or message == "Додати категорію" \
            or message == "Видалити категорію" \
            or message == "Назад":
        logging.info(f'Button "{message}" was triggered')

        # Виклик KeyboardButton
        reply_text = update.message.reply_text
        if message == "Меню":
            m_id = await reply_text("Оберіть опцію", reply_markup=nav.menu)
            bot_message_command.append(m_id.message_id)

        elif message == "Переглянути доходи":
            m_id = await reply_text(data.joined_text, reply_markup=nav.menu_show_income)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Переглянути витрати":
            m_id = await reply_text("data.all_categories", reply_markup=nav.menu_show_spending)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Статистика":
            m_id = await reply_text("Тут буде показано статистику.", reply_markup=nav.menu_show_statistic)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Переглянути категорії":
            m_id = await reply_text("На екран виводиться список категорій.", reply_markup=nav.menu_show_category)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Додати категорію":
            m_id = await reply_text("Введіть назву нової категорії", reply_markup=nav.menu_btn_back)
            bot_message_command.append(m_id.message_id)

        elif message == "Видалити категорію":
            m_id = await reply_text("Введіть назву категорії яку треба видалити", reply_markup=nav.menu_btn_back)
            bot_message_command.append(m_id.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)

        if not message == "Назад":
            chat_states = context.bot_data.get("chat_states", [])
            chat_states.append(update.message.text)
            context.bot_data["chat_states"] = chat_states
    else:
        chat_states = context.bot_data.get("chat_states", [])
        try:
            if chat_states[-1] == "Додати категорію":
                user_id = update.message.from_user.id
                text = update.message.text
                await context.bot.send_message(chat_id=user_id, text=f"Отримано вашу відповідь: {text}")
        except Exception as exception:
            logging.warning(f"⚠️ {exception} ⚠️")

    context.bot_data["bot_message_command"] = bot_message_command
    context.bot_data["bot_message"] = bot_message

    # Видаляємо повідомлення від бота
    try:
        for message_id in bot_message_command[:-1]:
            if message_id == 0:
                bot_message_command.pop(0)
            else:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                bot_message_command.pop(0)
                logging.info("❌ Message from bot  deleted ❌")
                context.bot_data["bot_message_command"] = [bot_message_command[-1]]
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")


async def back_to_previous(update: Update, context: CallbackContext) -> None:
    chat_states = context.bot_data.get("chat_states", [])
    reply_text = update.message.reply_text
    bot_message_command = context.bot_data.get("bot_message_command", [])

    try:
        state = chat_states[-1]
        if state == "Меню":
            chat_states.pop()
            await home(update, context)
        elif state == "Переглянути доходи" \
                or state == "Переглянути витрати" \
                or state == "Статистика" \
                or state == "Переглянути категорії":
            chat_states.pop()
            m_id = await reply_text("Оберіть опцію", reply_markup=nav.menu)
            bot_message_command.append(m_id.message_id)
        elif state == "Додати категорію" \
                or state == "Видалити категорію":
            chat_states.pop()
            m_id = await reply_text("На екран виводиться список категорій.", reply_markup=nav.menu_show_category)
            bot_message_command.append(m_id.message_id)
    except IndexError:
        logging.warning(f"⚠️ List index out of range ⚠️")
        await home(update, context)

    context.bot_data["bot_message_command"] = bot_message_command


async def clear(update: Update, context: CallbackContext) -> None:
    pass


# ----------------------------------------------------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------------------------------------------------

# noinspection SpellCheckingInspection
TOKEN_BOT = "6117967316:AAH3d5p-J-_D1mLHDCO6KEYr1pjYL7RcL8A"

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    # filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def run():
    app = ApplicationBuilder().token(TOKEN_BOT).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("home", home))
    app.add_handler(MessageHandler(filters.Regex(r"\w+"), message_from_user))

    app.run_polling()


if __name__ == "__main__":
    run()
