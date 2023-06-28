from telegram import ReplyKeyboardMarkup, KeyboardButton

# ----------------------------------------------------------------------------------------------------------------------
# Buttons
# ----------------------------------------------------------------------------------------------------------------------

btn_income = KeyboardButton("+")
btn_spending = KeyboardButton("-")
btn_show_income = KeyboardButton("Переглянути доходи")
btn_show_spending = KeyboardButton("Переглянути витрати")

btn_add = KeyboardButton("Додати")
btn_remove = KeyboardButton("Видалити")

btn_new = KeyboardButton("Додати новий запис")
btn_menu = KeyboardButton("Меню")
btn_back = KeyboardButton("Назад")
btn_forward = KeyboardButton("->")

btn_statistic = KeyboardButton("Статистика")
btn_week = KeyboardButton("Тиждень")
btn_month = KeyboardButton("Місяць")
btn_previous_month = KeyboardButton("Попередній місяць")
btn_year = KeyboardButton("Рік")

btn_add_category = KeyboardButton("Додати категорію")
btn_remove_category = KeyboardButton("Видалити категорію")
btn_show_category = KeyboardButton("Переглянути категорії")


# ----------------------------------------------------------------------------------------------------------------------
# ReplyKeyboardMarkup
# ----------------------------------------------------------------------------------------------------------------------

main_menu = ReplyKeyboardMarkup(
    [[btn_new], [btn_menu]],
    resize_keyboard=True
)
menu_spending_income = ReplyKeyboardMarkup(
    [[btn_spending, btn_income], [btn_back]],
    resize_keyboard=True
)
menu = ReplyKeyboardMarkup(
    [[btn_show_spending, btn_show_income], [btn_statistic], [btn_show_category], [btn_back]],
    resize_keyboard=True
)
menu_show_spending = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_forward], [btn_remove, btn_back, btn_add]],
    resize_keyboard=True
)
menu_show_income = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_forward], [btn_remove, btn_back, btn_add]],
    resize_keyboard=True
)
menu_show_statistic = ReplyKeyboardMarkup(
    [[btn_week, btn_month, btn_year], [btn_back]],
    resize_keyboard=True
)
menu_show_category = ReplyKeyboardMarkup(
    [[btn_add_category], [btn_remove_category], [btn_back]],
    resize_keyboard=True
)
menu_btn_back = ReplyKeyboardMarkup(
    [[btn_back]],
    resize_keyboard=True
)
