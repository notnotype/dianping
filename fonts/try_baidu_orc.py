import configparser
from json import dumps

from fontTools.ttLib import TTFont
from PIL import Image, ImageFont, ImageDraw
from fontTools.ttLib.ttFont import TTFont
from aip import AipOcr


def main():
    config = configparser.ConfigParser()
    config.read('../config.ini')

    # read config
    app_id = config.get('BaiduORC', 'AppID')
    api_key = config.get('BaiduORC', 'APIKey')
    secret_key = config.get('BaiduORC', 'SecretKey')

    # init baidu orc
    orc = AipOcr(app_id, api_key, secret_key)

    # open font file
    font_file = '2020-1-13.woff'
    font = TTFont(font_file)
    font2 = ImageFont.truetype(font_file, 20)

    # draw font
    cmap: dict = font.getBestCmap()
    del cmap[120]

    real_font_mapping = {}
    x_counts = 20
    y_counts = 20

    # get font info
    font_name = chr(list(cmap.keys())[0])
    font_size = list(font2.getsize(font_name))
    font_offset = list(font2.getoffset(font_name))

    font_size[0] += font_offset[0]
    font_size[1] += font_offset[1]

    print('font_name:', font_name)
    print('font_size:', font_size)
    print('font_offset:', font_offset)
    cmap_batch = list(cmap.items())[:x_counts * y_counts]
    canvas_size = font_size[0] * x_counts, font_size[1] * y_counts

    # drawing
    text = ''
    for index, each in enumerate(cmap_batch):
        char = chr(each[0])
        text += char
        if (index + 1) % x_counts == 0:
            text += '\n'

    text = text.strip()

    print('text:', text.encode('unicode_escape').decode())
    print('canvas_size', canvas_size)

    canvas = Image.new('RGB', canvas_size, (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((0, 0), text, fill=0, font=font2)
    canvas.show()
    canvas.save('temp.jpeg', format='jpeg')

    f = open('temp.jpeg', 'rb')
    result = orc.basicGeneral(f.read())
    result = '\n'.join([k['words'] for k in result['words_result']])
    f.close()
    print('result', dumps(result, indent=4, ensure_ascii=False))

    # a = text.split('\n')
    # b = result.split('\n')
    #
    # print(a)
    # print(b)

    real_font_mapping = dict(zip(text.replace('\n', ''), result.replace('\n', '')))

    real_font_mapping = dumps(real_font_mapping, indent=4, ensure_ascii=False)
    print(real_font_mapping)
    print(len(real_font_mapping))
    print(len(text))


if __name__ == '__main__':
    exit(main())
