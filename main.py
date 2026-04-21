from src.bot.core import InstaBot


def main():
    bot = InstaBot()
    if not bot.start():
        print("Login failed. Check credentials in .env")
        return

    # Example campaigns — adjust targets as needed
    bot.run_follow_campaign(target="target_account", limit=20)
    bot.run_hashtag_like(hashtag="photography", amount=15)


if __name__ == "__main__":
    main()
