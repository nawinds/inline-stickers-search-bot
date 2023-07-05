import logging
import re
from os import getenv
from time import time

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, CommandHelp
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineQuery, InlineQueryResultCachedSticker, ChatActions
from aiogram.utils import executor
from aiogram.utils.exceptions import InvalidQueryID

from data.db_session import create_session, global_init
from data.search_data import SearchData
from data.set_links import SetLink
from data.sticker_sets import StickerSet
from data.stickers import Sticker
from data.user_sets import UserSet
from search import Search, clear_q

logging.basicConfig(level=logging.INFO)

bot = Bot(token=getenv("TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class NewSetState(StatesGroup):
    title = State()
    sticker = State()
    prompt = State()


@dp.inline_handler(state="*")
async def handle_inline_query(query: InlineQuery):
    q = query.query
    start = time()
    results = Search(q, query.from_user.id).get_results()
    logging.info("SEARCH TIME: %s", time() - start)
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


# @dp.chosen_inline_handler(state="*")
# async def handle_chosen_inline_query(chosen_inline_result: ChosenInlineResult):
#     pass


@dp.message_handler(CommandStart(re.compile(r'add_set-([a-zA-Z]+)')), state="*")
async def cmd_start_add_set(message: types.Message):
    link_code = message.text.split("-")[1]
    session = create_session()
    link = session.query(SetLink).filter(SetLink.code == link_code).first()
    if not link:
        await message.answer("You used a link to add a new set, but the specified link does not exist")
        return
    buttons = [
        types.InlineKeyboardButton(text="Yes, add this set", callback_data=f"add_set-{link.set_id}"),
        types.InlineKeyboardButton(text="No, thanks", callback_data="add_set-0")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer(f'You used a link to add a *{link.set.title}* set. Are you sure you want to continue?',
                         reply_markup=keyboard, parse_mode="markdown")


@dp.callback_query_handler(lambda c: c.data.startswith("add_set-"), state="*")
async def callback_add_set(callback: types.CallbackQuery):
    set_id = int(callback.data.split("-")[1])
    await callback.message.edit_reply_markup()
    if set_id == 0:
        await callback.answer("Set adding cancelled")
        return
    session = create_session()
    sticker_set = session.query(StickerSet).get(set_id)
    if not sticker_set:
        await callback.answer("Sorry, this set no longer exists", show_alert=True)
        return
    await callback.answer("Adding the set...")
    await bot.send_chat_action(callback.from_user.id, ChatActions.TYPING)

    sticker_set.user_sets.append(UserSet(user_id=callback.from_user.id))
    session.commit()

    await bot.send_message(callback.from_user.id, "Set successfully added!")


@dp.callback_query_handler(lambda c: c.data.startswith("share_set-"), state="*")
async def callback_share_set(callback: types.CallbackQuery):
    set_id = int(callback.data.split("-")[1])
    await callback.message.edit_reply_markup()
    session = create_session()
    sticker_set = session.query(StickerSet).get(set_id)
    if not sticker_set:
        await callback.answer("Sorry, this set no longer exists", show_alert=True)
        return
    await callback.answer("Creating the link...")

    new_link = SetLink()
    sticker_set.set_links.append(new_link)
    session.commit()

    keyboard = types.InlineKeyboardMarkup()
    bot_info = await bot.me

    keyboard.add(types.InlineKeyboardButton(text="Turn on notifications",
                                            callback_data=f"notifications_on-{new_link.code}"))
    await bot.send_message(callback.from_user.id, f"Here is a link for adding the {sticker_set.title} set. "
                                                  f"You can now share it with your friends.\n\n"
                                                  f"https://t.me/{bot_info.username}?"
                                                  f"start=add\\_set-{new_link.code}\n\n"
                                                  f"*If you would like to receive notifications "
                                                  f"when someone adds your set, tap the button below.* "
                                                  f"You can view a full list of your links by sending "
                                                  f"/links command", reply_markup=keyboard, parse_mode="markdown")


@dp.callback_query_handler(lambda c: c.data.startswith("notifications_on-"), state="*")
async def callback_notifications_on_for_set(callback: types.CallbackQuery):
    link_code = callback.data.split("-")[1]
    await callback.message.edit_reply_markup()
    session = create_session()
    link = session.query(SetLink).filter(SetLink.code == link_code)
    if not link:
        await callback.answer("Sorry, this link no longer exists", show_alert=True)
        return
    await callback.answer("Enabling notifications...")

    link.notifications = True
    session.commit()
    await bot.send_message(callback.from_user.id, "Notifications enabled! You can disable them in the "
                                                  "list of your links by sending /links command")


@dp.message_handler(CommandStart(), state="*")
async def cmd_start(message: types.Message):
    bot_info = await bot.me
    await message.answer(f'Hi!\n'
                         f'This bot will help you find your stickers in inline mode. '
                         f'At first you should provide descriptions for every sticker you want to '
                         f'add to search results.\n\n'
                         f'*/new — add sticker to search index. Use this command if you want to add a description '
                         f'for sticker.*\n\n'
                         f'Stickers\' descriptions are collected into _sticker sets_. By default, '
                         f'stickers are kept in a default sticker set, unique for every user.\n\n'
                         f'*/set — create a new sticker set (you will be asked to send stickers '
                         f'and descriptions for it)*.\n\n'
                         f'You can share all your sticker sets except for the default set with other users by '
                         f'sending them the link to add your sticker set.\n\n'
                         f'*/share — create a link for sharing a sticker set.*\n\n'
                         f'To search for a sticker in any Telegram chat, just type "@{bot_info.username}" '
                         f'in the message input field and start typing your query. Sticker suggestions will '
                         f'appear above if there are any.\n\n'
                         f'*/help — all available bot commands.*\n\n'
                         f'_If you have any questions or suggestions, feel free to contact @nawinds!_\n\n'
                         f'[Source code of this bot](https://github.com/nawinds/inline-stickers-search-bot)',
                         parse_mode="markdown", disable_web_page_preview=True)


@dp.message_handler(CommandHelp(), state="*")
async def cmd_start(message: types.Message):
    await message.answer(f'Here is a list of available bot commands:\n\n'
                         f'/new — add sticker to search index. Use this command if you want to add a description '
                         f'for sticker.\n'
                         f'/set — create a new sticker set (you will be asked to send stickers '
                         f'and descriptions for it).\n'
                         f'/share — create a link for sharing a sticker set.\n'
                         f'/help — all available bot commands.\n'
                         f'_If you have any questions or suggestions, feel free to contact @nawinds!_\n\n'
                         f'[Source code of this bot](https://github.com/nawinds/inline-stickers-search-bot)',
                         parse_mode="markdown", disable_web_page_preview=True)


@dp.message_handler(Command('new'))
async def cmd_new(message: types.Message):
    await NewSetState.sticker.set()
    await message.answer('Please send a sticker to add it to search results')


@dp.message_handler(Command('set'))
async def cmd_set(message: types.Message):
    await NewSetState.title.set()
    await message.answer('Please send a title for the new set')


@dp.message_handler(Command('finish'), state=NewSetState.prompt)
async def process_set_prompt_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sticker_unique_id = data.get('sticker_unique_id')
    sticker_file_id = data.get('sticker_file')
    set_id = data.get('set_id')
    prompts = data.get('prompts')
    session = create_session()
    sticker = session.get(Sticker, sticker_unique_id)
    if not sticker:
        sticker = Sticker(sticker_unique_id=sticker_unique_id, sticker_file_id=sticker_file_id)
        session.add(sticker)
        session.commit()
    default_set = False
    if not set_id:
        default_set = True
        sticker_set = session.query(StickerSet).filter(StickerSet.owner_id == message.from_user.id,
                                                       StickerSet.default == True).first()
        if not sticker_set:
            sticker_set = StickerSet(title="Default sticker set", owner_id=message.from_user.id, default=True)
            session.add(sticker_set)
            sticker_set.user_sets.append(UserSet(user_id=message.from_user.id))
            session.commit()
        set_id = sticker_set.id

    for p in prompts:
        session.add(SearchData(sticker_unique_id=sticker_unique_id, keyword=p, set_id=set_id))
    session.commit()
    await state.update_data(prompts=[])
    if default_set:
        await state.finish()
        await message.answer("Sticker saved")
    else:
        await NewSetState.sticker.set()
        await message.answer("Sticker saved. Now send another sticker. If you don't want "
                             "to add another sticker to this set, send /finish_set")


@dp.message_handler(state=NewSetState.title)
async def process_set_title(message: types.Message, state: FSMContext):
    session = create_session()
    new_set = StickerSet(owner_id=message.from_user.id, title=message.text)
    session.add(new_set)
    session.commit()
    await state.update_data(title=message.text, set_id=new_set.id)
    await NewSetState.sticker.set()
    await message.answer('Please send a sticker for the new set')


@dp.message_handler(state=NewSetState.sticker, content_types=["sticker"])
async def process_set_sticker(message: types.Message, state: FSMContext):
    sticker_file = message.sticker.file_id
    sticker_unique_id = message.sticker.file_unique_id
    await state.update_data(sticker_file=sticker_file, sticker_unique_id=sticker_unique_id)
    await message.answer("Send a prompt for this sticker. To finish, send /finish")
    await NewSetState.prompt.set()


@dp.message_handler(state=NewSetState.prompt)
async def process_set_prompt(message: types.Message, state: FSMContext):
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
    await message.answer("Send a prompt for this sticker. To finish, send /finish")
    await NewSetState.prompt.set()


@dp.message_handler(Command('finish_set'), state=NewSetState.sticker)
async def cmd_finish_set(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Ok. Your set is now saved")


@dp.message_handler(Command('share'))
async def cmd_share(message: types.Message):
    buttons = [types.InlineKeyboardButton(text=sticker_set.title, callback_data=f"share_set-{sticker_set.id}")
               for sticker_set in create_session().query(StickerSet).
               filter(StickerSet.owner_id == message.from_user.id, StickerSet.default == False)]

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer(f'Please choose a sticker set you would like to share and I will generate a link',
                         reply_markup=keyboard, parse_mode="markdown")


#
# @dp.message_handler(Command('finish'), state=NewStickerState.prompt)
# async def process_prompt_finish(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     sticker_unique_id = data.get('sticker_unique_id')
#     sticker_file = data.get('sticker_file')
#     prompts = data.get('prompts')
#     await state.finish()
#     session = create_session()
#     sticker = session.get(Sticker, sticker_unique_id)
#     if not sticker:
#         sticker = Sticker(sticker_unique_id=sticker_unique_id, sticker_file_id=sticker_file)
#         session.add(sticker)
#         session.commit()
#     for p in prompts:
#         session.add(SearchData(sticker_unique_id=sticker_unique_id, keyword=p, user_id=message.from_user.id))
#     session.commit()
#     await message.answer("Sticker saved")


# @dp.message_handler(state=NewStickerState.sticker, content_types=["sticker"])
# async def process_new_sticker(message: types.Message, state: FSMContext):
#     sticker_file = message.sticker.file_id
#     sticker_unique_id = message.sticker.file_unique_id
#     await state.update_data(sticker_file=sticker_file, sticker_unique_id=sticker_unique_id)
#
#     # # Fetch stickers from selected pack
#     # stickers = await bot.get_sticker_set(pack_name)
#     # if not stickers.stickers:
#     #     await message.answer('No stickers found in the specified pack.')
#     #     await state.finish()
#     #     return
#     await message.answer("Send a prompt for this sticker. To finish, send /finish")
#     await NewStickerState.prompt.set()


# @dp.message_handler(state=NewStickerState.prompt)
# async def process_sticker_prompt(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     prompts = data.get('prompts', [])
#     new_prompt = clear_q(message.text)
#     await state.update_data(prompts=prompts + [new_prompt])
#     with open("known_words.txt", encoding="utf-8") as read_file:
#         known_words = read_file.read().split()
#     for i in new_prompt.split():
#         if i not in known_words:
#             known_words.append(i)
#     with open("known_words.txt", "w", encoding="utf-8") as write_file:
#         write_file.write(" ".join(known_words))
#     await message.answer("Send a prompt for this sticker. To finish, send /finish")
#     await NewStickerState.prompt.set()


if __name__ == '__main__':
    global_init("data/db/main.db")
    executor.start_polling(dp, skip_updates=True)
