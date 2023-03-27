from telebot import types
from database import get_user_by_phone
from sale import Sale, WAITING_ARTICLE, WAITING_SALE_PRICE, WAITING_PAYMENT_TYPE, CONFIRM_SALE

# Создание клавиатуры с кнопками в зависимости от роли пользователя
def create_buttons(user_role):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Общие кнопки для кассиров и администраторов
    button_sale = types.KeyboardButton("Продажа")
    button_return = types.KeyboardButton("Возврат")
    button_reports = types.KeyboardButton("Отчеты")

    keyboard.add(button_sale, button_return, button_reports)

    # Кнопки только для администраторов
    if user_role == 'админ':
        button_add_product = types.KeyboardButton("Добавить товар")
        button_users_rights = types.KeyboardButton("Права кассиров")
        button_stock_taking = types.KeyboardButton("Ревизия")
        keyboard.add(button_add_product)
        keyboard.add(button_users_rights, button_stock_taking)

    return keyboard

# Функция для обработки команды /start
def start_command(bot, message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Поделиться номером", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, "Пожалуйста, поделитесь своим номером телефона для авторизации:", reply_markup=keyboard)

# Функция для обработки контакта пользователя
def handle_contact(bot, message, user_data):
    phone_number = message.contact.phone_number
    user_info = get_user_by_phone(phone_number)

    if user_info:
        user_role = user_info[0]
        bot.send_message(message.chat.id, f"Добро пожаловать, {user_role}!")
        keyboard = create_buttons(user_role)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)

        user_data[message.chat.id] = {
            'role': user_role,
            'id': get_user_by_phone(phone_number)[0]  # Предполагая, что 'id' - это первое поле в таблице 'users'
        }
    else:
        bot.send_message(message.chat.id, "Извините, ваш номер телефона не найден.")

# Функция для обработки команды /sales
def sales_command(bot, message, sale_handler, user_data):
    chat_id = message.chat.id
    sale_handler[chat_id] = Sale()
    user_role = user_data[chat_id]['role']

    if user_role == 'кассир' or user_role == 'админ':
        bot.send_message(chat_id, "Введите артикул товара:")
    else:
        bot.send_message(chat_id, "У вас нет прав для выполнения этой операции.")

# Функция для обработки сообщений, связанных с продажей
def process_sale_message(bot, message, sale_handler, user_data):
    chat_id = message.chat.id
    sale = sale_handler[chat_id]
    response, keyboard = sale.process_step(message)

    if keyboard:
        bot.send_message(chat_id, response, reply_markup=keyboard)
    else:
        bot.send_message
