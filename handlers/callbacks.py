from string import Template

from aiogram import Router
from aiogram import types, F
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from data.db_session import create_session
from data.set_links import SetLink
from data.sticker_sets import StickerSet
from data.user_sets import UserSet
from instances import bot

callbacks = Router()
callbacks.message.filter(F.chat.type == "private")
I18nContext.gettext = I18nContext.get


@callbacks.callback_query(lambda c: c.data.startswith("add_set-"), StateFilter("*"))
async def add_set(callback: types.CallbackQuery, i18n: I18nContext):
    await callback.message.edit_reply_markup()
    set_id = int(callback.data.split("-")[1].split(",")[0])
    if set_id == 0:
        await callback.answer(i18n.gettext("callbacks.add_set.cancelled"))
        return
    notifications = bool(int(callback.data.split("-")[1].split(",")[1]))

    session = create_session()
    sticker_set = session.get(StickerSet, set_id)
    if not sticker_set:
        await callback.answer(i18n.gettext("callbacks.global.set_not_found"),
                              show_alert=True)
        return
    await callback.answer(i18n.gettext("callbacks.add_set.adding"))

    sticker_set.user_sets.append(UserSet(user_id=callback.from_user.id))
    session.commit()
    if notifications:
        await bot.send_message(
            sticker_set.owner_id,
            Template(i18n.gettext("callbacks.add_set.notification"))
            .substitute(title=sticker_set.title),
            parse_mode="markdown")
    await bot.send_message(callback.from_user.id, i18n.gettext("callbacks.add_set.added"))


@callbacks.callback_query(lambda c: c.data.startswith("share_set-"), StateFilter("*"))
async def share_set(callback: types.CallbackQuery, i18n: I18nContext):
    set_id = int(callback.data.split("-")[1])
    await callback.message.edit_reply_markup()
    session = create_session()
    sticker_set = session.get(StickerSet, set_id)
    if not sticker_set:
        await callback.answer(i18n.gettext("callbacks.global.set_not_found"),
                              show_alert=True)
        return
    await callback.answer()

    link = session.query(SetLink).filter(SetLink.set_id == set_id).first()
    if not link:
        link = SetLink()
        sticker_set.set_links.append(link)
        session.commit()

    bot_info = await bot.get_me()
    builder = InlineKeyboardBuilder()
    if sticker_set.owner_id == callback.from_user.id:
        if link.notifications:
            toggle_word = i18n.gettext("callbacks.global.disable")
        else:
            toggle_word = i18n.gettext("callbacks.global.enable")
        builder.button(text=toggle_word + i18n.gettext("callbacks.global.notifications"),
                       callback_data=f"notifications_"
                                     f"{'off' if link.notifications else 'on'}-"
                                     f"{link.code}")
    await bot.send_message(callback.from_user.id,
                           i18n.gettext("callbacks.share_set.link_text",
                                        title=sticker_set.title,
                                        username=bot_info.username,
                                        code=link.code), reply_markup=builder.as_markup(),
                           parse_mode="markdown")


async def notifications_toggle(callback: types.CallbackQuery, i18n: I18nContext, enable: bool):
    link_code = callback.data.split("-")[1]
    session = create_session()
    link = session.query(SetLink).filter(SetLink.code == link_code).first()
    if not link:
        await callback.answer(i18n.gettext("callbacks.notifications.link_not_found"), show_alert=True)
        return
    await callback.answer()

    link.notifications = enable
    session.commit()

    builder = InlineKeyboardBuilder()
    toggle_word = i18n.gettext("callbacks.global.disable") if enable else i18n.gettext("callbacks.global.enable")
    builder.button(text=toggle_word + i18n.gettext("callbacks.global.notifications"),
                   callback_data=f"notifications_{'off' if enable else 'on'}-{link.code}")

    await callback.message.edit_reply_markup(callback.message.message_id, builder.as_markup())
    await bot.send_message(
        callback.from_user.id,
        i18n.gettext("callbacks.notifications.notifications_capitalized") +
        i18n.gettext("callbacks.notifications.enabed") if enable else i18n.gettext(
            "callbacks.notifications.notifications_capitalized") + i18n.gettext("callbacks.notifications.disabed")
    )


@callbacks.callback_query(lambda c: c.data.startswith("notifications_on-"), StateFilter("*"))
async def notifications_on_for_set(callback: types.CallbackQuery, i18n: I18nContext):
    await notifications_toggle(callback, i18n, True)


@callbacks.callback_query(lambda c: c.data.startswith("notifications_off-"), StateFilter("*"))
async def notifications_off_for_set(callback: types.CallbackQuery, i18n: I18nContext):
    await notifications_toggle(callback, i18n, False)
