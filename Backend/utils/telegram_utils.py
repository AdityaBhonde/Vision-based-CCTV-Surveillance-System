import telegram, asyncio, cv2

TELEGRAM_BOT_TOKEN = "8465770268:AAHspvpjMrQJXA1Bmg0zGIISrseKhJrdcUw"
TELEGRAM_CHAT_ID = "6594618388"
bot = telegram.Bot(token=TELEGRAM_CHAT_ID)

def send_telegram_alert(msg, frame=None):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def send_all():
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
            if frame is not None:
                _, buffer = cv2.imencode(".jpg", frame)
                await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=buffer.tobytes())

        loop.run_until_complete(send_all())
        loop.close()
    except Exception as e:
        print(f"!!! CRITICAL TELEGRAM ERROR: {e}")
