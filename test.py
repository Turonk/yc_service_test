import yandexcloud

from yandex.cloud.resourcemanager.v1.folder_service_pb2 import (ListFoldersRequest)
import yandex.cloud.resourcemanager.v1.folder_pb2 
from yandex.cloud.resourcemanager.v1.folder_service_pb2_grpc import FolderServiceStub

from settings import SERVICE_ACC_CREDENTIALS, CLOUD_ID


def handler():
    folder_service = sdk.client(FolderServiceStub)
    
    folders = {}
    for c in folder_service.List(ListFoldersRequest(cloud_id=CLOUD_ID)).folders:
        folders[c.id] = c.name
    return folders


sdk = yandexcloud.SDK(service_account_key=SERVICE_ACC_CREDENTIALS)

print(handler())