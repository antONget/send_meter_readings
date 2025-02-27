from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging


def utils_keyboards_list_items(part_list_items: list,
                               callback_prefix_select: str,
                               callback_prefix_back: str,
                               callback_prefix_next: str,
                               page: int,
                               max_page: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для вывода списка в виде кнопок в столбец
    :param part_list_items:
    :param callback_prefix_select:
    :param callback_prefix_back:
    :param callback_prefix_next:
    :param page:
    :param max_page:
    :return:
    """
    logging.info(f"utils_keyboards_list_items")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for item_button, *item_callback in part_list_items:
        buttons.append(InlineKeyboardButton(text=item_button,
                                            callback_data=f'{callback_prefix_select}_{item_button}'))
    button_back = InlineKeyboardButton(text='Назад',
                                       callback_data=f'{callback_prefix_back}_{page}')
    button_next = InlineKeyboardButton(text='Вперед',
                                       callback_data=f'{callback_prefix_next}_{page}')
    button_page = InlineKeyboardButton(text=f'{page+1}/{max_page}',
                                       callback_data=f'none')
    kb_builder.row(*buttons, width=1)
    kb_builder.row(button_back, button_page, button_next)
    return kb_builder.as_markup()


async def utils_handler_pagination_and_select_item(list_items: list,
                                                   text_message_pagination: str,
                                                   text_message_select: str,
                                                   page: int,
                                                   count_item_page: int,
                                                   callback_prefix_select: str,
                                                   callback_prefix_back: str,
                                                   callback_prefix_next: str,
                                                   callback: CallbackQuery | None,
                                                   message: Message | None) -> None:
    logging.info(f'utils_keyboard_pagination_and_select_item')
    part = 0
    if len(list_items) % count_item_page:
        part = 1
    max_page = int(len(list_items)/count_item_page) + part
    if message:
        part_list_items = list_items[page * count_item_page:(page + 1) * count_item_page]
        keyboard = utils_keyboards_list_items(part_list_items=part_list_items,
                                              callback_prefix_select=callback_prefix_select,
                                              callback_prefix_back=callback_prefix_back,
                                              callback_prefix_next=callback_prefix_next,
                                              page=page,
                                              max_page=max_page)
        await message.answer(text=text_message_pagination,
                             reply_markup=keyboard)
        return
    if callback.data.startswith(callback_prefix_select):
        await callback.message.edit_text(text=text_message_select,
                                         reply_markup=None)
        return
    if callback.data.startswith(callback_prefix_back):
        page -= 1
        if page < 0:
            page = max_page - 1
    elif callback.data.startswith(callback_prefix_next):
        page += 1
        if page == max_page:
            page = 0
    part_list_items = list_items[page*count_item_page:(page+1)*count_item_page]
    keyboard = utils_keyboards_list_items(part_list_items=part_list_items,
                                          callback_prefix_select=callback_prefix_select,
                                          callback_prefix_back=callback_prefix_back,
                                          callback_prefix_next=callback_prefix_next,
                                          page=page,
                                          max_page=max_page)
    try:
        await callback.message.edit_text(text=text_message_pagination,
                                         reply_markup=keyboard)
    except:
        await callback.message.edit_text(text=f'{text_message_pagination}.',
                                         reply_markup=keyboard)
    await callback.answer()
