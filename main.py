import telebot
from telebot import types
from config import TOKEN
from auth import authorize_user
from buttons import *
from sale import Sale
from commands import *
from database import *

bot = telebot.TeleBot(TOKEN)

sale_handler = {}
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_phone = telebot.types.KeyboardButton(text="Поделиться номером", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, "Пожалуйста, поделитесь своим номером телефона для авторизации:", reply_markup=keyboard)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone_number = message.contact.phone_number
    user_data_dict = authorize_user(phone_number)

    if user_data_dict:
        chat_id = message.chat.id
        user_data[chat_id] = user_data_dict

        if user_data_dict['role'] == 'cashier':
            keyboard = create_cashier_buttons()
        elif user_data_dict['role'] == 'admin':
            keyboard = create_admin_buttons()

        bot.send_message(chat_id, f"Здравствуйте, {user_data_dict['name']}! Вы авторизованы как {user_data_dict['role']}.", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Номер телефона не найден. Пожалуйста, зарегистрируйтесь.")



@bot.message_handler(func=lambda message: message.text == "Продажа")
def sale(message):
    chat_id = message.chat.id
    sale_handler[chat_id] = Sale()
    user_role = user_data.get(chat_id, {}).get('role')
    if user_role == 'cashier' or user_role == 'admin':
        bot.send_message(chat_id, "Введите артикул товара:")
    else:
        bot.send_message(chat_id, "У вас нет прав для выполнения этой операции.")

@bot.message_handler(func=lambda message: message.chat.id in sale_handler)
def process_sale(message):
    chat_id = message.chat.id
    sale = sale_handler[chat_id]
    response, keyboard = sale.process_step(message), None

    if keyboard:
        bot.send_message(chat_id, response, reply_markup=keyboard)
    else:
        bot.send_message(chat_id, response)

    if sale.state == CONFIRM_SALE:
        user_id = user_data[chat_id]['id']
        store_id = user_data[chat_id]['store_id']
        response = sale.confirm_sale(user_id, store_id)
        bot.send_message(chat_id, response, reply_markup=create_buttons(user_data[chat_id]['role']))
    del sale_handler[chat_id]
    sale.next_step()

@bot.message_handler(func=lambda message: message.text == "Отменить")
def cancel_sale(message):
    chat_id = message.chat.id
    if chat_id in sale_handler:
        sale = sale_handler[chat_id]
        response = sale.cancel_sale()
        bot.send_message(chat_id, response, reply_markup=create_buttons(user_data[chat_id]['role']))
    del sale_handler[chat_id]

# Обработчик команд

if __name__ == '__main__':
    bot.polling(none_stop=True)