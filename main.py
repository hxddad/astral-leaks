import os
import discord
import praw
from dotenv import load_dotenv
import asyncio
from discord_interactions import verify_key_decorator

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
USER_ID = os.getenv('USER_ID')
DISCORD_PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

SUBREDDIT = 'HonkaiStarRail_Leaks'

@verify_key_decorator(DISCORD_PUBLIC_KEY)
async def fetch_new_reddit_posts(subreddit, last_post_id=None):
    subreddit = reddit.subreddit(subreddit)
    posts = []
    for submission in subreddit.new(limit=1):  # Fetch up to 1 new post
        if last_post_id and submission.id == last_post_id:
            break
        message = f"**{submission.title}**\nhttps://reddit.com{submission.permalink}"
        posts.append((submission.id, message))
    return posts

async def check_for_new_posts():
    await client.wait_until_ready()
    user = await client.fetch_user(USER_ID)  # Fetch the user by their ID
    if user is None:
        print(f"User with ID {USER_ID} not found")
        return
    last_post_id = None

    while not client.is_closed():
        try:
            new_posts = await fetch_new_reddit_posts(SUBREDDIT, last_post_id)
            if new_posts:
                last_post_id = new_posts[0][0]  # Update last_post_id to the most recent post
                for post_id, post_content in reversed(new_posts):
                    await user.send(post_content)  # Send the post to the user's DM
        except Exception as e:
            print(f"Error fetching or sending posts: {e}")
        await asyncio.sleep(10)  # Check every 10 seconds

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    client.loop.create_task(check_for_new_posts())

client.run(DISCORD_TOKEN)
