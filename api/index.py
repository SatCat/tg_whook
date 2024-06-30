import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
#from fastapi.requests import Request
#import uvicorn
import redis

BOT_TOKEN = os.environ.get('BOT_TOKEN') 
KV_USERNAME = os.environ.get('KV_USERNAME')
KV_PASS = os.environ.get('KV_PASS')
KV_HOST = os.environ.get('KV_HOST')
KV_PORT = os.environ.get('KV_PORT')
APP_HOST = os.environ.get('APP_HOST')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

r = redis.Redis(host=KV_HOST, port=KV_PORT, username=KV_USERNAME, password=KV_PASS, ssl=True)

def add_redis_msg(msg):
    time_str = format(datetime.utcnow()+timedelta(hours=11))+" GMT+11 "
    r.lpush('list_val', time_str+msg)    
add_redis_msg('App start!')


@asynccontextmanager
async def lifespan(app: FastAPI):
    add_redis_msg('TG_WebHook_start..')    
    await bot.set_webhook(url=f"https://{APP_HOST}/webhook",
                          allowed_updates=dp.resolve_used_update_types(),
                          drop_pending_updates=True)
    yield
    await bot.delete_webhook()
    add_redis_msg('TG_WebHook_done!')    


app = FastAPI(lifespan=lifespan)


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer('Привет!')


@app.post("/webhook")
async def webhook(request: Request) -> None:
    add_redis_msg('TG Msg')
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
