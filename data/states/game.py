import os
import random
import pygame as pg
from .. import tools, card, data, player
from ..GUI import button
from . import states


class Game(states.States):
    """For now(!): Create screen, 
    update both Player and Game, render gathered data
    """
    def __init__(self, screen_rect):
        super().__init__()
        self.screen_rect = screen_rect
        self.scaling_factor = int(self.screen_rect.width / 400)
        self.overlay_bg = pg.Surface((screen_rect.width, screen_rect.height))
        self.overlay_bg.fill(0)
        self.overlay_bg.set_alpha(200)
        self.overlay_card_position = (100, 200)
        self.database = data.data
        self.full_deck = []
        self.create_full_deck()
        self.card_size = self.full_deck[0].rect.size
        self.deck = []  # only playable cards
        self.fill_deck()
        self.table = []
        self.discard = []
        self.backend_path = os.path.join(tools.Image.path, "cards/other/backend.png")
        self.thickness_path = os.path.join(tools.Image.path, "cards/other/deck_thickness.png")
        self.gun_placeholder_path = os.path.join(tools.Image.path, "cards/other/gun_placeholder.png")
        self.backend_card = card.Card(
            self.backend_path, pg.image.load(self.backend_path), self.screen_rect
        )
        self.deck_thickness_card = card.Card(
            self.thickness_path, pg.image.load(self.thickness_path), self.screen_rect
        )
        self.gun_placeholder_card = card.Card(
            self.thickness_path, pg.image.load(self.gun_placeholder_path), self.screen_rect
        )

        self.bg_color = (255, 255, 255)
        self.help_overlay = False
        self.hand_card_bufferX = self.card_size[0] / 2

        # x and y to place deck in the middle of the screen (a bit left)
        self.play_deck_x = self.screen_rect.centerx - self.card_size[0]
        self.play_deck_y = self.screen_rect.centery - self.card_size[1] / 2
        self.hand_card_bufferY = 25
        self.bg = tools.Image.load("greenbg.png")
        self.bg_rect = self.bg.get_rect()

        self.help_btn_image = tools.Image.load("info.png")
        self.help_btn_image = pg.transform.scale(self.help_btn_image, (25 * self.scaling_factor, 
                                                                       25 * self.scaling_factor)
        )
        self.help_btn_image_rect = self.help_btn_image.get_rect(topleft=(0, 0))

        self.settings = tools.Image.load("gear.png")
        self.settings = pg.transform.scale(self.settings, (25, 25))
        self.settings_rect = self.settings.get_rect(topleft=(25, 0))

        button_config = {
            "hover_color": (100, 255, 100),
            "clicked_color": (255, 255, 255),
            "clicked_font_color": (0, 0, 0),
            "hover_font_color": (0, 0, 0),
            "font": tools.Font.load("impact.ttf", 8 * self.scaling_factor),
            "font_color": (0, 0, 0),
            "call_on_release": True,
        }

        self.play_button_width =  40 * self.scaling_factor
        self.play_button_height = 15 * self.scaling_factor
        self.play_card_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.card_to_discard,
            text="Play Card",
            **button_config,
        )
        self.equip_gun_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.player_equip_gun,
            text="Equip gun",
            **button_config,
        )
        self.equip_buff_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.player_equip_buff,
            text="Equip buff",
            **button_config,
        )
        self.player = player.Player("Tarn")

        #############TEMPORARY#############
        self.player1 = player.Player("Bot1")
        self.player2 = player.Player("Bot2")
        #############TEMPORARY#############

