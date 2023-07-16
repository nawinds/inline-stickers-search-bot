from aiogram import Router
from aiogram import types
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.db_session import create_session
from data.set_links import SetLink
from data.sticker_sets import StickerSet
from data.user_sets import UserSet
from instances import bot

callbacks = Router()


@callbacks.callback_query(lambda c: c.data.startswith("add_set-"), StateFilter("*"))
async def callback_add_set(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()
    set_id = int(callback.data.split("-")[1].split(",")[0])
    if set_id == 0:
        await callback.answer("Set adding cancelled")
        return
    notifications = bool(int(callback.data.split("-")[1].split(",")[1]))

    session = create_session()
    sticker_set = session.get(StickerSet, set_id)
    if not sticker_set:
        await callback.answer("Sorry, this set no longer exists", show_alert=True)
        return
    await callback.answer("Adding the set...")

    sticker_set.user_sets.append(UserSet(user_id=callback.from_user.id))
    session.commit()
    if notifications:
        await bot.send_message(sticker_set.owner_id, f"Your *{sticker_set.title}* set was added by someone",
                               parse_mode="markdown")
    await bot.send_message(callback.from_user.id, "Set successfully added!")


@callbacks.callback_query(lambda c: c.data.startswith("share_set-"), StateFilter("*"))
async def callback_share_set(callback: types.CallbackQuery):
    set_id = int(callback.data.split("-")[1])
    await callback.message.edit_reply_markup()
    session = create_session()
    sticker_set = session.get(StickerSet, set_id)
    if not sticker_set:
        await callback.answer("Sorry, this set no longer exists", show_alert=True)
        return
    await callback.answer()

    link = session.query(SetLink).filter(SetLink.set_id == set_id).first()
    if not link:
        link = SetLink()
        sticker_set.set_links.append(link)
        session.commit()

    bot_info = await bot.me
    builder = InlineKeyboardBuilder()
    if sticker_set.owner_id == callback.from_user.id:
        builder.button(text=f"Turn {'off' if link.notifications else 'on'} notifications",
                       callback_data=f"notifications_"
                                     f"{'off' if link.notifications else 'on'}-"
                                     f"{link.code}")
    await bot.send_message(callback.from_user.id, f"Here is a link for adding the {sticker_set.title} set. "
                                                  f"You can now share it with your friends.\n\n"
                                                  f"https://t.me/{bot_info.username}?"
                                                  f"start=add\\_set-{link.code}\n\n"
                                                  f"*If you would like to receive notifications "
                                                  f"when someone adds your set, tap the button below.* "
                                                  f"You can view a full list of your links by sending "
                                                  f"/links command", reply_markup=builder.as_markup(),
                           parse_mode="markdown")


async def notifications_toggle(callback: types.CallbackQuery, enable: bool):
    link_code = callback.data.split("-")[1]
    session = create_session()
    link = session.query(SetLink).filter(SetLink.code == link_code).first()
    if not link:
        await callback.answer("Sorry, this link no longer exists", show_alert=True)
        return
    await callback.answer()

    link.notifications = enable
    session.commit()

    builder = InlineKeyboardBuilder()

    builder.button(text=f"Turn {'off' if enable else 'on'} notifications",
                   callback_data=f"notifications_{'off' if enable else 'on'}-{link.code}")

    await callback.message.edit_reply_markup(builder.as_markup())
    await bot.send_message(callback.from_user.id, f"Notifications {'enabled' if enable else 'disabled'}!")


@callbacks.callback_query(lambda c: c.data.startswith("notifications_on-"), StateFilter("*"))
async def callback_notifications_on_for_set(callback: types.CallbackQuery):
    await notifications_toggle(callback, True)


@callbacks.callback_query(lambda c: c.data.startswith("notifications_off-"), StateFilter("*"))
async def callback_notifications_off_for_set(callback: types.CallbackQuery):
    await notifications_toggle(callback, False)
