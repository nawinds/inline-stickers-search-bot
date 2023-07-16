import re

from aiogram import Router
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from instances import NewSetState, bot

from data.db_session import create_session
from data.search_data import SearchData
from data.set_links import SetLink
from data.sticker_sets import StickerSet
from data.stickers import Sticker
from data.user_sets import UserSet

commands = Router()


@commands.message(CommandStart(re.compile(r'add_set-([a-zA-Z]+)')))
async def cmd_start_add_set(message: types.Message):
    link_code = message.text.split("-")[1]
    session = create_session()
    link = session.query(SetLink).filter(SetLink.code == link_code).first()
    if not link:
        await message.answer("You used a link to add a new set, but the specified link does not exist")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="Yes, add this set",
                   callback_data=f"add_set-{link.set_id},{int(link.notifications)}")
    builder.button(text="No, thanks", callback_data="add_set-0")
    builder.adjust(1)

    await message.answer(f'You used a link to add a *{link.set.title}* set. Are you sure you want to continue?',
                         reply_markup=builder.as_markup(), parse_mode="markdown")


@commands.message(CommandStart(), StateFilter(None))
async def cmd_start(message: types.Message):
    bot_info = await bot.get_me()
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


@commands.message(Command('help'), StateFilter(None))
async def cmd_help(message: types.Message):
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


@commands.message(Command('new'), StateFilter(None))
async def cmd_new(message: types.Message, state: FSMContext):
    await state.set_state(NewSetState.sticker)
    await message.answer('Please send a sticker to add it to search results.\n'
                         '_To cancel adding a sticker, send /cancel_',
                         parse_mode="markdown")


@commands.message(Command('set'), StateFilter(None))
async def cmd_set(message: types.Message, state: FSMContext):
    await state.set_state(NewSetState.title)
    await message.answer('Please send a title for the new set.\n'
                         '_To cancel creating the set, send /cancel_',
                         parse_mode="markdown")


@commands.message(Command('finish'), NewSetState.prompt)
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
        await state.clear()
        await message.answer("Sticker saved")
    else:
        await state.set_state(NewSetState.sticker)
        await message.answer("Sticker saved. Now send another sticker. If you don't want "
                             "to add another sticker to this set, send /finish_set")


@commands.message(Command('finish_set'), NewSetState.sticker)
async def cmd_finish_set(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ok. Your set is now saved")


@commands.message(Command('cancel'), StateFilter(NewSetState))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.reply("Action cancelled")


@commands.message(Command('share'))
async def cmd_share(message: types.Message):
    builder = InlineKeyboardBuilder()

    for sticker_set in create_session().query(StickerSet). \
            filter(StickerSet.owner_id == message.from_user.id, StickerSet.default == False):
        builder.button(text=sticker_set.title, callback_data=f"share_set-{sticker_set.id}")

    builder.adjust(1)

    if not builder.buttons:
        await message.answer("You don't have sticker sets that you can share. "
                             "Create one with /set command")
        return
    await message.answer(f'Please choose a sticker set you would like to share and I will generate a link',
                         reply_markup=builder.as_markup(), parse_mode="markdown")
