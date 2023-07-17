import time
import json
import logging
import datetime
import markups as nav
import my_token as token
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters


# ----------------------------------------------------------------------------------------------------------------------
# Function
# ----------------------------------------------------------------------------------------------------------------------

async def start(update: Update, context: CallbackContext) -> None:
    logging.info('Command "/start" was triggered.')

    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    reply_text = update.message.reply_text
    user_id = str(update.effective_chat.id)
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name

    await delete_message_from_user(update)

    message_1 = await reply_text("Привіт! Давай розкажу що я взагалі вмію.\n")
    message_2 = await reply_text(
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

    if user_id in data_base:
        data_base[user_id]["bot_message_info"] = [message_1.message_id, message_2.message_id]
    else:
        if len(data_base) == 0:
            data_base = {user_id: {}}
            with open("bot_data.json", "w") as file:
                json.dump(data_base, file, indent=4)

        data_base[user_id] = {
            "username": f"@{username}",
            "first_name": first_name,
            "last_name": last_name,
            "bot_message_info": [message_1.message_id, message_2.message_id],
            "bot_message": [],
            "chat_states": [],
            "selected_date": [],
            "selected_category": [],
            "categories": {}
        }

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)


async def home(update: Update, context: CallbackContext) -> None:
    logging.info('Command "/home" was triggered.')

    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)

    bot_message_info = data_base[user_id]["bot_message_info"]
    bot_message = data_base[user_id]["bot_message"]
    chat_states = data_base[user_id]["chat_states"]
    selected_category = data_base[user_id]["selected_category"]

    await delete_message_from_user(update)

    m = await update.message.reply_text("Оберіть параметр", reply_markup=nav.home)
    bot_message_info.append(m.message_id)

    # Deleting all bot messages and clear chat_states
    try:
        for message_id in reversed(bot_message):
            await context.bot.delete_message(user_id, message_id)
            bot_message.pop()

        for message_id in bot_message_info[:-1]:
            if message_id == 0:
                bot_message_info.pop(0)
            else:
                await context.bot.delete_message(user_id, message_id)
                bot_message_info.pop(0)

        for _ in reversed(chat_states):
            chat_states.pop()

        for _ in reversed(selected_category):
            selected_category.pop()

    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)

    logging.info("Clear ✔️")


async def delete_message_from_user(update: Update) -> None:
    try:
        await update.message.delete()
        logging.info("❌ Message from user deleted ❌")
    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")


async def delete_message_from_bot(update: Update, context: CallbackContext) -> None:

    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)
    delete_message = context.bot.delete_message

    bot_message_info = data_base[user_id]["bot_message_info"]
    bot_message = data_base[user_id]["bot_message"]

    try:
        for message_id in bot_message_info[:-1]:
            if message_id == 0:
                bot_message_info.pop(0)
            else:
                await delete_message(user_id, message_id)
                bot_message_info.pop(0)
                logging.info("❌ Message from bot  deleted ❌")

        for bot_message_id in bot_message[:-1]:
            if bot_message_id == 0:
                bot_message.pop(0)
            else:
                await delete_message(user_id, bot_message_id)
                bot_message.pop(0)
                logging.info("❌ Message from bot  deleted ❌")

    except Exception as exception:
        logging.warning(f"⚠️ {exception} ⚠️")

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)


