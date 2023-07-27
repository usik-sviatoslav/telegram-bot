import json
import logging
import re
from collections import OrderedDict

import markups as nav
import my_token as token

from time import sleep
from telegram import Update
from datetime import datetime, timedelta
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
            "selected_category_dates": [],
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
    selected_date = data_base[user_id]["selected_date"]
    selected_category_dates = data_base[user_id]["selected_category_dates"]
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

        chat_states.clear()
        selected_date.clear()
        selected_category.clear()
        selected_category_dates.clear()

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
    send_message = context.bot.send_message

    bot_message = data_base[user_id]["bot_message"]
    bot_message_info = data_base[user_id]["bot_message_info"]
    chat_states = data_base[user_id]["chat_states"]
    selected_date = data_base[user_id]["selected_date"]
    selected_category = data_base[user_id]["selected_category"]
    selected_category_dates = data_base[user_id]["selected_category_dates"]
    categories = data_base[user_id]['categories']
    day_m_y = str(datetime.now().date().strftime("%d.%m.%Y"))
    category_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(categories)])

    try:
        if chat_states[-1] in ["Меню", "Додати новий запис"]:
            chat_states.clear()

            with open("bot_data.json", "w") as file:
                json.dump(data_base, file, indent=4)

            await home(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

        elif chat_states[-1] == "Обрано категорію":
            chat_states.pop()
            selected_category.pop()
            m = await send_message(user_id, f"Оберіть категорію:\n\n{category_list}")
            bot_message_info.append(m.message_id)

            if len(bot_message) != 0:
                await delete_message(user_id, bot_message[0])
                bot_message.pop(0)

        elif chat_states[-1] in ["Обрати інший день", "-", "+"]:
            chat_states.pop()
            m = await reply_text(
                f"{day_m_y}\n"
                f"Категорія: {selected_category[-1]}", reply_markup=nav.menu_incomes_expenses
            )
            bot_message.append(m.message_id)
            bot_message_info.append(0)

        elif chat_states[-1] in [
            "Переглянути доходи", "Переглянути витрати", "Статистика",
            "Переглянути категорії", "Доходи детально", "Витрати детально"
        ]:
            if chat_states[-1] in ["Доходи детально", "Витрати детально", "Статистика"]:
                if not chat_states[-1] == "Статистика":
                    chat_states.pop()
                    selected_category.pop()

                selected_date.clear()
                selected_category_dates.clear()

            chat_states.pop()
            m = await reply_text("Оберіть параметр", reply_markup=nav.menu)
            bot_message_info.append(m.message_id)

            if len(bot_message) != 0:
                await delete_message(user_id, bot_message[0])
                bot_message.pop(0)

        elif chat_states[-1] in ["Додати категорію", "Видалити категорію"]:
            chat_states.pop()
            m = await reply_text("Оберіть параметр", reply_markup=nav.menu_show_category)
            bot_message_info.append(m.message_id)

    except IndexError:
        logging.warning(f"⚠️ List index out of range ⚠️")
        await home(update, context)

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)


