from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram import Bot
from django.conf import settings
from asgiref.sync import sync_to_async
from .models import Subscriber

TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN

# Функция для отправки рецепта вместе с фото
async def send_recipe_to_telegram(recipe):
    bot = Bot(token=TELEGRAM_TOKEN)
    message = f"Новый рецепт: {recipe.title}\n\nОписание: {recipe.description}"

    # Получаем активных подписчиков
    subscribers = await sync_to_async(list)(Subscriber.objects.filter(is_active=True))

    # Отправляем сообщение и фото каждому подписчику
    for subscriber in subscribers:
        try:
            # Отправляем сообщение с текстом
            await bot.send_message(chat_id=subscriber.chat_id, text=message)

            # Если у рецепта есть изображение, отправляем его
            if recipe.image:
                with open(recipe.image.path, 'rb') as image_file:
                    await bot.send_photo(chat_id=subscriber.chat_id, photo=image_file)

        except Exception as e:
            print(f"Ошибка отправки сообщения в чат {subscriber.chat_id}: {e}")




# Функция для обработки команды /start
async def start(update: Update, context):
    # Получаем chat_id пользователя
    chat_id = update.message.chat_id
    print(f"Получена команда /start от пользователя с chat_id: {chat_id}")

    # Отправляем приветственное сообщение
    await update.message.reply_text('Привет! Используйте /subscribe для подписки на уведомления.')

    # Отправляем сообщение с chat_id
    await update.message.reply_text(f'Ваш chat_id: {chat_id}')

    # Дополнительно можем сохранять или обновлять chat_id в базе данных
    username = update.message.chat.username
    subscriber, created = await sync_to_async(Subscriber.objects.get_or_create)(
        chat_id=chat_id,
        defaults={'username': username}
    )

    if not created and subscriber.is_active:
        await update.message.reply_text('Вы уже подписаны.')
    else:
        subscriber.is_active = True
        await sync_to_async(subscriber.save)()
        await update.message.reply_text('Ваш chat_id сохранен и вы подписаны на уведомления!')


# Функция для обработки команды /subscribe
async def subscribe(update: Update, context):
    chat_id = update.message.chat_id
    username = update.message.chat.username

    print(f"Received subscribe from {username} ({chat_id})")  # Логирование

    subscriber, created = await sync_to_async(Subscriber.objects.get_or_create)(
        chat_id=chat_id,
        defaults={'username': username}
    )

    if not created and subscriber.is_active:
        await update.message.reply_text('Вы уже подписаны.')
    else:
        subscriber.is_active = True
        await sync_to_async(subscriber.save)()
        await update.message.reply_text('Вы успешно подписались на уведомления!')


# Функция для обработки команды /unsubscribe
async def unsubscribe(update: Update, context):
    chat_id = update.message.chat_id

    try:
        # Обернем запрос в sync_to_async для работы с базой данных
        subscriber = await sync_to_async(Subscriber.objects.get)(chat_id=chat_id)
        subscriber.is_active = False
        await sync_to_async(subscriber.save)()
        await update.message.reply_text('Вы успешно отписались от уведомлений.')
    except Subscriber.DoesNotExist:
        await update.message.reply_text('Вы не были подписаны.')

# Запуск бота
def run_bot():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрация команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('subscribe', subscribe))
    application.add_handler(CommandHandler('unsubscribe', unsubscribe))

    # Запуск polling
    application.run_polling()


# Запуск бота
if __name__ == "__main__":
    run_bot()
