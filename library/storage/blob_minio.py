from minio import Minio
from io import StringIO, BytesIO
from library.meta.metaclass import Singleton

class MinioClient(metaclass=Singleton):    
    def __init__(
        self, 
        protocol: str,
        host_with_override: str,
        host: str,
        port: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False
    ):
        url = f"{host_with_override}:{port}"
        self.client = Minio(
            url, access_key=access_key, secret_key=secret_key, secure=secure
        )
        self.path = f"{protocol}://{host}:{port}/{bucket}"
        self.bucket = bucket        

    def write_stringio(self, input: StringIO, object_name: str) -> str:
        str_data = input.getvalue().encode('utf-8')
        data = BytesIO(str_data)
        self.client.put_object(
            self.bucket,
            object_name,
            data=data,
            length=len(str_data),
            content_type="text/csv"
        )
        return f"{self.path}/{object_name}"