import discord
from discord.ext import commands
import aiohttp
import asyncio
import logging

logger = logging.getLogger('AlienBot.new_posts')

class NewPosts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reddit')
    async def get_reddit_post(self, ctx, subreddit='funny'):
        """Get a random post from a subreddit"""
        logger.info(f"Reddit command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'} for r/{subreddit}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'https://www.reddit.com/r/{subreddit}/hot.json?limit=10') as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data['data']['children']
                        
                        if posts:
                            post = posts[0]['data']  # Get the first (hottest) post
                            title = post['title']
                            url = f"https://reddit.com{post['permalink']}"
                            
                            embed = discord.Embed(
                                title=f"🔥 Hot Post from r/{subreddit}",
                                description=title,
                                url=url,
                                color=0xff4500
                            )
                            embed.set_footer(text=f"Posted by u/{post['author']}")
                            
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send(f"No posts found in r/{subreddit}")
                    else:
                        await ctx.send(f"Couldn't fetch posts from r/{subreddit}")
        except Exception as e:
            logger.error(f"Error fetching Reddit post from r/{subreddit}: {str(e)}")
            await ctx.send(f"Error fetching Reddit post: {str(e)}")

    @commands.command(name='news')
    async def get_news(self, ctx):
        """Get the latest news (placeholder command)"""
        logger.info(f"News command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
        await ctx.send("📰 **News Command**\nThis is a placeholder for news functionality. You can integrate with news APIs like NewsAPI here!")

async def setup(bot):
    await bot.add_cog(NewPosts(bot))
