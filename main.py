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
        logging.info('Message from user deleted.')
        return await func(update, context)

    return wrapper


def delete_bot_messages(func):
    async def wrapper(update, context):
        messages = context.bot_data.get("bot_messages", [])
        await func(update, context)
        if len(messages) >= 2:
            # Видаляємо всі повідомлення, крім останнього
            for message_id in messages[:-1]:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
            context.bot_data["bot_messages"] = [messages[-1]]  # Залишаємо тільки останнє повідомлення

        logging.info('Message from bot deleted.')

    return wrapper


def save_current_state(func):
    async def wrapper(update, context):
        chat_id = update.effective_chat.id
        set_current_state(chat_id, func.__name__, context)
        context.user_data["current_state"] = func.__name__
        await func(update, context)

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


@delete_user_messages
@delete_bot_messages
@save_current_state
async def main_menu(update: Update, context: CallbackContext) -> None:
    logging.info('"main_menu" was opened.')

    message = await update.message.reply_text("Оберіть опцію", reply_markup=markups.main_menu)
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


@delete_user_messages
@delete_bot_messages
@save_current_state
async def menu(update: Update, context: CallbackContext) -> None:
    logging.info('"menu" was opened.')

    message = await update.message.reply_text(
        "Оберіть опцію",
        reply_markup=markups.menu
    )
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


@delete_user_messages
@delete_bot_messages
@save_current_state
async def menu_show_income(update: Update, context: CallbackContext) -> None:
    logging.info('"menu_show_income" was opened.')

    message = await update.message.reply_text(
        "На екран виводиться список категорій.",
        reply_markup=markups.menu_show_income
    )
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


@delete_user_messages
@delete_bot_messages
@save_current_state
async def menu_show_spending(update: Update, context: CallbackContext) -> None:
    logging.info('"menu_show_spending" was opened.')

    message = await update.message.reply_text(
        "На екран виводиться список категорій.\n"
        "Кожна категорія натискається, відкривається підкатегорія якщо є.\n"
        "Виводиться список і сума усіх витрат за останній місяць для категорії",
        reply_markup=markups.menu_show_spending
    )
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


@delete_user_messages
@delete_bot_messages
@save_current_state
async def menu_show_statistic(update: Update, context: CallbackContext) -> None:
    logging.info('"menu_show_spending" was opened.')

    message = await update.message.reply_text(
        "Тут буде показано статистику",
        reply_markup=markups.menu_show_statistic
    )
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


@delete_user_messages
@delete_bot_messages
@save_current_state
async def menu_show_category(update: Update, context: CallbackContext) -> None:
    logging.info('"menu_show_category" was opened.')

    message = await update.message.reply_text(
        "Тут буде показано список категорій",
        reply_markup=markups.menu_show_category
    )
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


@delete_user_messages
@delete_bot_messages
@save_current_state
async def menu_add_category(update: Update, context: CallbackContext) -> None:
    logging.info('"menu_add_category" was opened.')

    message = await update.message.reply_text(
        "Введіть назву нової категорії",
        reply_markup=markups.menu_btn_back
    )

    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


@delete_user_messages
@delete_bot_messages
@save_current_state
async def menu_remove_category(update: Update, context: CallbackContext) -> None:
    logging.info('"menu_remove_category" was opened.')

    message = await update.message.reply_text(
        "Введіть назву категорії яку треба видалити",
        reply_markup=markups.menu_btn_back
    )
    bot_messages = context.bot_data.get("bot_messages", [])
    bot_messages.append(message.message_id)
    context.bot_data["bot_messages"] = bot_messages


def get_current_state(chat_id, context):
    chat_states = context.bot_data.get("chat_states", {})
    current_state = chat_states.get(chat_id)
    return current_state


def set_current_state(chat_id, state, context):
    chat_states = context.bot_data.get("chat_states", {})
    chat_states[chat_id] = state
    context.bot_data["chat_states"] = chat_states


async def back(update: Update, context: CallbackContext):
    logging.info('"back" was triggered.')
    chat_id = update.effective_chat.id
    current_state = get_current_state(chat_id, context)

    if current_state == "menu":
        await main_menu(update, context)
    elif current_state == "menu_show_income":
        await menu(update, context)
    elif current_state == "menu_show_spending":
        await menu(update, context)
    elif current_state == "menu_show_statistic":
        await menu(update, context)
    elif current_state == "menu_show_category":
        await menu(update, context)
    elif current_state == "menu_add_category":
        await menu_show_category(update, context)
    elif current_state == "menu_remove_category":
        await menu_show_category(update, context)


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

    app.add_handler(MessageHandler(filters.Regex(r"^Назад$"), back))

    app.run_polling()


if __name__ == "__main__":
    run()
