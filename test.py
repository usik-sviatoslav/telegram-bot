import logging
import markups as nav
import bot_data as data
from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, MessageHandler, filters


# ----------------------------------------------------------------------------------------------------------------------
# Function
# ----------------------------------------------------------------------------------------------------------------------



class Menu:
    def __init__(self, text, reply_markup):
        self.text = text
        self.reply_markup = reply_markup

    async def start(update: Update, context: CallbackContext) -> None:
        logging.info('Command "/start" was triggered.')
        
        if update.message.text == "/start"
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
                reply_markup=markups.home
            )
            bot_message_command = context.bot_data.get("bot_message_command", [])
            bot_message_command.append(message_1.message_id)
            bot_message_command.append(message_2.message_id)
            context.bot_data["bot_message_command"] = bot_message_command

    async def home(update: Update, context: CallbackContext) -> None:
        logging.info('Command "/home" was triggered.')
        await update.message.reply_text("Оберіть опцію", reply_markup markups.home)

        bot_message = context.bot_data.get("bot_message", [])
        bot_message_command = context.bot_data.get("bot_message_command", [])

        for message_id in reversed(bot_message):
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
            bot_message.pop()

        for message_id in bot_message_command:
            if len(bot_message_command) >= 2:
                if message_id == 0:
                    bot_message_command.pop(0)

        logging.info("Clear ✔️")
    
    async def message_from_user(self, update: Update, context: CallbackContext) -> None:
        try:
            await update.message.delete()
            logging.info("❌ Message from user deleted ❌")
        except Exception as exception:
            logging.warning(f"⚠️ {exception} ⚠️")
        
        message = update.message.text
        if message == "Меню" \
                or message == "Переглянути доходи" \
                or message == "Переглянути витрати" \
                or message == "Статистика" \
                or message == "Переглянути категорії" \
                or message == "Додати категорію" \
                or message == "Видалити категорію" \
                or message == "Назад":
            logging.info(f'Button "{update.message.text}" was triggered')
            
            reply_text = update.message.reply_text
                await reply_text("Оберіть опцію", reply_markup=nav.menu)
            elif message == "Переглянути доходи":
                await reply_text(data.joined_text, reply_markup=nav.menu_show_income)
            elif message == "Переглянути витрати":
                await reply_text(data.all_categories, reply_markup=nav.menu_show_spending)
            elif message == "Статистика":
                await reply_text("Тут буде показано статистику.", reply_markup=nav.menu_show_statistic)
            elif message == "Переглянути категорії:
                await reply_text("На екран виводиться список категорій.", nav.menu_show_category)
            elif message == "Додати категорію":
                await reply_text("Введіть назву нової категорії", reply_markup=nav.menu_btn_back)
            elif message == "Видалити категорію":
                await reply_text("Введіть назву категорії яку треба видалити", reply_markup=nav.menu_btn_back) 



    async def __call__(self, update: Update, context: CallbackContext) -> None:
        logging.info(f'Button "{update.message.text}" was triggered')

        try:
            await update.message.delete()
            logging.info("❌ Message from user deleted ❌")
        except Exception as exception:
            logging.warning(f"⚠️ {exception} ⚠️")

        message = await update.message.reply_text(self.text, reply_markup=self.reply_markup)

        commands = [
            "Оберіть опцію", "Введіть назву нової категорії",
            "Введіть назву категорії яку треба видалити"
        ]

        # Отримуємо id повідомлення від бота, щоб потім видалити повідомлення
        bot_message_command = context.bot_data.get("bot_message_command", [])
        bot_message = context.bot_data.get("bot_message", [])
        if message.text in commands:
            bot_message_command.append(message.message_id)
            context.bot_data["bot_message_command"] = bot_message_command
        else:
            bot_message.append(message.message_id)
            context.bot_data["bot_message"] = bot_message
            bot_message_command.append(0)

        if len(bot_message_command) >= 2:
            for message_id in bot_message_command[:-1]:
                if message_id == 0:
                    bot_message_command.pop(0)
                else:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
                    bot_message_command.pop(0)
                    logging.info("❌ Message from bot  deleted ❌")
                    context.bot_data["bot_message_command"] = [bot_message_command[-1]]

        if not update.message.text == "Назад":
            chat_states = context.bot_data.get("chat_states", [])
            chat_states.append(update.message.text)
            context.bot_data["chat_states"] = chat_states

        if self.text:
            if self.text == "Введіть назву нової категорії":
                await input_from_user(update, context)
            elif self.text == "Введіть назву категорії яку треба видалити":
                await input_from_user(update, context)

    @staticmethod
    async def clear(update: Update, context: CallbackContext) -> None:
        

    @staticmethod
    async def back_to_previous(update: Update, context: CallbackContext) -> None:
        chat_states = context.bot_data.get("chat_states", [])

        try:
            state = chat_states[-1]
            if state == "Меню":
                chat_states.pop()
                await home.clear(update, context)
            elif state == "Переглянути доходи" \
                    or state == "Переглянути витрати"\
                    or state == "Статистика"\
                    or state == "Переглянути категорії":
                chat_states.pop()
                await menu(update, context)
            elif state == "Додати категорію" \
                    or state == "Видалити категорію":
                chat_states.pop()
                await menu_show_category(update, context)
        except IndexError:
            logging.warning(f"⚠️ List index out of range ⚠️")


async def input_from_user(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    text = update.message.text


home = Menu("Оберіть опцію", markups.home)
menu = Menu("Оберіть опцію", markups.menu)
menu_show_income = Menu(data.joined_text, markups.menu_show_income)
menu_show_spending = Menu(data.all_categories, markups.menu_show_spending)
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
    app.add_handler(CommandHandler("home", home.clear))
    app.add_handler(MessageHandler(filters.Regex(r"\w+"), Menu.message_from_user))

    app.run_polling()


if __name__ == "__main__":
    run()
