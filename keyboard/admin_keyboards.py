from aiogram import types


def main_admin_buttons():
    markup = types.ReplyKeyboardMarkup(keyboard=[],
                                       resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Выдать токен 📱')
    btn2 = types.KeyboardButton(text='Изменить время 🕑')
    markup.keyboard.append([btn1,
                            btn2])
    btn3 = types.KeyboardButton(text='Создать рассылку 🧑‍💻')
    btn4 = types.KeyboardButton(text='Добавить объект сотруднику 🚶')
    markup.keyboard.append([btn3,
                            btn4])
    return markup


def rassylka_buttons():
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn1 = types.InlineKeyboardButton(text='Всем сотрудникам',
                                      callback_data='Всем сотрудникам')
    btn2 = types.InlineKeyboardButton(text='Одному сотруднику',
                                      callback_data='Одному сотруднику')
    markup.inline_keyboard.append([btn1,
                                   btn2])
    return markup


def answer_to_report(user_id):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    btn_yes = types.InlineKeyboardButton(text='Принять ✅',
                                         callback_data=f'Принять {user_id}')
    btn_no = types.InlineKeyboardButton(text='Переснять ❌',
                                        callback_data=f'Переснять {user_id}')
    markup.inline_keyboard.append([btn_yes,
                                   btn_no])
    return markup


def ident_list_first_page(ident_list):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    cnt = 0
    for ident in ident_list:
        if cnt < 2:
            btn = types.InlineKeyboardButton(text=f'{ident[0]}',
                                             callback_data=f'Добавление:{ident[0]}')
            markup.inline_keyboard.append([btn])
            cnt += 1
        if cnt == 2:
            if ident != ident_list[-1]:
                btn_forward = types.InlineKeyboardButton(text='>>>',
                                                         callback_data='forward_ident_1')
                markup.inline_keyboard.append([btn_forward])
                break
    return markup


def ident_list_mid_and_last_page(ident_list: list, page: int):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    cnt = 0
    for ident in ident_list[page*2:]:
        if cnt < 2:
            btn = types.InlineKeyboardButton(text=f'{ident[0]}', callback_data=f'Добавление:{ident[0]}')
            markup.inline_keyboard.append([btn])
            cnt += 1
        if cnt == 2:
            if ident != ident_list[-1]:
                btn_back = types.InlineKeyboardButton(text='<<<', callback_data=f'back_ident_{page-1}')
                btn_forward = types.InlineKeyboardButton(text='>>>', callback_data=f'forward_ident_{page+1}')
                markup.inline_keyboard.append([btn_back, btn_forward])
                break
    else:
        btn_back = types.InlineKeyboardButton(text='<<<', callback_data=f'back_ident_{page - 1}')
        markup.inline_keyboard.append([btn_back])
    return markup
