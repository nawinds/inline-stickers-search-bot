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


class StickerSearchState(StatesGroup):
    pack_name = State()


@dp.inline_handler()
async def handle_inline_query(query: InlineQuery):
    pack_name = query.query

    # Fetch stickers from selected pack
    stickers = await bot.get_sticker_set(pack_name)
    results = []

    for sticker in stickers.stickers:
        results.append(
            InlineQueryResultCachedSticker(
                id=sticker.file_id,
                sticker_file_id=sticker.file_id
            )
        )

    try:
        await query.answer(results)
    except InvalidQueryID:
        # Catch InvalidQueryID error when user cancels the query
        pass


@dp.message_handler(Command('start'))
async def cmd_start(message: types.Message):
    await StickerSearchState.pack_name.set()
    await message.reply('Please enter the sticker pack name you want to search:')


@dp.message_handler(state=StickerSearchState.pack_name)
async def search_stickers(message: types.Message, state: FSMContext):
    pack_name = message.text

    # Fetch stickers from selected pack
    stickers = await bot.get_sticker_set(pack_name)
    if not stickers.stickers:
        await message.reply('No stickers found in the specified pack.')
        await state.finish()
        return

    # Display stickers
    await message.reply(f'Found {len(stickers.stickers)} stickers in the pack "{pack_name}":')
    for sticker in stickers.stickers:
        await message.reply_sticker(sticker.file_id)

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
