from aiogram import Router
from aiogram import types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram_i18n import I18nContext

from data.db_session import create_session
from data.sticker_sets import StickerSet
from data.user_sets import UserSet
from instances import NewSetState
from search import clear_q

data_processing = Router()
data_processing.message.filter(F.chat.type == "private")


@data_processing.message(StateFilter(NewSetState.title))
async def set_title(message: types.Message, state: FSMContext, i18n: I18nContext):
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
    await state.set_state(NewSetState.sticker)
    await message.answer(i18n.gettext("data_processing.set_title.success"))


@data_processing.message(StateFilter(NewSetState.sticker), F.content_type == 'sticker')
async def set_sticker(message: types.Message, state: FSMContext, i18n: I18nContext):
    sticker_file = message.sticker.file_id
    sticker_unique_id = message.sticker.file_unique_id
    await state.update_data(sticker_file=sticker_file, sticker_unique_id=sticker_unique_id)
    await message.answer(i18n.gettext("data_processing.set_sticker"))
    await state.set_state(NewSetState.prompt)


@data_processing.message(StateFilter(NewSetState.prompt))
async def set_prompt(message: types.Message, state: FSMContext, i18n: I18nContext):
    if len(message.text) > 1000:
        await message.reply(i18n.gettext("data_processing.set_prompt.limit"))
        return
    data = await state.get_data()
    prompts = data.get('prompts', [])
    new_prompt = clear_q(message.text)
    await state.update_data(prompts=prompts + [new_prompt])
    with open("known_words.txt", encoding="utf-8") as read_file:
        known_words = read_file.read().split()
    for i in new_prompt.split():
        if i not in known_words:
            known_words.append(i)
    with open("known_words.txt", "w", encoding="utf-8") as write_file:
        write_file.write(" ".join(known_words))
    await message.answer(i18n.gettext("data_processing.set_prompt.success"))
    await state.set_state(NewSetState.prompt)
