import os
import logging
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Укажите ваш токен Telegram и ключ Replicate API
TELEGRAM_TOKEN = os.getenv("8154376957:AAH2mVZHymltzpGeZSQw2lVvyIApAhE6qLQ", "YOUR_TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("r8_P1NA0w0zkZQWAK6ZaW0CXTaiS8y3Y013ELPc3", "YOUR_REPLICATE_API_KEY")

# Проверка токенов
if not TELEGRAM_TOKEN or not REPLICATE_API_TOKEN:
    logger.error("Необходимо установить TELEGRAM_BOT_TOKEN и REPLICATE_API_TOKEN!")
    exit(1)

# Функция обработки изображения через Replicate API
def process_image(image_path: str) -> str | None:
    try:
        url = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "version": "cc2015/stable-diffusion",  # Укажите версию модели
            "input": {"prompt": "Professional portrait"},
        }

        with open(image_path, "rb") as image_file:
            response = requests.post(url, headers=headers, json=data, files={"file": image_file})

        response.raise_for_status()  # Проверяем, что запрос прошел успешно
        result = response.json()
        return result.get("output", None)  # Возвращаем URL обработанного изображения

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при работе с API Replicate: {e}")
        return None
    except Exception as e:
        logger.error(f"Неизвестная ошибка при обработке изображения: {e}")
        return None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте мне фото, и я улучшу его!")
    logger.info(f"Пользователь {update.message.chat.id} использовал /start.")

# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Скачиваем фотографию
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = "input.jpg"
        await file.download_to_drive(file_path)
        logger.info(f"Фотография от {update.message.chat.id} скачана в {file_path}.")

        # Обрабатываем фото
        await update.message.reply_text("Обрабатываю фото, подождите...")
        processed_image_url = process_image(file_path)

        if processed_image_url:
            await update.message.reply_photo(processed_image_url)
            logger.info(f"Обработанное фото отправлено пользователю {update.message.chat.id}.")
        else:
            await update.message.reply_text("Что-то пошло не так, попробуйте еще раз.")
            logger.warning(f"Не удалось обработать фото для пользователя {update.message.chat.id}.")

    except Exception as e:
        logger.error(f"Ошибка при обработке фото от пользователя {update.message.chat.id}: {e}")
        await update.message.reply_text("Произошла ошибка при обработке вашего фото. Попробуйте позже.")

# Основной цикл
if __name__ == "__main__":
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        logger.info("Бот запущен!")
        app.run_polling()

    except Exception as e:
        logger.critical(f"Не удалось запустить бота: {e}")
        exit(1)
