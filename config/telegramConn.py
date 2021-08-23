from src.config.auth import telegramBotToken, telegramID, telegramGroupID


def sendMsg(ID=telegramID, msg=''):
    """
    Send Telegram Message to selected ID.
    """
    import telegram

    bot = telegram.Bot(token=telegramBotToken)

    bot.sendMessage(chat_id=ID,
                    text=f'{msg}')

#sendMsg(ID=telegramGroupID, msg='Puto el que lee')