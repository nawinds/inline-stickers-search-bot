��    +      t  ;   �      �     �     �     �     
     &     E     ^     v     �     �     �  &   �  1        L     j     z     �     �     �  0   �  '   �  0     +   K  %   w     �     �     �     �     �          &     E      ]  "   ~     �      �  "   �          !  !   @     b     r  �  �     i
     �
  )   �
     �
  '   �
     �
                     ;     D  !   L     n  �   }     n       �  �  ]   6  o   �       �     p   �  G   \  �   �  O     N   �  L     �  k  
   N  G   Y  S   �     �  6     =   >     |  !   �  7   �  3   �  �   )  C     �   Z     �              !                )                   %       
   	                (   *   "                 '                                    $          &                 #                      +              callbacks.add_set.added callbacks.add_set.adding callbacks.add_set.already_added callbacks.add_set.cancelled callbacks.add_set.notification callbacks.global.disable callbacks.global.enable callbacks.global.notifications callbacks.global.set_not_found callbacks.notifications.disabed callbacks.notifications.enabed callbacks.notifications.link_not_found callbacks.notifications.notifications_capitalized callbacks.share_set.link_text commands.cancel commands.finish_set commands.help.help_text commands.new commands.pack commands.process_set_prompt_finish.default_saved commands.process_set_prompt_finish.pack commands.process_set_prompt_finish.sticker_saved commands.process_set_prompt_skip.finish_set commands.process_set_prompt_skip.pack commands.set commands.share.choose commands.share.no_sets commands.start.hello_text commands.start_deep.no commands.start_deep.not_found commands.start_deep.reply_text commands.start_deep.yes data_processing.set_prompt.limit data_processing.set_prompt.success data_processing.set_sticker data_processing.set_sticker.pack data_processing.set_title.existing data_processing.set_title.limit data_processing.set_title.pack data_processing.set_title.success default_handler inline.handle.not_found Project-Id-Version: Inline stickers bot
PO-Revision-Date: 2023-07-30 22:20+0300
Last-Translator: Nikita Aksenov <me@nawinds.top>
Language-Team: Nikita Aksenov
Language: en
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
X-Generator: Poedit 3.3.2
X-Poedit-Basepath: ../../..
X-Poedit-KeywordsList: i18n.get(%)
X-Poedit-SearchPath-0: handlers
X-Poedit-SearchPath-1: main.py
X-Poedit-SearchPath-2: db_models
X-Poedit-SearchPath-3: modules
 Set was added successfully! Adding set... This set is already added to your account Set adding cancelled Your *{title}* set was added by someone Turn off Turn on  notifications Sorry, this set no longer exists disabled enabled Sorry, this link no longer exists Notifications  Here is a link for adding the {title} set. You can now share it with your friends.

https://t.me/{username}?start=add\_set-{code}

*You can receive notifications when someone adds your set. To enable/disable them, just tap the button below* Action cancelled Ok. Your set is now saved Here is a list of available bot commands:

/new — add sticker to search index. Use this command if you want to add a description for sticker.
/set — create a new sticker set (you will be asked to send stickers and descriptions for it).
/pack — create a new sticker set based on the sticker pack (bot will send stickers from the sticker pack one by one).
/share — create a link for sharing a sticker set.
/help — all available bot commands.
/ru — переключить язык на русский.

_If you have any questions or suggestions, feel free to contact @nawinds!_

[Source code of this bot](https://github.com/nawinds/inline-stickers-search-bot) Please send a sticker to add it to search results.
_To cancel adding a sticker, send /cancel_ Please send one sticker from the sticker pack you would like to add.
_To cancel creating the set, send /cancel_ Sticker saved Sticker saved. Now send a description for the sticker below.
If you would like to skip this sticker (not to add it to your set), send /skip.
If you don't want to continue adding stickers to this set, send /finish_set Sticker saved. Now send another sticker. 
If you don't want to add another sticker to this set, send /finish_set There are no more stickers in this sticker pack. Stickers set is saved! Sticker skipped. Now send a description for the sticker below.
If you would like to skip this sticker (not to add it to your set), send /skip.
If you don't want to continue adding stickers to this set, send /finish_set Please send a title for the new set.
_To cancel creating the set, send /cancel_ Please choose a sticker set you would like to share and I will generate a link You don't have sticker sets that you can share. Create one with /set command Hi!
This bot will help you find your stickers in inline mode. At first you should provide descriptions for every sticker you want to add to search results.

*/new — add sticker to search index. Use this command if you want to add a description for sticker.*

Stickers\' descriptions are collected into _sticker sets_. By default, stickers are kept in a default sticker set, unique for every user.

*/set — create a new sticker set (you will be asked to send stickers and descriptions for it).*
*/pack — create a new sticker set based on the sticker pack (bot will send stickers from the sticker pack one by one).*

You can share all your sticker sets except for the default set with other users by sending them the link to add your sticker set.

*/share — create a link for sharing a sticker set.*

To search for a sticker in any Telegram chat, just type "@{username}" in the message input field and start typing your query. Sticker suggestions will appear above if there are any.

*/help — all available bot commands.*
*/ru — переключить язык на русский.*

_If you have any questions or suggestions, feel free to contact @nawinds!_

[Source code of this bot](https://github.com/nawinds/inline-stickers-search-bot) No, thanks You used a link to add a new set, but the specified link does not exist You used a link to add a *{link_set_title}* set. Are you sure you want to continue? Yes, add this set This prompt exceeds 1000 characters. Please, try again Send another prompt for this sticker. To finish, send /finish Send a prompt for this sticker Send a title for this sticker set A set with this title already exists. Please, try again This title exceeds 50 characters. Please, try again Sticker set created! Now I will start sending stickers from the sticker pack one by one. There is the first sticker below. Please, send a description for it.
If you would like to skip this sticker (not to add it to the set), send /skip. Sticker set created! Please send the first sticker for your new set I am sorry, but I haven't understood your request. Please act in accordance with bot instructions. To view the list of basic bot commands, send /help Add stickers to search >> 