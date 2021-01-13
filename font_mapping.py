import configparser
from logging import getLogger

from PIL import Image, ImageFont, ImageDraw
from fontTools.ttLib.ttFont import TTFont
from aip import AipOcr

logger = getLogger('spider')


class FontMapping:
    def __init__(self, font_file: str = None):
        config = configparser.ConfigParser()
        config.read('config.ini')

        # read config
        app_id = config.get('BaiduORC', 'AppID')
        api_key = config.get('BaiduORC', 'APIKey')
        secret_key = config.get('BaiduORC', 'SecretKey')

        # init baidu orc
        self.orc = AipOcr(app_id, api_key, secret_key)

        self.config = config

        if font_file:
            self.get_mapping(font_file)

    def _orc(self, path: str) -> str:
        f = open(path, 'rb')
        result = self.orc.basicGeneral(f.read())
        result = '\n'.join([k['words'] for k in result['words_result']])
        f.close()
        return result

    def get_mapping(self, font_file: str) -> dict:
        # open font file
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

        # print('font_name:', font_name)
        # print('font_size:', font_size)
        # print('font_offset:', font_offset)
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

        # print('text:', text.encode('unicode_escape').decode())
        # print('canvas_size', canvas_size)

        canvas = Image.new('RGB', canvas_size, (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        draw.text((0, 0), text, fill=0, font=font2)
        canvas.show()
        canvas.save('temp.jpeg', format='jpeg')

        result = self._orc('temp.jpeg')

        real_font_mapping = dict(zip(text.replace('\n', ''), result.replace('\n', '')))

        self.real_font_mapping = real_font_mapping
        return real_font_mapping

    def mapping(self, char: str) -> str:
        if not self.real_font_mapping:
            raise RuntimeError('没有调用get_mapping方法')
        else:
            trans = str.maketrans(self.real_font_mapping)
            return char.translate(trans)


def main():
    fm = FontMapping()
    mp = fm.get_mapping('fonts/2020-1-13.woff')
    text = '\ue03f'
    result = fm.mapping(text)
    print(result)


if __name__ == '__main__':
    exit(main())
