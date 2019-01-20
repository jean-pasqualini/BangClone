class Player:
    """Class responsible for storing player specific data,
    transmitting actions to Game and receiving updates
    """
    def __init__(self, role=None, character=None, health=4, nickname):
        super().__init__()
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


    def card_to_discard(self, card=None):
        if not card:
            card = self.selected_card()
        if card in self.hand:
            self.hand.remove(card)
        elif card is self.gun:
            self.gun = None
        self.discard.append(card)
        self.button_sound.sound.play()

    def selected_card(self):
        for card in self.hand:
            if card.selected:
                print(card)
                return card

    def set_all_cards_select_to_false(self):
        for card in self.hand:
            card.selected = False

    def equip_gun(self, card=None):
        """"""
        if not card:
            card = self.selected_card()
        if self.gun:
            self.card_to_discard(self.gun)
        self.gun = card
        self.hand.remove(card)
        print(self.gun)
