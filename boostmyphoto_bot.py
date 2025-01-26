from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

# Замените на ваш токен Telegram и ключ Replicate API
TELEGRAM_TOKEN = "8154376957:AAH2mVZHymltzpGeZSQw2lVvyIApAhE6qLQ"
REPLICATE_API_TOKEN = "r8_P1NA0w0zkZQWAK6ZaW0CXTaiS8y3Y013ELPc3"

# Функция обработки изображения через Replicate API
def process_image(image_path):
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "version": "cc2015/stable-diffusion",  # Укажите версию модели
        "input": {"prompt": "Professional portrait"}
    }
    with open(image_path, "rb") as image_file:
        response = requests.post(url, headers=headers, json=data, files={"file": image_file})
    result = response.json()
    return result["output"] if "output" in result else None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте мне фото, и я улучшу его!!!")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "input.jpg"
    await file.download_to_drive(file_path)

    await update.message.reply_text("Обрабатываю фото, подождите...")
    processed_image_url = process_image(file_path)

    if processed_image_url:
        await update.message.reply_photo(processed_image_url)
    else:
        await update.message.reply_text("Что-то пошло не так, попробуйте еще раз.")

# Основной цикл
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    print("Бот запущен!")
    app.run_polling()
