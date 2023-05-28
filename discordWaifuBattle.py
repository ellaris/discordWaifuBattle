# -*- coding: utf-8 -*-
"""
Created on Sun May 21 15:57:34 2023

@author: tomas
"""
import random
import threading
import re
import json

class Player:
    name = ""
    
    cards = []
    index = -1
    score = 0
    field = ""
    vote = -1
    
    def __init__(self, name):
        global players
        self.name = name
        self.index = len(players)
        players.append(self)
    
    def addCard(self, card):
        self.cards.append(card)
        
    def playCard(self, index):
        _card = self.cards.pop(index)
        # add to
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
    
    JSON_FILE_NAME = "waifu_cards.json"
    
    def save_json_db(self):
        with open(self.JSON_FILE_NAME,"w") as file:
            json.dump(card_database, file) 
        
    def load_json_db(self):
        global card_database
        with open(self.JSON_FILE_NAME,"r") as file:
            card_database = json.load(file)
        
    def add_card(self, url, tag, owner):
        global card_database
        self.card_database.append({"url":url,"tag":tag,"owner":owner})
        self.save_json_db()
    
    
    def __init__(self):
        self.load_json_db()
        


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

# game_database = []




    

    
    def configure(self, play_rounds = 4, cards = card_database, selected_type = "", selected_timer = 60.0, allowed_cards = ""):
        # global rounds, playing_cards, allow_join, players, current_round, game_type, timer, game_database
        self.rounds = play_rounds
        self.current_round = 0
        self.players = []
        # field = []
        # playing_cards = cards.copy()
        # allow_join = True
        self.game_type = selected_type
        self.timer = selected_timer
        if allowed_cards == "":
            self.playing_cards = [card["url"] for card in  self.card_database if re.search(allowed_cards,card["tag"]) ]
        else:
            self.playing_cards =  self.card_database.copy()
        
    def join(self, name):
        # global rounds, playing_cards, allow_join
        if  self.current_round > 0:
            return("Game is in progress")
        if len( self.playing_cards) <  self.rounds:
            return("Not enough cards left!")
        
        p = Player(name)
        for i in range( self.rounds):
            p.addCard( self.playing_cards.pop(random.randint(0, len( self.playing_cards)-1)))
        self.display_hand(p)
        return(f"{name} successfully joined the waifu battle")
        
    def choose(self, player_name, card_index):
        # player_name = input("p:")
        # card_index = input("i:")
        player = None
        for p in  self.players:
            if p.name == player_name:
                player = p
                break
        if player:
            player.playCard(int(card_index))
        
    def vote(self, player_name, card_index):
        # player_name = input("p:")
        # card_index = input("i:")
        player = None
        for p in  self.players:
            if p.name == player_name:
                player = p
                break
        if player:
            player.registerVote(int(card_index))
            
    def start(self):
        # global allow_join, current_round, players, timer_value, voting
        self.timer_value =  self.timer
        # allow_join = False
        self.current_round += 1
        for player in  self.players:
            player.vote = -1
            
        # announce round and current mode
        self.display_round()
        self.display_mode()
        
        self.voting = False
        # choosing time!
        t = threading.Timer(1,  self.run_timer)
        t.start()
        # choose()
        
    def force_end(self):
        # global current_round, timer_value
        self.timer_value = 0
        self.current_round =  self.rounds + 1
        self.game_end()
        
    def round_end(self):
        # global current_round, players, rounds
        self.current_round += 1
        field = []
        for player in  self.players:
            if player.field == "": # no selection, select random
                player.playCard(random.randint(0, len(player.cards)-1))
            field.append(player.field)
            player.field = ""
            
        self.display_field(field)
        
        # announce current mode
        self.display_mode()
        
        # voting time!
        t = threading.Timer(1, self.run_timer)
        t.start()
        # vote()
        
    def collect_votes(self):
        # global players
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
        self.display_mode()
        
        for p in self.players:
            self.display_hand(p)
        
        t = threading.Timer(1, self.run_timer)
        t.start()
        
    def game_end(self):
        self.display_scores()
        
    def display_mode(self):
        # global timer
        mode_str = ""
        if self.voting:
            mode_str += "Vote"
        else:
            mode_str += "Choose"
        mode_str += f" in {self.timer} seconds"
        
        print(mode_str)
    
    def display_round(self):
        print(f"Round {self.current_round}")
        
    def display_vote_results(self, votes):
        vote_str = "Votes\n"
        for vote,player in zip(votes,self.players):
            vote_str += f"{player.name}: {vote}  "
        print(vote_str)
        
    def display_field(self, field):
        gt = self.game_type
        field_str = ""
        if self.game_type == "":
            gt = self.game_types[random.randint(0, len(self.game_types)-1)]
        field_str += f"Vote for: {gt}\n"
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
            
    def run_timer(self):
        # global timer, timer_value, voting
        self.time_left = int(self.timer_value)
        end_timer = False
        
        if self.voting:
            # check if everyone voted
            if all([player.vote >= 0 for player in players]):
                end_timer = True
        else:
            # check if everyone chose a card
            if all([player.field != "" for player in players]):
                end_timer = True
        if self.time_left < 1:
                end_timer = True
                
        if end_timer:
            if self.voting:
                self.collect_votes()
            else:
                self.round_end()
            self.voting = not self.voting
            self.timer_value = self.timer
            return(0)
        
        self.timer_value -= 1
        
        if self.time_left <= 3:
            self.display_time(self.time_left)
        if self.time_left >= 1:
            t = threading.Timer(1, self.run_timer)
            t.start()
    