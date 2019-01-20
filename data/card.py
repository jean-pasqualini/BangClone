import pygame as pg


class Card:
    """Represent any card using image, suit and dignity of it.
    If Class initialisated with screen rect passed - card will be scaled to it"""
    def __init__(self, path, image, screen_rect=None):
        if screen_rect:
            image_rect = image.get_rect()
            card_aspect_ratio = image_rect.width / image_rect.height
            scale_factor = 3.3
            card_size_scaled = (int((screen_rect.height / scale_factor) * card_aspect_ratio),
                                int(screen_rect.height / scale_factor),
            )

            self.surf = pg.transform.scale(image, card_size_scaled)
        else:
            self.surf = image
        self.path = path
        self.rect = self.surf.get_rect()
        self.selected = False
        self.suit = None
        self.dignity = None
