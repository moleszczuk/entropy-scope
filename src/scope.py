#!/usr/bin/python3

import sys
import click
from PIL import Image
from pathlib import Path

PIXELS_PER_BYTE = 10
DEFAULT_SATURATION = 0
DEFAULT_HUE = 0

def read_file(file_path):
    data=None
    with open(file_path, mode='rb') as f:
        data = f.read()
    return data

class EntropyImage:
    def __init__(self, bytes_per_row, rows_count, w=PIXELS_PER_BYTE, h=PIXELS_PER_BYTE):
        self.current_x = 0
        self.current_y = 0
        self.max_bytes_per_row = bytes_per_row
        self.max_rows_count = rows_count
        self.canvas = EntropyImage.new_image(bytes_per_row, rows_count)
        self.rect_width = PIXELS_PER_BYTE
        self.rect_height = PIXELS_PER_BYTE

    def byte_to_hue(byte):
        return int(100*float(byte)/255.)

    def new_image(bytes_per_row, rows_count):
        img_width = PIXELS_PER_BYTE * bytes_per_row
        img_height = PIXELS_PER_BYTE * rows_count
        img = Image.new('HSV', (img_width, img_height))
        return img

    # 0,0 at left-upper corner, counted in bytes (NOT PIXELS!)
    def add_rect(self, value, a, b):
        x = self.rect_width  * a 
        y = self.rect_height * b
        current_x = x
        current_y = y
        while current_x < (x+self.rect_width):
            while current_y < (y+self.rect_height):
                self.canvas.putpixel((current_x, current_y), (DEFAULT_HUE, DEFAULT_SATURATION, value))
                current_y += 1
            current_x += 1

    def add_byte(self, byte):
        value = byte
        if self.current_y == self.max_rows_count:
            return
        self.add_rect(EntropyImage.byte_to_hue(value), self.current_x, self.current_y)
        if self.current_x < self.max_bytes_per_row - 1:
            self.current_x += 1
        else:
            self.current_x = 0
            self.current_y += 1


    def get_raw_img(self):
        return self.canvas

def render_image(bytes2, offset=0, bytes_per_row=256, rows_count=-1):
    if rows_count < 1:
        rows_count = int(len(bytes2)/bytes_per_row)
    img = EntropyImage(bytes_per_row, rows_count)
    for b in bytes2:
        img.add_byte(b)
    return img.get_raw_img()

@click.command()
@click.argument('file')
def cli(file):
    data = read_file(Path(file))
    img = render_image(data)
    img.show()

if __name__ == '__main__':
    cli()

