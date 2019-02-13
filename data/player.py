import random
import os
import string
import pygame as pg
from . import tools, data

class Player:
    """Class responsible for storing player specific data,
    transmitting actions to Game and receiving updates
    """
    objects = []
    def __init__(self, nickname, role=None, character=None):
        super().__init__()
        self.id = self.randomize_id()
        self.nickname = nickname
        if not role:
            self.role = self.random_role()
        else:
            self.role = role
        self.role_image = tools.Image.load(f"roles/{self.role}.png")
        self.role_image_rect = self.role_image.get_rect()
        if not character:
            self.character = self.random_character()
        else:
            self.character = character
        self.character_image = tools.Image.load(f"chars/{self.character}.png")
        self.character_image_rect = self.character_image.get_rect()
        self.health = data.data[self.character]["life"]
        if self.role == "sheriff":
            self.health += 1
        self.alive = True
        self.hand = None
        self.is_hand_set = False
        self.gun = None
        self.buffs = []
        self.curses = []
        self.turn = False
        Player.objects.append(self)
        print(f"Player name: {self.nickname}, player id: {self.id}, character: {self.character}, role: {self.role} joined game")

    def selected_card(self):
        for card in self.hand:
            if card.selected:
                return card

    def set_all_cards_select_to_false(self):
        for card in self.hand:
            card.selected = False

    def equip_gun(self):
        """Equip gun from selected card,
        return old gun or None.
        """
        old_card = None
        card = self.selected_card()
        if self.gun:
            old_card = self.gun
        self.gun = card
        self.hand.remove(card)
        return old_card

    def equip_buff(self, card=None):
        """Equip buff card
        """
        if not card:
            card = self.selected_card()
        self.buffs.append(card)
        self.hand.remove(card)

    def randomize_id(self):
        """Return unique and random string as player's id."""
        id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=30))
        while id in Player.objects:
            self.randomize_id()
        return id

    def random_character(self):
        """Return random filename without extension from chars folder"""
        characters = []
        path = os.path.join(tools.Image.path, "chars")
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".png"):
                    characters.append(f[:-4])
        return random.choice(characters)

    def random_role(self):
        """Return random filename without extension from roles folder"""
        roles = []
        path = os.path.join(tools.Image.path, "roles")
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".png"):
                    roles.append(f[:-4])
        return random.choice(roles)

    @classmethod
    def get_player_by_id(cls, id):
        """Return all availible player objects"""
        for obj in cls.objects:
            if obj.id == id:
                return obj
