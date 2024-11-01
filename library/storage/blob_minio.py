from minio import Minio
from io import StringIO, BytesIO
from library.meta.env import MinioStoreConfig, get_minio_host, get_object_path
from library.meta.metaclass import Singleton

class MinioClient(metaclass=Singleton):    
    def __init__(
        self, 
        config: MinioStoreConfig,
        secure: bool = False
    ):
        self.config = config
        host = get_minio_host(self.config)
        self.client = Minio(
            host, access_key=config.access_key, secret_key=config.secret_key, secure=secure
        )

    def write_stringio(self, input: StringIO, object_name: str) -> str:
        str_data = input.getvalue().encode('utf-8')
        data = BytesIO(str_data)
        self.client.put_object(
            self.config.bucket,
            object_name,
            data=data,
            length=len(str_data),
            content_type="text/csv"
        )
        return get_object_path(self.config, object_name)