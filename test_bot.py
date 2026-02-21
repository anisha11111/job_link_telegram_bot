from telegram import Bot
import asyncio

TOKEN = "8316708976:AAEPN-t3QU0Pk8HTgVP22hD-7jYqCu_5plo"

async def main():
    bot = Bot(TOKEN)
    me = await bot.get_me()
    print("Connected to:", me.username)

asyncio.run(main())