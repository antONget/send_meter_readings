from aiogram import Bot, types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from config_data.config import Config, load_config
from keyboard import personal_keyboards, admin_keyboards
from database import requests


config: Config = load_config()
router = Router()


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


async def send_notification(day: str, bot: Bot):
    logging.info('send_notification')
    ids_list_water = requests.select_personal_id_by_day_water(day)
    ids_list_electro = requests.select_personal_id_by_day_electro(day)
    if ids_list_water:
        for id_ in ids_list_water:
            try:
                await bot.send_message(chat_id=int(id_[0]), text=f'Сегодня {day} число, необходимо отправить отчет за'
                                                                 f' воду, если у вас несколько объектов , введите'
                                                                 f' /start чтобы просмотреть для какого объекта нужно'
                                                                 f' отправить отчет')

            except Exception as e:
                print(e)
                admin_ids = str(config.tg_bot.admin_ids).split(',')
                for admin_id in admin_ids[1:]:
                    await bot.send_message(chat_id=int(admin_id), text=f'Сотрудник {id_} не получил оповещение,'
                                                                       f' возможно он заблокировал бота, либо не'
                                                                       f' запускал его')
    if ids_list_electro:
        for id_ in ids_list_electro:
            try:
                await bot.send_message(chat_id=int(id_[0]), text=f'Сегодня {day} число, необходимо отправить отчет'
                                                                 f' за электричество, если у вас несколько объектов,'
                                                                 f' введите /start чтобы просмотреть для какого объекта'
                                                                 f' нужно отправить отчет')

            except Exception as e:
                print(e)
                admin_ids = str(config.tg_bot.admin_ids).split(',')
                for admin_id in admin_ids[1:]:
                    await bot.send_message(chat_id=int(admin_id), text=f'Сотрудник {id_} не получил оповещение,'
                                                                       f' возможно он заблокировал бота, либо не'
                                                                       f' запускал его')


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
                    time_water = data[0][1]
                    time_electro = data[0][2]
                    await message.answer(f'Добрый день,вы являетесь ответственным за помещение "{name}"\n\n'
                                         f'Вам нужно присылать отчет за воду каждое {time_water} число, и отчет за '
                                         f'электричество каждое {time_electro} число',
                                         reply_markup=personal_keyboards.main_button_personal())
                else:
                    text = 'Вы являетесь ответственным за помещения:\n'

                    for elem in data:
                        text += f'{data.index(elem)+1}) "{elem[0]}", дни отчета: {elem[1]} число - вода, ' \
                                f'{elem[2]} число - электричество\n'
                    await message.answer(text=text, reply_markup=personal_keyboards.main_button_personal())

            else:
                await message.answer('На эту ссылку уже зарегистрирован человек')

        else:
            if requests.check_personal_without_comand(user_id):
                data = requests.check_personal_without_comand(user_id)
                if len(data) == 1:
                    name = data[0][0]
                    time_water = data[0][1]
                    time_electro = data[0][2]
                    await message.answer(f'Добрый день,вы являетесь ответственным за помещение "{name}"\n\n'
                                         f'Вам нужно присылать отчет за воду каждое {time_water} число, и отчет за '
                                         f'электричество каждое {time_electro} число',
                                         reply_markup=personal_keyboards.main_button_personal())
                else:
                    text = 'Вы являетесь ответственным за помещения:\n'

                    for elem in data:
                        text += f'{data.index(elem) + 1}) "{elem[0]}", дни отчета: {elem[1]} число - вода, ' \
                                f'{elem[2]} число - электричество\n'
                    await message.answer(text=text, reply_markup=personal_keyboards.main_button_personal())
            else:
                await message.answer('Вы не являетесь персоналом')


@router.message(F.text == 'Отправить отчет')
async def send_report(message: types.Message, state: FSMContext):
    logging.info('send_report')
    try:
        user_id = message.from_user.id
        data = requests.check_personal_without_comand(user_id)
        if len(data) == 1:
            await state.update_data(user_input=data[0][0])
            await message.answer(text='Выберите тип отчета', reply_markup=personal_keyboards.report_buttons())
            await state.set_state(FSMFillForm.get_photo_to_report)

        else:
            idents = []
            for elem in data:
                idents.append(elem[0])

            markup = personal_keyboards.choice_ident_buttons(idents)

            await message.answer(text='Выберите помещение отчет для которого хотите отправить',
                                 reply_markup=markup)
    except Exception as e:
        print(e)


@router.callback_query(F.data.startswith('Отчет:'))
async def get_ident_to_report(callback: types.CallbackQuery, state: FSMContext):
    logging.info('get_ident_to_report')
    user_id = callback.from_user.id
    data = requests.check_personal_without_comand(user_id)
    idents = []
    for elem in data:
        idents.append(elem[0])

    for ident in idents:
        if callback.data == f'Отчет:{ident}':
            await callback.answer()
            await state.update_data(user_input=ident)
            await callback.message.edit_text('Выберите тип отчета:', reply_markup=personal_keyboards.report_buttons())
            break


@router.callback_query(F.data == 'Воду')
async def get_report_tipe(callback: types.CallbackQuery, state: FSMContext):
    logging.info('get_report_tipe')
    await state.update_data(report_type=callback.data)
    await callback.answer()
    await callback.message.edit_text('Пришлите фото отчета за воду', reply_markup=None)
    await state.set_state(FSMFillForm.get_photo_to_report_choice)


@router.callback_query(F.data == 'Электричество')
async def get_report_tipe(callback: types.CallbackQuery, state: FSMContext):
    logging.info('get_report_tipe')
    await state.update_data(report_type=callback.data)
    await callback.answer()
    await callback.message.edit_text('Пришлите фото отчета за электричество', reply_markup=None)
    await state.set_state(FSMFillForm.get_photo_to_report_choice)


@router.message(StateFilter(FSMFillForm.get_photo_to_report_choice))
async def get_photo_to_report_choice(message: types.Message, state: FSMContext, bot: Bot):
    logging.info('get_photo_to_report_choice')
    try:
        photo = message.photo[-1]
        user_id = message.from_user.id
        markup = admin_keyboards.answer_to_report(user_id)
        ident = await state.get_data()
        ident = ident['user_input']
        report_type = await state.get_data()
        report_type = report_type['report_type']
        admin_id_list = str(config.tg_bot.admin_ids).split(',')

        for admin_id in admin_id_list:

            await bot.send_photo(chat_id=int(admin_id),
                                 photo=photo.file_id,
                                 caption=f'Отчет с помещения: "{ident}" за {report_type}',
                                 reply_markup=markup)
        await state.clear()

    except Exception as e:
        await message.answer('Вы отправили не фотографию, нажмите на кнопку и отправьте фото еще раз')
        await state.clear()
