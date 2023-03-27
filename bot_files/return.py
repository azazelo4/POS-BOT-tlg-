from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext

from database import get_product_by_order_id, update_product_stock, create_return

RETURN_ORDER_ID, RETURN_PRICE, RETURN_PAYMENT_TYPE, RETURN_REVIEW = range(4)

def return_order_id(update: Update, context: CallbackContext):
    order_id = update.message.text
    product = get_product_by_order_id(order_id)

    if product:
        context.user_data['product'] = product
        context.user_data['order_id'] = order_id
        reply_keyboard = [['Отмена']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(f"Введите сумму возврата:", reply_markup=markup)
        return RETURN_PRICE
    else:
        update.message.reply_text("Заказ не найден. Попробуйте еще раз или введите /cancel для отмены.")
        return RETURN_ORDER_ID

def return_price(update: Update, context: CallbackContext):
    price = float(update.message.text)
    context.user_data['price'] = price
    reply_keyboard = [['Наличные', 'Безналичные'], ['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Выберите тип оплаты:", reply_markup=markup)
    return RETURN_PAYMENT_TYPE

def return_payment_type(update: Update, context: CallbackContext):
    payment_type = update.message.text
    context.user_data['payment_type'] = payment_type

    product = context.user_data['product']
    price = context.user_data['price']

    reply_keyboard = [['Подтвердить'], ['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f"Проверьте информацию о возврате:\n\n"
                              f"ID заказа: {product.order_id}\n"
                              f"Название: {product.name}\n"
                              f"Цена: {price}\n"
                              f"Тип оплаты: {payment_type}\n\n"
                              f"Подтвердите возврат или отмените:", reply_markup=markup)
    return RETURN_REVIEW

def return_confirm(update: Update, context: CallbackContext):
    product = context.user_data['product']
    price = context.user_data['price']
    payment_type = context.user_data['payment_type']

    create_return(product.order_id, price, payment_type)
    update_product_stock(product.article, 1)

    update.message.reply_text("Возврат успешно завершен!")
    return ConversationHandler.END

def return_cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text('Возврат отменен.')
    return ConversationHandler.END

# Здесь добавьте остальные функции обработчиков для каждого шага
