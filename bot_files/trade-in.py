from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext

from database import get_product_by_article, update_product_stock, create_trade_in

TRADE_IN_OLD_ARTICLE, TRADE_IN_NEW_ARTICLE, TRADE_IN_DIFFERENCE, TRADE_IN_REVIEW = range(4)

def trade_in_old_article(update: Update, context: CallbackContext):
    old_article = update.message.text
    old_product = get_product_by_article(old_article)

    if old_product:
        context.user_data['old_product'] = old_product
        reply_keyboard = [['Отмена']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(f"Введите артикул нового товара:", reply_markup=markup)
        return TRADE_IN_NEW_ARTICLE
    else:
        update.message.reply_text("Товар не найден. Попробуйте еще раз или введите /cancel для отмены.")
        return TRADE_IN_OLD_ARTICLE

def trade_in_new_article(update: Update, context: CallbackContext):
    new_article = update.message.text
    new_product = get_product_by_article(new_article)

    if new_product:
        context.user_data['new_product'] = new_product
        reply_keyboard = [['Отмена']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(f"Введите разницу в цене:", reply_markup=markup)
        return TRADE_IN_DIFFERENCE
    else:
        update.message.reply_text("Товар не найден. Попробуйте еще раз или введите /cancel для отмены.")
        return TRADE_IN_NEW_ARTICLE

def trade_in_difference(update: Update, context: CallbackContext):
    difference = float(update.message.text)
    context.user_data['difference'] = difference

    old_product = context.user_data['old_product']
    new_product = context.user_data['new_product']

    reply_keyboard = [['Подтвердить'], ['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(f"Проверьте информацию об обмене:\n\n"
                              f"Старый товар: {old_product.name}\n"
                              f"Новый товар: {new_product.name}\n"
                              f"Разница в цене: {difference}\n\n"
                              f"Подтвердите обмен или отмените:", reply_markup=markup)
    return TRADE_IN_REVIEW

def trade_in_confirm(update: Update, context: CallbackContext):
    old_product = context.user_data['old_product']
    new_product = context.user_data['new_product']
    difference = context.user_data['difference']

    create_trade_in(old_product.article, new_product.article, difference)
    update_product_stock(old_product.article, 1)
    update_product_stock(new_product.article, -1)

    update.message.reply_text("Обмен успешно завершен!")
    return ConversationHandler.END

def trade_in_cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    update.message.reply_text('Обмен отменен.')
    return ConversationHandler.END

# Здесь добавьте остальные функции обработчиков для каждого шага
