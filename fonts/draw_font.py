from aip import AipOcr
from fontTools.ttLib import TTFont
from PIL import Image, ImageFont, ImageDraw
from PIL.ImageColor import colormap as color


def main():
    filename = '2020-1-12.woff'
    # font1 = TTFont(filename)
    # x_min = font1['head'].xMin
    # y_min = font1['head'].yMin
    # x_max = font1['head'].xMax
    # y_max = font1['head'].yMax
    # font_size = x_max - x_min, y_max - y_min

    font = ImageFont.truetype(filename, 40)
    print(font.getsize('\uF8F5'))
    print(font.getoffset('\uF8F5'))

    canvas = Image.new('RGB', font.getsize('\uF8F5'), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    # draw.line((0, 0) + canvas.size, fill=color['red'], width=1)
    draw.text((0, 0), u'\uF8F5\uF8F5\uF8F5\n\uF8F5\uF8F5\uF8F5', fill=0, font=font)
    # draw.arc((10, 10, 50, 50), 0, 270, fill=0)
    canvas.show()

    # recognize
    # APP_ID = '23531711'
    # API_KEY = 'QBTpbZYLLAmz72SneRkzLQjP'
    # SECRET_KEY = 'nEpMa9sonbmDV2KEOTo1SQzUBxLAbSBi'
    #
    # client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # canvas.save('temp.jpeg', format='jpeg')
    # result = client.basicGeneral(open('temp.jpeg', 'rb').read())
    # print(result)


if __name__ == '__main__':
    exit(main())
