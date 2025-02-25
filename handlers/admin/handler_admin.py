from aiogram import Bot, types, F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from utils.list_keyboard_select_item import utils_handler_pagination_and_select_item
import logging

from config_data.config import Config, load_config
from keyboard import personal_keyboards, admin_keyboards
from database import requests


config: Config = load_config()
router = Router()

button_list = config.tg_bot.button_list


class FSMFillForm(StatesGroup):
    get_ident = State()
    get_date_time = State()
    get_ident_for_mailing = State()
    get_text_to_mailing = State()
    fill_mailing = State()
    get_photo_to_report = State()
    get_photo_to_report_choice = State()
    get_failure_report = State()
    get_new_report_day = State()

    get_personal_id = State()
    get_report_day_for_new = State()
    get_ident_for_add_new = State()


def extract_arg(arg):
    return arg.split()[1:]


@router.message(Command('start'))
async def start(message: types.Message):
    logging.info('start')
    command = extract_arg(message.text)
    user_id = str(message.from_user.id)
    admin_id_list = str(config.tg_bot.admin_ids).split(',')
    if user_id in admin_id_list:

        markup = admin_keyboards.main_admin_buttons()
        await message.answer(text='Вы являетесь администратором, выберите действие',
                             reply_markup=markup)

    if user_id not in admin_id_list:
        if command:
            command = int(command[0])

            if requests.check_personal(command):
                requests.insert_personl_id_and(command, user_id)
                data = requests.check_personal_without_comand(user_id)
                if len(data) == 1:
                    name = data[0][0]
                    time = data[0][1]
                    await message.answer(text=f'Добрый день,вы являетесь ответственным за помещение "{name}"\n\n'
                                              f'Вам нужно присылать отчет каждое {time} число',
                                         reply_markup=personal_keyboards.main_button_personal())

                else:
                    text = 'Вы являетесь ответственным за помещения:\n'
                    objects = []
                    report_days = []

                    for elem in data:
                        objects.append(elem[0])
                        report_days.append(elem[1])

                    for object_ in objects:
                        text += f'{objects.index(object_)+1}) {object_}\n'

                    text += 'Вам нужно присылать отчеты\n'
                    for day in report_days:
                        text += f'{report_days.index(day)+1}) {day} число\n'

                    await message.answer(text=text,
                                         reply_markup=personal_keyboards.main_button_personal())
            else:
                await message.answer('На эту ссылку уже зарегистрирован человек')
        else:
            if requests.check_personal_without_comand(user_id):
                data = requests.check_personal_without_comand(user_id)
                if len(data) == 1:
                    name = data[0][0]
                    time = data[0][1]

                    await message.answer(f'Добрый день,вы являетесь ответственным за помещение "{name}"\n\n'
                                         f'Вам нужно присылать отчет каждое {time} число',
                                         reply_markup=personal_keyboards.main_button_personal())
                else:
                    text = 'Вы являетесь ответственным за помещения:\n'
                    objects = []
                    report_days = []
                    for elem in data:
                        objects.append(elem[0])
                        report_days.append(elem[1])
                    for object_ in objects:
                        text += f'{objects.index(object_)+1}) {object_}\n'
                    text += '\nВам нужно присылать отчеты\n'
                    for day in report_days:
                        text += f'{report_days.index(day)+1}) {day} число\n'

                    await message.answer(text=text,
                                         reply_markup=personal_keyboards.main_button_personal())
            else:
                await message.answer(text='Вы не являетесь персоналом')


@router.callback_query(or_f(F.data.startswith('Принять'),
                            F.data.startswith('Переснять')))
