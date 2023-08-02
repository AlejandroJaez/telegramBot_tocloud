import logging
import os
import pathlib

from telegram import Update, Location
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from dotenv import dotenv_values

config = dotenv_values(".env")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!"
    )


async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not isinstance(update.message.effective_attachment, Location):
        if isinstance(update.message.effective_attachment, tuple):
            attachment = await context.bot.get_file(
                update.message.effective_attachment[-1].file_id
            )
            file_extension = attachment.file_path.rsplit(".", 1)[-1]
            filename = attachment.file_path.split('/')[-1]
        else:
            attachment = await context.bot.get_file(
                update.message.effective_attachment.file_id
            )
            filename = attachment.file_path.split('/')[-1]

        save_path = "{0}".format(os.path.join(config["SAVE_DIR"], update.effective_user.username))
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        file = await attachment.download_to_drive(
            custom_path="{0}/{1}/{2}".format(config["SAVE_DIR"],
                                             update.effective_user.username, attachment.file_path.split('/')[-1]))
        if isinstance(file, pathlib.WindowsPath):
            send = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Archivo {} recibido!".format(filename),
                reply_to_message_id=update.message.id,
            )

        else:
            send = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Error en el almacenamiento de archivo!",
            )
        print(file)


if __name__ == "__main__":
    application = ApplicationBuilder().token(config["TOKEN"]).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.ATTACHMENT, downloader))

    application.run_polling()
