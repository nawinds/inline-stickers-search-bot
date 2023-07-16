from aiogram import Router
from aiogram import types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from data.db_session import create_session
from data.sticker_sets import StickerSet
from instances import NewSetState
from search import clear_q

data_processing = Router()


@data_processing.message(StateFilter(NewSetState.title))
async def process_set_title(message: types.Message, state: FSMContext):
    if len(message.text) > 50:
        await message.reply("This title exceeds 50 characters. Please, try again")
        return
    session = create_session()
    new_set = StickerSet(owner_id=message.from_user.id, title=message.text)
    session.add(new_set)
    session.commit()
    await state.update_data(title=message.text, set_id=new_set.id)
    await state.set_state(NewSetState.sticker)
    await message.answer('Sticker set created! Please send the first sticker for your new set')


@data_processing.message(StateFilter(NewSetState.sticker), F.content_type == 'sticker')
async def process_set_sticker(message: types.Message, state: FSMContext):
    sticker_file = message.sticker.file_id
    sticker_unique_id = message.sticker.file_unique_id
    await state.update_data(sticker_file=sticker_file, sticker_unique_id=sticker_unique_id)
    await message.answer("Send a prompt for this sticker")
    await state.set_state(NewSetState.prompt)


@data_processing.message(StateFilter(NewSetState.prompt))
async def process_set_prompt(message: types.Message, state: FSMContext):
    if len(message.text) > 1000:
        await message.reply("This prompt exceeds 1000 characters. Please, try again")
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
    await message.answer("Send another prompt for this sticker. To finish, send /finish")
    await state.set_state(NewSetState.prompt)
