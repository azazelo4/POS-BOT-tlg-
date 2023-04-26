import telebot
from telebot import types
from config import TOKEN
from auth import authorize_user
from buttons import *
from sale import *
from database import *
from report import *


bot = telebot.TeleBot(TOKEN)

sale_handler = {}
user_data = {}
report_handler = {}

#################----------- START -----------#################
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_phone = telebot.types.KeyboardButton(text="Поделиться номером", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(chat_id, "Пожалуйста, поделитесь своим номером телефона для авторизации:", reply_markup=keyboard)

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
        bot.send_message(chat_id, "Номер телефона не найден. Пожалуйста, обратитесь к администратору.")

def get_keyboard_by_role(chat_id):
    role = user_data[chat_id]['role']
    if role == 'cashier':
        return create_cashier_buttons()
    elif role == 'admin':
        return create_admin_buttons()
    else:
        return None
#################----------- HELP -----------#################
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    Бот в разработке и все здесь только для тестирования
    Доступные команды:
    /start - начать диалог с ботом, запросить номер телефона для авторизации
    /help - отобразить список доступных команд

    Как работать:
    Продажа - начать процесс продажи товара 
    введите тестовый артикул 12345678 или 2-1234, 
    сумму продажи 
    выберите тип оплаты - нал или безнал
    поттвердите продажу выбором потвердить или отменить

    можно нажать отмена на любом шаге.

    Для администраторов:
    (в разработке)
    """

    bot.send_message(message.chat.id, help_text)

#################----------- Sale Function -----------#################
@bot.message_handler(func=lambda message: sale_handler.get(message.chat.id) is None and message.text == 'Продажа')
def start_sale(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        sale_handler[chat_id] = Sale(user_data[chat_id])
        bot.send_message(chat_id, "Введите артикул товара:")
    else:
        bot.send_message(chat_id, "Вы не авторизованы. Пожалуйста, поделитесь своим номером телефона для авторизации, введя команду /start.")
    
def process_sale_step(message, chat_id, user_data):
    sale = sale_handler.get(chat_id, None)
    chat_id = message.chat.id
    result = sale.process_step(message, user_data)
    if result is None or (sale.state == SaleState.WAITING_ARTICLE and result == "Продажа подтверждена."):
        sale.reset()
        del sale_handler[chat_id]
        keyboard = get_keyboard_by_role(chat_id)
        bot.send_message(chat_id, "Операция отменена." if result is None else result, reply_markup=keyboard)
    else:
        if isinstance(result, tuple):
            response, keyboard = result
        else:
            response, keyboard = result, get_keyboard_by_role(chat_id)
        bot.send_document(chat_id, open('report.xlsx', 'rb'))


@bot.message_handler(func=lambda message: sale_handler.get(message.chat.id) is not None and sale_handler[message.chat.id].state == SaleState.WAITING_ARTICLE)
def process_article(message):
    chat_id = message.chat.id
    process_sale_step(message, chat_id, user_data.get(chat_id))

@bot.message_handler(func=lambda message: sale_handler.get(message.chat.id) is not None and sale_handler[message.chat.id].state == SaleState.WAITING_SALE_PRICE)
def process_sale_price(message):
    chat_id = message.chat.id
    process_sale_step(message, chat_id, user_data.get(chat_id))

@bot.message_handler(func=lambda message: sale_handler.get(message.chat.id) is not None and sale_handler[message.chat.id].state == SaleState.WAITING_PAYMENT_TYPE)
def process_payment_type(message):
    chat_id = message.chat.id
    process_sale_step(message, chat_id, user_data.get(chat_id))

@bot.message_handler(func=lambda message: sale_handler.get(message.chat.id) is not None and sale_handler[message.chat.id].state == SaleState.CONFIRM_SALE)
def confirm_sale(message):
    chat_id = message.chat.id
    process_sale_step(message, chat_id, user_data.get(chat_id))

#################----------- Report Function -----------#################
@bot.message_handler(func=lambda message: report_handler.get(message.chat.id) is None and message.text == 'Отчеты')
def start_report(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        report_handler[chat_id] = Report(user_data[chat_id])
        bot.send_message(chat_id, "Выберите тип отчета:")
    else:
        bot.send_message(chat_id, "Вы не авторизованы. Пожалуйста, поделитесь своим номером телефона для авторизации, введя команду /start.")

def process_report_step(message, chat_id, user_data):
    report = report_handler.get(chat_id, None)
    chat_id = message.chat.id
    result = report.process_report_step(message, user_data)
    if result is None or (report.state == ReportState.WAITING_TYPE and result == "Отчет готов."):
        report.reset()
        del report_handler[chat_id]
        keyboard = get_keyboard_by_role(chat_id)
        bot.send_message(chat_id, "Операция отменена." if result is None else result, reply_markup=keyboard)
    else:
        if isinstance(result, tuple):
            response, keyboard = result
        else:
            response, keyboard = result, get_keyboard_by_role(chat_id)
        bot.send_message(chat_id, response, reply_markup=keyboard)

@bot.message_handler(func=lambda message: report_handler.get(message.chat.id) is not None and report_handler[message.chat.id].state == ReportState.WAITING_TYPE)
def process_type(message):
    chat_id = message.chat.id
    process_report_step(message, chat_id, user_data.get(chat_id))

@bot.message_handler(func=lambda message: report_handler.get(message.chat.id) is not None and report_handler[message.chat.id].state == ReportState.WAITING_START_DATE)
def process_start_date(message):
    chat_id = message.chat.id
    process_report_step(message, chat_id, user_data.get(chat_id))

@bot.message_handler(func=lambda message: report_handler.get(message.chat.id) is not None and report_handler[message.chat.id].state == ReportState.WAITING_END_DATE)
def process_end_date(message):
    chat_id = message.chat.id
    process_report_step(message, chat_id, user_data.get(chat_id))
#################----------- END -----------#################

if __name__ == '__main__':
    bot.polling(none_stop=True)