# Telegram Bot Configuration

## 1. Create a Personal Telegram Bot

1.1 **Open BotFather** in Telegram:  
   [https://telegram.me/BotFather](https://telegram.me/BotFather)

1.2 **Create or retrieve a bot token**:
   - To create a new bot, type:  
     ```
     /newbot
     ```
   - To retrieve an existing bot token, type:  
     ```
     /token
     ```

1.3 **Follow the prompts from BotFather**:
   - Choose a **bot name** (e.g., `MyCustomBot`)
   - Choose a **username** (must end in `bot`, e.g., `mycustom_bot`)

1.4. **Save the bot token** provided by BotFather.  
   You will need this token to configure your bot.

---


##  2. Enrich config file
2.1 telegram client search bot by @bot_name
2.2 send message ```/start```
2.3 extract update_id.message.message_id.from.id https://api.telegram.org/bot{id:tocken}/getUpdates
2.4 add id to config file 

## Links:
[telegram_bot_tutorial](https://core.telegram.org/bots/tutorial)