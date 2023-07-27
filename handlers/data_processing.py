from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram_i18n import I18nContext

from db_models.db_session import create_session
from db_models.sticker_sets import StickerSet
from db_models.user_sets import UserSet
from handlers.commands import send_next_pack_sticker
from modules.instances import NewSetState, bot
from modules.search import clear_q

data_processing = Router()
data_processing.message.filter(F.chat.type == "private")


@data_processing.message(StateFilter(NewSetState.title))
async def set_title(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    if len(message.text) > 50:
        await message.reply(i18n.gettext("data_processing.set_title.limit"))
        return
    session = create_session()
    new_set = StickerSet(owner_id=message.from_user.id, title=message.text)
    session.add(new_set)
    session.commit()
    session.add(UserSet(user_id=message.from_user.id, set_id=new_set.id))
    session.commit()
    await state.update_data(title=message.text, set_id=new_set.id)
    data = await state.get_data()
    if data.get('set_base_type') == "pack":
        await message.answer(i18n.gettext("data_processing.set_title.pack"))
        sticker_pack = await bot.get_sticker_set(data.get("pack_name"))
        pack_stickers = sticker_pack.stickers
        await state.update_data(next_sticker=0)
        await send_next_pack_sticker(message, state, pack_stickers)
        await state.set_state(NewSetState.prompt)
        return
    await state.set_state(NewSetState.sticker)
    await message.answer(i18n.gettext("data_processing.set_title.success"))


@data_processing.message(StateFilter(NewSetState.sticker), F.content_type == 'sticker')
async def set_sticker(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    data = await state.get_data()
    if data.get('set_base_type') == "pack":
        await state.set_state(NewSetState.title)
        await state.update_data(pack_name=message.sticker.set_name)
        sticker_pack = await bot.get_sticker_set(message.sticker.set_name)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=sticker_pack.title)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(i18n.gettext("data_processing.set_sticker.pack"),
                             reply_markup=keyboard)
        return
    await state.set_state(NewSetState.prompt)
    sticker_file = message.sticker.file_id
    sticker_unique_id = message.sticker.file_unique_id
    await state.update_data(sticker_file=sticker_file, sticker_unique_id=sticker_unique_id)
    await message.answer(i18n.gettext("data_processing.set_sticker"))


@data_processing.message(StateFilter(NewSetState.prompt))
async def set_prompt(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    if len(message.text) > 1000:
        await message.reply(i18n.gettext("data_processing.set_prompt.limit"))
        return
    data = await state.get_data()
    prompts = data.get('prompts', [])
    new_prompt = clear_q(message.text)
    await state.update_data(prompts=prompts + [new_prompt])
    with open("data/dictionary.txt", encoding="utf-8") as read_file:
        dictionary = read_file.read().split()
    for i in new_prompt.split():
        if i not in dictionary:
            dictionary.append(i)
    with open("data/dictionary.txt", "w", encoding="utf-8") as write_file:
        write_file.write(" ".join(dictionary))
    await message.answer(i18n.gettext("data_processing.set_prompt.success"))
    await state.set_state(NewSetState.prompt)
