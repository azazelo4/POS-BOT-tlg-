from telebot import types
from database import get_product_by_article, get_min_price, record_sale
from main import user_data

# Состояния
WAITING_ARTICLE, WAITING_SALE_PRICE, WAITING_PAYMENT_TYPE, CONFIRM_SALE = range(4)

# Конечный автомат
class Sale:
    def __init__(self):
        self.state = WAITING_ARTICLE
        self.article = None
        self.sale_price = None
        self.payment_type = None
        self.product = None
        self.min_price = None

    def process_step(self, message, user_data):
        keyboard = None
        response = ""
        if message.text == 'Отмена':
            return None, None
        if self.state == WAITING_ARTICLE:
            self.article = message.text
            self.product = get_product_by_article(self.article)
            if self.product:
                product = {
                    
                }
                self.min_price = get_min_price(self.product)
                response = f"Артикул найден. Минимальная цена: {self.min_price}\nВведите сумму продажи:"
                self.next_step()
            else:
                response = "Артикул не найден. Пожалуйста, введите корректный артикул."
            return response

        elif self.state == WAITING_SALE_PRICE:
            self.sale_price = int(message.text)
            if self.sale_price >= self.min_price:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                button_cash = types.KeyboardButton("Нал")
                button_non_cash = types.KeyboardButton("Безнал")
                keyboard.add(button_cash, button_non_cash)
                response = "Выберите тип расчета:"
                self.next_step()
            elif message.text == 'Отмена':
                return None, None
            else:
                response = f"Сумма продажи не может быть меньше минимальной цены ({self.min_price}). Введите корректную сумму продажи."
            return response, keyboard

        elif self.state == WAITING_PAYMENT_TYPE:
            self.payment_type = message.text
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_confirm = types.KeyboardButton("Подтвердить")
            button_cancel = types.KeyboardButton("Отменить")
            keyboard.add(button_confirm, button_cancel)
            response = f"Артикул: {self.article}\nСумма продажи: {self.sale_price}\nТип расчета: {self.payment_type}\nПодтвердить или отменить?"
            self.next_step()
            return response, keyboard

        elif self.state == CONFIRM_SALE:
            if message.text == "Подтвердить":
                user_id = user_data[message.chat.id]['id']
                store_id = user_data[message.chat.id]['store_id']
                record_sale(self.product['id'], store_id, user_id, self.sale_price)
                self.reset()
                response = "Продажа подтверждена."
            else:
                self.reset()
                response = "Продажа отменена."
        return response



    def next_step(self):
        self.state = (self.state + 1) % 4

    def reset(self):
        self.state = None
        self.article = None
        self.sale_price = None
        self.payment_type = None
        self.product = None
        self.min_price = None
