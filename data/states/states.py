import pygame as pg
from .. import tools


class States:
    """State parent class"""
    def __init__(self):
        self.bogus_rect = pg.Surface([0, 0]).get_rect()
        self.screen_rect = self.bogus_rect
        self.button_volume = 0.2
        self.button_hover_volume = 0.1
        self.cards_shuffle_volume = 0.2
        self.button_sound = tools.Sound("button.wav")
        self.button_sound.sound.set_volume(self.button_volume)
        self.button_hover = tools.Sound("button_hover.wav")
        self.button_hover.sound.set_volume(self.button_hover_volume)
        self.cards_shuffle = tools.Sound("cards_shuffle.wav")
        self.cards_shuffle.sound.set_volume(self.cards_shuffle_volume)
        self.background_music_volume = 0.2
        self.background_music = tools.Music(self.background_music_volume)
        self.bg_color = (25, 25, 25)
        self.timer = 0.0
        self.quit = False
        self.done = False
        self.rendered = None
        self.next_list = None
        self.last_option = None
        self.gametitle = "BangClone"
        self.menu_option_deselect = (130, 10, 10)
        self.menu_option_select = (235, 25, 25)
        self.title_color = (50, 50, 50)
        self.text_basic_color = (255, 255, 255)
        self.text_hover_color = (100, 100, 100)
        self.text_color = self.text_basic_color

        self.selected_index = 0

        self.action = None
        self.keybinding = {
            "up": [pg.K_UP, pg.K_w],
            "down": [pg.K_DOWN, pg.K_s],
            "right": [pg.K_RIGHT, pg.K_d],
            "left": [pg.K_LEFT, pg.K_a],
            "select": pg.K_RETURN,
            "pause": pg.K_p,
            "back": pg.K_ESCAPE,
        }

    def update_controller_dict(self, keyname, event):
        self.controller_dict[keyname] = event.key

    def mouse_hover_sound(self):
        for i, opt in enumerate(self.rendered["des"]):
            if opt[1].collidepoint(pg.mouse.get_pos()):
                if self.last_option != opt:
                    self.button_hover.sound.play()
                    self.last_option = opt

    def mouse_menu_click(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for i, opt in enumerate(self.rendered["des"]):
                if opt[1].collidepoint(pg.mouse.get_pos()):
                    self.selected_index = i
                    self.select_option(i)
                    break

    def make_text(self, message, color, center, size, fonttype="impact.ttf"):
        font = tools.Font.load(fonttype, size)
        text = font.render(message, True, color)
        rect = text.get_rect(center=center)
        return text, rect

    def pre_render_options(self, screen_width):
        """handle selected and deselected menu options render """
        font_deselect = tools.Font.load("impact.ttf", int(3.5 * screen_width / 100)) 
        font_selected = tools.Font.load("impact.ttf", int(4.5 * screen_width / 100))

        rendered_msg = {"des": [], "sel": []}
        for option in self.options:
            d_rend = font_deselect.render(option, 1, self.menu_option_deselect)
            d_rect = d_rend.get_rect()
            s_rend = font_selected.render(option, 1, self.menu_option_select)
            s_rect = s_rend.get_rect()
            rendered_msg["des"].append((d_rend, d_rect))
            rendered_msg["sel"].append((s_rend, s_rect))
        self.rendered = rendered_msg

    def select_option(self, i):
        """select menu option via keys or mouse"""
        if i == len(self.next_list):
            self.quit = True
        else:
            self.button_sound.sound.play()
            self.next = self.next_list[i]
            self.done = True
            self.selected_index = 0

    def change_selected_option(self, op=0):
        """change highlighted menu option"""
        for i, opt in enumerate(self.rendered["des"]):
            if opt[1].collidepoint(pg.mouse.get_pos()):
                self.selected_index = i

        if op:
            self.selected_index += op
            max_ind = len(self.rendered["des"]) - 1
            if self.selected_index < 0:
                self.selected_index = max_ind
            elif self.selected_index > max_ind:
                self.selected_index = 0
            self.button_hover.sound.play()

    def play_next_track(self):
        self.background_music.track = (self.background_music.track + 1) % len(
                self.background_music.tracks)
        pg.mixer.music.load(
                self.background_music.tracks[self.background_music.track])
        pg.mixer.music.play()