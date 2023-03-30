from telebot import types

# Create a function to generate the appropriate buttons for the cashier's functionality
def create_cashier_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_sales = types.KeyboardButton("Продажа")
    button_refunds = types.KeyboardButton("Возврат")
    button_trade_in = types.KeyboardButton("Trade-In")
    button_purchases = types.KeyboardButton("Скупка")
    keyboard.add(button_sales, button_refunds, button_trade_in, button_purchases)
    return keyboard

# Create a function to generate the appropriate buttons for the admin's functionality
def create_admin_buttons():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_sales = types.KeyboardButton("Продажа")
    button_refunds = types.KeyboardButton("Возврат")
    button_trade_in = types.KeyboardButton("Trade-In")
    button_purchases = types.KeyboardButton("Скупка")
    button_product_cards = types.KeyboardButton("Добавить товар")
    button_reports = types.KeyboardButton("Отчеты")
    button_access_rights = types.KeyboardButton("Права")
    button_inventory_count = types.KeyboardButton("Ревизия")
    keyboard.add(button_sales, button_refunds, button_trade_in, button_purchases)
    keyboard.add(button_product_cards, button_reports, button_access_rights, button_inventory_count)
    return keyboard