################################################################################
#######################################GAME#####################################
################################################################################

    def card_to_discard(self, card=None):
        """Remove card from it's storage and move to discard"""
        if not card:
            card = self.player.selected_card()
        if card in self.player.hand:
            self.player.hand.remove(card)
        elif card in self.player.buffs:
            self.player.buffs.remove(card)
        elif card is self.player.gun:
            self.discard.append(card)
        self.discard.append(card)
        self.button_sound.sound.play()

    def check_select_deselect_card(self):
        """Check if card was selected/deselected. 
        If card is fully visible (the last one or/and selected) 
        it can be selected everywhere, otherwise only on left side of card.
        """
        for card in self.player.hand:
            half_width = int(card.rect.width / 2)
            card_left_side = card.rect.inflate(-half_width, 0)
            card_left_side.x -= int(half_width / 2)

            if card.selected:
                if card.rect.collidepoint(pg.mouse.get_pos()):
                    card.selected = not card.selected
                    self.button_sound.sound.play()
                    return card

            elif card == self.player.hand[-1]:
                if card.rect.collidepoint(pg.mouse.get_pos()):
                    self.player.set_all_cards_select_to_false()
                    card.selected = True
                    self.button_sound.sound.play()
                    return card

            else:
                if card_left_side.collidepoint(pg.mouse.get_pos()):
                    self.player.set_all_cards_select_to_false()
                    card.selected = True
                    self.button_sound.sound.play()
                    return card

    def fill_deck(self):
        """Fill deck with playable cards only"""
        for card in self.full_deck:
            if tools.get_category(card.path) not in ["roles", "characters", "other"]:
                self.deck.append(card)
        random.shuffle(self.deck)

    def draw_cards(self, N):
        """Return last N removed cards from deck"""
        drawn = self.deck[-N:]
        self.deck = self.deck[:-N]
        return drawn

    def discard_to_deck(self):
        """Pass reshuffled discard deck to play deck,
        leave last card in discard
        """
        if not self.deck:
            self.deck = self.discard[:-1]
            random.shuffle(self.deck)
            self.discard = self.discard[-1:]

    def create_full_deck(self):
        """Create full deck from all possible cards in data dict"""
        path = os.path.join(tools.Image.path, "cards")
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".png"):
                    path = os.path.abspath(os.path.join(root, f))
                    image = pg.image.load(path)
                    filename = tools.get_filename(path)
                    for i in range(self.database[filename]["max"]):
                        self.full_deck.append(card.Card(path, image, self.screen_rect))

    def player_equip_gun(self):
        """Player equip gun, discard previous gun"""
        card = self.player.equip_gun()
        if card:
            self.discard.append(card)
        self.button_sound.sound.play()

    def player_equip_buff(self):
        self.player.equip_buff()
        self.button_sound.sound.play()

    def cleanup(self):
        pass

    def entry(self):
        if not self.player.is_hand_set:
            self.player.is_hand_set = True
            # TEMPORARY
            self.player.hand = self.draw_cards(7)
            self.deck = self.deck[:15]


    ### SOME OF THESE WILL CALL SIMIAL PLAYER METHODS 

    def card_to_table(self, card):
        pass

    def card_to_target(self, card, target):
        pass

    def card_to_all(self, card):
        pass

################################################################################
######################################EVENTS####################################
################################################################################

    def get_event(self, event, keys):
        if not self.help_overlay:
            if self.player.selected_card():
                selected_card = self.player.selected_card()
                self.play_card_button.check_event(event)
                if tools.get_category(selected_card.path) == "guns":
                    self.equip_gun_button.check_event(event)
                elif tools.get_category(selected_card.path) == "buffs":
                    buff_names = []
                    for buff in self.player.buffs:
                        buff_names.append(tools.get_filename(buff.path))
                    if tools.get_filename(selected_card.path) not in buff_names:
                        self.equip_buff_button.check_event(event)

        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == self.keybinding["back"]:
                if not self.help_overlay:
                    self.button_sound.sound.play()
                    self.done = True
                    self.next = "MENU"
                else:
                    self.help_overlay = not self.help_overlay

        elif event.type == self.background_music.track_end:
            self.play_next_track()

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not self.help_overlay:
                self.check_select_deselect_card()
            if self.help_btn_image_rect.collidepoint(pg.mouse.get_pos()):
                if self.player.selected_card():
                    self.help_overlay = not self.help_overlay

