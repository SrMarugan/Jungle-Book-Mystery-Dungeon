from PIL import Image
from pathlib import Path
from generate_dungeon import generate

def char_to_color(c):
    color_map = {
        '.': (191, 119, 0),
        '#': (0, 0, 255),
        '0': (0, 0, 255),
        '<': (255, 0, 0),
        '>': (255, 255, 0)
    }
    
    return color_map.get(c, (0, 0, 255))

char_matrix = generate(8, 5, 8)

height = len(char_matrix)
width = len(char_matrix[0])

print(height, width)

pixel_size = 5
img = Image.new('RGB', (width * pixel_size, height * pixel_size))

pixels = img.load()

for i in range(height):
    for j in range(width):
        color = char_to_color(char_matrix[i][j])
        for y in range(pixel_size):
            for x in range(pixel_size):
                pixels[j * pixel_size + x, i * pixel_size + y] = color

img.save(Path(__file__).parent.joinpath(".data").joinpath("dungeon.png"))
