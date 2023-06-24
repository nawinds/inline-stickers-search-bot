import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineQuery, InlineQueryResultCachedSticker
from aiogram.utils import executor
from aiogram.utils.exceptions import InvalidQueryID

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token='6243367959:AAGSqfPJBw4LxF37N_kD--NiVk4HR3znLSg')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

stickers_list = {}


class StickerSearchState(StatesGroup):
    sticker = State()
    prompt = State()


@dp.inline_handler()
async def handle_inline_query(query: InlineQuery):
    q = query.query

    results = []

    results.append(
        InlineQueryResultCachedSticker(
            id="1",
            sticker_file_id=stickers_list[q]
        )
    )

    try:
        await query.answer(results)
    except InvalidQueryID:
        # Catch InvalidQueryID error when user cancels the query
        pass


@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    await message.reply('Please enter the sticker pack name you want to search:')


@dp.message_handler(Command('new'))
async def cmd_new(message: types.Message):
    await StickerSearchState.sticker.set()
    await message.reply('Please send a sticker to add it to search results')


@dp.message_handler(Command('finish'), state=StickerSearchState.prompt)
async def process_prompt_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sticker = data.get('sticker')
    prompts = data.get('prompts')
    await state.finish()
    for p in prompts:
        stickers_list[p] = sticker
    await message.reply("Sticker saved")


@dp.message_handler(state=StickerSearchState.sticker, content_types=["sticker"])
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
    await StickerSearchState.prompt.set()


@dp.message_handler(state=StickerSearchState.prompt)
async def process_prompt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prompts = data.get('prompts', [])
    await state.update_data(prompts=prompts + [message.text])

    await message.reply("Send a prompt for this sticker. To finish, send /finish")
    await StickerSearchState.prompt.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