################################################################################
######################################UPDATE####################################
################################################################################
    
    def update(self, now, keys):
        if not self.help_overlay:
            self.discard_to_deck()
            self.update_hand_position()
            self.update_table_decks_pisition()
            self.update_buffs_position()
            if not self.player.selected_card():
                card.Card.deselect_cards() 

            # TEMPORARY
            if not self.player.hand and self.deck:
                self.player.hand = self.draw_cards(4) or self.draw_cards(len(self.deck))

        else:
            filename = tools.get_filename(self.player.selected_card().path)
            self.help_overlay_title, self.help_overlay_title_rect = self.make_text(
                filename.title(),
                (255, 255, 255),
                (self.screen_rect.centerx, 100),
                60,
                fonttype="impact.ttf",
            )

            string = self.database[filename]["info"]
            my_font = tools.Font.load("impact.ttf", 20)
            self.help_overlay_text_rect = pg.Rect((400, 200, 300, 300))
            self.help_overlay_text = tools.render_textrect(
                string,
                my_font,
                self.help_overlay_text_rect,
                (216, 216, 216),
                (48, 48, 48, 255),
                0,
            )

    def reposition_card_buttons(self):
        """place buttons on top of the selected card"""
        self.play_card_button.rect.center = self.player.selected_card().rect.center
        self.play_card_button.rect.y -= (self.card_size[1] / 2 
                                        + self.play_button_height/2 
                                        + 2 * self.scaling_factor
                                        )
        self.equip_gun_button.rect.x = self.play_card_button.rect.right + 5
        self.equip_gun_button.rect.y = self.play_card_button.rect.y
        self.equip_buff_button.rect.x = self.play_card_button.rect.right + 5
        self.equip_buff_button.rect.y = self.play_card_button.rect.y

    def update_table_decks_pisition(self):
        self.deck_thickness_card.rect.y = self.play_deck_y - (0.01 * len(self.deck))
        self.deck_thickness_card.rect.x = self.play_deck_x - (0.2 * len(self.deck))

    def update_hand_position(self):
        """Center hand in the middle of the screen,
        shift all cards after selected to make it fully visible.
        """
        move = []
        hand_width = (len(self.player.hand) + 1) * self.hand_card_bufferX
        hand_x = self.screen_rect.centerx - hand_width / 2
        for i, card in enumerate(self.player.hand):
            card.rect.y = self.screen_rect.bottom - card.surf.get_height() * 1.05
            if card.selected:
                card.rect.y -= self.hand_card_bufferY
                move = self.player.hand[i+1:]
            card.rect.x = hand_x + i * self.hand_card_bufferX
        for i, c in enumerate(move):
            c.rect.x = hand_x + self.player.hand.index(move[i]) * self.hand_card_bufferX  + self.card_size[0] * 1.1 / 2

    def update_buffs_position(self):
        buffs_width = (len(self.player.hand) + 1) * self.hand_card_bufferX
        buffs_x = self.screen_rect.centerx - buffs_width / 2
        for i, card in enumerate(self.player.buffs):
            card.rect.y = self.screen_rect.bottom - card.surf.get_height() * 1.25
            card.rect.x = buffs_x + i * self.hand_card_bufferX

################################################################################
######################################RENDER####################################
################################################################################

    def render(self, screen):
        screen.blit(self.bg, self.bg_rect)
        self.render_table_decks(screen)
        self.render_gun(screen)
        self.render_buffs(screen)
        self.render_hand(screen)
        if self.help_overlay: 
            self.render_overlay(screen)

    def render_gun(self, screen):
        screen.blit(self.gun_placeholder_card.surf, 
                    (self.screen_rect.width - self.card_size[0] - self.scaling_factor, 
                     self.screen_rect.bottom - self.card_size[1] * 1.05)
            )
        if self.player.gun:
            screen.blit(self.player.gun.surf, 
                        (self.screen_rect.width - self.card_size[0] - self.scaling_factor, 
                         self.screen_rect.bottom - self.card_size[1] * 1.05)
            )

    def render_hand(self, screen):
        c = None
        for card in self.player.hand:
            if card.selected:
                c = card
            else:
                screen.blit(card.surf, (card.rect.x, card.rect.y))
        if c:
            screen.blit(c.surf, (c.rect.x, c.rect.y))
        self.render_play_buttons(screen)

    def render_buffs(self, screen):
        for card in self.player.buffs:
            screen.blit(card.surf, (card.rect.x, card.rect.y))

    def render_play_buttons(self, screen):
        """Render play buttons on top of the selected card.
        Equip gun button for guns
        Equip buff button for buffs which are not applied already
        Play Card for all cards (TEMPORARY)
        """
        if self.player.selected_card():
            self.reposition_card_buttons()
            self.play_card_button.render(screen)
            if tools.get_category(self.player.selected_card().path) == "guns":
                self.equip_gun_button.render(screen)
            elif tools.get_category(self.player.selected_card().path) == "buffs":
                buff_names = []
                for buff in self.player.buffs:
                    buff_names.append(tools.get_filename(buff.path))
                if tools.get_filename(self.player.selected_card().path) not in buff_names:
                    self.equip_buff_button.render(screen)
            screen.blit(self.help_btn_image, self.help_btn_image_rect)

    def render_overlay(self, screen):
        screen.blit(self.overlay_bg, (0, 0))
        screen.blit(self.help_overlay_title, self.help_overlay_title_rect)
        screen.blit(self.help_overlay_text, self.help_overlay_text_rect)
        sel = self.player.selected_card()
        screen.blit(sel.surf, self.overlay_card_position)

    def render_table_decks(self, screen):
        if self.deck:
            screen.blit(
                self.deck_thickness_card.surf,
                (self.deck_thickness_card.rect.x, self.deck_thickness_card.rect.y),
            )

            screen.blit(self.backend_card.surf, (self.play_deck_x, self.play_deck_y))
        if self.discard:
            screen.blit(self.discard[-1].surf, 
                        (self.play_deck_x + self.card_size[0] * 1.1, 
                         self.play_deck_y
                         )
            )
