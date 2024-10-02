import os

from google.cloud.secretmanager import SecretManagerServiceAsyncClient
from google.cloud.secretmanager_v1.types import Secret, SecretPayload

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)


BOT_TOKEN = os.environ["BOT_TOKEN"]
PROJECT_ID = os.environ["GCP_PROJECT_ID"]

client = SecretManagerServiceAsyncClient()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm a bot to store your user's secret.")
    await update.message.reply_text("Run /set <value> to set your user's secret.")
    await update.message.reply_text("Run /get to get your secret.")


async def set_secret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /set <value>")
        return

    user_id = update.effective_user.id
    secret_id = str(user_id)
    secret_data = context.args[0].encode()

    # Create the secret
    parent = client.common_project_path(PROJECT_ID)
    secret = Secret({"replication": {"automatic": {}}})
    await client.create_secret(secret_id=secret_id, parent=parent, secret=secret)

    # Add a version
    parent = client.secret_path(PROJECT_ID, secret_id)
    payload = SecretPayload({"data": secret_data})
    await client.add_secret_version(parent=parent, payload=payload)


async def get_secret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    secret_id = str(user_id)
    secret_name = client.secret_version_path(PROJECT_ID, secret_id, "latest")

    # Access the secret
    try:
        response = await client.access_secret_version(name=secret_name)
    except:
        await update.message.reply_text("No secret found")

    secret_data = response.payload.data
    await update.message.reply_text(f"Your secret: {secret_data.decode()}")


async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Unknown message")


def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set", set_secret))
    app.add_handler(CommandHandler("get", get_secret))

    app.add_handler(MessageHandler(filters.ALL, unknown_message))

    app.run_polling()


if __name__ == "__main__":
    main()
