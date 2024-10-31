from dataclasses import dataclass
from minio import Minio
from io import StringIO, BytesIO
from library.meta.metaclass import Singleton

@dataclass
class MinioStoreConfig:
    protocol: str
    host: str
    port: str    
    access_key: str
    secret_key: str
    local: bool

class MinioClient(metaclass=Singleton):    
    def __init__(
        self, 
        config: MinioStoreConfig,
        secure: bool = False
    ):
        self.config = config
        self.client = Minio(self._get_host(), access_key=config.access_key, secret_key=config.secret_key, secure=secure)

    def _get_host(self) -> str:
        return f"{self.config.host}:{self.config.port}"
    
    def _get_object_path(self, bucket: str, object_name: str) -> str:
        # self.config.local hardcode to minio to allow workflo tests to run
        return f"{self.config.protocol}://{"minio:9000" if self.config.local else self._get_host()}/{bucket}/{object_name}"

    def write_stringio(self, input: StringIO, object_name: str, bucket: str) -> str:
        str_data = input.getvalue().encode('utf-8')
        data = BytesIO(str_data)
        result = self.client.put_object(
            bucket,
            object_name,
            data=data,
            length=len(str_data),
            content_type="text/csv"
        )
        return self._get_object_path(bucket, object_name)