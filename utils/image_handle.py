import base64
import io
import math
import os
from io import BytesIO

import cv2
import numpy as np
import requests
from PIL import Image

from app.utils.yunet import YuNet


class ImageHandle:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ImageHandle, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def _init(self):
        # get real path project
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.model = YuNet(modelPath=project_root + "/weights/face_detection_yunet_2023mar.onnx",
                           confThreshold=0.7,
                           )

    def convert_image(self, contents):
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image

    def decode_base64_to_image(self, base64_str):
        try:
            img_data = base64.b64decode(base64_str)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            return None

    def decode_url_to_image(self, url):
        try:
            img_data = requests.get(url).content
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            return None

    def compress_image_to_size(self, image, target_size, ):
        try:
            img_bytes = cv2.imencode('.jpg', image)[1].tobytes()
            # Open the image
            opened_image = Image.open(io.BytesIO(img_bytes))
            if opened_image.mode == "RGBA":
                opened_image = opened_image.convert("RGB")
        except Exception as e:
            raise ValueError("Cannot identify image file") from e

        original_size = len(img_bytes)
        ratio = math.sqrt(target_size * 1024 / original_size)  # Initial resize ratio

        while True:
            # Calculate the new dimensions
            new_size = (int(opened_image.width * ratio), int(opened_image.height * ratio))
            resized_image = opened_image.resize(new_size, Image.LANCZOS)

            # Save the resized image to a BytesIO stream
            output = io.BytesIO()
            resized_image.save(output, format="JPEG", quality=85)  # Adjust quality if needed
            resized_image_bytes = output.getvalue()

            # Convert the bytes to a base64 string
            base64_image = base64.b64encode(resized_image_bytes)

            # Check if the base64 string meets the size requirement
            if len(base64_image) <= target_size * 1024:  # target_size in bytes
                break

            # Adjust the ratio for further resizing
            ratio *= 0.9  # Reduce the ratio slightly for the next iteration

        return resized_image_bytes

    def convert_image_to_byte(self, image):
        img_encoded = self.compress_image_to_size(image, 100)
        if img_encoded is None:
            print("Error compress image")
            _, img_encoded = cv2.imencode('.jpg', image)
        # return BytesIO(img_encoded.tobytes())
        return img_encoded

    def check_face(self, image):
        inputSize = [128, 128]
        h, w, _ = image.shape
        if w > inputSize[0]:
            inputSize[1] = int(inputSize[0] * h / w)
            img = cv2.resize(image, (inputSize[0], inputSize[1]))
        else:
            img = image.copy()
            inputSize[0] = w
            inputSize[1] = h

        self.model.setInputSize(inputSize)
        results = self.model.infer(img)
        return self.visualize(inputSize, image, results)

    def save_face(self, image):
        inputSize = [128, 128]
        h, w, _ = image.shape
        if w > inputSize[0]:
            inputSize[1] = int(inputSize[0] * h / w)
            img = cv2.resize(image, (inputSize[0], inputSize[1]))
        else:
            img = image.copy()
            inputSize[0] = w
            inputSize[1] = h

        self.model.setInputSize(inputSize)
        results = self.model.infer(img)
        face = self.visualize_get_face(inputSize, image, results)
        if face is not None:
            return BytesIO(self.convert_image_to_byte(face))
        return None

    def visualize_get_face(self, inputSize, image, results):
        h, w, _ = image.shape
        temp_acreage = 0
        data_temp = None
        face_crop = None
        for det in results:
            bbox = det[0:4].astype(np.int32)
            bbox[0] = int(bbox[0] * w / inputSize[0])
            bbox[1] = int(bbox[1] * h / inputSize[1])
            bbox[2] = int(bbox[2] * w / inputSize[0])
            bbox[3] = int(bbox[3] * h / inputSize[1])
            x, y, bw, bh = bbox
            if bw * bh > temp_acreage:
                temp_acreage = bw * bh
                data_temp = bbox

        if data_temp is not None:
            x, y, bw, bh = data_temp
            x_pad = max(x - int(bw * 0.3), 0)
            y_pad = max(y - int(bh * 0.3), 0)
            w_pad = min(bw + int(bw * 0.6), w - x_pad)
            h_pad = min(bh + int(bh * 0.6), h - y_pad)
            face_crop = image[y_pad:y_pad + h_pad, x_pad:x_pad + w_pad]
        return face_crop

    def visualize(self, inputSize, image, results):
        h, w, _ = image.shape
        list_face = []
        for det in results:
            bbox = det[0:4].astype(np.int32)
            bbox[0] = int(bbox[0] * w / inputSize[0])
            bbox[1] = int(bbox[1] * h / inputSize[1])
            bbox[2] = int(bbox[2] * w / inputSize[0])
            bbox[3] = int(bbox[3] * h / inputSize[1])
            x, y, bw, bh = bbox
            x_pad = max(x - int(bw * 0.3), 0)
            y_pad = max(y - int(bh * 0.3), 0)
            w_pad = min(bw + int(bw * 0.6), w - x_pad)
            h_pad = min(bh + int(bh * 0.6), h - y_pad)
            face_crop = image[y_pad:y_pad + h_pad, x_pad:x_pad + w_pad]
            list_face.append(face_crop)

        return list_face
