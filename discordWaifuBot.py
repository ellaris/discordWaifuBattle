# -*- coding: utf-8 -*-
"""
Created on Sun May 28 10:58:57 2023

@author: tomas
"""

# import discordWaifuBattle as wb
from discordWaifuBattle import Player, WaifuBattleGame
import random
import asyncio

class DiscordPlayer(Player):
    webhook = None
    
    def setWebhook(self, hook):
        self.webhook = hook
        
    async def sendMessage(self, message):
        if self.webhook:
            await self.webhook.send(wait = True, content = message, ephemeral = True)

class WaifuBattleGameBot(WaifuBattleGame):
    
    print_stack = []
    message = None
    
    # def __init__(self):
        # super().__init__()
    
    def join(self, name, webhook):
        if  self.current_round > 0:
            return("Game is in progress")
        if len( self.playing_cards) <  self.rounds:
            return("Not enough cards left!")
        
        p = DiscordPlayer(name, len(self.players))
        p.setWebhook(webhook)
        self.players.append(p)
        
        for i in range( self.rounds):
            p.addCard( self.playing_cards.pop(random.randint(0, len( self.playing_cards)-1)))
        self.display_hand(p)
        return(f"{name} successfully joined the waifu battle")
        
    def configure(self, channel, play_rounds = 4, cards = [], selected_type = "", selected_timer = 60.0, allowed_cards = ""):
        super().configure(play_rounds, cards, selected_type, selected_timer, allowed_cards)
        self.game_channel = channel
        
    async def sendPrintStack(self, embeds = None, view = None, new_message = False):
        content = "\n".join(self.print_stack)
        self.print_stack = []
        if new_message or not self.message:
            if embeds and view:
                self.message = await self.game_channel.send(content=content, embeds = embeds, view = view)
            elif embeds:
                self.message = await self.game_channel.send(content=content, embeds = embeds)
            elif view:
                self.message = await self.game_channel.send(content=content, view = view)
            else:
                self.message = await self.game_channel.send(content=content)
        else:
            if embeds and view:
                await self.message.edit(content = content, embeds = embeds, view = view)
            elif embeds:
                await self.message.edit(content = content, embeds = embeds)
            elif view:
                await self.message.edit(content = content, view = view)
            else:
                await self.message.edit(content = content)
        
        
    def display_mode(self):
        mode_str = ""
        if self.voting:
            mode_str += "Vote"
        else:
            mode_str += "Choose"
        mode_str += f" in {self.timer} seconds"
        
        self.print_stack.append(mode_str)
    
    def display_round(self):
        self.print_stack.append(f"Round {self.current_round}")
        
    def display_vote_results(self, votes):
        vote_str = "Votes\n"
        for vote,player in zip(votes,self.players):
            vote_str += f"{player.name}: {vote}  "
        self.print_stack.append(vote_str)
        loop.create_task( self.sendPrintStack())
        
        
    def display_field(self, field):
        gt = self.game_type
        field_str = ""
        if self.game_type == "":
            gt = self.game_types[random.randint(0, len(self.game_types)-1)]
        field_str += f"Vote for: {gt}\n"
        embeds = []
        view = discord.ui.View()
        for i,card in enumerate(field):
            embed = discord.Embed()
            embed.set_image(url=card)
            embeds.append(embed)
            button = ChooseVoteButton(value= i, view = view, label = str(i))
            # button.callback = lambda (name: discord.user): self.vote(name,i)
            view.add_item(button)
            
        self.print_stack.append(field_str)
        loop.create_task( self.sendPrintStack(embeds=embeds, view = view, new_message=True))
        
    def display_scores(self, compact=False):
        sorted_players = sorted(self.players, key = lambda player: player.score, reverse=True)
        scores_str = "Score:\n"
        for player in sorted_players:
            if compact:
                scores_str += f"{player.name}:{player.score} "
            else:
                scores_str += f"\n{player.name} has score of {player.score}"
        self.print_stack.append(scores_str)
        loop.create_task( self.sendPrintStack())
            
    def display_hand(self, player):
        # hand_str = ""
        # hand_str += player.name+"\n"
        embeds = []
        view = discord.ui.View()
        for i, card in enumerate(player.cards):
            # hand_str += f"{card} \n"
            embed = discord.Embed()
            embed.set_image(url=card)
            embeds.append(embed)
            button = ChooseVoteButton(value= i, view = view, label = str(i))
            view.add_item(button)
            
        # self.print_stack.append(hand_str)
        
        
        # embed.set_author(name=user.name,icon_url=user.avatar.url)
        # embed.set_thumbnail(url=bot.user.avatar.url)
        loop.create_task( self.player_deliver(player, embeds, view))
        
    async def player_deliver(self, player,embeds,view):
        await player.webhook.send(content = "Hand", embeds=embeds, ephemeral = True, view = view)
            
    def display_time(self, time_left):
        self.print_stack.append(f"{time_left}")
        loop.create_task( self.sendPrintStack())
        
    def start(self):
        loop.create_task( self.sendPrintStack(new_message=True))
        super().start()
        
    # def round_end(self):
    #     global loop
    #     loop = asyncio.get_event_loop()
    #     super().round_end()
    
    # async def collect_votes(self):
        # await super().collect_votes()
    

