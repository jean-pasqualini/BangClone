import pygame as pg
from .. import tools


class Splash(tools.States):
    def __init__(self, screen_rect):
        super().__init__()
        self.text = ["Brought to you by", "metulburr & tarn"]
        self.screen_rect = screen_rect
        self.next = "MENU"
        self.timeout = 10
        self.start_time = 0
        self.cover = pg.Surface((screen_rect.width, screen_rect.height))
        self.cover.fill((255, 255, 255))
        self.cover_alpha = 256
        self.alpha_step = 3
        self.switch_frame = True

        # frame 1
        self.pygame_surf = pg.image.load(
            "resources/graphics/pygame_logo.png"
        ).convert_alpha()
        self.python_surf = pg.image.load(
            "resources/graphics/python_powered.png"
        ).convert_alpha()
        self.bang_surf = pg.image.load(
            "resources/graphics/bang_logo.png"
        ).convert_alpha()
        self.python_logo = pg.transform.scale(self.python_surf, (250, 214))
        self.pygame_logo = pg.transform.scale(self.pygame_surf, (250, 99))

        # responsive settings
        self.center_y = self.screen_rect.centery - len(self.text) * 25
        self.gap_x = 10
        self.gap_y = 10
        self.bottom = self.screen_rect.bottom
        self.python_logo_height = self.python_logo.get_rect().height
        self.pygame_logo_height = self.pygame_logo.get_rect().height
        self.right = self.screen_rect.right
        self.pygame_logo_width = self.pygame_logo.get_rect().width

        self.python_y = self.bottom - self.python_logo_height - self.gap_y
        self.python_x = self.gap_x

        # text
        text = ["Brought to you by",'metulburr & tarn']
        self.rendered_text = self.make_text_list("Fixedsys500c", 50, text, (0,0,0), self.center_y - len(text), 50)

        # horizontally align-center logos
        self.pygame_x = self.right - self.pygame_logo_width - self.gap_x
        self.pygame_y = self.bottom - (
            (self.python_logo_height - self.pygame_logo_height) / 2
            + self.pygame_logo_height
        )  

    def make_text_list(self, font, size, strings, color, start_y, y_space):
        rendered_text = []
        for i, string in enumerate(strings):
            msg = self.render_font(font, size, string, color)
            rect = msg.get_rect(
                center=(self.screen_rect.centerx, start_y + i * y_space)
            )
            rendered_text.append((msg, rect))
        return rendered_text

    def render_font(self, font, size, msg, color=(255, 255, 255)):
        selected_font = tools.Font.load("impact.ttf", size)
        return selected_font.render(msg, 1, color)

    def update(self, surface, keys):
        self.current_time = pg.time.get_ticks()
        self.cover.set_alpha(self.cover_alpha)
        self.cover_alpha = max(self.cover_alpha - self.alpha_step, 0)
        if self.current_time - self.start_time > 1000.0 * self.timeout:
            self.done = True

    def render(self, screen):
        if self.current_time - self.start_time < 1000.0 * self.timeout / 3:
            self.cover_alpha = 255
            screen.blit(self.cover, (0, 0))
            for msg in self.rendered_text:
                screen.blit(*msg)
        else:
            screen.blit(self.python_logo, (self.python_x, self.python_y))
            screen.blit(self.pygame_logo, (self.pygame_x, self.pygame_y))
            screen.blit(
                self.bang_surf,
                (
                    int(self.screen_rect.center[0] - self.bang_surf.get_rect().width / 2),
                    int(
                        self.screen_rect.center[1]
                        - self.bang_surf.get_rect().height / 2
                        - 50
                    ),
                ),
            )

            screen.blit(self.cover, (0, 0))


    def get_event(self, event, keys):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            self.done = True

    def cleanup(self):
        pass
