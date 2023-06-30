import logging
import markups
import bot_data as data
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters


# ----------------------------------------------------------------------------------------------------------------------
# Function
# ----------------------------------------------------------------------------------------------------------------------

async def start(update: Update, context: CallbackContext) -> None:
    logging.info('Command "/start" was triggered.')
    await update.message.delete()
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
        reply_markup=markups.home
    )
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message_1.message_id)
    bot_messages.append(message_2.message_id)
    context.bot_data["bot_messages"] = bot_messages


class Menu:
    def __init__(self, text, reply_markup):
        self.text = text
        self.reply_markup = reply_markup

    async def __call__(self, update: Update, context: CallbackContext) -> None:
        logging.info(f'Button "{update.message.text}" was triggered')
        await update.message.delete()
        logging.info("Message from user deleted.")
        message = await update.message.reply_text(self.text, reply_markup=self.reply_markup)

        bot_commands = [
            "Оберіть опцію", "Введіть назву нової категорії",
            "Введіть назву категорії яку треба видалити"
        ]

        # Отримуємо id повідомлення від бота, щоб потім видалити повідомлення
        bot_messages = context.bot_data.get("bot_messages", [])
        if message.text in bot_commands:
            bot_messages.append(message.message_id)
            context.bot_data["bot_messages"] = bot_messages
        else:
            bot_messages.append(0)

        try:
            if len(bot_messages) >= 2:
                for message_id in bot_messages[:-1]:
                    if message_id:
                        if message_id == 0:
                            bot_messages.pop(0)
                        else:
                            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                            bot_messages.pop(0)
                            logging.info("Message from bot deleted.")
                            context.bot_data["bot_messages"] = [bot_messages[-1]]

        except Exception as exception:
            raise exception

        if not update.message.text == "Назад":
            chat_states = context.bot_data.get("chat_states", [])
            chat_states.append(update.message.text)
            context.bot_data["chat_states"] = chat_states

    @staticmethod
    async def back_to_previous(update: Update, context: CallbackContext) -> None:
        chat_states = context.bot_data.get("chat_states", [])

        if chat_states[-1] == "Меню":
            chat_states.pop()
            await home(update, context)
        elif chat_states[-1] == "Переглянути доходи":
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Переглянути витрати":
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Статистика":
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Переглянути категорії":
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Додати категорію":
            chat_states.pop()
            await menu_show_category(update, context)
        elif chat_states[-1] == "Видалити категорію":
            chat_states.pop()
            await menu_show_category(update, context)


home = Menu("Оберіть опцію", markups.home)
menu = Menu("Оберіть опцію", markups.menu)
menu_show_income = Menu(data.joined_text, markups.menu_show_income)
menu_show_spending = Menu("На екран виводиться список категорій.", markups.menu_show_spending)
menu_show_statistic = Menu("Тут буде показано статистику.", markups.menu_show_statistic)
menu_show_category = Menu("На екран виводиться список категорій.", markups.menu_show_category)
menu_add_category = Menu("Введіть назву нової категорії", markups.menu_btn_back)
menu_remove_category = Menu("Введіть назву категорії яку треба видалити", markups.menu_btn_back)


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
    app.add_handler(MessageHandler(filters.Regex(r"^Меню$"), menu))
    app.add_handler(MessageHandler(filters.Regex(r"^Переглянути доходи$"), menu_show_income))
    app.add_handler(MessageHandler(filters.Regex(r"^Переглянути витрати$"), menu_show_spending))
    app.add_handler(MessageHandler(filters.Regex(r"^Статистика$"), menu_show_statistic))
    app.add_handler(MessageHandler(filters.Regex(r"^Переглянути категорії$"), menu_show_category))
    app.add_handler(MessageHandler(filters.Regex(r"^Додати категорію$"), menu_add_category))
    app.add_handler(MessageHandler(filters.Regex(r"^Видалити категорію$"), menu_remove_category))

    app.add_handler(MessageHandler(filters.Regex(r"^Назад$"), Menu.back_to_previous))

    app.run_polling()


if __name__ == "__main__":
    run()