async def back_to_previous(update: Update, context: CallbackContext) -> None:
    logging.info(f'Button "Назад" was triggered')

    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)
    reply_text = update.message.reply_text
    delete_message = context.bot.delete_message

    bot_message_info = data_base[user_id]["bot_message_info"]
    bot_message = data_base[user_id]["bot_message"]
    chat_states = data_base[user_id]["chat_states"]

    try:
        state = chat_states[-1]
        if state == "Меню" or state == "Додати новий запис" \
                or state == "Обрано категорію" or state == "-" or state == "+":
            for _ in reversed(chat_states):
                chat_states.pop()

            with open("bot_data.json", "w") as file:
                json.dump(data_base, file, indent=4)

            await home(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

        elif state == "Переглянути доходи" or state == "Переглянути витрати" or state == "Статистика" \
                or state == "Переглянути категорії" or state == "Доходи детально" or state == "Витрати детально":
            if state == "Доходи детально" or state == "Витрати детально":
                chat_states.pop()

            chat_states.pop()
            m = await reply_text("Оберіть параметр", reply_markup=nav.menu)
            bot_message_info.append(m.message_id)

            if len(bot_message) != 0:
                await delete_message(user_id, bot_message[0])
                bot_message.pop(0)

        elif state == "Додати категорію" or state == "Видалити категорію":
            chat_states.pop()
            m = await reply_text("Оберіть параметр", reply_markup=nav.menu_show_category)
            bot_message_info.append(m.message_id)

    except IndexError:
        logging.warning(f"⚠️ List index out of range ⚠️")
        await home(update, context)

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)


