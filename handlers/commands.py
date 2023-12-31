from typing import List

from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_i18n import I18nContext

from db_models.db_session import create_session
from db_models.search_data import SearchData
from db_models.set_links import SetLink
from db_models.sticker_sets import StickerSet
from db_models.stickers import Sticker
from db_models.user_sets import UserSet
from modules.instances import NewSetState, bot, escape_md

commands = Router()
commands.message.filter(F.chat.type == "private")
I18nContext.gettext = I18nContext.get


@commands.message(F.text.regexp(r'/start add_set-([a-zA-Z]+)'))
async def cmd_start_add_set(message: types.Message, i18n: I18nContext) -> None:
    link_code = message.text.split("-")[1]
    session = create_session()
    link = session.query(SetLink).filter(SetLink.code == link_code).first()
    if not link:
        await message.answer(i18n.gettext("commands.start_deep.not_found"))
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=i18n.gettext("commands.start_deep.yes"),
                                               callback_data=f"add_set-{link.set_id},{int(link.notifications)}"),
                          InlineKeyboardButton(text=i18n.gettext("commands.start_deep.no"),
                                               callback_data="add_set-0")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(i18n.gettext("commands.start_deep.reply_text", link_set_title=escape_md(link.set.title)),
                         reply_markup=keyboard, parse_mode="markdown")


@commands.message(CommandStart(), StateFilter(None))
async def cmd_start(message: types.Message, i18n: I18nContext) -> None:
    bot_info = await bot.get_me()
    await message.answer(i18n.gettext("commands.start.hello_text", username=escape_md(bot_info.username)),
                         parse_mode="markdown", disable_web_page_preview=True)


@commands.message(Command('help'), StateFilter(None))
async def cmd_help(message: types.Message, i18n: I18nContext) -> None:
    await message.answer(i18n.gettext("commands.help.help_text"),
                         parse_mode="markdown", disable_web_page_preview=True)


@commands.message(Command('en'), StateFilter(None))
async def cmd_en(message: types.Message, state: FSMContext) -> None:
    await state.update_data(locale="en")
    await message.answer("Language set to English")


@commands.message(Command('ru'), StateFilter(None))
async def cmd_ru(message: types.Message, state: FSMContext) -> None:
    await state.update_data(locale="ru")
    await message.answer("Язык сменён на русский")


@commands.message(Command('new'), StateFilter(None))
async def cmd_new(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    await state.set_state(NewSetState.sticker)
    await message.answer(i18n.gettext("commands.new"),
                         parse_mode="markdown")


@commands.message(Command('set'), StateFilter(None))
async def cmd_set(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    await state.set_state(NewSetState.title)
    await message.answer(i18n.gettext("commands.set"),
                         parse_mode="markdown")


@commands.message(Command('pack'), StateFilter(None))
async def cmd_pack(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    await state.set_state(NewSetState.sticker)
    await state.update_data(set_base_type="pack")
    await message.answer(i18n.gettext("commands.pack"),
                         parse_mode="markdown")


async def send_next_pack_sticker(message: types.Message, state: FSMContext,
                                 pack_stickers: List[types.sticker.Sticker]) -> None:
    data = await state.get_data()
    await message.answer_sticker(pack_stickers[int(data.get("next_sticker"))].file_id)
    sticker_file = pack_stickers[int(data.get("next_sticker"))].file_id
    sticker_unique_id = pack_stickers[int(data.get("next_sticker"))].file_unique_id
    await state.update_data(sticker_file=sticker_file, sticker_unique_id=sticker_unique_id,
                            next_sticker=int(data.get("next_sticker")) + 1)


@commands.message(Command('skip'), NewSetState.prompt)
async def process_set_prompt_skip(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    data = await state.get_data()
    if data.get('set_base_type') == "pack":
        sticker_pack = await bot.get_sticker_set(data.get("pack_name"))
        pack_stickers = sticker_pack.stickers
        if len(pack_stickers) > int(data.get("next_sticker")):
            await message.answer(i18n.gettext("commands.process_set_prompt_skip.pack"))
            await send_next_pack_sticker(message, state, pack_stickers)
            return
        await message.answer(i18n.gettext("commands.process_set_prompt_skip.finish_set"))
        locale = data.get("locale")
        await state.clear()
        await state.update_data(locale=locale)


@commands.message(Command('finish'), NewSetState.prompt)
async def process_set_prompt_finish(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
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
        locale = data.get("locale")
        await state.clear()
        await state.update_data(locale=locale)
        await message.answer(i18n.gettext("commands.process_set_prompt_finish.default_saved"))
    else:
        if data.get('set_base_type') == "pack":
            sticker_pack = await bot.get_sticker_set(data.get("pack_name"))
            pack_stickers = sticker_pack.stickers
            if len(pack_stickers) > int(data.get("next_sticker")):
                await message.answer(i18n.gettext("commands.process_set_prompt_finish.pack"))
                await send_next_pack_sticker(message, state, pack_stickers)
            else:
                await message.answer(i18n.gettext("commands.process_set_prompt_skip.finish_set"))
                locale = data.get("locale")
                await state.clear()
                await state.update_data(locale=locale)
            return
        await state.set_state(NewSetState.sticker)
        await message.answer(i18n.gettext("commands.process_set_prompt_finish.sticker_saved"))


@commands.message(Command('finish_set'), NewSetState.sticker)
async def cmd_finish_set(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    data = await state.get_data()
    locale = data.get("locale")
    await state.clear()
    await state.update_data(locale=locale)
    await message.answer(i18n.gettext("commands.finish_set"))


@commands.message(Command('cancel'), StateFilter(NewSetState))
async def cmd_cancel(message: types.Message, state: FSMContext, i18n: I18nContext) -> None:
    data = await state.get_data()
    locale = data.get("locale")
    await state.clear()
    await state.update_data(locale=locale)
    await message.reply(i18n.gettext("commands.cancel"))


@commands.message(Command('share'))
async def cmd_share(message: types.Message, i18n: I18nContext) -> None:
    sets = create_session().query(StickerSet). \
        filter(StickerSet.owner_id == message.from_user.id, StickerSet.default == False).all()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=sticker_set.title,
                                               callback_data=f"share_set-{sticker_set.id}")]
                         for sticker_set in sets]
    )

    if not sets:
        await message.answer(i18n.gettext("commands.share.no_sets"))
        return
    await message.answer(i18n.gettext("commands.share.choose"),
                         reply_markup=keyboard, parse_mode="markdown")
