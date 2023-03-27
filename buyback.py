from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext

from database import get_product_by_article, create_buyback

BUYBACK_ARTICLE, BUYBACK_PRICE, BUYBACK_PAYMENT_TYPE, BUYBACK_REVIEW = range(4)

def buyback_article(update: Update, context: CallbackContext):
    article = update.message.text
    product = get_product_by_article(article)

    if product:
        context.user_data['product'] = product
        reply_keyboard = [['Отмена']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(f"Введите цену скупки:", reply_markup=markup)
        return BUYBACK_PRICE
    else:
        update.message.reply_text("Товар не найден. Попробуйте еще раз или введите /cancel для отмены.")
        return BUYBACK_ARTICLE

def buyback_price(update: Update, context: CallbackContext):
    price = float(update.message.text)
    context.user_data['price'] = price

    reply_keyboard = [['Наличные', 'Безналичные'], ['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f"Выберите тип оплаты:", reply_markup=markup)
    return BUYBACK_PAYMENT_TYPE

def buyback_payment_type(update: Update, context: CallbackContext):
    payment_type = update.message.text
    context.user_data['payment_type'] = payment_type

    product = context.user_data['product']
    price = context.user_data['price']

    reply_keyboard = [['Подтвердить'], ['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f"Проверьте информацию о скупке:\n\n"
                              f"Товар: {product.name}\n"
                              f"Цена скупки: {price}\n"
                              f"Тип оплаты: {payment_type}\n\n"
                              f"Подтвердите скупку или отмените:", reply_markup=markup)
    return BUYBACK_REVIEW

def buyback_confirm(update: Update, context: CallbackContext):
    product = context.user_data['product']
    price = context.user_data['price']
    payment_type = context.user_data['payment_type']

    create_buyback(product.article, price, payment_type)

    update.message.reply_text("Скупка успешно завершена!")
    return ConversationHandler.END

def buyback_cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text('Скупка отменена.')
    return ConversationHandler.END

# Здесь добавьте остальные функции обработчиков для каждого шага
