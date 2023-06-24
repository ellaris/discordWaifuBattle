# -*- coding: utf-8 -*-
"""
Created on Sun May 21 15:57:34 2023

@author: tomas
"""
import random
import threading
import re
import json
import asyncio

# card_database = [
#     {
#      "url":"https://e0.pxfuel.com/wallpapers/524/906/desktop-wallpaper-best-waifu-chika-fujiwara-love-is-war-2020-anime-waifu-thumbnail.jpg", "tag":"base" ,"owner":"base"
#      },
#     {
#      "url":"https://w0.peakpx.com/wallpaper/1020/514/HD-wallpaper-chizuru-mizuhara-anime-best-waifu-big-oppai-girl-rent-a-girlfriend-waifu-thumbnail.jpg", "tag":"base" ,"owner":"base"
#     },
#      {
#       "url":"https://w7.pngwing.com/pngs/97/193/png-transparent-nezuko-waifu-senyor-thumbnail.png", "tag":"base" ,"owner":"base"
#      },
#      {
#       "url":"https://e7.pngegg.com/pngimages/906/702/png-clipart-anime-board-waifu-anime-cg-artwork-cartoon.png", "tag":"base" ,"owner":"base"
#      },
#      {
#       "url":"https://i.redd.it/anime-waifu-v0-0kvzp0q70nha1.png?width=3072&format=png&auto=webp&s=60993640f0418bd479bb53e7ed503c9d2ffba107", "tag":"base" ,"owner":"base"
#      },
#     {
#      "url":"https://i.waifu.pics/3DpVCc3.jpg", "tag":"base" ,"owner":"base"
#     },
#     ]

class Player:
    name = ""
    
    cards = []
    index = -1
    score = 0
    field = ""
    vote = -1
    
    def __init__(self, name, index):
        self.name = name
        self.index = index
    
    def addCard(self, card):
        self.cards.append(card)
        
    def playCard(self, index):
        _card = self.cards.pop(index)
        self.field = _card
        
    def registerVote(self, vote):
        self.vote = vote
        
