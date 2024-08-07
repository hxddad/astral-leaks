import os
import discord
import praw
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

CHANNEL_ID = 1268267896547709031  # Replace with your correct channel ID
SUBREDDIT = 'HonkaiStarRail_Leaks'

async def fetch_new_reddit_posts(subreddit, last_post_id=None):
    subreddit = reddit.subreddit(subreddit)
    posts = []
    for submission in subreddit.new(limit=1):  # Fetch up to 10 new posts
        if last_post_id and submission.id == last_post_id:
            break
        message = f"**{submission.title}**\nhttps://reddit.com{submission.permalink}"
        posts.append((submission.id, message))
    return posts

async def check_for_new_posts():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel with ID {CHANNEL_ID} not found")
        return
    last_post_id = None

    while not client.is_closed():
        try:
            new_posts = await fetch_new_reddit_posts(SUBREDDIT, last_post_id)
            if new_posts:
                last_post_id = new_posts[0][0]  # Update last_post_id to the most recent post
                for post_id, post_content in reversed(new_posts):
                    await channel.send(post_content)
        except Exception as e:
            print(f"Error fetching or sending posts: {e}")
        await asyncio.sleep(10)  # Check every 10 seconds

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    client.loop.create_task(check_for_new_posts())

client.run(DISCORD_TOKEN)
