from telegram import ReplyKeyboardMarkup, KeyboardButton

# ----------------------------------------------------------------------------------------------------------------------
# Buttons
# ----------------------------------------------------------------------------------------------------------------------
buttons = [
    "+", "-", "Переглянути доходи", "Переглянути витрати", "Додати", "Видалити", "Перейти на головну сторінку",
    "Додати новий запис", "Меню", "Назад", "->", "Статистика", "Тиждень", "Місяць", "Попередній місяць", "Рік",
    "Додати категорію", "Видалити категорію", "Переглянути категорії"
]

btn_incomes = KeyboardButton("+")
btn_expenses = KeyboardButton("-")
btn_show_incomes = KeyboardButton("Переглянути доходи")
btn_show_expenses = KeyboardButton("Переглянути витрати")

btn_add = KeyboardButton("Додати")
btn_remove = KeyboardButton("Видалити")

btn_home = KeyboardButton("Перейти на головну сторінку")
btn_new = KeyboardButton("Додати новий запис")
btn_menu = KeyboardButton("Меню")
btn_back = KeyboardButton("Назад")
btn_forward = KeyboardButton("→")

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

home = ReplyKeyboardMarkup(
    [[btn_new], [btn_menu]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_expenses_incomes = ReplyKeyboardMarkup(
    [[btn_expenses, btn_incomes], [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu = ReplyKeyboardMarkup(
    [[btn_show_expenses, btn_show_incomes], [btn_statistic], [btn_show_category], [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_expenses = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_forward], [btn_remove, btn_back, btn_add]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_incomes = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_forward], [btn_remove, btn_back, btn_add]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_statistic = ReplyKeyboardMarkup(
    [[btn_week, btn_month, btn_year], [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_category = ReplyKeyboardMarkup(
    [[btn_add_category], [btn_remove_category], [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_btn_back = ReplyKeyboardMarkup(
    [[btn_back]],
    resize_keyboard=True, is_persistent=True
)
menu_incomes_expenses = ReplyKeyboardMarkup(
    [[btn_incomes, btn_expenses], [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_new_category = ReplyKeyboardMarkup(
    [[btn_add_category], [btn_home]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
