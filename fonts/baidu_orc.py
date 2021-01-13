import configparser

from aip import AipOcr


class BaiduOrc:

    def __init__(self, app_id, api_key, secret_key):
        self.client = AipOcr(app_id, api_key, secret_key)

    def recognize(self, path) -> str:
        # options = {"language_type": "CHN_ENG",
        #            "detect_direction": "true",
        #            "detect_language": "true",
        #            "probability": "true"}
        f = open(path, mode='rb')
        result = self.client.basicGeneral(f.read())
        f.close()
        return result
