import string

from PIL import Image, ImageDraw

printable = set(string.printable)

GRAY = '#6B696A'
NORMAL_HEIGHT = 1000
TINY_HEIGHT = 800


def remove_white_edge(image):
    """
    移除图片白边
    :param image: 图片对象
    :return: 移除白边后的图片对象
    """
    # 获取像素信息
    pixels = image.load()

    # 获取图像大小
    width, height = image.size

    # 计算最小的 X、Y、最大的 X、Y 坐标
    min_x, min_y = width - 1, height - 1
    max_x, max_y = 0, 0
    for y in range(height):
        for x in range(width):
            if pixels[x, y] != (255, 255, 255):
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    # 计算新的图像大小
    new_width = max_x - min_x + 1
    new_height = max_y - min_y + 1

    # 裁剪图像
    new_image = image.crop((min_x, min_y, max_x + 1, max_y + 1))
    return new_image


def concatenate_image(images, align='left'):
    """
    将多张图片拼接成一列
    :param images: 图片对象列表
    :param align: 对齐方向，left/center/right
    :return: 拼接后的图片对象
    """
    widths, heights = zip(*(i.size for i in images))

    sum_height = sum(heights)
    max_width = max(widths)

    new_img = Image.new('RGB', (max_width, sum_height), color='white')

    x_offset = 0
    y_offset = 0
    if 'left' == align:
        for img in images:
            new_img.paste(img, (0, y_offset))
            y_offset += img.height
    elif 'center' == align:
        for img in images:
            x_offset = int((max_width - img.width) / 2)
            new_img.paste(img, (x_offset, y_offset))
            y_offset += img.height
    elif 'right' == align:
        for img in images:
            x_offset = max_width - img.width  # 右对齐
            new_img.paste(img, (x_offset, y_offset))
            y_offset += img.height
    return new_img


def padding_image(image, padding_size, padding_location='tb'):
    """
    在图片四周填充白色像素
    :param image: 图片对象
    :param padding_size: 填充像素大小
    :param padding_location: 填充位置，top/bottom/left/right
    :return: 填充白色像素后的图片对象
    """
    if image is None:
        return None

    total_width, total_height = image.size
    x_offset, y_offset = 0, 0
    if 't' in padding_location:
        total_height += padding_size
        y_offset += padding_size
    if 'b' in padding_location:
        total_height += padding_size
    if 'l' in padding_location:
        total_width += padding_size
        x_offset += padding_size
    if 'r' in padding_location:
        total_width += padding_size

    padding_img = Image.new('RGB', (total_width, total_height), color='white')
    padding_img.paste(image, (x_offset, y_offset))
    return padding_img


