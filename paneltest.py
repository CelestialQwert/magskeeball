from PIL import Image
from PIL import ImageDraw
import pygame
from rgbmatrix import RGBMatrix, RGBMatrixOptions

options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 6
options.parallel = 1
options.hardware_mapping = "adafruit-hat-pwm"
options.brightness = 50
options.gpio_slowdown = 1
options.show_refresh_rate = 2
options.drop_privileges = True

matrix = RGBMatrix(options = options)

image = Image.new("RGB", (192, 32))
draw = ImageDraw.Draw(image)

draw.rectangle((10, 10, 30, 30), fill=(0, 0, 255), outline=(0, 0, 255))
draw.line((0, 0, 191, 31), fill=(255, 0, 0))
draw.line((0, 31, 191, 0), fill=(0, 255, 0))

matrix.SetImage(image, 0, 0)

input('press enter to init pygame')
pygame.init()
input('press enter to end')
