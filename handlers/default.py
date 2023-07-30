from aiogram import Router, types
from aiogram_i18n import I18nContext

default = Router()
I18nContext.gettext = I18nContext.get


@default.message()
async def default_handler(message: types.Message, i18n: I18nContext) -> None:
    await message.reply(i18n.gettext("default_handler"))
