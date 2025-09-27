import discord
from discord.ext import commands
import random
import logging

logger = logging.getLogger('AlienBot.jokes')

class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='joke')
    async def tell_joke(self, ctx):
        """Tell a random joke"""
        logger.info(f"Joke command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        joke = random.choice(jokes)
        logger.debug(f"Selected joke: {joke}")
        await ctx.send(joke)

    @commands.command(name='dad_joke')
    async def dad_joke(self, ctx):
        """Tell a dad joke"""
        logger.info(f"Dad joke command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
        dad_jokes = [
            "I'm reading a book about anti-gravity. It's impossible to put down!",
            "Why don't skeletons fight each other? They don't have the guts!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the coffee file a police report? It got mugged!",
            "What do you call a dinosaur that crashes his car? Tyrannosaurus Wrecks!"
        ]
        joke = random.choice(dad_jokes)
        logger.debug(f"Selected dad joke: {joke}")
        await ctx.send(f"🤣 **Dad Joke Alert!** 🤣\n{joke}")

async def setup(bot):
    await bot.add_cog(Jokes(bot))
