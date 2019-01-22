import random
import string


class Player:
    """Class responsible for storing player specific data,
    transmitting actions to Game and receiving updates
    """
    objects = []
    def __init__(self, nickname, role=None, character=None, health=4):
        super().__init__()
        self.id = self.randomize_id()
        self.nickname = nickname
        self.role = role
        self.character = character
        self.hand = None
        self.is_hand_set = False        
        self.gun = None
        self.active_cards = []
        self.health = health
        self.alive = True
        self.buffs = []
        self.curses = []
        Player.objects.append(self)
        print(f"Player name: {self.nickname}, player id: {self.id} joined game")


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

    def randomize_id(self):
        """Return unique and random string as player's id."""
        id = ''.join(random.choices(string.ascii_lowercase + string.digits + string.punctuation, k=20))
        while id in Player.objects:
            self.randomize_id()
        return id

    @classmethod
    def get_players(cls):
        """Return all availible player objects"""
        ids = [obj for obj in cls.objects]
        return ids