async def category_actions(update, context, message):
    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    reply_text = update.message.reply_text
    user_id = str(update.effective_chat.id)
    delete_message = context.bot.delete_message
    send_message = context.bot.send_message

    bot_message = data_base[user_id]["bot_message"]
    bot_message_info = data_base[user_id]["bot_message_info"]
    chat_states = data_base[user_id]["chat_states"]
    selected_category = data_base[user_id]["selected_category"]
    categories = data_base[user_id]['categories']

    async def show_category_list():
        new_category_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(categories)])
        new_list_m = await reply_text(new_category_list, reply_markup=nav.menu_btn_back)
        bot_message.append(new_list_m.message_id)

    if chat_states[-1] == "Додати категорію":
        categories.update({message: {}})
        add_category_m = await send_message(user_id, f'Додано нову категорію "{message}"')
        bot_message_info.append(add_category_m.message_id)

        sleep(2)
        await delete_message(user_id, bot_message_info[-1])
        bot_message_info.pop()

        await show_category_list()

    elif chat_states[-1] == "Видалити категорію":
        if message.isalpha():
            if message in categories:
                selected_category.append(message)
            else:
                logging.info(f'No category "{message}"')
                no_category_m = await send_message(user_id, f'Категорії "{message}" немає')
                bot_message_info.append(no_category_m.message_id)

                sleep(2)
                await delete_message(user_id, bot_message_info[-1])
                bot_message_info.pop()

        elif message.isnumeric():
            if int(message) <= len(categories) and int(message) != 0:
                selected_category.append(list(categories.keys())[int(message) - 1])
            else:
                logging.info('No number in list')
                no_in_list_m = await send_message(user_id, 'Немає такого значення у списку!')
                bot_message_info.append(no_in_list_m.message_id)

                sleep(2)
                await delete_message(user_id, bot_message_info[-1])
                bot_message_info.pop()

        if len(selected_category) != 0:
            del_category_m = await send_message(user_id, f'Видалено категорію "{selected_category[-1]}"')
            bot_message_info.append(del_category_m.message_id)

            sleep(2)
            await delete_message(user_id, bot_message_info[-1])
            bot_message_info.pop()

            categories.pop(selected_category[-1])
            selected_category.pop()

            if len(categories) == 0:
                chat_states.pop()
                del_all_m = await send_message(user_id, "Усі категорії видалено!")
                bot_message_info.append(del_all_m.message_id)

                await delete_message(user_id, bot_message_info[0])
                bot_message_info.pop(0)
                await delete_message(user_id, bot_message[-1])
                bot_message.pop()

                sleep(2)
                no_category_m = await reply_text("Поки немає жодної категорії", reply_markup=nav.menu_show_category)
                bot_message_info.append(no_category_m.message_id)

                await delete_message(user_id, bot_message_info[0])
                bot_message_info.pop(0)

            else:
                await show_category_list()

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)


async def handle_expense_or_income(update, context, message, category_type):
    logging.info(f'Button "{message}" was triggered')
    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)
    reply_text = update.message.reply_text
    send_message = context.bot.send_message
    delete_message = context.bot.delete_message
    categories = data_base[user_id]['categories']
    chat_states = data_base[user_id]["chat_states"]
    bot_message = data_base[user_id]["bot_message"]
    bot_message_info = data_base[user_id]["bot_message_info"]

    dict_data = {}
    dict_data.update(read_data(update, message=message))

    if len(categories) == 0 or sum(dict_data.values()) == 0:
        m_info = await send_message(user_id, f"Поки немає жодних {category_type}")
        bot_message_info.append(m_info.message_id)
        chat_states.pop()

        sleep(2)
        await delete_message(user_id, bot_message_info[-1])
        bot_message_info.pop()

    else:
        categories_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(dict_data.keys())])

        m_categories_list = await send_message(user_id, categories_list)
        bot_message.append(m_categories_list.message_id)
        m_info = await reply_text(
            "Введіть назву або № категорії для перегляду детальної інформації",
            reply_markup=nav.menu_btn_back
        )
        bot_message_info.append(m_info.message_id)

    with open("bot_data.json", "w") as f:
        json.dump(data_base, f, indent=4)


async def handle_statistic(update, message_type, date_type=None, selected_date=None):
    logging.info(f'Button "{message_type}" was triggered')

    exp_data = read_data(update, "exp", date_type, message_type, selected_date=selected_date[-1])
    inc_data = read_data(update, "inc", date_type, message_type, selected_date=selected_date[-1])

    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)
    reply_text = update.message.reply_text
    bot_message_info = data_base[user_id]["bot_message_info"]
    selected_category_dates = data_base[user_id]["selected_category_dates"]

    list_of_inc = [f"{category} ({amount:_} грн.)".replace("_", " ") for category, amount in inc_data.items()]
    list_of_exp = [f"{category} ({amount:_} грн.)".replace("_", " ") for category, amount in exp_data.items()]
    formatted_list = []

    message = None
    reply_markup = None
    if date_type == "week":
        start_date_str, end_date_str = selected_date[-1].split(' - ')
        start_day, start_month, start_year = start_date_str.split('.')
        end_day, end_month, end_year = end_date_str.split('.')
        date = f"{start_day}.{start_month} - {end_day}.{end_month}"

        message = f"Статистика за {start_year} рік\nз {date} день\n\n"
        reply_markup = nav.menu_show_statistic_week_1 if len(selected_date) == 1 else nav.menu_show_statistic_week_2

    elif date_type == "month":
        month, year = selected_date[-1].split('.')
        message = f"Статистика за {nav.month_name[month]} {year} року\n\n"
        reply_markup = nav.menu_show_statistic_month_1 if len(selected_date) == 1 else nav.menu_show_statistic_month_2

    elif date_type == "year":
        message = f"Статистика за {selected_date[-1]} рік\n\n"
        reply_markup = nav.menu_show_statistic_year_1 if len(selected_date) == 1 else nav.menu_show_statistic_year_2

    if list_of_inc:
        formatted_list_of_inc = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(list_of_inc)])
        formatted_list.append(f"{message}{'—' * 16}\nДоходи:\n\n{formatted_list_of_inc}\n{'—' * 16}")
    else:
        formatted_list.append(f"{message}{'—' * 16}\nДоходів не було\n{'—' * 16}")

    if list_of_exp:
        formatted_list_of_exp = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(list_of_exp)])
        formatted_list.append(f"Витрати:\n\n{formatted_list_of_exp}\n{'—' * 16}")
    else:
        formatted_list.append(f"Витрат не було\n{'—' * 16}\n")

    finally_formatted_list = "\n\n".join(formatted_list)
    m = await reply_text(finally_formatted_list, reply_markup=reply_markup)
    bot_message_info.append(m.message_id)

    if message_type != "→":
        selected_category_dates.pop()

    with open("bot_data.json", "w") as f:
        json.dump(data_base, f, indent=4)


