import logging
from time import time

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import InlineQuery, InlineQueryResultCachedSticker, ChosenInlineResult
from aiogram_i18n import I18nContext

from modules.search import Search

inline = Router()
I18nContext.gettext = I18nContext.get


@inline.inline_query(StateFilter("*"))
async def handle_inline_query(query: InlineQuery, i18n: I18nContext) -> None:
    q = query.query
    start = time()
    results = Search(q, query.from_user.id).get_results()
    logging.info("SEARCH TIME: %s", time() - start)
    inline_results = []
    if results:
        for i in range(len(results)):
            inline_results.append(
                InlineQueryResultCachedSticker(
                    id=str(i),
                    sticker_file_id=results[i]
                )
            )

        await query.answer(inline_results, cache_time=60, is_personal=True)
    else:
        await query.answer([], cache_time=0, is_personal=True,
                           switch_pm_text=i18n.gettext("inline.handle.not_found"),
                           switch_pm_parameter="inline")


@inline.chosen_inline_result(StateFilter("*"))
async def handle_chosen_inline_query(chosen_inline_result: ChosenInlineResult) -> None:
    logging.info("Chosen result with id %s", chosen_inline_result.result_id)
