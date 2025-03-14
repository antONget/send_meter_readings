from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import FSInputFile

import logging

router = Router()


@router.callback_query()
async def all_callback(callback: CallbackQuery) -> None:
    logging.info(f'all_callback: {callback.message.chat.id}')
    logging.info(callback.data)


@router.message()
async def all_message(message: Message) -> None:
    logging.info(f'all_message')
    if message.photo:
        logging.info(f'all_message message.photo')
        logging.info(message.photo[-1].file_id)

    if message.sticker:
        logging.info(f'all_message message.sticker')
        logging.info(message.sticker.file_id)

    if message.text == '/get_logfile':
        file_path = "py_log.log"
        await message.answer_document(FSInputFile(file_path))

    if message.text == '/get_dbfile':
        file_path = "database/DATABASE.sql"
        await message.answer_document(FSInputFile(file_path))