# testing
loop = asyncio.get_event_loop()
game = WaifuBattleGameBot()
# game.configure(selected_timer=4.0)
# game.join("alice")
# game.start()

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
    
class ChooseVoteButton(discord.ui.Button):
    
    view = None
    
    def __init__(self, value, view, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.view = view
        
    async def callback(self, interaciton: discord.Interaction):
        username = interaciton.user.name
        if game.voting:
            game.vote(username, self.value)
            await interaciton.response.send_message(content= f"voted for {self.value}",ephemeral = True, delete_after = 5)
        else:
            game.choose(username, self.value)
            await interaciton.response.send_message(content= f"{self.value} chosen",ephemeral = True, delete_after = 5)
        self.view.stop()
    
class JoinView(discord.ui.View):
    
    joined = False
    # def __init__(self,*,owner):
    #     super().__init__()
    #     self.owner = owner

    @discord.ui.button(label="Join")
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if not self.joined:
            username = interaction.user.name
            webhook = interaction.followup
            game.join(username, webhook)
            # webhook.send(content="You successfully joined the game", ephemeral=True)
        
        self.joined = True
        # self.stop()
        return await interaction.response.send_message("You successfully joined the game",ephemeral=True, delete_after= 3.0)

    @discord.ui.button(label="Start")
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        # self.value = "N"
        game.start()
        self.stop()
        # await interaction.delete_original_response()
        return await interaction.response.send_message("Let The Waifu Battles Begin!", delete_after = 5.0)

# Commands
@tree.command(name="configure", description="Configure waifu game")
async def configure(interaction):
    # await interaction.response.send_message(content="")
    view = JoinView()
    game.configure(interaction.channel, selected_timer=4.0)
    await interaction.response.send_message(content="Get ready for waifu battles!", view = view)
    # await view.wait()
    # print(view.value)
    # await msg.delete()
    
@tree.command(name="stop", description="Stop the waifu game")
async def stop(interaction):
    game.force_end()
    await interaction.response.send_message(content="Game ended")

    
    
    
# # Commands
# @tree.command(name="token", description="Generate a waifu token")
# async def token(interaction, prompt: str = "girl", border: str = None):
#     """
#     Token image generation
    
#     :param prompt: Comma seperated descriptors (eg. green, short hair, armor)
#     :param border: Border type to surround the token with
    
#     :return: tokenized image
#     """
#     # ctx = await discord.ext.commands.Context(interaction)
#     # channel = ctx.message.channel
#     # emoji = '\N{THUMBS UP SIGN}'
#     # or '\U0001f44d' or '👍'
#     # await ctx.message.add_reaction(emoji)

#     user = interaction.user
#     previous_status = bot.guilds[0].get_member(bot.user.id).activity
#     await interaction.response.send_message(content=f"Generating a token for you: {prompt} in {border}",ephemeral = True, delete_after= 10.0)
    
#     # Change activity for the task
#     await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=' waifu being born'))
    
    
#     async with interaction.channel.typing():
#     # Long Calculation
#         image_file = "token.png"
#         try:
#             args = [sys.executable,"temp.py"]
#             if prompt:
#                 args.append(prompt)
#             else:
#                 args.append("")
#             if border:
#                 args.append(border)
#             else:
#                 args.append("")
#             print(prompt)
#             print(border)
#             image_generated = subprocess.call(args)
#             print("image generated")
#             if image_generated == 0:
#                 file = discord.File(image_file, filename=image_file)
#                 content = f"{user.name} here is your: {prompt}"
#                 if border:
#                     content += f" in a {border} border"
                    
#                 embed = discord.Embed(colour= 5500000,description=content)
#                 embed.set_image(url=f"attachment://{image_file}")
#                 embed.set_author(name=user.name,icon_url=user.avatar.url)
#                 embed.set_thumbnail(url=bot.user.avatar.url)
                
#                 await interaction.channel.send(file=file, embed=embed)
#             else:
#                 await interaction.channel.send(content="Waifu couldn't be born ",ephemeral = True, delete_after = 10.0)
#         except Exception as e:
#             print("ERROR")
#             print(e)
#     # Reset the status
#     await bot.change_presence(activity=previous_status)
    
# # autocomplete
# @token.autocomplete('border')
# async def border_autocomplete(
#     interaction: discord.Interaction,
#     current: str,
# ) -> list[app_commands.Choice[str]]:
#     borders = ["ring", "wavey", "octagon", "flat", "double"]
#     return [
#         app_commands.Choice(name=border, value=border)
#         for border in borders if current.lower() in border.lower()
#     ]

# @token.autocomplete('prompt')
# async def prompt_autocomplete(
#     interaction: discord.Interaction,
#     current: str,
# ) -> list[app_commands.Choice[str]]:
#     prompts = ["1girl, small breasts, green, dress", "1girl, small breasts, yellow, blouse, skirt", "1girl, small breasts, brown, leather armor", "1girl, small breasts, red, weapon, armor", "1girl, small breasts, purple, robe, witch hat, magic"]
#     return [
#         app_commands.Choice(name=prompt, value=prompt)
#         for prompt in prompts if current.lower() in prompt.lower()
#     ]
    
bot.run(DISCORD_TOKEN)


#%% discord bot

# import os, discord
# from discord.ext import commands

# from replit import db
# from game import *

# DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# bot = commands.Bot(command_prefix="/")

# @bot.event
# async def on_ready():
#     print(f"{bot.user} has connected to Discord!")
    
# # Commands
# @bot.command(name="create", help="Create a character.")
# async def create(ctx, name=None):
#     user_id = ctx.message.author.id

#     # if no name is specified, use the creator's nickname
#     if not name:
#         name = ctx.message.author.name
        
#     embed = discord.Embed(title=f"{character.name} status", description=mode_text, color=MODE_COLOR[character.mode])
#     embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    
    
#     embed.add_field(name="Stats", value=f"""
# **HP:**    {character.hp}/{character.max_hp}
# **ATTACK:**   {character.attack}
# **DEFENSE:**   {character.defense}
# **MANA:**  {character.mana}
# **LEVEL:** {character.level}
# **XP:**    {character.xp}/{character.xp+xp_needed}
#     """, inline=True)
    
#     emoji = '\N{THUMBS UP SIGN}'
# # or '\U0001f44d' or '👍'
# await message.add_reaction(emoji)
    
# file = discord.File("path/to/my/image.png", filename="image.png")
# embed = discord.Embed()
# embed.set_image(url="attachment://image.png")
# await channel.send(file=file, embed=embed)

# # Define a simple View that gives us a confirmation menu
# class Confirm(discord.ui.View):
#     def __init__(self):
#         super().__init__()
#         self.value = None

#     # When the confirm button is pressed, set the inner value to `True` and
#     # stop the View from listening to more input.
#     # We also send the user an ephemeral message that we're confirming their choice.
#     @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
#     async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_message('Confirming', ephemeral=True)
#         self.value = True
#         self.stop()

#     # This one is similar to the confirmation button except sets the inner value to `False`
#     @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
#     async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_message('Cancelling', ephemeral=True)
#         self.value = F
        
# @bot.command()
# async def ask(ctx: commands.Context):
#     """Asks the user a question to confirm something."""
#     # We create the view and assign it to a variable so we can wait for it later.
#     view = Confirm()
#     await ctx.send('Do you want to continue?', view=view)
#     # Wait for the View to stop listening for input...
#     await view.wait()
#     if view.value is None:
#         print('Timed out...')
#     elif view.value:
#         print('Confirmed...')
#     else:
#         print('Cancelled...')
        
        
# # Define a simple View that gives us a counter button
# class Counter(discord.ui.View):

#     # Define the actual button
#     # When pressed, this increments the number displayed until it hits 5.
#     # When it hits 5, the counter button is disabled and it turns green.
#     # note: The name of the function does not matter to the library
#     @discord.ui.button(label='0', style=discord.ButtonStyle.red)
#     async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
#         number = int(button.label) if button.label else 0
#         if number + 1 >= 5:
#             button.style = discord.ButtonStyle.green
#             button.disabled = True
#         button.label = str(number + 1)

#         # Make sure to update the message with our updated selves
#         await interaction.response.edit_message(view=self)


# # Define a View that will give us our own personal counter button
# class EphemeralCounter(discord.ui.View):
#     # When this button is pressed, it will respond with a Counter view that will
#     # give the button presser their own personal button they can press 5 times.
#     @discord.ui.button(label='Click', style=discord.ButtonStyle.blurple)
#     async def receive(self, interaction: discord.Interaction, button: discord.ui.Button):
#         # ephemeral=True makes the message hidden from everyone except the button presser
#         await interaction.response.send_message('Enjoy!', view=Counter(), ephemeral=True)


# bot = EphemeralCounterBot()


# @bot.command()
# async def counter(ctx: commands.Context):
#     """Starts a counter for pressing."""
#     await ctx.send('Press!', view=EphemeralCounter())

# bot.run(DISCORD_TOKEN)