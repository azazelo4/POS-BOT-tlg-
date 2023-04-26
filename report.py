from enum import Enum
import datetime
from database import generate_report
from telebot import types
import openpyxl

class ReportState(Enum):
    WAITING_TYPE = 1
    WAITING_START_DATE = 2
    WAITING_END_DATE = 3

class Report:
    def __init__(self, user_data):
        self.state = ReportState.WAITING_TYPE
        self.user_data = user_data
        self.today = datetime.date.today()
        self.start_date = None
        self.end_date = None

    def process_waiting_type(self, message, user_data):
        if message.text == 'Отмена':
            self.reset()
            return None
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_daily = types.KeyboardButton("Ежедневный")
            button_weekly = types.KeyboardButton("Еженедельный")
            button_monthly = types.KeyboardButton("Ежемесячный")
            button_custom = types.KeyboardButton("Другой")
            button_cancel = types.KeyboardButton("Отмена")
            keyboard.add(button_daily, button_weekly, button_monthly, button_custom, button_cancel)
            if message.text == "Ежедневный":
                start_date = self.today - datetime.timedelta(days=1)
                end_date = self.today
                report_data = generate_report(start_date, end_date)
                wb = self.generate_excel_report(report_data)
                wb.seek(0)
                response = "Отчет готов."
                bot.send_document(self.user_data['chat_id'], io.BytesIO(wb.read()), filename='report.xlsx')

            elif message.text == "Еженедельный":
                start_date = self.today - datetime.timedelta(days=7)
                end_date = self.today
                report_data = generate_report(start_date, end_date)
                response = "Отчет готов."
            elif message.text == "Ежемесячный":
                start_date = self.today - datetime.timedelta(days=30)
                end_date = self.today
                report_data = generate_report(start_date, end_date)
                response = "Отчет готов."
            elif message.text == "Другой":
                self.state = ReportState.WAITING_START_DATE
                self.start_date = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
                return "введите период отчета в формате ГГГГ-ММ-ДД:"
        return response, keyboard
                
    def process_waiting_start_date(self, message, user_data):
        try:
            self.start_date = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
            self.state = ReportState.WAITING_END_DATE
            return "Введите дату окончания отчета в формате ГГГГ-ММ-ДД"
        except ValueError:
            return "Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД"

    def process_waiting_end_date(self, message, user_data):
        try:
            self.end_date = datetime.datetime.strptime(message.text, "%Y-%m-%d").date()
            report_data = generate_report(self.start_date, self.end_date)
            response = "Отчет готов."
            self.reset()
            return report_data, None, response
        except ValueError:
            return "техническая ошибка"
        
    def generate_excel_report(self, chat_id, report_data):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet['A1'] = 'Название товара'
        sheet['B1'] = 'Продавец'
        sheet['C1'] = 'Магазин'
        sheet['D1'] = 'Сумма продаж'
        sheet['E1'] = 'Дата продажи'
        sheet['F1'] = 'Тип расчета'
        for i, row in enumerate(report_data):
            sheet.cell(row=i+2, column=1).value = row[0]
            sheet.cell(row=i+2, column=2).value = row[1]
            sheet.cell(row=i+2, column=3).value = row[2]
            sheet.cell(row=i+2, column=4).value = row[3]
            sheet.cell(row=i+2, column=5).value = row[4].strftime('%d.%m.%Y')
            sheet.cell(row=i+2, column=6).value = row[5]
        wb.save('report.xlsx')

    def reset(self):
        self.state = ReportState.WAITING_TYPE
        self.start_date = None
        self.end_date = None
        return None

    def process_report_step(self, message, user_data):
        if self.state == ReportState.WAITING_TYPE:
            return self.process_waiting_type(message, user_data)
        elif self.state == ReportState.WAITING_START_DATE:
            return self.process_waiting_start_date(message, user_data)
        elif self.state == ReportState.WAITING_END_DATE:
            return self.process_waiting_end_date(message, user_data)