from telegram import ReplyKeyboardMarkup, KeyboardButton

# ----------------------------------------------------------------------------------------------------------------------
# Buttons
# ----------------------------------------------------------------------------------------------------------------------

month_name = {
    "01": "Січень", "02": "Лютий", "03": "Березень", "04": "Квітень", "05": "Травень", "06": "Червень",
    "07": "Липень", "08": "Серпень", "09": "Вересень", "10": "Жовтень", "11": "Листопад", "12": "Грудень"
}

btn_incomes = KeyboardButton("+")
btn_expenses = KeyboardButton("-")
btn_other_day = KeyboardButton("Обрати інший день")

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
btn_year = KeyboardButton("Рік")
btn_previous_week = KeyboardButton("Попередній тиждень")
btn_previous_month = KeyboardButton("Попередній місяць")
btn_previous_year = KeyboardButton("Попередній рік")

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
menu_incomes_expenses = ReplyKeyboardMarkup(
    [[btn_incomes, btn_expenses], [btn_other_day],  [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu = ReplyKeyboardMarkup(
    [[btn_show_expenses, btn_show_incomes], [btn_statistic], [btn_show_category], [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_expenses_1 = ReplyKeyboardMarkup(
    [[btn_previous_month], [btn_remove, btn_menu, btn_add]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_expenses_2 = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_forward], [btn_remove, btn_menu, btn_add]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_incomes_1 = ReplyKeyboardMarkup(
    [[btn_previous_month], [btn_remove, btn_menu, btn_add]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_incomes_2 = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_forward], [btn_remove, btn_menu, btn_add]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_show_statistic_week_1 = ReplyKeyboardMarkup(
    [[btn_previous_week, btn_month], [btn_menu]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Статистика за тиждень"
)
menu_show_statistic_week_2 = ReplyKeyboardMarkup(
    [[btn_previous_week, btn_forward], [btn_menu, btn_month]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Статистика за тиждень"
)
menu_show_statistic_month_1 = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_year], [btn_menu]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Статистика за місяць"
)
menu_show_statistic_month_2 = ReplyKeyboardMarkup(
    [[btn_previous_month, btn_forward], [btn_menu, btn_year]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Статистика за місяць"
)
menu_show_statistic_year_1 = ReplyKeyboardMarkup(
    [[btn_previous_year, btn_week], [btn_menu]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Статистика за рік"
)
menu_show_statistic_year_2 = ReplyKeyboardMarkup(
    [[btn_previous_year, btn_forward], [btn_menu, btn_week]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Статистика за рік"
)
menu_show_category = ReplyKeyboardMarkup(
    [[btn_add_category], [btn_remove_category], [btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
menu_btn_back = ReplyKeyboardMarkup(
    [[btn_back]],
    resize_keyboard=True, is_persistent=True
)
menu_btn_back_date_1 = ReplyKeyboardMarkup(
    [[btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="DD.MM.YYYY"
)
menu_btn_back_date_2 = ReplyKeyboardMarkup(
    [[btn_back]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="DD.MM №"
)
menu_new_category = ReplyKeyboardMarkup(
    [[btn_add_category], [btn_home]],
    resize_keyboard=True, is_persistent=True, input_field_placeholder="Оберіть параметр"
)
