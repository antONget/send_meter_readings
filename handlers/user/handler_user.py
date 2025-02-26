from aiogram import Bot, types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
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
    ids_list = requests.select_personal_id_by_day(day)
    for id_ in ids_list:
        try:
            await bot.send_message(chat_id=int(id_),
                                   text=f'Сегодня {day} число,'
                                        f' необходимо отправить отчет, если у вас несколько обьектов,'
                                        f' введите /start чтобы просмотреть для какого обьекта нужно'
                                        f' отправить отчет')

        except Exception as e:
            print(e)
            admin_ids = str(config.tg_bot.admin_ids).split(',')
            for admin_id in admin_ids[1:]:
                await bot.send_message(chat_id=int(admin_id),
                                       text=f'Сотрудник {id_} не получил оповещение,'
                                       f' возможно он заблокировал бота, либо не запускал его')


@router.message(Command('send_file'))
async def send_file(message: types.Message):
    file_name = 'py_log.log'
    await message.answer_document(FSInputFile(file_name), caption='12132')


@router.message(Command('start'))
async def start(message: types.Message):
    logging.info('start')
    print(123123)
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
                    await message.answer(f'Добрый день,вы являетесь ответственным за помещение "{name}"\n\n'
                                         f'Вам нужно присылать отчет каждое {time} число',
                                         reply_markup=personal_keyboards.main_button_personal())
                else:
                    text = 'Вы являетесь ответственным за помещения:\n'

                    for elem in data:
                        text += f'{data.index(elem)}) {elem[0]} - день отчета: {elem[1]} число\n'
                    await message.answer(text, reply_markup=personal_keyboards.main_button_personal())

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
                    await message.answer(text=f'Добрый день,вы являетесь ответственным за помещение "{name}"\n\n'
                                              f'Вам нужно присылать отчет каждое {time} число',
                                         reply_markup=personal_keyboards.main_button_personal())
                else:
                    text = 'Вы являетесь ответственным за помещения:\n'

                    for elem in data:
                        text += f'{data.index(elem)}) {elem[0]} - день отчета: {elem[1]} число\n'
                    await message.answer(text, reply_markup=personal_keyboards.main_button_personal())
            else:
                await message.answer('Вы не являетесь персоналом')


@router.message(F.text == 'Отправить отчет')
async def send_report(message: types.Message, state: FSMContext):
    logging.info('send_report')
    user_id = message.from_user.id
    data = requests.check_personal_without_comand(user_id)
    if len(data) == 1:
        await message.answer(text='Пришлите фото для отчета')
        await state.set_state(FSMFillForm.get_photo_to_report)

    else:
        idents = []
        for elem in data:
            idents.append(elem[0])

        markup = personal_keyboards.choice_ident_buttons(idents)

        await message.answer(text='Выберите помещение отчет для которого хотите отправить',
                             reply_markup=markup)


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
            await callback.message.answer(text=f'Пришлите фото для отчета для помещения: {ident}')
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
        admin_id_list = str(config.tg_bot.admin_ids).split(',')

        for admin_id in admin_id_list:

            await bot.send_photo(chat_id=int(admin_id),
                                 photo=photo.file_id,
                                 caption=f'Отчет с помещения: "{ident}"',
                                 reply_markup=markup)
        await state.clear()

    except Exception as e:
        print(e)
        await message.answer('Вы отправили не фотографию, нажмите на кнопку и отправьте фото еще раз')
        await state.clear()


@router.message(F.photo, StateFilter(FSMFillForm.get_photo_to_report))
async def get_photo_to_report(message: types.Message, state: FSMContext, bot: Bot):
    logging.info('get_photo_to_report')
    try:
        photo = message.photo[-1]
        user_id = message.from_user.id
        markup = admin_keyboards.answer_to_report(user_id)
        ident = requests.check_personal_without_comand(user_id)[0]
        admin_id_list = str(config.tg_bot.admin_ids).split(',')
        for admin_id in admin_id_list:
            try:
                await bot.send_photo(chat_id=int(admin_id),
                                     photo=photo.file_id,
                                     caption=f'Отчет с помещения: "{ident}"',
                                     reply_markup=markup)
            except:
                pass
        await state.clear()

    except Exception as e:
        await message.answer('Вы отправили не фотографию,нажмите на кнопку и отправьте фото еще раз')
        await state.clear()
