"""Represent state of actual game play table. 
Handle updating table info, rendering everythibg to screen, 
handling player events.
"""
import os
import random
import pygame as pg
from .. import tools, card, data, player
from ..GUI import button
from . import states
from PodSixNet.Connection import connection, ConnectionListener


class Game(states.States, ConnectionListener):
    """Store play table info, players, handle events, receive updated&rendered info
    Implement game logic.
    """
    def __init__(self, screen_rect):
        states.States.__init__(self)
        self.screen_rect = screen_rect
        self.cards_database = data.data
        self.roles_database = data.roles
        self.deck = []  # only playable cards
        self.create_deck()
        self.table = []
        self.discard = []
        self.connected = False
        self.player = player.Player("Tarn")
        # self.enemy_player = player.Player("Bot1")

        self.button_functions = [self.card_to_discard, self.player_equip_gun, self.player_equip_buff]
        self.visualizer = GameVisualizer(self.screen_rect, self.player, self.deck, self.discard, self.button_functions)

        self.Connect(('localhost', 1337))
        connection.Send({"player": self.player.id})

    def Network_hello(self, data):
        print(data["message"])

    def card_to_discard(self, card=None):
        """Remove card from it's storage (except deck) and move to discard.
        if no card passed - discards self selected card
        """
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
        connection.Send({"action": "card", "card": card.path})

    def check_select_deselect_card(self):
        """Check if card was hovered by mouse.
        If card is fully visible (the last one or/and selected)
        it can be selected everywhere, otherwise only on left (visible) side of card.
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

    def draw_cards(self, N):
        """Return last N removed cards from deck"""
        drawn = self.deck[-N:]
        self.deck = self.deck[:-N]
        return drawn

    def discard_to_deck_reshuffle(self):
        """Pass reshuffled discard deck to play deck,
        leave last card in discard
        """
        if not self.deck:
            self.deck = self.discard[:-1]
            random.shuffle(self.deck)
            self.discard = self.discard[-1:]

    def create_deck(self):
        """Fill shuffled deck with playable decks in specified amounts from db"""
        path = os.path.join(tools.Image.path, "cards")
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".png"):
                    path = os.path.abspath(os.path.join(root, f))
                    image = pg.image.load(path)
                    filename = tools.get_filename(path)
                    if tools.get_category(path) not in ["roles", "characters", "other"]:
                        for i in range(self.cards_database[filename]["max"]):
                            self.deck.append(card.Card(path, image, self.screen_rect))
        random.shuffle(self.deck)

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
        # if not self.player.is_hand_set:
            # self.player.is_hand_set = True
            # TEMPORARY
        self.player.hand = self.draw_cards(7)
        # self.enemy_player.hand = self.draw_cards(7)
        # print(self.enemy_player.hand)

################################################################################
##################################_MAIN_METHODS_################################
################################################################################

    def get_event(self, event, keys):
        if not self.visualizer.card_help_overlay:
            if self.player.selected_card():
                selected_card = self.player.selected_card()
                self.visualizer.play_card_button.check_event(event)
                if tools.get_category(selected_card.path) == "guns":
                    self.visualizer.equip_gun_button.check_event(event)
                elif tools.get_category(selected_card.path) == "buffs":
                    buff_names = []
                    for buff in self.player.buffs:
                        buff_names.append(tools.get_filename(buff.path))
                    if tools.get_filename(selected_card.path) not in buff_names:
                        self.visualizer.equip_buff_button.check_event(event)

            if self.visualizer.role_rect.collidepoint(pg.mouse.get_pos()) and not self.visualizer.character_rect.collidepoint(pg.mouse.get_pos()):
                    self.visualizer.role_overlay = True
            else:
                self.visualizer.role_overlay = False
            if self.visualizer.character_rect.collidepoint(pg.mouse.get_pos()):
                self.visualizer.character_overlay = True
            else:
                self.visualizer.character_overlay = False

        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == self.keybinding["back"]:
                if not self.visualizer.card_help_overlay:
                    self.button_sound.sound.play()
                    self.done = True
                    self.next = "MENU"
                else:
                    self.visualizer.card_help_overlay = not self.visualizer.card_help_overlay

        elif event.type == self.background_music.track_end:
            self.play_next_track()

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if not self.visualizer.card_help_overlay:
                self.check_select_deselect_card()
            if self.visualizer.help_btn_image_rect.collidepoint(pg.mouse.get_pos()):
                if self.player.selected_card():
                    self.visualizer.card_help_overlay = not self.visualizer.card_help_overlay

    def update(self, now, keys):
        """Recalculate all needed information for render and game status"""
        # Get info from server first
        connection.Pump()
        self.Pump()
        self.discard_to_deck_reshuffle()
        self.visualizer.update_hand_position()
        self.visualizer.update_table_decks_pisition()
        self.visualizer.update_buffs_position()
        # deselect card if player used it somehow
        if not self.player.selected_card():
            card.Card.deselect_cards()
        if self.visualizer.card_help_overlay:
            self.visualizer.update_card_overlay()
        if self.visualizer.character_overlay:
            self.visualizer.update_character_overlay()
        if self.visualizer.role_overlay:
            self.visualizer.update_role_overlay()

            ###TEMPORARY###
        if not self.player.hand and self.deck:          # TEMPORARY
            self.player.hand = self.draw_cards(5) or self.draw_cards(len(self.deck))
        # if not self.enemy_player.hand and self.deck:    # TEMPORARY
            # self.enemy_player.hand = self.draw_cards(5) or self.draw_cards(len(self.deck))


    def render(self, screen):
        """Show everything needed on screen in particular order"""
        screen.blit(self.visualizer.bg, self.visualizer.bg_rect)
        self.visualizer.render_table_decks(screen)
        self.visualizer.render_gun(screen)
        self.visualizer.render_buffs(screen)
        self.visualizer.render_hand(screen)
        self.visualizer.render_role(screen)
        self.visualizer.render_character(screen)
        self.visualizer.render_health(screen)
        if self.visualizer.card_help_overlay:
            self.visualizer.render_card_overlay(screen)
        if self.visualizer.role_overlay:
            self.visualizer.render_role_overlay(screen)
        if self.visualizer.character_overlay:
            self.visualizer.render_character_overlay(screen)


class GameVisualizer(states.States):
    def __init__(self, screen_rect, player, deck, discard, button_functions):
        super().__init__()
        self.screen_rect = screen_rect
        self.scaling_factor = int(self.screen_rect.width / 400)
        self.player = player
        self.deck = deck
        self.discard = discard
        self.card_size = self.deck[0].rect.size
        self.card_help_overlay = False
        self.character_overlay = False
        self.role_overlay = False
        self.overlay_bg = pg.Surface((screen_rect.width, screen_rect.height))
        self.overlay_bg.fill(0)
        self.overlay_bg.set_alpha(200)
        self.overlay_rect = pg.Rect((self.screen_rect.centerx * 1.1, 
                                                    200, 
                                                    100 * self.scaling_factor,
                                                    100 * self.scaling_factor)
                                                   )
        self.hand_card_bufferX = self.card_size[0] / 2
        self.player.role_image = pg.transform.scale(self.player.role_image, (50 * self.scaling_factor,
                                                                       50 * self.scaling_factor)
        )
        self.player.role_image_rect = self.player.role_image.get_rect()
        self.player.character_image = pg.transform.scale(self.player.character_image, (60 * self.scaling_factor,
                                                                       60 * self.scaling_factor)
        )
        self.player.character_image_rect = self.player.character_image.get_rect()

        self.role_rect = pg.Rect((self.screen_rect.left + 50 * self.scaling_factor,
                           self.screen_rect.bottom - (self.card_size[1] / 2 * 1.05) - self.player.role_image_rect.height / 2),
                          (self.player.role_image_rect.width, self.player.role_image_rect.height)
        )
        self.character_rect = pg.Rect((self.screen_rect.left + 10 * self.scaling_factor,
                                self.screen_rect.bottom - (self.card_size[1] / 2 * 1.05) - self.player.character_image_rect.height / 2),
                                (self.player.character_image_rect.width, self.player.character_image_rect.height)
        )

        self.bullet = tools.Image.load("bullet.png")
        self.bullet = pg.transform.scale(self.bullet, (15 * self.scaling_factor, 15 * self.scaling_factor))
        self.bullet_rect = self.bullet.get_rect(topleft=(25, 0))

        backend_path = os.path.join(tools.Image.path, "cards/other/backend.png")
        thickness_path = os.path.join(tools.Image.path, "cards/other/deck_thickness.png")
        gun_placeholder_path = os.path.join(tools.Image.path, "cards/other/gun_placeholder.png")
        self.backend_card = card.Card(
            backend_path, pg.image.load(backend_path), self.screen_rect
        )
        self.deck_thickness_card = card.Card(
            thickness_path, pg.image.load(thickness_path), self.screen_rect
        )
        self.gun_placeholder_card = card.Card(
            gun_placeholder_path, pg.image.load(gun_placeholder_path), self.screen_rect
        )

        self.button_functions = button_functions

        self.play_deck_x = self.screen_rect.centerx - self.card_size[0]
        self.play_deck_y = self.screen_rect.centery - self.card_size[1] / 2
        self.hand_card_bufferY = 10 * self.scaling_factor
        self.bg = tools.Image.load("greenbg.png")
        self.bg_rect = self.bg.get_rect()
        self.help_btn_image = tools.Image.load("info.png")
        self.help_btn_image = pg.transform.scale(self.help_btn_image, (25 * self.scaling_factor,
                                                                       25 * self.scaling_factor)
        )
        self.help_btn_image_rect = self.help_btn_image.get_rect(topleft=(0, 0))

        self.settings = tools.Image.load("gear.png")
        self.settings = pg.transform.scale(self.settings, (25 * self.scaling_factor, 25 * self.scaling_factor))
        self.settings_rect = self.settings.get_rect()

        button_config = {
            "hover_color": (100, 255, 100),
            "clicked_color": (255, 255, 255),
            "clicked_font_color": (0, 0, 0),
            "hover_font_color": (0, 0, 0),
            "font": tools.Font.load("impact.ttf", 8 * self.scaling_factor),
            "font_color": (0, 0, 0),
            "call_on_release": False,
        }

        self.play_button_width =  40 * self.scaling_factor
        self.play_button_height = 15 * self.scaling_factor
        self.play_card_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.button_functions[0],
            text="Play Card",
            **button_config,
        )
        self.equip_gun_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.button_functions[1],
            text="Equip gun",
            **button_config,
        )
        self.equip_buff_button = button.Button(
            (0, 0, self.play_button_width, self.play_button_height),
            (100, 200, 100),
            self.button_functions[2],
            text="Equip buff",
            **button_config,
        )

    # RENDER
    def render_health(self, screen):
        """Show player health as bullet pictures above role image"""
        for i in range(self.player.health):
            screen.blit(self.bullet,
                    (8 * self.scaling_factor + self.screen_rect.left + self.scaling_factor * i * 18,
                     self.screen_rect.bottom - self.player.role_image_rect.height * 1.65)
        )

    def render_gun(self, screen):
        """Render gun placeholder and gun over it if present"""
        screen.blit(self.gun_placeholder_card.surf,
                    (self.screen_rect.width - self.card_size[0] - self.scaling_factor,
                     self.screen_rect.bottom - self.card_size[1] * 1.05)
        )
        if self.player.gun:
            screen.blit(self.player.gun.surf,
                        (self.screen_rect.width - self.card_size[0] - self.scaling_factor,
                         self.screen_rect.bottom - self.card_size[1] * 1.05)
            )

    def render_role(self, screen):
        """Show circled image of player's role shifted to the right under character image"""
        screen.blit(self.player.role_image,
                    (self.screen_rect.left + 50 * self.scaling_factor,
                     self.screen_rect.bottom - (self.card_size[1] / 2 * 1.05) - self.player.role_image_rect.height / 2)
        )

    def render_character(self, screen):
        """Show image of player's character shifted to the left on top of role image"""
        screen.blit(self.player.character_image,
                    (self.screen_rect.left + 10 * self.scaling_factor,
                     self.screen_rect.bottom - (self.card_size[1] / 2 * 1.05) - self.player.character_image_rect.height / 2)
        )

    def render_hand(self, screen):
        """Show hand cards one by one overlaying each other with step of half card size.
        Show play buttons on top of selected card if present."""
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
        """show little part of buff cards under player's hand"""
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

    def render_card_overlay(self, screen):
        screen.blit(self.overlay_bg, (0, 0))
        screen.blit(self.card_help_overlay_title, self.card_help_overlay_title_rect)
        screen.blit(self.card_help_overlay_text, self.card_help_overlay_text_rect)
        sel = self.player.selected_card()
        screen.blit(sel.surf, (self.screen_rect.centerx - self.card_size[0] * 1.1, 200))

    def render_role_overlay(self, screen):
        screen.blit(self.overlay_bg, (0, 0))
        screen.blit(self.role_overlay_title, self.role_overlay_title_rect)
        screen.blit(self.role_overlay_text, self.role_overlay_text_rect)
        image = pg.transform.scale(self.player.role_image, (100 * self.scaling_factor, 100 * self.scaling_factor))
        screen.blit(image, (self.screen_rect.centerx - image.get_rect().width * 1.1, 200))

    def render_character_overlay(self, screen):
        screen.blit(self.overlay_bg, (0, 0))
        screen.blit(self.character_overlay_title, self.character_overlay_title_rect)
        screen.blit(self.character_overlay_text, self.character_overlay_text_rect)
        image = pg.transform.scale(self.player.character_image, (100 * self.scaling_factor, 100 * self.scaling_factor))
        screen.blit(image, (self.screen_rect.centerx - image.get_rect().width * 1.1, 200))

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

    # UPDATE
    def update_card_overlay(self):
        filename = tools.get_filename(self.player.selected_card().path)
        self.card_help_overlay_title, self.card_help_overlay_title_rect = self.make_text(
            filename.title(),
            (255, 255, 255),
            (self.screen_rect.centerx, 100),
            60,
            fonttype="impact.ttf",
        )

        string = data.data[filename]["info"]
        my_font = tools.Font.load("impact.ttf", 20)
        self.card_help_overlay_text_rect = self.overlay_rect
        self.card_help_overlay_text = tools.render_textrect(
            string,
            my_font,
            self.card_help_overlay_text_rect,
            (216, 216, 216),
            (48, 48, 48, 255),
            0,
        )

    def update_role_overlay(self, role=None):
        if not role:
            role = self.player.role
        else:
            role = role
        self.role_overlay_title, self.role_overlay_title_rect = self.make_text(
            role.title(),
            (255, 255, 255),
            (self.screen_rect.centerx, 100),
            60,
            fonttype="impact.ttf",
        )

        string = data.roles[role]["info"]
        my_font = tools.Font.load("impact.ttf", 20)
        self.role_overlay_text_rect = self.overlay_rect
        self.role_overlay_text = tools.render_textrect(
            string,
            my_font,
            self.role_overlay_text_rect,
            (216, 216, 216),
            (48, 48, 48, 255),
            0,
        )

    def update_character_overlay(self, character=None):
        if not character:
            character = self.player.character
        else:
            character = character
        self.character_overlay_title, self.character_overlay_title_rect = self.make_text(
            character.replace("_", " ").title(),
            (255, 255, 255),
            (self.screen_rect.centerx, 100),
            60,
            fonttype="impact.ttf",
        )

        string = data.data[character]["info"]
        my_font = tools.Font.load("impact.ttf", 20)
        self.character_overlay_text_rect = self.overlay_rect
        self.character_overlay_text = tools.render_textrect(
            string,
            my_font,
            self.character_overlay_text_rect,
            (216, 216, 216),
            (48, 48, 48, 255),
            0,
        )

    def reposition_card_buttons(self):
        """Place buttons on top of the selected card"""
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

    def update_enemy_hand_position(self, player):
        hand_width = (len(self.player.hand) + 1)
        # TODO

    def update_buffs_position(self):
        buffs_width = (len(self.player.hand) + 1) * self.hand_card_bufferX
        buffs_x = self.screen_rect.centerx - buffs_width / 2
        for i, card in enumerate(self.player.buffs):
            card.rect.y = self.screen_rect.bottom - card.surf.get_height() * 1.25
            card.rect.x = buffs_x + i * self.hand_card_bufferX
