from io import BytesIO
from PIL import Image

from app.core.setting_env import settings


async def convert_BytesIO_to_webp(image_bytes, quality=settings.QUALITY_IMAGE, keep_transparency=False, lossless=False):
    """
    Convert an image from bytes to WEBP format with customizable options.
    - quality: Đặt chất lượng ảnh WEBP từ 0 đến 100 (giá trị cao hơn nghĩa là chất lượng tốt hơn, nhưng kích thước tệp lớn hơn).
    - keep_transparency: Quyết định có giữ độ trong suốt (alpha channel) hay không
    - lossless: Quyết định có sử dụng nén không mất dữ liệu hay không.
    Args:
        image_bytes (bytes): The input image data in bytes.
        quality (int): The quality of the WEBP image (0-100). Default is 80.
        keep_transparency (bool): Whether to keep transparency (alpha channel) if present. Default is True.
        lossless (bool): Whether to use lossless compression. Default is False.

    Returns:
        bytes: The converted image in WEBP format as bytes.
    """
    # Mở ảnh từ bytesIO
    with BytesIO(image_bytes) as input_bytes:
        image = Image.open(input_bytes)

        # Tạo đối tượng BytesIO để lưu ảnh WEBP
        output_bytes = BytesIO()

        # Xác định các tham số chuyển đổi
        save_kwargs = {
            'format': 'WEBP',
            'quality': quality,
            'lossless': lossless
        }

        # Nếu ảnh có kênh alpha và yêu cầu giữ độ trong suốt
        if 'A' in image.getbands() and keep_transparency:
            save_kwargs['transparency'] = 0  # Giữ độ trong suốt

        # Chuyển đổi ảnh sang định dạng WEBP và lưu vào output_bytes
        image.save(output_bytes, **save_kwargs)
    return output_bytes.getvalue()

