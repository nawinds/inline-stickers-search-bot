from aiogram import Router
from aiogram import types, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from data.db_session import create_session
from data.search_data import SearchData
from data.set_links import SetLink
from data.sticker_sets import StickerSet
from data.stickers import Sticker
from data.user_sets import UserSet
from instances import NewSetState
from instances import bot

commands = Router()
commands.message.filter(F.chat.type == "private")
I18nContext.gettext = I18nContext.get


@commands.message(F.text.regexp(r'/start add_set-([a-zA-Z]+)'))
async def cmd_start_add_set(message: types.Message, i18n: I18nContext):
    link_code = message.text.split("-")[1]
    session = create_session()
    link = session.query(SetLink).filter(SetLink.code == link_code).first()
    if not link:
        await message.answer(i18n.gettext("commands.start_deep.not_found"))
        return

    builder = InlineKeyboardBuilder()
    builder.button(text=i18n.gettext("commands.start_deep.yes"),
                   callback_data=f"add_set-{link.set_id},{int(link.notifications)}")
    builder.button(text=i18n.gettext("commands.start_deep.no"), callback_data="add_set-0")
    builder.adjust(1)

    await message.answer(i18n.gettext("commands.start_deep.reply_text", link_set_title=link.set.title),
                         reply_markup=builder.as_markup(), parse_mode="markdown")


@commands.message(CommandStart(), StateFilter(None))
async def cmd_start(message: types.Message, i18n: I18nContext):
    bot_info = await bot.get_me()
    await message.answer(i18n.gettext("commands.start.hello_text", username=bot_info.username),
                         parse_mode="markdown", disable_web_page_preview=True)


@commands.message(Command('help'), StateFilter(None))
async def cmd_help(message: types.Message, i18n: I18nContext):
    await message.answer(i18n.gettext("commands.help.help_text"),
                         parse_mode="markdown", disable_web_page_preview=True)


@commands.message(Command('new'), StateFilter(None))
async def cmd_new(message: types.Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(NewSetState.sticker)
    await message.answer(i18n.gettext("commands.new"),
                         parse_mode="markdown")


@commands.message(Command('set'), StateFilter(None))
async def cmd_set(message: types.Message, state: FSMContext, i18n: I18nContext):
    await state.set_state(NewSetState.title)
    await message.answer(i18n.gettext("commands.set"),
                         parse_mode="markdown")


@commands.message(Command('finish'), NewSetState.prompt)
async def process_set_prompt_finish(message: types.Message, state: FSMContext, i18n: I18nContext):
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
        await message.answer(i18n.gettext("commands.process_set_prompt_finish.default_saved"))
    else:
        await state.set_state(NewSetState.sticker)
        await message.answer(i18n.gettext("commands.process_set_prompt_finish.sticker_saved"))


@commands.message(Command('finish_set'), NewSetState.sticker)
async def cmd_finish_set(message: types.Message, state: FSMContext, i18n: I18nContext):
    await state.clear()
    await message.answer(i18n.gettext("commands.finish_set"))


@commands.message(Command('cancel'), StateFilter(NewSetState))
async def cmd_cancel(message: types.Message, state: FSMContext, i18n: I18nContext):
    await state.clear()
    await message.reply(i18n.gettext("commands.cancel"))


@commands.message(Command('share'))
async def cmd_share(message: types.Message, i18n: I18nContext):
    builder = InlineKeyboardBuilder()
    sets = create_session().query(StickerSet). \
        filter(StickerSet.owner_id == message.from_user.id, StickerSet.default == False).all()
    for sticker_set in sets:
        builder.button(text=sticker_set.title, callback_data=f"share_set-{sticker_set.id}")

    builder.adjust(1)
    if not sets:
        await message.answer(i18n.gettext("commands.share.no_sets"))
        return
    await message.answer(i18n.gettext("commands.share.choose"),
                         reply_markup=builder.as_markup(), parse_mode="markdown")
