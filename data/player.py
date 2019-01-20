class Player:
    """Class responsible for storing player specific data,
    transmitting actions to Game and receiving updates
    """
    def __init__(self, nickname, role=None, character=None, health=4):
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

    def selected_card(self):
        for card in self.hand:
            if card.selected:
                print(card)
                return card

    def set_all_cards_select_to_false(self):
        for card in self.hand:
            card.selected = False

