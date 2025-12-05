import base64
import io

from PIL import Image, ImageGrab
from ui_tars import action_parser

class Screen:
    def __init__(self):
        pass
    def screenshot_base64(self, resize_factor: float = None, format: str= "png", quality: int = 100):
        """
        获取截屏
        :param resize_factor: 缩放因子，默认为None就调用smart_resize来缩放好传输给qwen25vl
        :param format: 格式，可选png/jpeg
        :param quality: 图片质量，jpeg有效
        :return: [{"type": f"image/{format}", "content": base64_encoded}], origin_width, origin_height
        """
        image = ImageGrab.grab()
        # 缩放
        origin_width = image.size[0]
        origin_height = image.size[1]
        if resize_factor is None:
            new_height, new_width = action_parser.smart_resize(origin_height, origin_width)
            print("original size", image.size)
            print("resize to", (new_width, new_height))
        else:
            new_width = int(origin_width * resize_factor)
            new_height = int(origin_height * resize_factor)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        img_byte_arr= io.BytesIO()
        format = format.lower()
        if format == "png":
            image.save(img_byte_arr, format=format)
        elif format == "jpeg":
            image.save(img_byte_arr, format=format, quality=quality)
        else:
            raise ValueError("[Screen]Unsupported format: ", format)

        img_bytes = img_byte_arr.getvalue()
        base64_encoded = base64.b64encode(img_bytes).decode('utf-8')

        return {"type": f"image/{format}", "content": base64_encoded}, origin_width, origin_height

    def screenshhot_pil(self, resize_factor: float = 0.5):
        """
        获取截屏并返回PIL图像对象
        :param resize_factor: 缩放因子
        :return: PIL Image对象, origin_width, origin_height
        """
        image = ImageGrab.grab()
        # 缩放
        origin_width = image.size[0]
        origin_height = image.size[1]
        if resize_factor is None:
            new_height, new_width = action_parser.smart_resize(origin_height, origin_width)
            print("original size", image.size)
            print("resize to", (new_width, new_height))
        else:
            new_width = int(image.size[0] * resize_factor)
            new_height = int(image.size[1] * resize_factor)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return image, origin_width, origin_height

screen = Screen()
screen.screenshot_base64()
# print(screen.screenshot_base64())