import logging
import markups

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters


# ----------------------------------------------------------------------------------------------------------------------
# Decorator
# ----------------------------------------------------------------------------------------------------------------------

def delete_user_messages(func):
    async def wrapper(update, context):
        await update.message.delete()
        await func(update, context)
        logging.info('Message from user deleted.')

    return wrapper


def delete_bot_messages(func):
    async def wrapper(update, context):
        messages = context.bot_data.get("bot_messages", [])
        await func(update, context)
        if len(messages) >= 2:
            for message_id in messages[:-1]:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
            context.bot_data["bot_messages"] = [messages[-1]]
        logging.info('Message from bot deleted.')

    return wrapper


# ----------------------------------------------------------------------------------------------------------------------
# Function
# ----------------------------------------------------------------------------------------------------------------------

@delete_user_messages
async def start(update: Update, context: CallbackContext) -> None:
    logging.info('Command "/start" was triggered.')
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
        reply_markup=markups.main_menu
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

        message = await update.message.reply_text(self.text, reply_markup=self.reply_markup)

        chat_states = context.bot_data.get("chat_states", [])
        chat_states.append(update.message.text)
        context.bot_data["chat_states"] = chat_states

        bot_messages = context.bot_data.get("bot_messages", [])
        bot_messages.append(message.message_id)
        context.bot_data["bot_messages"] = bot_messages

    @staticmethod
    async def back_to_previous(update: Update, context: CallbackContext) -> None:
        chat_states = context.bot_data.get("chat_states", [])

        if chat_states[-1] == "Меню":
            await main_menu(update, context)
            context.bot_data["chat_states"] = [chat_states[-1]]
            chat_states.pop()
        elif chat_states[-1] == "Переглянути доходи":
            context.bot_data["chat_states"] = [chat_states[-1]]
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Переглянути витрати":
            context.bot_data["chat_states"] = [chat_states[-1]]
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Статистика":
            context.bot_data["chat_states"] = [chat_states[-1]]
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Переглянути категорії":
            context.bot_data["chat_states"] = [chat_states[-1]]
            chat_states.pop()
            await menu(update, context)
        elif chat_states[-1] == "Додати категорію":
            context.bot_data["chat_states"] = [chat_states[-1]]
            chat_states.pop()
            await menu_show_category(update, context)
        elif chat_states[-1] == "Видалити категорію":
            context.bot_data["chat_states"] = [chat_states[-1]]
            chat_states.pop()
            await menu_show_category(update, context)


main_menu = Menu("Оберіть опцію", markups.main_menu)
menu = Menu("Оберіть опцію", markups.menu)
menu_show_income = Menu("На екран виводиться список категорій.", markups.menu_show_income)
menu_show_spending = Menu("На екран виводиться список категорій.", markups.menu_show_spending)
menu_show_statistic = Menu("Тут буде показано статистику.", markups.menu_show_statistic)
menu_show_category = Menu("На екран виводиться список категорій.", markups.menu_show_category)
menu_add_category = Menu("Введіть назву нової категорії", markups.menu_btn_back)
menu_remove_category = Menu("Введіть назву категорії яку треба видалити", markups.menu_btn_back)


# ----------------------------------------------------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------------------------------------------------

# noinspection SpellCheckingInspection
TOKEN_BOT = "5813491047:AAHnwTeChugvOLpQsa_jPMotXM69QATCYVk"

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    # filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def run():
    app = ApplicationBuilder().token(TOKEN_BOT).build()

    app.add_handler(CommandHandler("start", start))
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
