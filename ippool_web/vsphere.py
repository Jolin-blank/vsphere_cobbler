from vmware.vapi.vsphere.client import create_vsphere_client
from samples.vsphere.vcenter.vm.create.create_basic_vm import CreateBasicVM
from samples.vsphere.common.ssl_helper import get_unverified_session

search = 'gzhc.local'


def create_client():
    session = get_unverified_session()
    client = create_vsphere_client(server='192.168.111.101', username='administrator@vsphere.local',
                                   password='GZhc20!(', session=session)
    return client


def create_vm(vm_name, cpu, memory, cap):
    session = get_unverified_session()
    client = create_vsphere_client(server='192.168.111.101', username='administrator@vsphere.local',
                                   password='GZhc20!(', session=session)
    create_basic_vm = CreateBasicVM(client=client, vm_name=vm_name, cpu=cpu, memory=memory, cap=cap)
    create_basic_vm.run()
