import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineQuery, ChosenInlineResult, InlineQueryResultCachedSticker
from aiogram.utils import executor
from aiogram.utils.exceptions import InvalidQueryID
from search import Search, clear_q
from data.search_data import SearchData
from data.sticker_sets import StickerSet
from data.sticker_sets_data import StickerSetsData
from data.db_session import create_session, global_init
from time import time

logging.basicConfig(level=logging.INFO)

bot = Bot(token='6243367959:AAGSqfPJBw4LxF37N_kD--NiVk4HR3znLSg')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class NewStickerState(StatesGroup):
    sticker = State()
    prompt = State()


class NewSetState(StatesGroup):
    title = State()
    sticker = State()
    prompt = State()


@dp.inline_handler()
async def handle_inline_query(query: InlineQuery):
    q = query.query
    start = time()
    results = Search(q, query.from_user.id).get_results()
    print("SEARCH TIME:", time() - start)
    inline_results = []

    for i in range(len(results)):
        inline_results.append(
            InlineQueryResultCachedSticker(
                id=str(i),
                sticker_file_id=results[i]
            )
        )
    try:
        await query.answer(inline_results)
    except InvalidQueryID:
        # Catch InvalidQueryID error when user cancels the query
        pass


@dp.chosen_inline_handler()
async def handle_chosen_inline_query(chosen_inline_result: ChosenInlineResult):
    pass


@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    await message.reply('Please enter the sticker pack name you want to search:')


@dp.message_handler(Command('new'))
async def cmd_new(message: types.Message):
    await NewStickerState.sticker.set()
    await message.reply('Please send a sticker to add it to search results')


@dp.message_handler(Command('set'))
async def cmd_set(message: types.Message):
    await NewSetState.title.set()
    await message.reply('Please send a title for the new set')


@dp.message_handler(Command('finish'), state=NewSetState.prompt)
async def process_prompt_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sticker = data.get('sticker')
    prompts = data.get('prompts')
    await NewSetState.sticker.set()
    session = create_session()
    for p in prompts:
        session.add(SearchData(sticker_id=sticker, keyword=p, user_id=message.from_user.id))
    session.commit()
    session.add(StickerSetsData(set_id=data.get("set_id"), sticker_id=sticker))
    session.commit()
    await message.reply("Sticker saved. Now send another sticker. If you don't want "
                        "to add another sticker to this set, send /finish_set")


@dp.message_handler(state=NewSetState.title)
async def cmd_set(message: types.Message, state: FSMContext):
    session = create_session()
    new_set = StickerSet(owner_id=message.from_user.id, title=message.text)
    session.add(new_set)
    session.commit()
    await state.update_data(title=message.text, set_id=new_set.set_id)
    await NewSetState.sticker.set()
    await message.reply('Please send a sticker for the new set')


@dp.message_handler(state=NewSetState.sticker, content_types=["sticker"])
async def process_sticker(message: types.Message, state: FSMContext):
    sticker = message.sticker.file_id
    await state.update_data(sticker=sticker)
    await message.reply("Send a prompt for this sticker. To finish, send /finish")
    await NewSetState.prompt.set()


@dp.message_handler(state=NewSetState.prompt)
async def process_prompt(message: types.Message, state: FSMContext):
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
    await message.reply("Send a prompt for this sticker. To finish, send /finish")
    await NewSetState.prompt.set()


@dp.message_handler(Command('finish_set'), state=NewSetState.sticker)
async def process_prompt_finish_set(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Ok. Your set is now saved")


@dp.message_handler(Command('finish'), state=NewStickerState.prompt)
async def process_prompt_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sticker = data.get('sticker')
    prompts = data.get('prompts')
    await state.finish()
    session = create_session()
    for p in prompts:
        session.add(SearchData(sticker_id=sticker, keyword=p, user_id=message.from_user.id))
    session.commit()
    await message.reply("Sticker saved")


@dp.message_handler(state=NewStickerState.sticker, content_types=["sticker"])
async def process_sticker(message: types.Message, state: FSMContext):
    sticker = message.sticker.file_id
    await state.update_data(sticker=sticker)

    # # Fetch stickers from selected pack
    # stickers = await bot.get_sticker_set(pack_name)
    # if not stickers.stickers:
    #     await message.reply('No stickers found in the specified pack.')
    #     await state.finish()
    #     return
    await message.reply("Send a prompt for this sticker. To finish, send /finish")
    await NewStickerState.prompt.set()


@dp.message_handler(state=NewStickerState.prompt)
async def process_prompt(message: types.Message, state: FSMContext):
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
    await message.reply("Send a prompt for this sticker. To finish, send /finish")
    await NewStickerState.prompt.set()


if __name__ == '__main__':
    global_init("data/db/main.db")
    executor.start_polling(dp, skip_updates=True)
