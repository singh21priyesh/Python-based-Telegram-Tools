import sys
import asyncio
from telegram import Bot
from telegram.error import TelegramError

bot_token = '1234578900873633'#
bot = Bot(token=bot_token)
group_chat_id = -111111111119  # your group ID

# --- Functions ---
async def ban_user(user_id):
    try:
        await bot.ban_chat_member(chat_id=group_chat_id, user_id=user_id)
        print(f"✅ User {user_id} has been kicked from the group. He Cannot Join untill you unban him")
    except TelegramError as e:
        print(f"❌ Error banning user {user_id}: {e}")

async def unban_user(user_id):
    try:
        await bot.unban_chat_member(chat_id=group_chat_id, user_id=user_id)
        print(f"✅ User {user_id} has been unbanned and can now rejoin the group.")
    except TelegramError as e:
        print(f"❌ Error unbanning user {user_id}: {e}")

# --- Main Menu Logic ---
async def main():
    while True:
        print("\nChoose an action:")
        print("1. Ban a user")
        print("2. Unban a user")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ").strip()

        if choice in {'1', '2'}:
            user_id_input = input("Enter the Telegram User ID: ").strip()
            if not user_id_input.isdigit():
                print("⚠️ Invalid user ID.")
                continue
            user_id = int(user_id_input)

            if choice == '1':
                await ban_user(user_id)
            elif choice == '2':
                await unban_user(user_id)
        elif choice == '3':
            print("Exiting...")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

# --- Run ---
if __name__ == "__main__":
    asyncio.run(main())
