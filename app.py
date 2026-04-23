import asyncio, sys
from flask import Flask
from threading import Thread
import bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Support Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try: asyncio.get_running_loop()
    except RuntimeError: asyncio.set_event_loop(asyncio.new_event_loop())
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    bot.main()