async def detail_transaction(update, context, reply_markup=None, category=None, forward=None):
    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)
    reply_text = update.message.reply_text
    send_message = context.bot.send_message
    bot_message_info = data_base[user_id]["bot_message_info"]
    bot_message = data_base[user_id]["bot_message"]
    chat_states = data_base[user_id]["chat_states"]
    selected_date = data_base[user_id]["selected_date"]
    categories = data_base[user_id]['categories']
    selected_category = data_base[user_id]["selected_category"]
    selected_category_dates = data_base[user_id]["selected_category_dates"]

    dict_data = {}
    dict_data.update(read_data(update, message=chat_states[-1]))

    func = int(category) <= len(dict_data.keys()) if isinstance(category, int) else category
    num = int(category) if isinstance(category, int) else category

    if func or func is None:
        action = ""
        if chat_states[-1] in ["Переглянути доходи", "Доходи детально"]:
            action = "Доходи"
        elif chat_states[-1] in ["Переглянути витрати", "Витрати детально"]:
            action = "Витрати"

        if isinstance(category, int):
            selected_category.append(list(dict_data.keys())[num - 1])

        if chat_states[-1] in ["Переглянути доходи", "Переглянути витрати"]:
            chat_states.append(f"{action} детально")

        if len(selected_category_dates) == 0 and len(selected_date) == 1:
            selected_category_dates.extend(list(categories[selected_category[-1]].keys()))

        dict_data.clear()

        with open("bot_data.json", "w") as f:
            json.dump(data_base, f, indent=4)

        dict_data.update(read_data(
            update, message=chat_states[-1], category=selected_category[-1], selected_date=selected_date[-1]
        ))

        async def show_detail_transaction():
            formatted = []
            total_sum = sum(value[0] for value in dict_data.values())

            for current_day, values in dict_data.items():
                result = "\n".join(
                    [f"{i}.  {line:_} грн.".replace("_", " ")for i, line in enumerate(values, start=1)]
                )
                formatted.extend([f"{current_day[:5]} ({sum(values):_} грн.)\n{result}".replace("_", " ")])

            detailed_list = "\n\n".join(formatted)
            month, year = selected_date[-1].split('.')

            transaction = await reply_text(
                f'{action} у категорії "{selected_category[-1]}"\n'
                f'за {nav.month_name[month]} {year} року\n({total_sum} грн.)\n{"—" * 16}\n\n'
                f'{detailed_list}', reply_markup=reply_markup
            )

            bot_message.append(transaction.message_id)
            bot_message_info.append(0)

            if forward is None:
                selected_category_dates.pop()

        if len(dict_data) != 0:
            await show_detail_transaction()

        else:
            try:
                if len(selected_category_dates) != 0:
                    selected_date.pop()

                selected_date.append(selected_category_dates[-1])
                dict_data.update(read_data(
                    update, message=chat_states[-1], category=selected_category[-1], selected_date=selected_date[-1]
                ))
                await show_detail_transaction()

            except IndexError:
                selected_date.pop()
                m = await send_message(user_id, 'Більше немає записів!')
                bot_message_info.append(m.message_id)
                sleep(2)
                bot_message_info.append(0)

    else:
        selected_date.pop()
        trans = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
        bot_message_info.append(trans.message_id)

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)


