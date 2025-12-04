# ===================== telegram_utils.py (FINAL) =====================
import telegram
import asyncio
import cv2

# Your Telegram credentials
TELEGRAM_BOT_TOKEN = "7991128246:AAGEY31YvCbSfOcRuCAFfKEbv-N6lB6Fpd8"
TELEGRAM_CHAT_ID = "1766205546"

# FIXED: Correct bot initialization (YOU HAD CHAT ID HERE BY MISTAKE)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


async def _send_async(msg, frame=None):
    """Async internal execution"""
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=msg,
        parse_mode="Markdown"
    )

    # Send photo if frame exists
    if frame is not None:
        ok, buffer = cv2.imencode(".jpg", frame)
        if ok:
            await bot.send_photo(
                chat_id=TELEGRAM_CHAT_ID,
                photo=buffer.tobytes()
            )


def send_telegram_alert(msg: str, frame=None):
    """Main function used by DB Utils"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_send_async(msg, frame))
        loop.close()
        print("[TELEGRAM] Notification sent successfully.")
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

