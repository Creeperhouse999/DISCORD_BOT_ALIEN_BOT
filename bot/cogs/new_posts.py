import discord
from discord.ext import commands
import logging
import os
from datetime import datetime

logger = logging.getLogger('AlienBot.new_posts')

class NewPosts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.post_channel_id = os.getenv("POST_CHANNEL_ID")  # Channel to monitor for posts
        self.notification_channel_id = os.getenv("CHANNEL_ID")  # Channel to send notifications
        self.notified_threads = set()  # Track threads we've already notified about

    @commands.command(name='setup_posts')
    async def setup_posts(self, ctx, post_channel_id: int, notification_channel_id: int):
        """Setup post monitoring channels"""
        self.post_channel_id = post_channel_id
        self.notification_channel_id = notification_channel_id
        
        logger.info(f"Post monitoring setup: Post channel {post_channel_id}, Notification channel {notification_channel_id}")
        await ctx.send(f"✅ **Post Monitoring Setup**\n"
                      f"📝 Post channel: <#{post_channel_id}>\n"
                      f"🔔 Notification channel: <#{notification_channel_id}>")

    @commands.command(name='post')
    async def create_post(self, ctx, *, content):
        """Create a post in the designated post channel"""
        if not self.post_channel_id:
            await ctx.send("❌ Post channel not configured. Use `!setup_posts` first.")
            return
        
        try:
            post_channel = self.bot.get_channel(int(self.post_channel_id))
            if not post_channel:
                await ctx.send("❌ Post channel not found.")
                return
            
            # Create embed for the post
            embed = discord.Embed(
                title="📝 New Post",
                description=content,
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            embed.set_footer(text=f"Posted by {ctx.author.name}")
            
            # Send post to designated channel
            post_message = await post_channel.send(embed=embed)
            
            # Send notification to notification channel
            if self.notification_channel_id:
                notification_channel = self.bot.get_channel(int(self.notification_channel_id))
                if notification_channel:
                    notification_embed = discord.Embed(
                        title="🔔 New Post Created!",
                        description=f"**{ctx.author.display_name}** created a new post in <#{self.post_channel_id}>",
                        color=0xffa500,
                        timestamp=datetime.now()
                    )
                    notification_embed.add_field(name="Post Content", value=content[:100] + "..." if len(content) > 100 else content, inline=False)
                    notification_embed.add_field(name="Jump to Post", value=f"[Click here]({post_message.jump_url})", inline=False)
                    
                    await notification_channel.send(embed=notification_embed)
            
            await ctx.send(f"✅ **Post created successfully!**\n"
                          f"📝 Posted in: <#{self.post_channel_id}>\n"
                          f"🔗 [Jump to post]({post_message.jump_url})")
            
            logger.info(f"Post created by {ctx.author} in channel {self.post_channel_id}")
            
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            await ctx.send(f"❌ Error creating post: {str(e)}")

    @commands.command(name='post_status')
    async def post_status(self, ctx):
        """Check post monitoring status"""
        status_embed = discord.Embed(
            title="📊 Post Monitoring Status",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        if self.post_channel_id:
            post_channel = self.bot.get_channel(int(self.post_channel_id))
            status_embed.add_field(
                name="📝 Post Channel", 
                value=f"<#{self.post_channel_id}>" if post_channel else f"❌ Channel not found (ID: {self.post_channel_id})",
                inline=False
            )
        else:
            status_embed.add_field(name="📝 Post Channel", value="❌ Not configured", inline=False)
        
        if self.notification_channel_id:
            notification_channel = self.bot.get_channel(int(self.notification_channel_id))
            status_embed.add_field(
                name="🔔 Notification Channel", 
                value=f"<#{self.notification_channel_id}>" if notification_channel else f"❌ Channel not found (ID: {self.notification_channel_id})",
                inline=False
            )
        else:
            status_embed.add_field(name="🔔 Notification Channel", value="❌ Not configured", inline=False)
        
        await ctx.send(embed=status_embed)

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        """Detect when a new forum post (thread) is created"""
        # Check if thread is in the monitored channel
        if not self.post_channel_id or str(thread.parent_id) != str(self.post_channel_id):
            return
        
        # Check if we've already notified about this thread
        if thread.id in self.notified_threads:
            return
        
        # Send notification about new forum post
        try:
            if self.notification_channel_id:
                notification_channel = self.bot.get_channel(int(self.notification_channel_id))
                if notification_channel:
                    # Get the first message in the thread to get content
                    first_message = None
                    try:
                        async for message in thread.history(limit=1, oldest_first=True):
                            first_message = message
                            break
                    except:
                        pass
                    
                    notification_embed = discord.Embed(
                        title="📋 New Forum Post Created!",
                        description=f"**{thread.owner.display_name if thread.owner else 'Unknown'}** created a new forum post in <#{self.post_channel_id}>",
                        color=0x9b59b6,
                        timestamp=datetime.now()
                    )
                    
                    # Add thread title
                    notification_embed.add_field(name="Post Title", value=thread.name, inline=False)
                    
                    # Add content if available
                    if first_message and first_message.content:
                        content = first_message.content
                        if len(content) > 200:
                            content = content[:200] + "..."
                        notification_embed.add_field(name="Post Content", value=content, inline=False)
                    
                    # Add thread info
                    notification_embed.add_field(name="Thread", value=f"[Click here]({thread.jump_url})", inline=False)
                    
                    # Add author info
                    if thread.owner:
                        notification_embed.set_author(
                            name=thread.owner.display_name, 
                            icon_url=thread.owner.avatar.url if thread.owner.avatar else None
                        )
                    
                    await notification_channel.send(embed=notification_embed)
                    
                    # Mark this thread as notified
                    self.notified_threads.add(thread.id)
                    
                    logger.info(f"Forum post notification sent for thread '{thread.name}' by {thread.owner} in channel {self.post_channel_id}")
        
        except Exception as e:
            logger.error(f"Error sending forum post notification: {str(e)}")

async def setup(bot):
    await bot.add_cog(NewPosts(bot))