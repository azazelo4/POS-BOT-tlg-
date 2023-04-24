from enum import Enum
from telebot import types
from database import get_product_by_article, get_min_price, record_sale
from main import user_data

class SaleState(Enum):
    WAITING_ARTICLE = 1
    WAITING_SALE_PRICE = 2
    WAITING_PAYMENT_TYPE = 3
    CONFIRM_SALE = 4

class Sale:
    def __init__(self, user_data):
        self.state = SaleState.WAITING_ARTICLE
        self.article = None
        self.sale_price = None
        self.payment_type = None
        self.product = None
        self.min_price = None
        self.user_data = user_data

    def process_waiting_article(self, message, user_data):
        if message.text == 'Отмена':
            self.reset()
            return None
        else:
            self.article = message.text
            try:
                self.product = get_product_by_article(self.article)
                if self.product:
                    self.min_price = self.product['min_price']
                    response = f"Артикул найден.\n Изделие: {self.product['product_type']}.\n Цена: {self.product['price']}\n Минимальная цена: {self.product['min_price']}\nВведите сумму продажи:"
                    self.state = SaleState.WAITING_SALE_PRICE
                else:
                    response = "Артикул не найден. Пожалуйста, введите корректный артикул."
            except:
                response = "Произошла ошибка. Попробуйте еще раз."
        return response


    def process_waiting_sale_price(self, message, user_data):
        if message.text == 'Отмена':
            self.reset()
            return None, None
        else:
            try:
                self.sale_price = int(message.text)
            except ValueError:
                return "Пожалуйста, введите корректное числовое значение суммы продажи.", None

            if self.sale_price >= self.min_price:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_cash = types.KeyboardButton("Нал")
                button_non_cash = types.KeyboardButton("Безнал")
                button_cancel = types.KeyboardButton("Отмена")
                keyboard.add(button_cash, button_non_cash, button_cancel)
                response = "Выберите тип расчета:"
                self.state = SaleState.WAITING_PAYMENT_TYPE
            else:
                response = f"Сумма продажи не может быть меньше минимальной цены ({self.min_price}). Введите корректную сумму продажи."
                keyboard = None
            return response, keyboard

    def process_waiting_payment_type(self, message, user_data):
        if message.text == 'Отмена':
            self.reset()
            return None, None
        else:
            self.payment_type = message.text
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_confirm = types.KeyboardButton("Подтвердить")
            button_cancel = types.KeyboardButton("Отменить")
            keyboard.add(button_confirm, button_cancel)
            response = f"Артикул: {self.article}\nСумма продажи: {self.sale_price}\nТип расчета: {self.payment_type}\nПодтвердить или отменить?"
            self.state = SaleState.CONFIRM_SALE
        return response, keyboard

    
    def process_confirm_sale(self, message, user_id):
        user_id = self.user_data.get('id', None)
        if user_id is not None:
            if message.text == "Подтвердить":
                store_id = self.user_data.get('store_id')
                record_sale(self.product['id'], store_id, user_id, self.sale_price)
                self.reset()
                response = "Продажа подтверждена."
            else:
                self.reset()
                response = "Продажа отменена."
        else:
            response = "Ошибка: пользователь не авторизован."
        return response

    def process_step(self, message, user_data):
        if self.state == SaleState.WAITING_ARTICLE:
            return self.process_waiting_article(message, user_data)
        elif self.state == SaleState.WAITING_SALE_PRICE:
            return self.process_waiting_sale_price(message, user_data)
        elif self.state == SaleState.WAITING_PAYMENT_TYPE:
            return self.process_waiting_payment_type(message, user_data)
        elif self.state == SaleState.CONFIRM_SALE:
            return self.process_confirm_sale(message, user_data)

    def reset(self):
        self.state = SaleState.WAITING_ARTICLE
        self.article = None
        self.sale_price = None
        self.payment_type = None
        self.product = None
        self.min_price = None
