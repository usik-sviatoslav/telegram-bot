import logging
import time

import markups as nav
import bot_data as data
import my_token as token
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters


# ----------------------------------------------------------------------------------------------------------------------
# Function
# ----------------------------------------------------------------------------------------------------------------------

async def start(update: Update, context: CallbackContext) -> None:
    logging.info('Command "/start" was triggered.')

    await delete_message_from_user(update)

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

    await delete_message_from_user(update)

    bot_message = context.bot_data.get("bot_message", [])
    bot_message_command = context.bot_data.get("bot_message_command", [])
    chat_states = context.bot_data.get("chat_states", [])

    m_id = await update.message.reply_text("Оберіть параметр", reply_markup=nav.home)
    bot_message_command.append(m_id.message_id)

    # Видаляємо усі повідомлення від бота та очищаємо chat_states 51-68
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

        for _ in reversed(chat_states):
            chat_states.pop()

    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")

    logging.info("Clear ✔️")


async def delete_message_from_user(update: Update) -> None:
    try:
        await update.message.delete()
        logging.info("❌ Message from user deleted ❌")
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")


async def delete_message_from_bot(update: Update, context: CallbackContext) -> None:
    bot_message_command = context.bot_data.get("bot_message_command", [])
    bot_message = context.bot_data.get("bot_message", [])

    try:
        for message_id in bot_message_command[:-1]:
            if message_id == 0:
                bot_message_command.pop(0)
            else:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                context.bot_data["bot_message_command"] = [bot_message_command[-1]]
                bot_message_command.pop(0)
                logging.info("❌ Message from bot  deleted ❌")

        for bot_message_id in bot_message[:-1]:
            if bot_message_id == 0:
                bot_message.pop(0)
            else:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bot_message_id)
                context.bot_data["bot_message"] = [bot_message[-1]]
                bot_message.pop(0)
                logging.info("❌ Message from bot  deleted ❌")

    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")


async def back_to_previous(update: Update, context: CallbackContext) -> None:
    logging.info(f'Button "Назад" was triggered')

    chat_states = context.bot_data.get("chat_states", [])
    reply_text = update.message.reply_text
    bot_message_command = context.bot_data.get("bot_message_command", [])

    try:
        state = chat_states[-1]
        if state == "Меню" \
                or state == "Додати новий запис" \
                or state == "Обрано категорію":
            for _ in reversed(chat_states):
                chat_states.pop()
            await home(update, context)

        elif state == "Переглянути доходи" \
                or state == "Переглянути витрати" \
                or state == "Статистика" \
                or state == "Переглянути категорії":
            chat_states.pop()
            m_id = await reply_text("Оберіть параметр", reply_markup=nav.menu)
            bot_message_command.append(m_id.message_id)

        elif state == "Додати категорію" \
                or state == "Видалити категорію":
            chat_states.pop()
            m_id = await reply_text("Оберіть параметр", reply_markup=nav.menu_show_category)
            bot_message_command.append(m_id.message_id)

    except IndexError:
        logging.warning(f"⚠️ List index out of range ⚠️")
        await home(update, context)

    context.bot_data["bot_message_command"] = bot_message_command