def square_image(image):
    """
    将图片按照正方形进行填充
    :param image: 图片对象
    :return: 填充后的图片对象
    """
    # 计算图片的宽度和高度
    width, height = image.size

    # 计算需要填充的白色区域大小
    delta_w = abs(width - height)
    padding = (delta_w // 2, 0) if width < height else (0, delta_w // 2)

    # 创建新的正方形画布
    square_size = max(width, height)
    square_img = Image.new('RGB', (square_size, square_size), color='white')

    # 将输入的图片粘贴到正方形画布的中心位置
    square_img.paste(image, padding)

    # 返回正方形图片对象
    return square_img


def resize_image_with_height(image, height):
    """
    按照高度对图片进行缩放
    :param image: 图片对象
    :param height: 指定高度
    :return: 按照高度缩放后的图片对象
    """
    # 获取原始图片的宽度和高度
    width, old_height = image.size

    # 计算缩放后的宽度
    scale = height / old_height
    new_width = round(width * scale)

    # 进行等比缩放
    resized_image = image.resize((new_width, height), Image.ANTIALIAS)

    # 返回缩放后的图片对象
    return resized_image


def resize_image_with_width(image, width):
    """
    按照宽度对图片进行缩放
    :param image: 图片对象
    :param width: 指定宽度
    :return: 按照宽度缩放后的图片对象
    """
    # 获取原始图片的宽度和高度
    old_width, height = image.size

    # 计算缩放后的宽度
    scale = width / old_width
    new_height = round(height * scale)

    # 进行等比缩放
    resized_image = image.resize((width, new_height), Image.ANTIALIAS)

    # 返回缩放后的图片对象
    return resized_image


def append_image_by_side(background, images, side='left', padding=200, is_start=False):
    """
    将图片横向拼接到背景图片中
    :param background: 背景图片对象
    :param images: 图片对象列表
    :param side: 拼接方向，left/right
    :param padding: 图片之间的间距
    :param is_start: 是否在最左侧添加 padding
    :return: 拼接后的图片对象
    """
    if 'right' == side:
        if is_start:
            x_offset = background.width - padding
        else:
            x_offset = background.width
        images.reverse()
        for i in images:
            if i is None:
                continue
            i = resize_image_with_height(i, background.height)
            x_offset -= i.width
            x_offset -= padding
            background.paste(i, (x_offset, 0))
    else:
        if is_start:
            x_offset = padding
        else:
            x_offset = 0
        for i in images:
            if i is None:
                continue
            i = resize_image_with_height(i, background.height)
            background.paste(i, (x_offset, 0))
            x_offset += i.width
            x_offset += padding


class ImageProcessor(object):
    """
    水印边框
    """

    def __init__(self, font, bold_font):
        self.font = font
        self.bold_font = bold_font

    def text_to_image(self, content, is_bold=False, fill='black'):
        """
        将文字内容转换为图片
        :param content:
        :param is_bold:
        :param fill:
        :return:
        """
        if content == '':
            content = '   '
        font = self.bold_font if is_bold else self.font
        text_width, text_height = font.getsize(content)
        image = Image.new('RGB', (text_width, text_height), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), content, fill=fill, font=font)
        return image

    def normal_watermark(self, container, config, is_logo_left=True):
        """
        生成一个默认布局的水印图片
        :param container: 图片对象
        :param config: 水印配置
        :param is_logo_left: logo 位置
        :return: 添加水印后的图片对象
        """
        ratio = .1 if container.ratio >= 1 else .13
        padding_ratio = .618

        watermark = Image.new('RGB', (int(NORMAL_HEIGHT / ratio), NORMAL_HEIGHT), color='white')
        empty_padding = Image.new('RGB', (10, 50), color='white')

        # 填充左边的文字内容
        left_top = self.text_to_image(container.get_attribute_str(config.left_top), is_bold=config.left_top.is_bold)
        left_bottom = self.text_to_image(container.get_attribute_str(config.left_bottom),
                                         is_bold=config.left_bottom.is_bold, fill=GRAY)
        left = concatenate_image([left_top, empty_padding, left_bottom])
        # 填充右边的文字内容
        right_top = self.text_to_image(container.get_attribute_str(config.right_top), is_bold=config.right_top.is_bold)
        right_bottom = self.text_to_image(container.get_attribute_str(config.right_bottom),
                                          is_bold=config.right_bottom.is_bold, fill=GRAY)
        right = concatenate_image([right_top, empty_padding, right_bottom])

        max_height = max(left.height, right.height)
        left = padding_image(left, int(max_height * padding_ratio), 'tb')
        right = padding_image(right, int(max_height * padding_ratio), 't')
        right = padding_image(right, left.height - right.height, 'b')

        logo = container.get_logo()
        if is_logo_left:
            # 如果 logo 在左边
            append_image_by_side(watermark, [logo, left], is_start=logo is None)
            append_image_by_side(watermark, [right], side='right')
        else:
            # 如果 logo 在右边
            if logo is not None:
                # 如果 logo 不为空，等比例缩小 logo
                logo = padding_image(logo, int(padding_ratio * logo.height))
            # 插入一根线条用于分割 logo 和文字
            line = Image.new('RGB', (20, 1000), color=GRAY)
            line = padding_image(line, int(padding_ratio * line.height * .8))
            append_image_by_side(watermark, [left], is_start=True)
            append_image_by_side(watermark, [logo, line, right], side='right')

        watermark = resize_image_with_width(watermark, container.width)
        image = Image.new('RGB', (container.width, container.height + watermark.height), color='white')
        image.paste(container.img)
        image.paste(watermark, (0, container.height))
        return image

    def square_watermark(self, container):
        """
        生成一个1：1布局的水印图片
        :param container: 图片对象
        :return: 填充白边后的图片对象
        """
        return square_image(container.img)
