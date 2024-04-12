# from .common import *
from PIL import Image, ImageFont, ImageDraw
import sys
import pygame
import platform
import time

from . import resources as res

REAL = 0
EMULATED = 1
BOTH = 2

pygame.init()


class Panel:

    def __init__(self, scale=6):

        if platform.system() != "Windows":
            self.init_real_panel()
            self.buffer_canvas = Image.new("RGBA", (192, 32))
            self.real_panel = True
            self.emulated_panel = False
            print("Hello LED panel!")
        else:
            self.init_emulated_panel(scale)
            self.real_panel = False
            self.emulated_panel = True
            print("Hello emulated panel!")

        self.canvas = Image.new("RGBA", (96, 64))
        self.draw = ImageDraw.Draw(self.canvas)
        self.paste = self.canvas.paste

    def init_real_panel(self):
        from rgbmatrix import RGBMatrix, RGBMatrixOptions

        self.options = RGBMatrixOptions()
        self.options.rows = 32
        self.options.chain_length = 6
        self.options.parallel = 1
        self.options.brightness = 50
        # self.options.show_refresh_rate = 1
        self.options.pwm_bits = 11
        self.gpio_slowdown = 2
        self.options.pwm_lsb_nanoseconds = 130
        # self.options.disable_hardware_pulsing = True
        self.options.hardware_mapping = "adafruit-hat-pwm"
        self.no_drop_privs = True
        self.matrix = RGBMatrix(options=self.options)
        # print('real panel loaded, waiting 5 seconds to drop root...')
        # time.sleep(5)

    def init_emulated_panel(self, scale):
        self.e_size = tuple([x * scale for x in (96, 64)])
        self.emu_panel = pygame.display.set_mode(self.e_size)
        pygame.display.set_caption("MAGskeeball (virtual score panel)")

    def update(self):
        if self.real_panel:
            top = self.canvas.crop((0, 0, 96, 32))
            bottom = self.canvas.crop((0, 32, 96, 64))
            self.buffer_canvas.paste(top, (0, 0))
            self.buffer_canvas.paste(bottom, (96, 0))
            self.matrix.SetImage(self.buffer_canvas.convert("RGB"))
        if self.emulated_panel:
            data = self.canvas.resize(self.e_size, Image.NEAREST).tobytes()
            mode = self.canvas.mode
            pyg_canvas = pygame.image.fromstring(data, self.e_size, mode)
            self.emu_panel.fill((0, 0, 0))
            self.emu_panel.blit(pyg_canvas, (0, 0))
            pygame.display.update()

    def paste(self, image, coords):
        self.canvas.paste(image, coords)

    def clear(self):
        self.draw.rectangle((0, 0, 96, 64), fill=(0, 0, 0))

    def fill(self, color):
        self.draw.rectangle((0, 0, 96, 64), fill=color)

    def draw_text(self, pos, text, font, color):
        if isinstance(color, str):
            colour_tuple = res.COLORS[color]
        else:
            colour_tuple = color
        self.draw.text(pos, str(text), font=res.FONTS[font], fill=colour_tuple)

    def draw_time(self, pos=(7, 6), display_time=0, color="WHITE"):
        posx, posy = pos
        minutes = display_time // (60 * res.FPS)
        seconds = (display_time // res.FPS) % 60
        fraction = round(100.0 / res.FPS * (display_time % res.FPS))
        fill_col = res.COLORS[color]

        self.draw_text((posx, posy), f"{minutes:01d}", "Digital14", color)
        self.draw_text((21 + posx, posy), f"{seconds:02d}", "Digital14", color)
        self.draw_text((56 + posx, posy), f"{fraction:02d}", "Digital14", color)
        self.draw.rectangle([14 + posx, 12 + posy, 17 + posx, 15 + posy], fill=fill_col)
        self.draw.rectangle([14 + posx, 3 + posy, 17 + posx, 6 + posy], fill=fill_col)
        self.draw.rectangle([49 + posx, 15 + posy, 52 + posx, 18 + posy], fill=fill_col)
