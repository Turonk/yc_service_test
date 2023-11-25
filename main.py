import os
import subprocess


from prettytable import PrettyTable


from yandex.cloud.compute.v1.instance_pb2 import IPV4, Instance
from yandex.cloud.compute.v1.instance_service_pb2 import (
    GetInstanceRequest,
    CreateInstanceRequest,
    ResourcesSpec,
    AttachedDiskSpec,
    NetworkInterfaceSpec,
    PrimaryAddressSpec,
    ListInstancesRequest,
    MoveInstanceRequest,
    RestartInstanceRequest,
    StartInstanceRequest,
    StopInstanceRequest,
    OneToOneNatSpec,
    DeleteInstanceRequest,
    CreateInstanceMetadata,
    DeleteInstanceMetadata,
    
)

from yandex.cloud.resourcemanager.v1.folder_service_pb2 import (GetFolderRequest,
                                                                ListFoldersRequest, 
                                                                DeleteFolderRequest)
import yandex.cloud.resourcemanager.v1.folder_pb2 


from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub
from yandex.cloud.resourcemanager.v1.folder_service_pb2_grpc import FolderServiceStub


import yandexcloud
from settings import CLOUD_ID, SERVICE_ACC_CREDENTIALS


FOLDER_FIELD_NAMES = ["#", "folder name", "folder id"]
INSTANCE_FIELD_NAMES = ["#", "instance name",
                        "instance id", "status",
                        "public_id", "disk_id"]


def create_table(data: object,
                 field_names: list,
                 instance_name: str = None) -> PrettyTable:
    """ Печатает в терминал список переданных данных в виде таблицы. """
    table = PrettyTable()
    table.field_names = field_names

    index = 0

    for item in data:
        match type(item):
            case yandex.cloud.resourcemanager.v1.folder_pb2.Folder:
                table.add_row([index, item.name, item.id])
            case yandex.cloud.compute.v1.instance_pb2.Instance:
                table.add_row(
                    [index,
                     item.name,
                     item.id, 
                     item.status,
                     item.network_interfaces[0].primary_v4_address.one_to_one_nat.address,
                     item.boot_disk.disk_id]
                    )
            case _:
                print("This object is not recognized.")
        index += 1
    return table

def get_folder_obj():
    folders = folder_service.List(ListFoldersRequest(cloud_id=CLOUD_ID)).folders
    print(create_table(folders, FOLDER_FIELD_NAMES))

    current_folder = folders[int(input('Введите индекс '))]
    return folders, current_folder

def create_ssh_keys(key_name):
    # path_to_ssh = get_path_to_dir(cohort_name, key_name)
    if not os.path.isfile(key_name):
        subprocess.call(f'ssh-keygen -t rsa -f {key_name} -N 7KqoI_py', shell=True)

    with open(key_name+'.pub', 'r') as ssh_pub_file:
        ssh_key = ssh_pub_file.readline()
    return ssh_key

def create_virtual_machines(folder_id):
    key_name = 'test-key'
    ssh_key = create_ssh_keys(key_name)
    try:
        instance = instance_service.Create(CreateInstanceRequest(
            folder_id=folder_id,
            name=key_name,
            description='testing',
            zone_id='ru-central1-b',
            platform_id='standard-v2',
            resources_spec=
                {
                    'memory': 2147483648, 
                    'cores': 2,
                    'core_fraction': 5
                },
            metadata=
                {
                    'user-data': f"#cloud-config\nusers:\n  - name: yc-user\n    groups: sudo\n    shell: /bin/bash\n    sudo: ['ALL=(ALL) NOPASSWD:ALL']\n    ssh-authorized-keys:\n    - {ssh_key}\n"
                },
            boot_disk_spec=
                {
                    'disk_spec': 
                        {
                            'size': 21474836480,
                            'image_id': 'fd8ingbofbh3j5h7i8ll'
                        }
                }, 
            network_interface_specs= 
                [{
                    'subnet_id': 'e2l1jc1u14th4r42up4t',
                    'primary_v4_address_spec': {'one_to_one_nat_spec': {'ip_version': 'IPV4'}}
                }],   
        ))
        print(instance)
        print('Complite')
    except Exception as e:
        print(e)

def delete_instance(instance_id):
    request = instance_service.Delete(DeleteInstanceRequest(instance_id=instance_id))
    return request

def restart_instance(current_instance):
    request = instance_service.Restart(RestartInstanceRequest(instance_id=current_instance.id))
    return request.description


def start_instance(current_instance):
    request = instance_service.Start(StartInstanceRequest(instance_id=current_instance.id))
    return request.description

def stop_instance(current_instance):
    request = instance_service.Stop(StopInstanceRequest(instance_id=current_instance.id))
    return request.description


def instance_manage(selected_instances):
    print(f'''
        Введите команду для работы с машинами
        del - удалить;
        restart - перезагрузить машину;
        start - запусить виртуальную машину;
        stop - остановить виртуальную машину;
    ''')
    comand = input('Ввод команды: ')

    match comand:
        case 'del': 
            for instance in selected_instances:
                print(delete_instance(instance.id))
        case 'restart':
            for current_instance in selected_instances:
                print(restart_instance(current_instance))
        case 'stop':
            for current_instance in selected_instances:
                print(stop_instance(current_instance))
        case 'start':
            for current_instance in selected_instances:
                print(start_instance(current_instance))



def get_folder_data():
    folders, current_folder = get_folder_obj()

    instances = instance_service.List(ListInstancesRequest(folder_id=current_folder.id)).instances
    print(create_table(instances, INSTANCE_FIELD_NAMES))

    return folders, instances, current_folder


def check_instances():

    folders, instances, current_folder = get_folder_data()
    
    selected_instances = []
    check_indexes = input('Введите индексы машин через пробел ').split()
    for index in check_indexes:
        selected_instances.append(instances[int(index)])
    print(create_table(selected_instances, INSTANCE_FIELD_NAMES))
    instance_manage(selected_instances)


if __name__ == '__main__':
    
    sdk = yandexcloud.SDK(service_account_key=SERVICE_ACC_CREDENTIALS)

    folder_service = sdk.client(FolderServiceStub)
    instance_service = sdk.client(InstanceServiceStub)

    # folders, folder = get_folder_obj()
    # create_virtual_machines(folder.id)
    check_instances() 