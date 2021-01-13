from fontTools.ttLib.ttFont import TTFont


def main():
    filename = '2020-1-12'
    font = TTFont(filename + '.woff')
    font.saveXML(filename + '.xml')
    # font.close()
    # font = TTFont()
    # font.importXML('20201-11.xml')


if __name__ == '__main__':
    exit(main())