async def message_handler(update: Update, context: CallbackContext) -> None:
    bot_message_command = context.bot_data.get("bot_message_command", [])
    bot_message = context.bot_data.get("bot_message", [])
    chat_states = context.bot_data.get("chat_states", [])
    reply_text = update.message.reply_text
    chat_id = update.effective_chat.id
    message = update.message.text

    await delete_message_from_user(update)

    # Перевірка введеного тексту 158-347
    if len(chat_states) == 0:
        if message == "Додати новий запис":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("Оберіть категорію", reply_markup=nav.btn_back)
            bot_message_command.append(m_id.message_id)

        elif message == "Меню":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("Оберіть параметр", reply_markup=nav.menu)
            bot_message_command.append(m_id.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)

    elif chat_states[-1] == "Додати новий запис":
        if message in data.t:
            logging.info(f'Category "{message}" was selected')
            chat_states.append("Обрано категорію")

            m_id = await reply_text(f"Обрано категорію: {message}", reply_markup=nav.menu_income_spending)
            bot_message_command.append(m_id.message_id)

        elif message == "Додати категорію":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("Введіть назву нової категорії", reply_markup=nav.menu_btn_back)
            bot_message_command.append(m_id.message_id)

        elif message == "Перейти на головну сторінку":
            await home(update, context)

        else:
            logging.info(f'No category "{message}"')

            m_id = await reply_text(f'Категорії "{message}" немає', reply_markup=nav.menu_new_category)
            bot_message_command.append(m_id.message_id)

    elif chat_states[-1] == "Обрано категорію":
        if message == "+":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await context.bot.send_message(chat_id, "Введіть суму доходу")
            bot_message_command.append(m_id.message_id)
        elif message == "-":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await context.bot.send_message(chat_id, "Введіть суму витрат")
            bot_message_command.append(m_id.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)

    elif chat_states[-1] == "+" or chat_states[-1] == "-":
        if message.isdigit():
            if chat_states[-1] == "+":
                m_id = await context.bot.send_message(chat_id, f"До категорії додано {message} грн.")
                bot_message_command.append(m_id.message_id)
            elif chat_states[-1] == "-":
                m_id = await context.bot.send_message(chat_id, f"До категорії додано -{message} грн.")
                bot_message_command.append(m_id.message_id)

            chat_states.append("До категорії додано")
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=bot_message_command[0])
            context.bot_data["bot_message_command"] = [bot_message_command[-1]]
            bot_message_command.pop(0)
            time.sleep(2)

        else:
            m_id = await context.bot.send_message(chat_id, f"Введіть число")
            bot_message_command.append(m_id.message_id)

    elif chat_states[-1] == "Меню":
        if message == "Переглянути доходи":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text(data.joined_text, reply_markup=nav.menu_show_income)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Переглянути витрати":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("data.all_categories", reply_markup=nav.menu_show_spending)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Статистика":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("Тут буде показано статистику.", reply_markup=nav.menu_show_statistic)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Переглянути категорії":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("На екран виводиться список категорій.", reply_markup=nav.menu_show_category)
            bot_message.append(m_id.message_id)
            bot_message_command.append(0)

        elif message == "Назад":
            await back_to_previous(update, context)

    elif chat_states[-1] == "Переглянути доходи" or chat_states[-1] == "Переглянути витрати":
        # Спільні характеристики
        if message == "Попередній місяць":
            logging.info(f'Button "{message}" was triggered')
            # chat_states.append(message)

        elif message == "→":
            logging.info(f'Button "{message}" was triggered')
            # chat_states.append(message)

        elif message == "Назад":
            await back_to_previous(update, context)

        # Різні характеристики
        if chat_states[-1] == "Переглянути доходи":
            if message == "Видалити":
                logging.info(f'Button "{message}" was triggered')
                # chat_states.append(message)

            elif message == "Додати":
                logging.info(f'Button "{message}" was triggered')
                # chat_states.append(message)

        elif chat_states[-1] == "Переглянути витрати":
            if message == "Видалити":
                logging.info(f'Button "{message}" was triggered')
                # chat_states.append(message)

            elif message == "Додати":
                logging.info(f'Button "{message}" was triggered')
                # chat_states.append(message)

    elif chat_states[-1] == "Статистика":
        if message == "Тиждень":
            logging.info(f'Button "{message}" was triggered')
            # chat_states.append(message)

        elif message == "Місяць":
            logging.info(f'Button "{message}" was triggered')
            # chat_states.append(message)

        elif message == "Рік":
            logging.info(f'Button "{message}" was triggered')
            # chat_states.append(message)

        elif message == "Назад":
            await back_to_previous(update, context)

    elif chat_states[-1] == "Переглянути категорії":
        if message == "Додати категорію":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("Введіть назву нової категорії", reply_markup=nav.menu_btn_back)
            bot_message_command.append(m_id.message_id)

        elif message == "Видалити категорію":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m_id = await reply_text("Введіть назву категорії яку треба видалити", reply_markup=nav.menu_btn_back)
            bot_message_command.append(m_id.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)

    elif chat_states[-1] == "Додати категорію" or chat_states[-1] == "Видалити категорію":
        if not message == "Назад":
            if chat_states[-1] == "Додати категорію":
                m_id = await reply_text(
                    f"Додано нову категорію: {message}\n\n{'Тут буде оновлений список категорій'}",
                    reply_markup=nav.menu_btn_back
                )
                bot_message.append(m_id.message_id)
            elif chat_states[-1] == "Видалити категорію":
                m_id = await reply_text(
                    f"Видалено категорію: {message}\n\n{'Тут буде оновлений список категорій'}",
                    reply_markup=nav.menu_btn_back
                )
                bot_message.append(m_id.message_id)
            bot_message_command.append(0)
        else:
            if len(chat_states) == 2:
                await home(update, context)
            else:
                await back_to_previous(update, context)

    context.bot_data["chat_states"] = chat_states
    context.bot_data["bot_message_command"] = bot_message_command
    context.bot_data["bot_message"] = bot_message

    try:
        if chat_states[-1] == "До категорії додано":
            await home(update, context)
        else:
            await delete_message_from_bot(update, context)
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")


# ----------------------------------------------------------------------------------------------------------------------
# App
# ----------------------------------------------------------------------------------------------------------------------


logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    # filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def run():
    app = ApplicationBuilder().token(token.TOKEN_BOT).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("home", home))
    app.add_handler(MessageHandler(filters.Regex(r"[\w+]?[→]?"), message_handler))

    app.run_polling()


if __name__ == "__main__":
    run()
