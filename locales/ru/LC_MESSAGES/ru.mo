��    )      d  ;   �      �     �     �     �     �          %     >     V     u     �     �  &   �  1   �     ,     J     Z     n     �     �  0   �  '   �  0   �  +   +  %   W     }     �     �     �     �     �          %      =  "   ^     �      �     �     �  !   �       �  7  '   7
      _
  @   �
  .   �
  ;   �
     ,     ?     P  H   h     �     �  N   �     $  y  <  !   �     �    �  �     �   �     �  �  �  �   `  _   B  �  �  �   /  �   �  �   r  k       w   �   �   �   +!  &   �!  �   �!  �   �"  D   t#  Q   �#  �   $  �  �$  o   B&  0   �&              !                (                   %       
   	                '       "                                                      $          &                 #                      )              callbacks.add_set.added callbacks.add_set.adding callbacks.add_set.already_added callbacks.add_set.cancelled callbacks.add_set.notification callbacks.global.disable callbacks.global.enable callbacks.global.notifications callbacks.global.set_not_found callbacks.notifications.disabed callbacks.notifications.enabed callbacks.notifications.link_not_found callbacks.notifications.notifications_capitalized callbacks.share_set.link_text commands.cancel commands.finish_set commands.help.help_text commands.new commands.pack commands.process_set_prompt_finish.default_saved commands.process_set_prompt_finish.pack commands.process_set_prompt_finish.sticker_saved commands.process_set_prompt_skip.finish_set commands.process_set_prompt_skip.pack commands.set commands.share.choose commands.share.no_sets commands.start.hello_text commands.start_deep.no commands.start_deep.not_found commands.start_deep.reply_text commands.start_deep.yes data_processing.set_prompt.limit data_processing.set_prompt.success data_processing.set_sticker data_processing.set_sticker.pack data_processing.set_title.limit data_processing.set_title.pack data_processing.set_title.success inline.handle.not_found Project-Id-Version: Inline stickers bot
PO-Revision-Date: 2023-07-26 12:15+0300
Last-Translator: Nikita Aksenov <me@nawinds.top>
Language-Team: Nikita Aksenov
Language: ru
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 3.3.2
X-Poedit-Basepath: ../../..
X-Poedit-KeywordsList: i18n.get(%)
X-Poedit-SearchPath-0: data
X-Poedit-SearchPath-1: handlers
X-Poedit-SearchPath-2: instances.py
X-Poedit-SearchPath-3: main.py
X-Poedit-SearchPath-4: search.py
 Сет успешно добавлен! Добавление сета... Этот сет уже добавлен в Ваш аккаунт Добавление сета отменено Ваш сет *{title}* был кем-то добавлен Выключить Включить  уведомления Извините, этот сет больше не существует выключены включены Простите, этой ссылки больше не существует Уведомления  Ниже ссылка для добавления сета {title}. Вы можете поделиться ей с друзьями.

https://t.me/{username}?start=add\_set-{code}

*Вы можете получать уведомления, когда кто-то добавляет Ваш сет. Включать и выключать их можно кнопкой ниже* Действие отменено Ок. Сет сохранён Ниже список доступных команд:

/new — добавить стикер в поиск. Используйте эту команду, если Вы хотите добавить описание для стикера.
/set — создать новый сет стикеров (Вам будет необходимо отправить добавляемые стикеры и описания к ним).
/share — создать ссылку для добавления сета стикеров.
/help — все доступные команды бота.

_По всем вопросам и предложениям Вы всегда можете написать @nawinds!_

[Исходный код бота](https://github.com/nawinds/inline-stickers-search-bot) Пожалуйста, отправьте стикер, чтобы добавить его в поисковую выдачу.
_Чтобы отменить добавление стикера, отправьте /cancel_ Пришлите один стикер из стикерпака, который Вы хотите добавить.
_Чтобы отменить создание сета, отправьте /cancel_ Стикер сохранён Стикер сохранён. Теперь отправьте описание для стикера ниже. 
Если Вы хотите пропустить этот стикер и не добавлять его в стикерпак, отправьте /skip. 
Если Вы больше не хотите добавлять стикеры в этот сет, отправьте /finish_set Стикер сохранён. Теперь отправьте следующий стикер. Если Вы больше не хотите добавлять стикеры в этот сет, отправьте /finish_set Больше стикеров в этом стикерпаке нет. Сет сохранён! Стикер пропущен. Теперь отправьте описание для стикера ниже. 
Если Вы хотите пропустить этот стикер и не добавлять его в стикерпак, отправьте /skip. 
Если Вы больше не хотите добавлять стикеры в этот сет, отправьте /finish_set Придумайте название для своего нового сета.
_Чтобы отменить создание сета, отправьте /cancel_ Пожалуйста, выберите сет стикеров, которым Вы хотите поделиться и я сгенерирую ссылку У Вас нет сетов стикеров, которыми можно поделиться. Создайте такой сет командой /set Привет!
Этот бот позволяет искать стикеры в инлайн-режиме. Для начала Вам нужно написать описания для каждого стикера, который Вы хотите добавить в поисковую выдачу.

*/new — добавить стикер в поиск. Используйте эту команду, если Вы хотите добавить описание для стикера.*

Описания стикеров собираются в _сеты стикеров_. По умолчанию, стикеры добавляются в дефолтный сет стикеров, уникальный для каждого пользователя.

*/set — создать новый сет стикеров (Вам будет необходимо отправить добавляемые стикеры и описания к ним)*.

Вы можете поделиться всеми своими сетами за исключением дефолтного с другими пользователями, отправив им ссылку на добавление Вашего сета стикеров.

*/share — создать ссылку для добавления сета стикеров.*

Чтобы найти стикер в любом чате Telegram, введите "@{username}" в поле нового сообщения и начните писать свой запрос. Если по Вашему запросу найдутся стикеры, они появятся выше.

*/help — все доступные команды бота.*

_По всем вопросам и предложениям Вы всегда можете написать @nawinds!_

[Исходный код бота](https://github.com/nawinds/inline-stickers-search-bot) Нет, спасибо Вы использовали ссылку для добавления нового сета, но указанная ссылка не существует Вы использовали ссылку для добавления сета *{link_set_title}*. Вы уверены, что хотите продолжить? Да, добавить этот сет Описание не должно быть длиннее 1000 стикеров. Пожалуйста, попробуйте ещё раз Отправьте еще одно описание для этого стикера. Если Вы не хотите добавлять больше описаний для стикера, воспользуйтесь командой /finish Отправьте описание для этого стикера Придумайте описание для этого сета стикеров Название не должно быть длиннее 50 символов. Пожалуйста, попробуйте еще раз Сет стикеров создан! Теперь я буду по очереди присылать Вам стикеры из стикерпака. Ниже пришлю первый стикер. Пожалуйста, придумайте описание для него.
Если Вы хотите пропустить этот стикер и не добавлять его в стикерпак, отправьте /skip. Сет стикеров создан! Отправьте первый стикер для Вашего сета Добавить стикеры в поиск >> 