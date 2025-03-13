from io import BytesIO

from miniopy_async import Minio

from app.core.setting_env import settings


class MinioServices:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(MinioServices, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def _init(self):
        self.minio_url = settings.MINIO_SERVER
        self.minio_access_key = settings.MINIO_ACCESS_KEY
        self.minio_secret_key = settings.MINIO_SECRET_KEY
        self.bucket = settings.BUCKET
        try:
            self.client = Minio(
                self.minio_url,
                access_key=self.minio_access_key,
                secret_key=self.minio_secret_key,
                secure=settings.MINIO_PROTOCOL == "https"

            )

        except Exception as e:
            print(f"Error initializing MinIO client: {e}")

    async def create_bucket(self):
        try:
            public_policy = f"""
                                        {{
                                          "Version": "2012-10-17",
                                          "Statement": [
                                            {{
                                              "Effect": "Allow",
                                              "Principal": {{
                                                "AWS": ["*"]
                                              }},
                                              "Action": [
                                                "s3:ListBucketMultipartUploads",
                                                "s3:GetBucketLocation",
                                                "s3:ListBucket"
                                              ],
                                              "Resource": ["arn:aws:s3:::oryza-metadata-linh-1"]
                                            }},
                                            {{
                                              "Effect": "Allow",
                                              "Principal": {{
                                                "AWS": ["*"]
                                              }},
                                              "Action": [
                                                "s3:GetObject",
                                                "s3:ListMultipartUploadParts",
                                                "s3:PutObject",
                                                "s3:AbortMultipartUpload",
                                                "s3:DeleteObject"
                                              ],
                                              "Resource": ["arn:aws:s3:::oryza-metadata-linh-1/*"]
                                            }}
                                          ]
                                        }}
                                        """

            if not await self.client.bucket_exists(self.bucket):
                print("Bucket not exists")
                await self.client.make_bucket(self.bucket)
            # policy = await self.client.get_bucket_policy(self.bucket)
            # print(policy)
            await self.client.set_bucket_policy(self.bucket, policy=public_policy)
        except Exception as e:
            print(f"Error create_bucket: {e}")

    async def upload_file_from_bytesIO(self, data: BytesIO, name_file_minio: str, bucket=None):
        if bucket is None:
            bucket = self.bucket

        try:
            await self.client.put_object(bucket, name_file_minio, data, len(data.getvalue()))
            return f"{settings.MINIO_PROTOCOL}://{self.minio_url}/{bucket}/{name_file_minio}"
        except Exception as e:
            print("Error upload_file: ", e)
            return None

    async def delete_file(self, name_file_minio: str, bucket=None):
        if bucket is None:
            bucket = self.bucket

        try:
            await self.client.remove_object(bucket, name_file_minio)
            return True
        except Exception as e:
            print("Error delete_file: ", e)
            return False

    async def delete_file_from_link(self, link: str, bucket=None):
        if bucket is None:
            bucket = self.bucket

        try:
            name_file = link.split(f"{settings.MINIO_PROTOCOL}://{self.minio_url}/{bucket}/")[1]
            await self.client.remove_object(bucket, name_file)
            return True
        except Exception as e:
            print("Error delete_file_from_link: ", e)
            return False
