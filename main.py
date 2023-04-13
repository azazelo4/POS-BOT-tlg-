import telebot
from telebot import types
from config import TOKEN
from auth import authorize_user
from buttons import *
from sale import *
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

        bot.send_message(chat_id, f"Здравствуйте, {user_data_dict['name']}! Вы авторизованы как {user_data_dict['role']}. для справки введите команду /help", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Номер телефона не найден. Пожалуйста, зарегистрируйтесь.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    Доступные команды:
    /start - начать диалог с ботом, запросить номер телефона для авторизации
    /help - отобразить список доступных команд

    Для кассиров:
    Продажа - начать процесс продажи товара (введите артикул (12345678), сумму продажи и выберите тип оплаты)

    Для администраторов:
    (список команд администратора, если есть)
    """

    bot.send_message(message.chat.id, help_text)


def get_keyboard_by_role(chat_id):
    role = user_data[chat_id]['role']
    if role == 'cashier':
        return create_cashier_buttons()
    elif role == 'admin':
        return create_admin_buttons()
    else:
        return None

#Sale function 
sale = None

@bot.message_handler(func=lambda message: sale is None and message.text == 'Продажа')
def start_sale(message):
    global sale
    sale = Sale()
    bot.send_message(message.chat.id, 'Введите артикул:')


@bot.message_handler(func=lambda message: sale is not None and sale.state == WAITING_ARTICLE)
def process_article(message):
    response = sale.process_step(message, user_data)
    if isinstance(response, tuple):
        text, keyboard = response
        bot.send_message(message.chat.id, text, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: sale is not None and sale.state == WAITING_SALE_PRICE)
def process_sale_price(message):
    response, keyboard = sale.process_step(message, user_data)
    if response is None:
        sale.reset()
        sale = None
        bot.send_message(message.chat.id, "Продажа отменена.")
    else:
        bot.send_message(message.chat.id, response, reply_markup=keyboard)


@bot.message_handler(func=lambda message: sale is not None and sale.state == WAITING_PAYMENT_TYPE)
def process_payment_type(message):
    response, keyboard = sale.process_step(message)
    bot.send_message(message.chat.id, response, reply_markup=keyboard)


@bot.message_handler(func=lambda message: sale is not None and sale.state == CONFIRM_SALE)
def confirm_sale(message):
    global sale
    response = sale.process_step(message)
    bot.send_message(message.chat.id, response)
    sale = None

@bot.message_handler(func=lambda message: sale is not None and message.text == 'Отмена')
def cancel_sale(message):
    global sale
    sale.reset()
    sale = None
    keyboard = get_keyboard_by_role(message.chat.id)
    bot.send_message(message.chat.id, "Продажа отменена.", reply_markup=keyboard)

@bot.message_handler(func=lambda message: sale is not None and sale.state == CONFIRM_SALE)
def confirm_sale(message):
    global sale
    response = sale.process_step(message, user_data)
    sale = None
    keyboard = get_keyboard_by_role(message.chat.id)
    bot.send_message(message.chat.id, response, reply_markup=keyboard)


#

if __name__ == '__main__':
    bot.polling(none_stop=True)