from aiogram import types


def main_button_personal():
    markup = types.ReplyKeyboardMarkup(keyboard=[],
                                       resize_keyboard=True)
    btn = types.KeyboardButton(text='Отправить отчет')
    markup.keyboard.append([btn])
    return markup


def choice_ident_buttons(ident_list):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    for ident in ident_list:
        btn = types.InlineKeyboardButton(text=f'{ident}',
                                         callback_data=f'Отчет:{ident}')
        markup.inline_keyboard.append([btn])
    return markup


def report_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Электричество', callback_data='Электричество')
    btn2 = types.InlineKeyboardButton(text='Вода', callback_data='Воду')
    markup.inline_keyboard.append([btn1, btn2])
    return markup
