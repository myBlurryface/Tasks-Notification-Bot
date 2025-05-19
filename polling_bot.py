import os
import aiohttp
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
TASK_MANAGER_URL = os.getenv("TASK_MANAGER_URL")
DJANGO_WEBHOOK_PATH = os.getenv("DJANGO_WEBHOOK_PATH", "/django/webhook")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8443))
DJANGO_SECRET_TOKEN = os.getenv("DJANGO_SECRET_TOKEN", "")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def welcome(message: types.Message):
    await bot.send_message(message.from_user.id,
                           "Привет! Я бот, который будет напоминать тебе "
                           "об активных задачах за 10 минут до дедлайна!")


@dp.message(Command("mytasks"))
async def send_tasks(message: types.Message):
    tg_user_id = message.from_user.id
    url = f"{TASK_MANAGER_URL}?telegram_user_id={tg_user_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                tasks_list = await response.json()
                if not tasks_list:
                    await bot.send_message(tg_user_id, "У вас нет задач.")
                for task in tasks_list:
                    text_status = "done" if task["status"] is False else "undone"
                    await bot.send_message(
                        chat_id=tg_user_id,
                        text=f"------------------------------\n"
                             f"Задача: {task["title"]}\n"
                             f"Описание: {task["description"]}\n"
                             f"Дедлайн: {task["deadline"]}\n"
                             f"Статуc: {text_status}\n"
                             f"------------------------------"
                        )
            else:
                await bot.send_message(tg_user_id, (await response.json()).get("Error"))


@dp.message(Command("done"))
async def send_tasks(message: types.Message):
    tg_user_id = message.from_user.id
    args = message.text.split()

    if len(args) < 2:
        await bot.send_message(tg_user_id, "Пожалуйста, укажите id задачи. Пример: /start 123")
        return

    try:
        task_id = int(args[1])
    except ValueError:
        await bot.send_message(tg_user_id, "id задачи должно быть числом. Пример: /start 123")
        return

    url = f"{TASK_MANAGER_URL}{task_id}/"
    payload = {"task_status": True}

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, json=payload) as response:
            if response.status == 200:
                text_response = await response.json()
                await bot.send_message(message.from_user.id, text_response)
            else:
                await bot.send_message(message.from_user.id, (await response.json()).get("Error"))


async def send_notifications_of_tasks(request: web.Request):
    secret_token = request.headers.get("X-Django-Secret-Token")
    if DJANGO_SECRET_TOKEN and secret_token != DJANGO_SECRET_TOKEN:
        return web.Response(status=403, text="Invalid secret token")

    try:
        tasks = await request.json()
        for task in tasks:
            tg_user_id = task.get("tg_user_id")
            text = (f"Задача: {task['title']}\n"
                    f"Описание: {task['description']}\n"
                    f"Дедлайн: {task['deadline']}\n")

            await bot.send_message(chat_id=tg_user_id, text=text)
        return web.Response(status=200, text="All notifications has been sent")
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")


async def start_web_server():
    app = aiohttp.web.Application()
    app.router.add_post(DJANGO_WEBHOOK_PATH, send_notifications_of_tasks)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", WEBHOOK_PORT)
    await site.start()
    print(f"Веб-сервер запущен на http://0.0.0.0:{WEBHOOK_PORT}{DJANGO_WEBHOOK_PATH}")
    return runner


async def main():
    try:
        web_runner = await start_web_server()
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")
        raise
    finally:
        await bot.session.close()
        await web_runner.cleanup()
        print("Сессия бота и веб-сервер закрыты")


if __name__ == "__main__":
    asyncio.run(main())