def get_current_week():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    week_str = f"{start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}"
    return week_str


def sort_by_week(update, dates_dict, selected_date, message_type):
    sorted_dates = sorted(dates_dict.keys(), key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
    weekly_dict = {}
    selected_week = 0

    for date_str in sorted_dates:
        date = datetime.strptime(date_str, "%d.%m.%Y")
        start_of_week = date - timedelta(days=date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_str = f"{start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}"

        if week_str not in weekly_dict:
            weekly_dict[week_str] = 0

        weekly_dict[week_str] += dates_dict[date_str]

    if selected_date in weekly_dict.keys():
        selected_week += weekly_dict[selected_date]

    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)
    selected_category_dates = data_base[user_id]["selected_category_dates"]

    if message_type not in ["Попередній тиждень", "Попередній місяць", "Попередній рік", "→"]:
        for key in weekly_dict.keys():
            if key not in selected_category_dates:
                selected_category_dates.extend([key])

        def parse_date(date_range):
            start_date_str, end_date_str = date_range.split(' - ')
            start_day, start_month, start_year = map(int, start_date_str.split('.'))
            return start_year, start_month, start_day

        sorted_dates = sorted(selected_category_dates, key=parse_date)
        selected_category_dates.clear()

        with open("bot_data.json", "w") as file:
            json.dump(data_base, file, indent=4)

        selected_category_dates.extend(sorted_dates)

    with open("bot_data.json", "w") as file:
        json.dump(data_base, file, indent=4)

    return selected_week


def read_data(update, current_dict=None, date_type=None, message=None, category=None, selected_date=None):
    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    user_id = str(update.effective_chat.id)
    categories = data_base[user_id]['categories']

    message_types_1 = ("Переглянути доходи", "Переглянути витрати")
    message_types_2 = ("Доходи детально", "Витрати детально")
    message_types_3 = (
        "Статистика", "Попередній тиждень", "Попередній місяць", "Попередній рік", "Тиждень", "Місяць", "Рік", "→"
    )

    if date_type is None:
        if message in message_types_1:
            dict_data = {}
            for category, month_year in categories.items():
                incomes_expenses = []
                for month, day in month_year.items():
                    for current_day, data in day.items():
                        operation = data.get("incomes", []) if message == message_types_1[0] \
                            else data.get("expenses", [])
                        if sum(operation) != 0:
                            incomes_expenses.extend(operation)

                result = sum(incomes_expenses)
                if result != 0:
                    dict_data[category] = result

            return dict_data

        elif message in message_types_2:
            dict_data = {}
            for categories, month_year in categories.items():
                if categories == category:
                    for month, day in month_year.items():
                        if month == selected_date:
                            for current_day, data in day.items():
                                operation = data.get("incomes", []) if message == message_types_2[0] \
                                    else data.get("expenses", [])
                                if sum(operation) != 0:
                                    dict_data[current_day] = operation

            return dict_data

    elif message in message_types_3:
        if date_type == "week":
            week_income_expense = {}
            for categories, month_year in categories.items():
                all_days = {}
                for month, day in month_year.items():
                    for current_day, data in day.items():
                        operation = data.get("incomes", []) if current_dict == "inc" else data.get("expenses", [])
                        if sum(operation) != 0:
                            all_days[current_day] = sum(operation)
                        else:
                            all_days[current_day] = 0

                result = sort_by_week(update, all_days, selected_date, message)
                if result != 0:
                    week_income_expense[categories] = result

            return week_income_expense

        elif date_type in ("month", "year"):
            month_year_income_expense = {}
            for category, month_year in categories.items():
                incomes_expenses = []
                for month, day in month_year.items():
                    month = month if date_type == "month" else month[3:]
                    if month == selected_date:
                        for current_day, data in day.items():
                            operation = data.get("incomes", []) if current_dict == "inc" else data.get("expenses", [])
                            if sum(operation) != 0:
                                incomes_expenses.extend(operation)

                        result = sum(incomes_expenses)
                        if result != 0:
                            month_year_income_expense[category] = result

            return month_year_income_expense


async def message_handler(update: Update, context: CallbackContext) -> None:
    with open("bot_data.json", "r") as file:
        data_base = json.load(file)

    message = update.message.text
    reply_text = update.message.reply_text
    send_message = context.bot.send_message
    delete_message = context.bot.delete_message
    user_id = str(update.effective_chat.id)
    year = str(datetime.now().date().strftime("%Y"))
    month_y = str(datetime.now().date().strftime("%m.%Y"))
    day_m_y = str(datetime.now().date().strftime("%d.%m.%Y"))

    bot_message_info = data_base[user_id]["bot_message_info"]
    bot_message = data_base[user_id]["bot_message"]
    chat_states = data_base[user_id]["chat_states"]
    selected_date = data_base[user_id]["selected_date"]
    selected_category = data_base[user_id]["selected_category"]
    categories = data_base[user_id]['categories']
    selected_category_dates = data_base[user_id]["selected_category_dates"]

    # Print the received dictionaries in a list
    category_list = "\n".join([f"{i + 1}. {line}" for i, line in enumerate(categories)])

    await delete_message_from_user(update)

    # Checking messages from the user 707-1173
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
                bot_message_info.append(m.message_id)

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

            m = await reply_text(
                f"{day_m_y}\n"
                f"Категорія: {message}", reply_markup=nav.menu_incomes_expenses
            )
            bot_message.append(m.message_id)
            bot_message_info.append(0)

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
                    f"{day_m_y}\n"
                    f"Категорія: {selected_category[0]}", reply_markup=nav.menu_incomes_expenses
                )
                bot_message.append(m.message_id)
                bot_message_info.append(0)

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

        elif message == "Обрати інший день":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)

            m = await reply_text("Введіть дату", reply_markup=nav.menu_btn_back_date)
            bot_message_info.append(m.message_id)

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)

    elif chat_states[-1] in ["+", "-", "Обрати інший день"]:
        def update_category(sel_category, date_month_y, date_day_m_y, state, amount=None):
            if date_month_y not in list(categories[sel_category].keys()):
                categories[sel_category].update({date_month_y: {date_day_m_y: {"incomes": [], "expenses": []}}})
            elif date_day_m_y not in list(categories[sel_category][date_month_y].keys()):
                categories[sel_category][date_month_y].update({date_day_m_y: {"incomes": [], "expenses": []}})

            if chat_states[-1] in ["+", "-"]:
                key = "incomes" if state == "+" else "expenses"
                date_day_m_y = selected_date[-1] if len(selected_date) != 0 else date_day_m_y
                if state == "+":
                    categories[sel_category][date_month_y][date_day_m_y][key].extend([amount])
                else:
                    categories[sel_category][date_month_y][date_day_m_y][key].extend([-1 * amount])

            categories[sel_category][date_month_y] = OrderedDict(sorted(categories[sel_category][date_month_y].items()))
            categories[sel_category] = OrderedDict(sorted(categories[sel_category].items()))

        if message.isdigit():
            if chat_states[-1] in ["+", "-"]:
                try:
                    update_category(selected_category[-1], month_y, day_m_y, chat_states[-1], int(message))
                except KeyError:
                    update_category(selected_category[-1], month_y, day_m_y, chat_states[-1], int(message))

                selected_category.pop()
                amount_msg = message if chat_states[-1] == "+" else f"-{message}"
                m = await send_message(user_id, f"До категорії додано {int(amount_msg):_} грн.".replace("_", " "))
                bot_message_info.append(m.message_id)

            chat_states.append("До категорії додано")
            await delete_message(user_id, bot_message_info[0])
            bot_message_info.pop(0)
            sleep(2)

        elif chat_states[-1] == "Обрати інший день":
            if re.match(r"\d{2}\.\d{2}\.\d{4}", message):
                try:
                    data = datetime.strptime(message, "%d.%m.%Y")
                    month_y = f'{data.strftime("%m.%Y")}'
                    day_m_y = f'{data.strftime("%d.%m.%Y")}'

                    if len(selected_date) != 0:
                        selected_date.pop()
                        selected_date.append(day_m_y)
                    else:
                        selected_date.append(day_m_y)

                    update_category(selected_category[-1], month_y, day_m_y, chat_states[-1])
                    chat_states.pop()

                    m = await reply_text(
                        f"Обрано {selected_date[-1]}\n"
                        f"Категорія: {selected_category[0]}", reply_markup=nav.menu_incomes_expenses
                    )
                    bot_message.append(m.message_id)
                    bot_message_info.append(0)

                except ValueError:
                    logging.info('No valid date')
                    no_in_list_m = await send_message(user_id, 'Дату введено не коректно!')
                    bot_message_info.append(no_in_list_m.message_id)

                    sleep(2)
                    await delete_message(user_id, bot_message_info[-1])
                    bot_message_info.pop()

            elif message == "Назад":
                await back_to_previous(update, context)
                with open("bot_data.json", "r") as file:
                    data_base = json.load(file)

            else:
                logging.info('No valid date')
                no_in_list_m = await send_message(user_id, 'Дату введено не коректно!')
                bot_message_info.append(no_in_list_m.message_id)

                sleep(2)
                await delete_message(user_id, bot_message_info[-1])
                bot_message_info.pop()

        elif message == "Назад":
            await back_to_previous(update, context)
            with open("bot_data.json", "r") as file:
                data_base = json.load(file)
        else:
            m = await reply_text(f"Введіть число", reply_markup=nav.menu_btn_back)
            bot_message_info.append(m.message_id)

    elif chat_states[-1] == "Меню":
        if message in ["Переглянути доходи", "Переглянути витрати"]:
            chat_states.append(message)
            with open("bot_data.json", "w") as f:
                json.dump(data_base, f, indent=4)

            command = "доходів" if message == "Переглянути доходи" else "витрат"
            await handle_expense_or_income(update, context, message, command)

        elif message == "Статистика":
            value = 0
            for i in list(categories.values()):
                if len(i) != 0:
                    value += 1

            if len(list(categories)) == 0 or value == 0:
                m = await send_message(user_id, "Немає даних для статистики!")
                bot_message_info.append(m.message_id)

                sleep(2)
                await delete_message(user_id, bot_message_info[-1])
                bot_message_info.pop()

            else:
                chat_states.append(message)
                selected_date.append(get_current_week())
                with open("bot_data.json", "w") as f:
                    json.dump(data_base, f, indent=4)

                await handle_statistic(update, message, "week", selected_date)

        elif message == "Переглянути категорії":
            logging.info(f'Button "{message}" was triggered')
            chat_states.append(message)
            with open("bot_data.json", "w") as f:
                json.dump(data_base, f, indent=4)

            if len(categories) == 0:
                m = await reply_text("Поки немає жодної категорії", reply_markup=nav.menu_show_category)
                bot_message_info.append(m.message_id)
            else:
                m = await reply_text(category_list, reply_markup=nav.menu_show_category)
                bot_message.append(m.message_id)
                bot_message_info.append(0)

            with open("bot_data.json", "w") as f:
                json.dump(data_base, f, indent=4)

        elif message == "Назад":
            await back_to_previous(update, context)

        with open("bot_data.json", "r") as file:
            data_base = json.load(file)

    elif chat_states[-1] in ["Переглянути доходи", "Переглянути витрати"]:
        if message in categories or message.isnumeric():
            if message.isalpha():
                selected_category.append(message)

            selected_date.append(month_y)
            with open("bot_data.json", "w") as file:
                json.dump(data_base, file, indent=4)

            category = message if message.isalpha() else int(message)
            command = ["Переглянути доходи", "Переглянути витрати"]

            if message.isalpha() and chat_states[-1] in command:
                reply_markup = nav.menu_show_incomes_1 if chat_states[-1] == command[0] else nav.menu_show_expenses_1
                await detail_transaction(update, context, reply_markup, category)

            elif message.isnumeric() and category != 0 and chat_states[-1] in command:
                reply_markup = nav.menu_show_incomes_1 if chat_states[-1] == command[0] else nav.menu_show_expenses_1
                await detail_transaction(update, context, reply_markup, category)

            else:
                if category == 0:
                    selected_date.pop()
                m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                bot_message_info.append(m.message_id)
                with open("bot_data.json", "w") as file:
                    json.dump(data_base, file, indent=4)

        elif message == "Назад":
            await back_to_previous(update, context)

        else:
            if message.isalpha():
                m = await reply_text(f'Категорії "{message}" немає. Введіть існуючу', reply_markup=nav.menu_btn_back)
                bot_message_info.append(m.message_id)
            else:
                m = await reply_text('Немає такого значення у списку!', reply_markup=nav.menu_btn_back)
                bot_message_info.append(m.message_id)
            with open("bot_data.json", "w") as file:
                json.dump(data_base, file, indent=4)

        with open("bot_data.json", "r") as file:
            data_base = json.load(file)

    elif chat_states[-1] in ["Доходи детально", "Витрати детально"]:
        # General functions
        if message in ["Попередній місяць", "→"]:
            logging.info(f'Button "{message}" was triggered')

            forward = None
            if message == "Попередній місяць":
                selected_date.append(
                    (datetime.strptime(selected_date[-1], "%m.%Y") - timedelta(days=1)).strftime("%m.%Y")
                )
            elif message == "→":
                selected_category_dates.extend([selected_date[-1]])
                selected_date.pop()
                forward = "→"
            category = None

            with open("bot_data.json", "w") as fi:
                json.dump(data_base, fi, indent=4)

            if chat_states[-1] == "Доходи детально":
                reply_markup = nav.menu_show_incomes_1 if len(selected_date) == 1 else nav.menu_show_incomes_2
                await detail_transaction(update, context, reply_markup, category, forward)
            elif chat_states[-1] == "Витрати детально":
                reply_markup = nav.menu_show_expenses_1 if len(selected_date) == 1 else nav.menu_show_expenses_2
                await detail_transaction(update, context, reply_markup, category, forward)

        elif message == "Меню":
            await back_to_previous(update, context)

        else:
            if message not in ["Видалити", "Додати"]:
                logging.info(f'Invalid command was entered')
                m = await send_message(user_id, 'Немає таких даних!')
                bot_message_info.append(m.message_id)
                sleep(2)
                bot_message_info.append(0)
                with open("bot_data.json", "w") as file:
                    json.dump(data_base, file, indent=4)

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

        with open("bot_data.json", "r") as file:
            data_base = json.load(file)

    elif chat_states[-1] == "Статистика":
        date_type = {
            "Попередній тиждень": "week",
            "Попередній місяць": "month",
            "Попередній рік": "year",
        }
        message_actions = {
            "Тиждень": ("week", get_current_week()),
            "Місяць": ("month", month_y),
            "Рік": ("year", year)
        }

        if message in date_type.keys():
            logging.info(f'Button "{message}" was triggered')
            try:
                selected_date.append(selected_category_dates[-1])
                with open("bot_data.json", "w") as f:
                    json.dump(data_base, f, indent=4)

                await handle_statistic(update, message, date_type.get(message), selected_date)

            except IndexError:
                m = await send_message(user_id, 'Більше немає записів!')
                bot_message_info.append(m.message_id)
                sleep(2)
                await delete_message(user_id, bot_message_info[-1])
                bot_message_info.pop()

        if message in message_actions:
            logging.info(f'Button "{message}" was triggered')

            selected_date.clear()
            selected_category_dates.clear()
            selected_date.append(message_actions[message][1])

            if message in ("Місяць", "Рік"):
                for category, dates in categories.items():
                    for date in dates.keys():
                        date = date if message == "Місяць" else date[3:]
                        if date not in selected_category_dates:
                            selected_category_dates.append(date)

            with open("bot_data.json", "w") as file:
                json.dump(data_base, file, indent=4)

            await handle_statistic(update, message, message_actions[message][0], selected_date)

        elif message == "→":
            logging.info(f'Button "{message}" was triggered')
            selected_category_dates.append(selected_date[-1])
            selected_date.pop()
            with open("bot_data.json", "w") as file:
                json.dump(data_base, file, indent=4)

            data_type = None
            if re.match(r"\d{2}.\d{2}.\d{4} - \d{2}.\d{2}.\d{4}", selected_date[-1]):
                data_type = "week"

            elif re.match(r"\d{2}.\d{4}", selected_date[-1]):
                data_type = "month"

            elif re.match(r"\d{4}", selected_date[-1]):
                data_type = "year"

            await handle_statistic(update, message, data_type, selected_date)

        elif message == "Меню":
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

    elif chat_states[-1] in ["Додати категорію", "Видалити категорію"]:
        if not message == "Назад":
            if chat_states[-1] in ["Додати категорію", "Видалити категорію"]:
                await category_actions(update, context, message)
        else:
            if len(chat_states) <= 2:
                await home(update, context)
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
