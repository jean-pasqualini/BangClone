import pygame as pg
from .. import tools
import random


class Menu(tools.States):
    def __init__(self, screen_rect):
        super().__init__()
        self.screen_rect = screen_rect
        self.options = ["Play", "View Cards", "Quit"]
        self.next_list = ["GAME", "CARDVIEW"]
        # self.title, self.title_rect = self.make_text(
        #     "Boom", self.title_color, (self.screen_rect.centerx, 75), 150
        # )
        self.title_logo = pg.image.load(
            "resources/graphics/bang_logo_bw.png"
        ).convert_alpha()
        self.pre_render_options(self.screen_rect.width)
        self.from_bottom = 200
        self.spacer = 100 * self.screen_rect.width / 1000

    def get_event(self, event, keys):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key in [pg.K_UP, pg.K_w]:
                self.change_selected_option(-1)
            elif event.key in [pg.K_DOWN, pg.K_s]:
                self.change_selected_option(1)
            elif event.key == pg.K_RETURN:
                self.select_option(self.selected_index)
        elif event.type == self.background_music.track_end:
            self.background_music.track = (self.background_music.track + 1) % len(
                self.background_music.tracks
            )
            pg.mixer.music.load(
                self.background_music.tracks[self.background_music.track]
            )
            pg.mixer.music.play()
        self.mouse_menu_click(event)

    def update(self, now, keys):
        pg.mouse.set_visible(True)
        self.mouse_hover_sound()
        self.change_selected_option()

    def render(self, screen):
        screen.fill(self.bg_color)
        # screen.blit(self.title,self.title_rect)
        screen.blit(
            self.title_logo,
            (
                int(self.screen_rect.center[0] - self.title_logo.get_rect().width / 2),
                int(
                    self.screen_rect.center[1]
                    - self.title_logo.get_rect().height / 2
                    - 50
                ),
            ),
        )

        for i, opt in enumerate(self.rendered["des"]):
            opt[1].center = (
                self.screen_rect.centerx,
                self.screen_rect.centery + (i * self.spacer) - self.spacer * len(self.rendered) / 2,
            )
            if i == self.selected_index:
                rend_img, rend_rect = self.rendered["sel"][i]
                rend_rect.center = opt[1].center
                screen.blit(rend_img, rend_rect)
            else:
                screen.blit(opt[0], opt[1])

    def cleanup(self):
        pass
        # pg.mixer.music.stop()
        # self.background_music.setup(self.background_music_volume)

    def entry(self):
        pass