async def message_handler(update: Update, context: CallbackContext) -> None:

    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    message = update.message.text
    reply_text = update.message.reply_text
    send_message = context.bot.send_message
    delete_message = context.bot.delete_message
    user_id = str(update.effective_chat.id)
    month_year = str(datetime.datetime.now().date().strftime("%m.%Y"))
    day_month = str(datetime.datetime.now().date().strftime("%d.%m"))

    bot_message_info = data_base[user_id]["bot_message_info"]
    bot_message = data_base[user_id]["bot_message"]
    chat_states = data_base[user_id]["chat_states"]
    selected_date = data_base[user_id]["selected_date"]
    selected_category = data_base[user_id]["selected_category"]
    categories = data_base[user_id]['categories']

    # Get income/expense values to the dictionary
    incomes_dict = {}
    expenses_dict = {}
    categories_date_incomes_dict = {}
    categories_date_expenses_dict = {}

    for category, dates in categories.items():
        incomes_list = []
        expenses_list = []
        month_incomes_dict = {}
        month_expenses_dict = {}

        for month, day in dates.items():
            day_incomes_dict = {}
            day_expenses_dict = {}

            for date, expenses_data in day.items():
                incomes = expenses_data.get("incomes", [])
                expenses = expenses_data.get("expenses", [])

                if len(incomes) != 0:
                    incomes_list.extend(incomes)
                    day_incomes_dict[date] = incomes
                if len(expenses) != 0:
                    expenses_list.extend(expenses)
                    day_expenses_dict[date] = expenses

            if len(incomes_list) != 0:
                incomes_dict[category] = sum(incomes_list)
                month_incomes_dict[month] = day_incomes_dict
            if len(expenses_list) != 0:
                expenses_dict[category] = sum(expenses_list)
                month_expenses_dict[month] = day_expenses_dict

        if len(incomes_list) != 0:
            categories_date_incomes_dict[category] = month_incomes_dict
        if len(expenses_list) != 0:
            categories_date_expenses_dict[category] = month_expenses_dict

    # Format the income/expense dictionary
    formatted_incomes = []
    formatted_expenses = []
    for category, amount in incomes_dict.items():
        formatted_incomes.append(f"{category} ({amount} грн.)")
    for category, amount in expenses_dict.items():
        formatted_expenses.append(f"{category} ({amount} грн.)")

    # Print the received dictionaries in a list
    category_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(categories)])
    income_categories_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(formatted_incomes)])
    expense_categories_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(formatted_expenses)])

    await delete_message_from_user(update)

    # Checking messages from the user 261-669
    if len(chat_states) == 0:
        if message == "Додати новий запис":
            if len(categories) == 0:
                chat_states.append("Додати категорію")
                m = await reply_text(
                    "Спочатку треба додати категорію!\n"
                    "Введіть назву нової категорії:", reply_markup=nav.menu_btn_back
                )
                bot_message_info.append(m.message_id)

            else:
                logging.info(f'Button "{message}" was triggered')
                chat_states.append(message)

                m = await send_message(user_id, f"Оберіть категорію:\n\n{category_list}")
                bot_message.append(m.message_id)
                bot_message_info.append(0)

        elif message == "Меню":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m = await reply_text("Оберіть параметр", reply_markup=nav.menu)
            bot_message_info.append(m.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

    elif chat_states[-1] == "Додати новий запис":
        if message in categories:
            chat_states.append("Обрано категорію")
            selected_category.append(message)
            logging.info(f'Category "{message}" was selected')

            m = await reply_text(f"Обрано категорію: {message}", reply_markup=nav.menu_incomes_expenses)
            bot_message_info.append(m.message_id)

        elif message == "Додати категорію":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m = await reply_text("Введіть назву нової категорії", reply_markup=nav.menu_btn_back)
            bot_message_info.append(m.message_id)

        elif message == "Перейти на головну сторінку":
            await home(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

        elif message.isnumeric():
            if int(message) <= len(categories) and int(message) != 0:
                chat_states.append("Обрано категорію")
                selected_category.append(list(categories.keys())[int(message) - 1])
                logging.info(f'Category "{selected_category[0]}" was selected')

                m = await reply_text(
                    f"Обрано категорію: {selected_category[0]}", reply_markup=nav.menu_incomes_expenses
                )
                bot_message.append(m.message_id)

            else:
                logging.info('list out of range')
                m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                bot_message_info.append(m.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

        else:
            logging.info(f'No category "{message}"')
            if message.isalpha():
                m = await reply_text(f'Категорії "{message}" немає', reply_markup=nav.menu_new_category)
                bot_message_info.append(m.message_id)

    elif chat_states[-1] == "Обрано категорію":
        if message == "+":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m = await reply_text("Введіть суму доходу", reply_markup=nav.menu_btn_back)
            bot_message_info.append(m.message_id)
        elif message == "-":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m = await reply_text("Введіть суму витрат", reply_markup=nav.menu_btn_back)
            bot_message_info.append(m.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

    elif chat_states[-1] == "+" or chat_states[-1] == "-":
        if message.isdigit():
            def func():
                if month_year not in list(categories[selected_category[-1]].keys()):
                    categories[selected_category[-1]].update({month_year: {day_month: {"incomes": [], "expenses": []}}})
                else:
                    categories[selected_category[-1]][month_year].update({day_month: {"incomes": [], "expenses": []}})

            if chat_states[-1] == "+":
                try:
                    categories[selected_category[-1]][month_year][day_month]["incomes"].extend([int(message)])
                except KeyError:
                    func()
                    categories[selected_category[-1]][month_year][day_month]["incomes"].extend([int(message)])
                selected_category.pop()

                m = await send_message(user_id, f"До категорії додано {message} грн.")
                bot_message_info.append(m.message_id)

            elif chat_states[-1] == "-":
                try:
                    categories[selected_category[-1]][month_year][day_month]["expenses"].extend([-1 * (int(message))])
                except KeyError:
                    func()
                    categories[selected_category[-1]][month_year][day_month]["expenses"].extend([-1 * (int(message))])
                selected_category.pop()

                m = await send_message(user_id, f"До категорії додано -{message} грн.")
                bot_message_info.append(m.message_id)

            chat_states.append("До категорії додано")
            await delete_message(user_id, bot_message_info[0])
            bot_message_info.pop(0)
            time.sleep(2)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)
        else:
            m = await send_message(user_id, f"Введіть число")
            bot_message_info.append(m.message_id)

    elif chat_states[-1] == "Меню":
        if message == "Переглянути доходи" or message == "Переглянути витрати":
            logging.info(f'Button "{message}" was triggered')

            if message == "Переглянути доходи":
                if len(categories) == 0 or sum(incomes_dict.values()) == 0:
                    m = await reply_text("Поки немає жодного доходу", reply_markup=nav.menu)
                    bot_message_info.append(m.message_id)
                else:
                    chat_states.append(message)
                    m = await send_message(user_id, income_categories_list)
                    bot_message.append(m.message_id)
                    m = await reply_text(
                        "Введіть назву або № категорії для перегляду детальної інформації",
                        reply_markup=nav.menu_btn_back
                    )
                    bot_message_info.append(m.message_id)

            elif message == "Переглянути витрати":
                if len(categories) == 0 or sum(expenses_dict.values()) == 0:
                    m = await reply_text("Поки немає жодних витрат", reply_markup=nav.menu)
                    bot_message_info.append(m.message_id)
                else:
                    chat_states.append(message)
                    m = await send_message(user_id, expense_categories_list)
                    bot_message.append(m.message_id)
                    m = await reply_text(
                        "Введіть назву або № категорії для перегляду детальної інформації",
                        reply_markup=nav.menu_btn_back
                    )
                    bot_message_info.append(m.message_id)

        elif message == "Статистика":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m = await reply_text("Тут буде показано статистику.", reply_markup=nav.menu_show_statistic)
            bot_message.append(m.message_id)
            bot_message_info.append(0)

        elif message == "Переглянути категорії":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            if len(categories) == 0:
                m = await reply_text("Поки немає жодної категорії", reply_markup=nav.menu_show_category)
                bot_message_info.append(m.message_id)
            else:
                m = await reply_text(category_list, reply_markup=nav.menu_show_category)
                bot_message.append(m.message_id)
                bot_message_info.append(0)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

    elif chat_states[-1] == "Переглянути доходи" or chat_states[-1] == "Переглянути витрати":
        def detailed_list():
            formatted = []

            def format_values():
                result = "\n".join([f"{i}. {line} грн." for i, line in enumerate(values, start=1)])
                formatted.extend([f"{day} ({sum(values)} грн.)\n{result}"])

            if chat_states[-1] == "Доходи детально":
                for day, values in categories_date_incomes_dict[selected_category[-1]][selected_date[-1]].items():
                    format_values()

            elif chat_states[-1] == "Витрати детально":
                for day, values in categories_date_expenses_dict[selected_category[-1]][selected_date[-1]].items():
                    format_values()

            finally_formatted = "\n\n".join(formatted)
            return finally_formatted

        async def income_detail():
            chat_states.append("Доходи детально")

            income_for_category = [incomes_dict[key] for key in selected_category if key in incomes_dict]

            incomes_m = await reply_text(
                f'Доходи у категорії "{selected_category[-1]}"\n'
                f'за липень 2023 ({income_for_category[0]} грн.)\n\n'
                f'{detailed_list()}',
                reply_markup=nav.menu_show_incomes
            )
            bot_message.append(incomes_m.message_id)
            bot_message_info.append(0)

        async def expense_detail():
            chat_states.append("Витрати детально")

            expense_for_category = [expenses_dict[key] for key in selected_category if key in expenses_dict]

            expenses_m = await reply_text(
                f'Витрати у категорії "{selected_category[-1]}"\n'
                f'за липень 2023 ({expense_for_category[0]} грн.)\n\n'
                f'{detailed_list()}',
                reply_markup=nav.menu_show_expenses
            )
            bot_message.append(expenses_m.message_id)
            bot_message_info.append(0)

        if message in categories or message.isnumeric():
            selected_date.append(month_year)

            if message.isalpha():
                selected_category.append(message)
                if chat_states[-1] == "Переглянути доходи":
                    await income_detail()

                elif chat_states[-1] == "Переглянути витрати":
                    await expense_detail()

            elif message.isnumeric():
                if int(message) != 0:
                    if chat_states[-1] == "Переглянути доходи":
                        if int(message) <= len(formatted_incomes):
                            selected_category.append(formatted_incomes[int(message) - 1].split(' ')[0])
                            await income_detail()
                        else:
                            m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                            bot_message_info.append(m.message_id)

                    elif chat_states[-1] == "Переглянути витрати":
                        if int(message) <= len(formatted_expenses):
                            selected_category.append(formatted_expenses[int(message) - 1].split(' ')[0])
                            await expense_detail()
                        else:
                            m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                            bot_message_info.append(m.message_id)
                else:
                    m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                    bot_message_info.append(m.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

        else:
            if message.isalpha():
                m = await reply_text(f'Категорії "{message}" немає. Введіть існуючу', reply_markup=nav.menu_btn_back)
                bot_message_info.append(m.message_id)
            else:
                m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                bot_message_info.append(m.message_id)

    elif chat_states[-1] == "Доходи детально" or chat_states[-1] == "Витрати детально":
        # General functions
        if message == "Попередній місяць":
            logging.info(f'Button "{message}" was triggered')
            # chat_states.append(message)

        elif message == "→":
            logging.info(f'Button "{message}" was triggered')
            # chat_states.append(message)

        elif message == "Меню":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

        # Individual functions
        if chat_states[-1] == "Доходи детально":
            if message == "Видалити":
                logging.info(f'Button "{message}" was triggered')
                # chat_states.append(message)

            elif message == "Додати":
                logging.info(f'Button "{message}" was triggered')
                # chat_states.append(message)

        elif chat_states[-1] == "Витрати детально":
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
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

    elif chat_states[-1] == "Переглянути категорії":
        if message == "Додати категорію":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m = await reply_text("Введіть назву нової категорії", reply_markup=nav.menu_btn_back)
            bot_message_info.append(m.message_id)

        elif message == "Видалити категорію":
            if len(categories) == 0:
                logging.info(f'Button "{message}" was triggered')

                m = await reply_text("Немає жодної категорії для видалення!", reply_markup=nav.menu_show_category)
                bot_message_info.append(m.message_id)

            else:
                logging.info(f'Button "{message}" was triggered')
                chat_states.append(message)

                m = await reply_text(
                    "Введіть назву або № категорії яку треба видалити.\n\n""⚠️ Зверніть увагу ⚠️\n"
                    "Усі дані категорії видаляться!", reply_markup=nav.menu_btn_back
                )
                bot_message_info.append(m.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

    elif chat_states[-1] == "Додати категорію" or chat_states[-1] == "Видалити категорію":
        async def category_actions():
            # Notifications about creating or deleting a category
            if chat_states[-1] == "Додати категорію":
                add_category_m = await send_message(user_id, f'Додано нову категорію "{message}"')
                bot_message_info.append(add_category_m.message_id)

            elif chat_states[-1] == "Видалити категорію":
                if len(categories) == 0:
                    chat_states.pop()
                    del_all_m = await reply_text("Усі категорії видалено!", reply_markup=nav.menu_show_category)
                    bot_message_info.append(del_all_m.message_id)
                elif len(selected_category) != 0:
                    del_category_m = await send_message(user_id, f'Видалено категорію "{selected_category[-1]}"')
                    selected_category.pop()
                    bot_message_info.append(del_category_m.message_id)

            # Print updated categories list
            if len(categories) != 0:
                new_category_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(categories)])
                new_list_m = await reply_text(new_category_list, reply_markup=nav.menu_btn_back)
                bot_message.append(new_list_m.message_id)

            # Deleting and delaying messages to be deleted
            if len(bot_message) == 2:
                await delete_message(user_id, bot_message[0])
                bot_message.pop(0)

            if len(bot_message_info) == 2:
                await delete_message(user_id, bot_message_info[0])
                bot_message_info.pop(0)

            if len(categories) != 0:
                time.sleep(2)
                await delete_message(user_id, bot_message_info[0])
                bot_message_info.pop(0)
            else:
                await delete_message(user_id, bot_message[0])
                bot_message.pop(0)

        if not message == "Назад":
            # Update bot_data.json for incomes & expense in selected category
            if chat_states[-1] == "Додати категорію":
                categories.update({message: {}})
                await category_actions()

            elif chat_states[-1] == "Видалити категорію":
                if message.isalpha():
                    categories.pop(message)
                elif message.isnumeric():
                    if int(message) <= len(categories) and int(message) != 0:
                        selected_category.append(list(categories.keys())[int(message) - 1])
                        categories.pop(selected_category[-1])
                        await category_actions()
                    else:
                        logging.info('list out of range')
                        m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                        bot_message_info.append(m.message_id)

        else:
            if len(chat_states) <= 2:
                await home(update, context)
                with open("bot_data.json", "r") as file:
                    data_base = json.load(file)
            else:
                await back_to_previous(update, context)
                with open("bot_data.json", "r") as file:
                    data_base = json.load(file)

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)

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
