import os
from minio import Minio

class MinioClient:
    def __init__(self):
        # Removemos os valores padrão. Agora, se a variável não existir na .env,
        # o Python vai acusar um KeyError imediatamente.
        self.client = Minio(
            endpoint=os.environ["MINIO_ENDPOINT"],
            access_key=os.environ["MINIO_ROOT_USER"],
            secret_key=os.environ["MINIO_ROOT_PASSWORD"],
            secure=os.environ.get("MINIO_SECURE", "").lower() == "true"
        )
        self.bucket_name = os.environ["MINIO_BUCKET"]

    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Uploads a file to MinIO.
        Returns the object name.
        """
        try:
            self.client.fput_object(self.bucket_name, object_name, file_path)
            return object_name
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e

    def get_presigned_url(self, object_name: str) -> str:
        """
        Generates a presigned URL for retrieving the object.
        """
        try:
            return self.client.get_presigned_url("GET", self.bucket_name, object_name)
        except Exception as e:
            print(f"Error generating url: {e}")
            raise e

# Singleton instance
minio_client = MinioClient()