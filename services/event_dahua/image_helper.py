import io
import cv2
import numpy as np
from PIL import Image
# def crop_top_image(image, crop_height=65):
#     return image[crop_height:, :]
# def crop_image_motor_from_bytes(image, output_format='.WEBP'):
#     data_img = io.BytesIO(image)
#     np_arr = np.frombuffer(data_img.read(), np.uint8)
#     image_cv = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)
#     cropped_image = crop_top_image(image_cv)
#     _, buffer = cv2.imencode(output_format, cropped_image)
#     return buffer
def remap_coordinates(coords, max_original, image_width, image_height):
    remapped_coords = []
    for x, y in coords:
        x_remapped = int((x / max_original) * image_width)
        y_remapped = int((y / max_original) * image_height)
        remapped_coords.append((x_remapped, y_remapped))
    return remapped_coords


def crop_image(actual_content, bbox: list):
    if bbox == [0, 0, 0, 0]:
        return False
    image = Image.open(io.BytesIO(actual_content))
    width, height = image.size
    left_top_remap = (int(bbox[0]) / 8192, int(bbox[1]) / 8192)
    right_bottom_remap = (int(bbox[2]) / 8192, int(bbox[3]) / 8192)
    left_top_remap = (
        int(left_top_remap[0] * width),
        int(left_top_remap[1] * height),
    )
    right_bottom_remap = (
        int(right_bottom_remap[0] * width),
        int(right_bottom_remap[1] * height),
    )
    crop_rectangle = (
            left_top_remap[0],
            left_top_remap[1],
            right_bottom_remap[0] ,
            right_bottom_remap[1] ,
        )
    # Perform the crop
    cropped_image = image.crop(crop_rectangle)

    # Convert the cropped image to bytes
    img_byte_arr = io.BytesIO()
    cropped_image.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr

def crop_image_original(actual_content, bbox: list):
    if bbox == [0, 0, 0, 0]:
        return False
    image = Image.open(io.BytesIO(actual_content))
    original_bbox=int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
    cropped_image = image.crop(original_bbox)
    img_byte_arr = io.BytesIO()
    cropped_image.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr
