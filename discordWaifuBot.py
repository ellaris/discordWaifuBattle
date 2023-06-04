# -*- coding: utf-8 -*-
"""
Created on Sun May 28 10:58:57 2023

@author: tomas
"""

import discordWaifuBattle as wb

# testing
game = wb.WaifuBattleGame()
game.configure(selected_timer=4.0)
game.join("alice")
game.start()

#%% Sample app

import os, discord
from discord.ext import commands
from discord import app_commands

import subprocess
import sys
import time

# import nest_asyncio
# nest_asyncio.apply()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

# bot = commands.Bot(command_prefix="/",intents=intents)
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    # await tree.set_translator()
    await tree.sync()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=' waifu requests'))
    print(f"{bot.user} has connected to Discord!")
    
    
class SpamView(discord.ui.View):
    
    # owner = None
    # def __init__(self,*,owner):
    #     super().__init__()
    #     self.owner = owner

    @discord.ui.button(label="Yes")
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = "Y"
        self.stop()
        return await interaction.response.send_message("Nah, I'm done with you",ephemeral=True, delete_after= 10.0)

    @discord.ui.button(label="No")
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = "N"
        self.stop()
        return await interaction.response.send_message("Ok I'll stop bothering you",ephemeral=True, delete_after= 10.0)

# Commands
@tree.command(name="spam", description="Spam me with invisible messages")
async def spam(interaction):
    await interaction.response.send_message(content="Ok",ephemeral=True, delete_after= 2.0)
    time.sleep(2)
    webhook = interaction.followup
    msg = await webhook.send(wait=True, content="How do you like it now?",ephemeral=True)
    time.sleep(2)
    
    # await webhook.delete()
    # view = discord.ui.View()
    # btn = discord.ui.Button(label="Yes")
    # view.add_item(btn)
    # btn = discord.ui.Button(label="No")
    # view.add_item(btn)
    view = SpamView()
    await msg.delete()
    msg = await webhook.send(wait=True, content="Want me to keep going?",ephemeral=True, view = view)
    await view.wait()
    print(view.value)
    await msg.delete()
    
    
    
# Commands
@tree.command(name="token", description="Generate a waifu token")
async def token(interaction, prompt: str = "girl", border: str = None):
    """
    Token image generation
    
    :param prompt: Comma seperated descriptors (eg. green, short hair, armor)
    :param border: Border type to surround the token with
    
    :return: tokenized image
    """
    # ctx = await discord.ext.commands.Context(interaction)
    # channel = ctx.message.channel
    # emoji = '\N{THUMBS UP SIGN}'
    # or '\U0001f44d' or '👍'
    # await ctx.message.add_reaction(emoji)

    user = interaction.user
    previous_status = bot.guilds[0].get_member(bot.user.id).activity
    await interaction.response.send_message(content=f"Generating a token for you: {prompt} in {border}",ephemeral = True, delete_after= 10.0)
    
    # Change activity for the task
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=' waifu being born'))
    
    
    async with interaction.channel.typing():
    # Long Calculation
        image_file = "token.png"
        try:
            args = [sys.executable,"temp.py"]
            if prompt:
                args.append(prompt)
            else:
                args.append("")
            if border:
                args.append(border)
            else:
                args.append("")
            print(prompt)
            print(border)
            image_generated = subprocess.call(args)
            print("image generated")
            if image_generated == 0:
                file = discord.File(image_file, filename=image_file)
                content = f"{user.name} here is your: {prompt}"
                if border:
                    content += f" in a {border} border"
                    
                embed = discord.Embed(colour= 5500000,description=content)
                embed.set_image(url=f"attachment://{image_file}")
                embed.set_author(name=user.name,icon_url=user.avatar.url)
                embed.set_thumbnail(url=bot.user.avatar.url)
                
                await interaction.channel.send(file=file, embed=embed)
            else:
                await interaction.channel.send(content="Waifu couldn't be born ",ephemeral = True, delete_after = 10.0)
        except Exception as e:
            print("ERROR")
            print(e)
    # Reset the status
    await bot.change_presence(activity=previous_status)
    
# autocomplete
@token.autocomplete('border')
async def border_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    borders = ["ring", "wavey", "octagon", "flat", "double"]
    return [
        app_commands.Choice(name=border, value=border)
        for border in borders if current.lower() in border.lower()
    ]

@token.autocomplete('prompt')
async def prompt_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    prompts = ["1girl, small breasts, green, dress", "1girl, small breasts, yellow, blouse, skirt", "1girl, small breasts, brown, leather armor", "1girl, small breasts, red, weapon, armor", "1girl, small breasts, purple, robe, witch hat, magic"]
    return [
        app_commands.Choice(name=prompt, value=prompt)
        for prompt in prompts if current.lower() in prompt.lower()
    ]
    
bot.run(DISCORD_TOKEN)


#%% discord bot

import os, discord
from discord.ext import commands

from replit import db
from game import *

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="/")

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    
# Commands
@bot.command(name="create", help="Create a character.")
async def create(ctx, name=None):
    user_id = ctx.message.author.id

    # if no name is specified, use the creator's nickname
    if not name:
        name = ctx.message.author.name
        
    embed = discord.Embed(title=f"{character.name} status", description=mode_text, color=MODE_COLOR[character.mode])
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    
    
    embed.add_field(name="Stats", value=f"""
**HP:**    {character.hp}/{character.max_hp}
**ATTACK:**   {character.attack}
**DEFENSE:**   {character.defense}
**MANA:**  {character.mana}
**LEVEL:** {character.level}
**XP:**    {character.xp}/{character.xp+xp_needed}
    """, inline=True)
    
    emoji = '\N{THUMBS UP SIGN}'
# or '\U0001f44d' or '👍'
await message.add_reaction(emoji)
    
file = discord.File("path/to/my/image.png", filename="image.png")
embed = discord.Embed()
embed.set_image(url="attachment://image.png")
await channel.send(file=file, embed=embed)

# Define a simple View that gives us a confirmation menu
class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = F
        
@bot.command()
async def ask(ctx: commands.Context):
    """Asks the user a question to confirm something."""
    # We create the view and assign it to a variable so we can wait for it later.
    view = Confirm()
    await ctx.send('Do you want to continue?', view=view)
    # Wait for the View to stop listening for input...
    await view.wait()
    if view.value is None:
        print('Timed out...')
    elif view.value:
        print('Confirmed...')
    else:
        print('Cancelled...')
        
        
# Define a simple View that gives us a counter button
class Counter(discord.ui.View):

    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @discord.ui.button(label='0', style=discord.ButtonStyle.red)
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = int(button.label) if button.label else 0
        if number + 1 >= 5:
            button.style = discord.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)


# Define a View that will give us our own personal counter button
class EphemeralCounter(discord.ui.View):
    # When this button is pressed, it will respond with a Counter view that will
    # give the button presser their own personal button they can press 5 times.
    @discord.ui.button(label='Click', style=discord.ButtonStyle.blurple)
    async def receive(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ephemeral=True makes the message hidden from everyone except the button presser
        await interaction.response.send_message('Enjoy!', view=Counter(), ephemeral=True)


bot = EphemeralCounterBot()


@bot.command()
async def counter(ctx: commands.Context):
    """Starts a counter for pressing."""
    await ctx.send('Press!', view=EphemeralCounter())

bot.run(DISCORD_TOKEN)