async def answer_to_report(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    logging.info('answer_to_report')
    ids_list = requests.get_all_personal_ids()
    for id_ in ids_list:
        if callback.data == f'Принять {id_[0]}':
            await callback.answer()
            await callback.message.answer('Отчет принят!')
            await bot.send_message(chat_id=id_[0],
                                   text='Отчет принят!')
            break

        if callback.data == f'Переснять {id_[0]}':
            await callback.answer()
            await callback.message.answer('Введите причину отказа')
            await state.update_data(user_input=id_[0])
            await state.set_state(FSMFillForm.get_failure_report)
            break


@router.message(StateFilter(FSMFillForm.get_failure_report))
async def get_failure_report(message: types.Message,
                             state: FSMContext,
                             bot: Bot):
    logging.info('get_failure_report')
    if str(message.text) not in button_list:
        message_to_report = message.text
        message_to_report = 'Отчет не принят, причина:\n' + message_to_report

        pers_id_cort = await state.get_data()
        pers_id = pers_id_cort['user_input']

        await bot.send_message(chat_id=pers_id, text=message_to_report)
        await message.answer('Причина отказа отправлена')
        await state.clear()

    else:
        await main_admin(message, state)
        await state.clear()


@router.message(or_f(F.text == 'Выдать токен 📱',
                     F.text == 'Изменить время 🕑',
                     F.text == 'Создать рассылку 🧑‍💻',
                     F.text == 'Добавить объект сотруднику 🚶'),
                StateFilter(default_state))
async def main_admin(message: types.Message, state: FSMContext):
    logging.info('main_admin')
    if message.text == 'Выдать токен 📱':
        await message.answer('Введите идентификатор помещения')
        await state.set_state(FSMFillForm.get_ident)

    if message.text == 'Создать рассылку 🧑‍💻':
        await message.answer(text='Хотите отправить рассылку всем сотрудникам или одному',
                             reply_markup=admin_keyboards.rassylka_buttons())

    if message.text == 'Изменить время 🕑':
        ident_list = requests.get_premises_ident()
        await utils_handler_pagination_and_select_item(list_items=ident_list,
                                                       text_message_pagination='Выберите объект для изменения времени',
                                                       text_message_select='Введите новый день сдачи отчета для'
                                                                           ' объекта',
                                                       page=0,
                                                       count_item_page=3,
                                                       callback_prefix_select='Добавление',
                                                       callback_prefix_back='back_ident',
                                                       callback_prefix_next='next_ident',
                                                       callback=None,
                                                       message=message)
        # markup = admin_keyboards.ident_list_first_page(ident_list)
        # await message.answer(text=f'Выберите объект для изменения времени\n'
        #                           f'Страница 1/{int(len(ident_list)/2)+1}',
        #                      reply_markup=markup)

    if message.text == 'Добавить объект сотруднику 🚶':
        await message.answer(text='Пришлите telegram id сотрудника для отправки ему сообщения\n'
                                  'Получить telegram id пользователя можно с помощью бота:\n'
                                  '@getmyid_bot или @username_to_id_bot',
                             reply_markup=None)
        await state.set_state(FSMFillForm.get_personal_id)


@router.message(StateFilter(FSMFillForm.get_personal_id))
async def get_peronal_id_for_new(message: types.Message, state: FSMContext):
    logging.info('get_peronal_id_for_new')
    if str(message.text) not in button_list:
        personal_id = message.text
        personal_ids_list = requests.get_all_personal_ids()
        for id_ in personal_ids_list:
            if str(personal_id) == str(id_[0]):
                await state.update_data(personal_id=message.text)
                await message.answer(text='Введите индентификатор помещения')
                await state.set_state(FSMFillForm.get_ident_for_add_new)
                break
        else:
            await message.answer('Такого сотрудника нет, проверьте id и отправьте его еще раз')
            await state.set_state(FSMFillForm.get_personal_id)

    else:
        await main_admin(message=message, state=state)
        await state.clear()


@router.message(StateFilter(FSMFillForm.get_ident_for_add_new))
async def get_ident_for_add_new(message: types.Message, state: FSMContext):
    logging.info('get_ident_for_add_new')
    if str(message.text) not in button_list:
        await state.update_data(ident=message.text)
        await message.answer(text='Введите день, в который вам будет приходить отчет')
        await state.set_state(FSMFillForm.get_report_day_for_new)
    else:
        await main_admin(message=message, state=state)
        await state.clear()


@router.message(StateFilter(FSMFillForm.get_report_day_for_new))
async def get_ident_for_add_new(message: types.Message, state: FSMContext, bot: Bot):
    logging.info('get_ident_for_add_new')
    if str(message.text) not in button_list:
        try:
            int_message = int(message.text)
            if 1 <= int_message <= 31:
                report_day = message.text
                ident = await state.get_data()
                ident = ident['ident']
                personal_id = await state.get_data()
                personal_id = personal_id['personal_id']
                requests.add_another_oject_to_personal(ident=ident, personal_id=personal_id, day=report_day)

                await message.answer('Объект добавлен сотруднику')
                await bot.send_message(chat_id=personal_id,
                                       text=f'Вам добавлен объект: "{ident}"\n'
                                            f'Вам нужно отправлять отчет каждое {report_day} число')
                await state.clear()

            else:
                await message.answer('Введено некоректное число, введите еще раз')
                await state.set_state(FSMFillForm.get_report_day_for_new)

        except Exception as e:
            await message.answer('Введено некоректное число, введите еще раз')
            await state.set_state(FSMFillForm.get_report_day_for_new)

    else:
        await main_admin(message=message, state=state)
        await state.clear()


@router.callback_query(or_f(F.data.startswith('next_ident'),
                            F.data.startswith('back_ident')))
async def pagination_ident(callback: types.CallbackQuery):
    logging.info(f'pagination_ident {callback.data}')
    page = int(callback.data.split('_')[-1])
    ident_list = requests.get_premises_ident()
    await utils_handler_pagination_and_select_item(list_items=ident_list,
                                                   text_message_pagination='Выберите объект для изменения времени',
                                                   text_message_select='Введите новый день сдачи отчета для объекта',
                                                   page=page,
                                                   count_item_page=3,
                                                   callback_prefix_select='Добавление',
                                                   callback_prefix_back='back_ident',
                                                   callback_prefix_next='next_ident',
                                                   callback=callback,
                                                   message=None)
#     ident_list = requests.get_premises_ident()
#     print(ident_list)
#     for ident in ident_list:
#         page = int(ident_list.index(ident)/2)
#         print(page)
#         if callback.data == f'forward_ident_{page}':
#             markup = admin_keyboards.ident_list_mid_and_last_page(ident_list=ident_list, page=page)
#             await callback.message.edit_text(text=f'Выберите объект для изменения времени\n'
#                                                   f'Страница {page+1}/{int(len(ident_list)/2)+1}',
#                                              reply_markup=markup)
#         if callback.data == f'back_ident_{page}':
#             if page == 0:
#                 markup = admin_keyboards.ident_list_first_page(ident_list)
#                 await callback.message.edit_text(text=f'Выберите объект для изменения времени\n'
#                                                       f'Страница 1/{int(len(ident_list) / 2) + 1}',
#                                                  reply_markup=markup)
#
#             else:
#                 markup = admin_keyboards.ident_list_mid_and_last_page(ident_list=ident_list, page=page)
#                 await callback.message.edit_text(text=f'Выберите объект для изменения времени\n'
#                                                       f'Страница {page+1}/{int(len(ident_list)/2)+1}',
#                                                  reply_markup=markup)
#     await callback.answer()


@router.callback_query(F.data.startswith('Добавление_'))
async def get_ident_to_change_day(callback: types.CallbackQuery, state: FSMContext):
    logging.info('get_ident_to_change_day')
    ident_list = requests.get_premises_ident()
    for ident in ident_list:
        await callback.answer()
        await state.update_data(ident=ident[0])
        await callback.message.edit_text(f'Введите новый день сдачи отчета для объекта "{ident[0]}"')
        await state.set_state(FSMFillForm.get_new_report_day)
        break


@router.message(StateFilter(FSMFillForm.get_new_report_day))
async def get_new_report_day(message: types.Message, state: FSMContext, bot: Bot):
    logging.info('get_new_report_day')
    if str(message.text) not in button_list:

        try:
            int_message = int(message.text)

            if 1 <= int_message <= 31:

                new_day = message.text
                ident_cort = await state.get_data()
                ident = ident_cort['ident']
                requests.update_day(ident=ident, day=new_day)
                personal_id = requests.select_personal_id_by_ident(ident)[0][0]
                await message.answer(f'День сдачи отчета для помещения "{ident}" изменен')
                try:
                    await bot.send_message(chat_id=personal_id,
                                           text=f'День сдачи отчета для помещения "{ident}" изменен на {new_day} число')

                except Exception as e:
                    await message.answer(text=f'Бот не смог оповестить пользователя')

            else:
                await message.answer('Введено некоректное число, введите его еще раз')
                await state.set_state(FSMFillForm.get_new_report_day)

        except Exception as e:
            await message.answer('Введено некоректное число, введите его еще раз')
            await state.set_state(FSMFillForm.get_new_report_day)

    else:
        await main_admin(message, state)
    await state.clear()


@router.message(StateFilter(FSMFillForm.get_ident))
async def get_ident(message: types.Message, state: FSMContext):
    logging.info('get_ident')
    await state.update_data(user_input=message.text)
    await message.answer('Введите день месяца в который вам будет приходить отчет')
    await state.set_state(FSMFillForm.get_date_time)


@router.message(StateFilter(FSMFillForm.get_date_time))
async def get_data_time(message: types.Message, state: FSMContext):
    logging.info('get_data_time')
    if str(message.text) not in button_list:
        time = message.text
        ident_cort = await state.get_data()
        ident = ident_cort['user_input']
        requests.insert_data_and_ident(ident=ident, time=time)
        data = requests.get_id_for_premises(ident)
        link = f'https://t.me/{config.tg_bot.bot_name_for_link}?start={data}'
        await message.answer(text=f'Ссылка сгенерирована:<code>{link}</code>'
                                  f'\n\nСкопируйте нажатием и перешлите эту ссылку сотруднику',
                             parse_mode='HTML')
        await state.clear()
    else:
        await main_admin(message, state)
        await state.clear()


@router.callback_query(or_f(F.data == 'Всем сотрудникам', F.data == 'Одному сотруднику'))
async def mailing(callback: types.CallbackQuery, state: FSMContext):
    logging.info('mailing')
    if callback.data == 'Одному сотруднику':
        await callback.message.edit_text(text='Пришлите telegram id сотрудника для отправки ему сообщения\n'
                                              'Получить telegram id пользователя можно с помощью бота:\n'
                                              '@getmyid_bot или @username_to_id_bot',
                                         reply_markup=None)
        await state.set_state(FSMFillForm.get_ident_for_mailing)
    if callback.data == 'Всем сотрудникам':
        await callback.message.edit_text(text='Введите текст для рассылки',
                                         reply_markup=None)
        await state.set_state(FSMFillForm.fill_mailing)


@router.message(StateFilter(FSMFillForm.fill_mailing))
async def get_text_for_mailing(message: types.Message, state: FSMContext, bot: Bot):
    logging.info('get_text_for_mailing')
    if str(message.text) not in button_list:
        text = str(message.text)
        text = 'Рассылка от администратора\n\n' + text
        ids_list = requests.get_all_personal_ids()
        for id_ in ids_list:
            try:
                await bot.send_message(chat_id=id_[0],text=text)

            except Exception as e:
                await message.answer(f'Пользователь {id_} не оповещен, возможно он заблокировал бота, либо не запускал его')

        await message.answer('Рассылка отправлена всем сотрудникам')
        await state.clear()

    else:
        await main_admin(message, state)
        await state.clear()


@router.message(StateFilter(FSMFillForm.get_ident_for_mailing))
async def get_ident_for_mailing(message: types.Message, state: FSMContext):
    logging.info('get_ident_for_mailing')
    if str(message.text) not in button_list:
        await state.update_data(user_input=message.text)
        await message.answer('Введите текст сообщения')
        await state.set_state(FSMFillForm.get_text_to_mailing)

    else:
        await main_admin(message=message, state=state)
        await state.clear()


@router.message(StateFilter(FSMFillForm.get_text_to_mailing))
async def send_message_ro_one_person(message: types.Message, state: FSMContext, bot: Bot):
    logging.info('send_message_ro_one_person')
    if str(message.text) not in button_list:
        mailing_text = message.text
        mailing_text = 'Сообщение от администратора:\n\n' + mailing_text
        data = await state.get_data()
        id_ = data['user_input']
        try:
            await bot.send_message(chat_id=id_,
                                   text=mailing_text)
            await state.clear()
            await message.answer('Сообщение отправлено!')

        except Exception as e:
            await message.answer('Произошла ошибка при отправке сообщения,возможные причины:\n'
                                 '1) Пользователь заблокировал бота\n'
                                 '2) Пользователь не запускал бота\n'
                                 '3) Введен неверный id\n'
                                 'Нажмите на кнопку "Создать рассылку" и попробуйте снова')
            await state.clear()

    else:
        await main_admin(message, state)
        await state.clear()
