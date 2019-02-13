import pygame as pg
from .. import tools, data
from ..GUI import button
import os
from ..card import Card  # States.set_cards()
from . import states


class Viewer(states.States):
    def __init__(self, screen_rect):
        super().__init__()
        self.screen_rect = screen_rect
        self.scaling_factor = int(self.screen_rect.width / 400)
        self.options = ["Back"]
        self.next_list = ["MENU"]
        self.title, self.title_rect = self.make_text(
            "Card Viewer", self.title_color, (self.screen_rect.centerx, 75), 150
        )
        self.pre_render_options(self.screen_rect.width)
        self.from_bottom = 550
        self.spacer = 75
        self.create_deck()
        self.card_size = self.cards[0].rect.size
        self.update_image(0)
        self.database = data.data

        button_config = {
            "hover_color": (150, 150, 150),
            "clicked_color": (255, 255, 255),
            "clicked_font_color": (0, 0, 0),
            "hover_font_color": (0, 0, 0),
            "font": tools.Font.load("impact.ttf", 12),
        }
        self.play_button_width =  40 * self.scaling_factor
        self.play_button_height = 15 * self.scaling_factor
        self.next_button = button.Button(
            (self.screen_rect.left + 50 * self.scaling_factor, 
             self.screen_rect.centery + 50 * self.scaling_factor, 
             self.play_button_width, 
             self.play_button_height
            ),
            (100, 100, 100),
            lambda x=1: self.switch_card(x),
            text="Next",
            **button_config
        )
        self.prev_button = button.Button(
            (self.screen_rect.right - 50 * self.scaling_factor - self.play_button_width, 
             self.screen_rect.centery + 50 * self.scaling_factor,
             self.play_button_width, 
             self.play_button_height
            ),
            (100, 100, 100),
            lambda x=-1: self.switch_card(x),
            text="Previous",
            **button_config
        )

    def create_deck(self):
        """Dill deck with all cards, except 'other' category"""
        self.cards = []
        path = os.path.join(tools.Image.path, "cards")
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".png"):
                    path = os.path.abspath(os.path.join(root, f))
                    image = pg.image.load(path)
                    card = Card(path)
                    if tools.get_category(card.path) != "other":
                        self.cards.append(card)

    def callback_test(self):
        print("callback")

    def update_category(self, text):
        self.category, self.category_rect = self.make_text(
            text,
            (255, 255, 255),
            (self.screen_rect.centerx, 162),
            15,
            fonttype="impact.ttf",
        )

    def update_image(self, val):
        self.image = self.cards[val].surf
        self.image_rect = self.image.get_rect(
            centerx=self.screen_rect.centerx - self.card_size[0] / 2,
            centery=self.screen_rect.centery + 50,
        )
        self.path = self.cards[val].path
        category = tools.get_category(self.path)
        self.update_category(category.title())

    def switch_card(self, num):
        for i, obj in enumerate(self.cards):
            if obj.surf == self.image:
                ind = i
        ind += num
        if ind < 0:
            ind = len(self.cards) - 1
        elif ind > len(self.cards) - 1:
            ind = 0

        self.update_image(ind)
        self.button_sound.sound.play()

    def get_event(self, event, keys):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key in self.keybinding["left"]:
                self.switch_card(-1)
            elif event.key in self.keybinding["right"]:
                self.switch_card(1)
            elif event.key in self.keybinding["up"]:
                self.change_selected_option(-1)
            elif event.key in self.keybinding["down"]:
                self.change_selected_option(1)
            elif event.key == self.keybinding["select"]:
                self.select_option(self.selected_index)
            elif event.key == self.keybinding["back"]:
                self.button_sound.sound.play()
                self.done = True
                self.next = "MENU"
        elif event.type == self.background_music.track_end:
            self.play_next_track()
        self.mouse_menu_click(event)
        self.next_button.check_event(event)
        self.prev_button.check_event(event)

    def update(self, now, keys):
        pg.mouse.set_visible(True)
        self.mouse_hover_sound()
        self.change_selected_option()

        filename = tools.get_filename(self.path)
        self.help_overlay_title, self.help_overlay_title_rect = self.make_text(
            filename.title(),
            (255, 255, 255),
            (self.screen_rect.centerx, 100),
            60 * self.scaling_factor,
            fonttype="impact.ttf",
        )

        string = self.database[filename]["info"]
        my_font = tools.Font.load("impact.ttf", 8 * self.scaling_factor)
        self.help_overlay_text_rect = pg.Rect((self.screen_rect.centerx + self.screen_rect.width / 16, 
                                               self.screen_rect.centery - self.card_size[1] / 2 + 50, 
                                               150 * self.scaling_factor, 
                                               200 * self.scaling_factor
                                               )
                                             )
        self.help_overlay_text = tools.render_textrect(
            string,
            my_font,
            self.help_overlay_text_rect,
            (216, 216, 216),
            self.bg_color,
            0,
        )

    def render(self, screen):
        screen.fill(self.bg_color)
        screen.blit(self.title, self.title_rect)
        screen.blit(self.category, self.category_rect)
        screen.blit(self.image, self.image_rect)
        # screen.blit(self.help_overlay_title, self.help_overlay_title_rect)
        screen.blit(self.help_overlay_text, self.help_overlay_text_rect)
        for i, opt in enumerate(self.rendered["des"]):
            opt[1].center = (
                self.screen_rect.centerx,
                self.screen_rect.height - self.scaling_factor * 20 + i * self.spacer,
            )
            if i == self.selected_index:
                rend_img, rend_rect = self.rendered["sel"][i]
                rend_rect.center = opt[1].center
                screen.blit(rend_img, rend_rect)
            else:
                screen.blit(opt[0], opt[1])
        self.next_button.render(screen)
        self.prev_button.render(screen)

    def cleanup(self):
        pg.display.set_caption("Boom")

    def entry(self):
        pass
