import discord
from discord.ext import commands
import random
import logging

logger = logging.getLogger('AlienBot.jokes')

class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_joke = None  # Track the last joke told

    def get_random_joke(self, jokes):
        """Get a random joke that's different from the last one"""
        if len(jokes) == 1:
            return jokes[0]  # If only one joke, return it
        
        # Filter out the last joke
        available_jokes = [joke for joke in jokes if joke != self.last_joke]
        
        # If all jokes were the same as last one (shouldn't happen with 5 jokes), use all jokes
        if not available_jokes:
            available_jokes = jokes
        
        return random.choice(available_jokes)

    @commands.command(name='joke')
    async def tell_joke(self, ctx):
        """Tell a random joke about Mr. Piotr"""
        logger.info(f"Joke command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
        jokes = [
            "Why Mr. Piotr is always late on the lesson? Because he has to park his UFO and he can't find a parking spot big enough.",
            "Why is The Nóż so useful? Because it can scare kids.",
            "Why is Mr. Piotr stealing cows? Because their milk is expensive in the galaxy.",
            "Why does Mr. Piotr have a human skin color? Because he doesn't want anybody to see his green skin.",
            "Why does Mr. Piotr write with his PC pen? Because he can't see letters clearly with his alien eyes."
        ]
        
        # Get a joke that's different from the last one
        joke = self.get_random_joke(jokes)
        self.last_joke = joke  # Update the last joke
        
        logger.debug(f"Selected joke: {joke}")
        await ctx.send(joke)

async def setup(bot):
    await bot.add_cog(Jokes(bot))