class WaifuBattleGame:
    
    voting = False
    timer = 60.0
    timer_value = 0
    rounds = 4
    current_round = 0
    players = []
    game_type = ""
    game_types = ["Pretty","Ugly","Fat","Booba","Flat","Skinny"]
    playing_cards = []
    card_database = []
    loop = None
    
    JSON_FILE_NAME = "waifu_cards.json"
    
    def save_json_db(self):
        with open(self.JSON_FILE_NAME,"w") as file:
            json.dump(self.card_database, file) 
        
    def load_json_db(self):
        with open(self.JSON_FILE_NAME,"r") as file:
            self.card_database = json.load(file)
        
    def add_card(self, url, tag, owner):
        self.card_database.append({"url":url,"tag":tag,"owner":owner})
        self.save_json_db()
    
    
    def __init__(self):
        self.load_json_db()
        self.loop = asyncio.get_running_loop()

    def configure(self, play_rounds = 4, cards = card_database, selected_type = "", selected_timer = 60.0, allowed_cards = ""):
        self.rounds = play_rounds
        self.current_round = 0
        self.players = []
        self.game_type = selected_type
        self.timer = selected_timer
        if allowed_cards != "":
            self.playing_cards = [card["url"] for card in  self.card_database if re.search(allowed_cards,card["tag"]) ]
        else:
            self.playing_cards =  self.card_database.copy()
        
    def join(self, name):
        if  self.current_round > 0:
            return("Game is in progress")
        if len( self.playing_cards) <  self.rounds:
            return("Not enough cards left!")
        
        p = Player(name, len(self.players))
        self.players.append(p)
        
        for i in range( self.rounds):
            p.addCard( self.playing_cards.pop(random.randint(0, len( self.playing_cards)-1)))
        self.display_hand(p)
        return(f"{name} successfully joined the waifu battle")
        
    def choose(self, player_name, card_index):
        # player_name = input("p:")
        # card_index = input("i:")
        success = False
        player = None
        for p in  self.players:
            if p.name == player_name:
                player = p
                break
        if player and player.field == "":
            player.playCard(int(card_index))
            success = True
        return success
        
    def vote(self, player_name, card_index):
        # player_name = input("p:")
        # card_index = input("i:")
        success = False
        player = None
        for p in  self.players:
            if p.name == player_name:
                player = p
                break
        if player and player.vote == -1:
            player.registerVote(int(card_index))
            success = True
        return success
            
    def start(self):
        self.timer_value =  self.timer
        self.current_round += 1
        for player in  self.players:
            player.vote = -1
            
        # announce round and current mode
        self.display_round()
        self.display_mode()
        
        self.voting = False
        # choosing time!
        # t = threading.Timer(1, self.run_timer)
        # t.start()
        self.loop.create_task(self.run_timer())
        # choose()
        
    def force_end(self):
        self.timer_value = 0
        self.current_round =  self.rounds + 1
        self.game_end()
        
    def round_end(self):
        self.current_round += 1
        field = []
        for player in  self.players:
            if player.field == "": # no selection, select random
                player.playCard(random.randint(0, len(player.cards)-1))
            field.append(player.field)
            player.field = ""
            
        self.display_field(field)
        
        # announce current mode
        self.voting = True
        self.display_mode()
        
        # voting time!
        # t = threading.Timer(1, self.run_timer)
        # t.start()
        self.loop.create_task(self.run_timer())
        # vote()
        
    def collect_votes(self):
        votes = []
        for player in self.players:
            votes.append(0)
        for player in self.players:
            if player.vote == -1:
                player.registerVote(random.randint(0, len(self.players)-1))
            if self.players.index(player) == player.vote:
                votes[player.vote] -= 1
            else:
                votes[player.vote] += 1
            player.vote = -1
        winner = self.players[votes.index(max(votes))]
        winner.score += 1
        
        # announce voting results
        self.display_vote_results(votes)
        
        if self.current_round > self.rounds:
            self.game_end()
            return("")
        
        self.display_scores(compact=True)
        
        # announce round and current mode
        self.display_round()
        self.voting = False
        self.display_mode()
        
        for p in self.players:
            self.display_hand(p)
        
        # choosing time
        # t = threading.Timer(1, self.run_timer)
        # t.start()
        self.loop.create_task(self.run_timer())
        
    def game_end(self):
        self.display_scores()
        
    def display_mode(self):
        mode_str = ""
        if self.voting:
            mode_str += "Vote"
        else:
            mode_str += "Choose"
        mode_str += f" in {self.timer} seconds"
        
        print(mode_str)
    
    def display_round(self):
        gt = self.game_type
        if self.game_type == "":
            gt = self.game_types[random.randint(0, len(self.game_types)-1)]
        print(f"Round {self.current_round}\nCategory: {gt}")
        
    def display_vote_results(self, votes):
        vote_str = "Votes\n"
        for vote,player in zip(votes,self.players):
            vote_str += f"{player.name}: {vote}  "
        print(vote_str)
        
    def display_field(self, field):
        field_str = ""
        field_str += "Vote \n"
        for card in field:
            field_str += f"{card}\n"
        print(field_str)
        
    def display_scores(self, compact=False):
        sorted_players = sorted(self.players, key = lambda player: player.score, reverse=True)
        scores_str = "Score:\n"
        for player in sorted_players:
            if compact:
                scores_str += f"{player.name}:{player.score} "
            else:
                scores_str += f"\n{player.name} has score of {player.score}"
        print(scores_str)
            
    def display_hand(self, player):
        hand_str = ""
        hand_str += player.name+"\n"
        for card in player.cards:
            hand_str += f"{card} \n"
            
        print(hand_str)
            
    def display_time(self, time_left):
        print(f"{time_left}")
            
    async def run_timer(self):
        self.time_left = int(self.timer_value)
        end_timer = False
        await asyncio.sleep(1)
        
        if self.voting:
            # check if everyone voted
            if all([player.vote >= 0 for player in self.players]):
                end_timer = True
        else:
            # check if everyone chose a card
            if all([player.field != "" for player in self.players]):
                end_timer = True
        if self.time_left < 1:
                end_timer = True
                
        if end_timer:
            if self.voting:
                self.collect_votes()
            else:
                self.round_end()
            # self.voting = not self.voting
            self.timer_value = self.timer
            return(0)
        
        self.timer_value -= 1
        
        if self.time_left <= 3:
            self.display_time(self.time_left)
        if self.time_left >= 1:
            # t = threading.Timer(1, self.run_timer)
            # t.start()
            self.loop.create_task(self.run_timer())
    