import pygame as pg
import pickle


class Card:
    """Represent any card using image, suit and dignity of it.
    If Class initialisated with screen rect passed - card will be scaled to it.
    Store all objects in class list variable
    """
    objects = []
    def __init__(self, path, screen_rect=None):
        self.path = path
        self.screen_rect = screen_rect
        self.surf = self.image_from_path(path)
        self.rect = self.surf.get_rect()
        self.selected = False
        self.suit = None
        self.dignity = None
        Card.objects.append(self)

    def image_from_path(self, path):
        """Create image from path, 
        scale it to screen if object created with screen_rect passed
        """
        image = pg.image.load(path)
        if self.screen_rect:
            image_rect = image.get_rect()
            card_aspect_ratio = image_rect.width / image_rect.height
            scale_factor = 4
            card_size_scaled = (int((self.screen_rect.height / scale_factor) * card_aspect_ratio),
                                int(self.screen_rect.height / scale_factor),
            )

            return pg.transform.scale(image, card_size_scaled)
        else:
            return image

    @classmethod
    def deselect_cards(cls):
        for card in cls.objects:
            card.selected = False
