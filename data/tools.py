import pygame as pg
import os
import shutil
import random


def clean_files():
    """remove all pyc files and __pycache__ direcetories in subdirectory"""
    for root, dirs, files in os.walk("."):
        for dir in dirs:
            if dir == "__pycache__":
                path = os.path.join(root, dir)
                print("removing {}".format(os.path.abspath(path)))
                shutil.rmtree(path)
        for name in files:
            if name.endswith(".pyc"):
                path = os.path.join(root, name)
                print("removing {}".format(os.path.abspath(path)))
                os.remove(path)


def get_category(path):
    """get category from image fullpath of card"""
    return os.path.split(os.path.split(path)[0])[1]


def get_filename(path):
    """get filename from image fullpath of card"""
    return os.path.split(os.path.splitext(path)[0])[1]

class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


def render_textrect(string, font, rect, text_color, background_color, justification=0):
    """Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Takes the following arguments:

    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rectstyle giving the size of the surface requested.
    text_color - a three-byte tuple of the rgb value of the
                 text color. ex (0, 0, 0) = BLACK
    background_color - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

    Returns the following values:

    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(" ")
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException(
                        "The word " + word + " is too long to fit in the rect passed."
                    )
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pg.Surface(rect.size).convert()
    # surface.fill(0)
    # surface.set_alpha(0)
    surface.fill(background_color)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException(
                "Once word-wrapped, the text string was too tall to fit in the rect."
            )
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(
                    tempsurface,
                    ((rect.width - tempsurface.get_width()) / 2, accumulated_height),
                )
            elif justification == 2:
                surface.blit(
                    tempsurface,
                    (rect.width - tempsurface.get_width(), accumulated_height),
                )
            else:
                raise TextRectException(
                    "Invalid justification argument: " + str(justification)
                )
        accumulated_height += font.size(line)[1]

    return surface


class Image:
    path = "resources/graphics"

    @staticmethod
    def load(filename):
        p = os.path.join(Image.path, filename)
        return pg.image.load(os.path.abspath(p))


class Font:
    path = "resources/fonts"

    @staticmethod
    def load(filename, size):
        p = os.path.join(Font.path, filename)
        return pg.font.Font(os.path.abspath(p), size)


class Sound:
    def __init__(self, filename):
        self.path = os.path.join("resources", "sound")
        self.fullpath = os.path.join(self.path, filename)
        pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=128)
        self.sound = pg.mixer.Sound(self.fullpath)


class Music:
    def __init__(self, volume):
        self.path = os.path.join("resources", "music")
        self.setup(volume)

    def setup(self, volume):
        self.track_end = pg.USEREVENT + 1
        self.tracks = []
        self.track = 0
        for track in os.listdir(self.path):
            self.tracks.append(os.path.join(self.path, track))
        random.shuffle(self.tracks)
        pg.mixer.music.set_volume(volume)
        pg.mixer.music.set_endevent(self.track_end)
        pg.mixer.music.load(self.tracks[0])
