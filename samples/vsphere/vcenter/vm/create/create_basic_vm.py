#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2016-2018. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'
__vcenter_version__ = '6.5+'

from com.vmware.vcenter.vm.hardware_client import (
    Disk, Ethernet)
from com.vmware.vcenter.vm_client import (Power)
from com.vmware.vcenter.vm.hardware.adapter_client import Sata
from com.vmware.vcenter_client import VM, Network
from com.vmware.vcenter.vm.hardware_client import Memory
from com.vmware.vcenter.ovf_client import DiskProvisioningType
from vmware.vapi.vsphere.client import create_vsphere_client
from com.vmware.vcenter.vm.hardware_client import Cpu
from com.vmware.vcenter.vm.hardware_client import Ethernet
from samples.vsphere.common.ssl_helper import get_unverified_session
from samples.vsphere.common import sample_cli
from samples.vsphere.common import sample_util
from samples.vsphere.common.sample_util import pp
from samples.vsphere.vcenter.helper import network_helper
from samples.vsphere.vcenter.helper.vm_helper import get_vm


class UpdateNetwork(object):
    def __init__(self, client=None, vm_name=None, network=None):
        self.client = client
        self.vm_name = vm_name
        self.network = network
        self.datacenter_name = 'Datacenter'

    def update_network(self):
        nic = '4000'
        vm = get_vm(self.client, vm_name=self.vm_name)
        network_info = self.client.vcenter.vm.hardware.Ethernet.get(vm=vm, nic=nic)
        dv_portgroup_name = self.network
        distributed_network = network_helper.get_network_backing(
            self.client,
            dv_portgroup_name,
            self.datacenter_name,
            Network.Type.DISTRIBUTED_PORTGROUP)
        print(distributed_network)
        nics = Ethernet.UpdateSpec(start_connected=True, mac_type='MANUAL', mac_address=network_info.mac_address,
                                   backing=Ethernet.BackingSpec(
                                       type=Ethernet.BackingType.DISTRIBUTED_PORTGROUP,
                                       network=distributed_network))
        self.client.vcenter.vm.hardware.Ethernet.update(vm=vm, nic=nic, spec=nics)


class CreateBasicVM(object):
    """
    Demonstrates how to create a basic VM with following configuration:
    2 disks, 1 nic

    Sample Prerequisites:
        - datacenter
        - vm folder
        - datastore
        - standard switch network
    """

    def __init__(self, client=None, placement_spec=None, cpu=4, memory=4, cap=30, vm_name=None):
        self.client = client
        self.placement_spec = placement_spec
        self.vm_name = vm_name
        self.cleardata = None
        self.cpu = cpu
        self.memory = memory * 1024
        self.cap = cap * 1024 * 1024 * 1024

        # Execute the sample in standalone mode.
        if not self.client:
            parser = sample_cli.build_arg_parser()
            parser.add_argument('-n', '--vm_name',
                                action='store',
                                help='Name of the testing vm')
            args = sample_util.process_cli_args(parser.parse_args())
            if args.vm_name:
                self.vm_name = args.vm_name
            self.cleardata = args.cleardata

            session = get_unverified_session() if args.skipverification else None
            self.client = create_vsphere_client(server=args.server,
                                                username=args.username,
                                                password=args.password,
                                                session=session)

    def run(self):
        # Get a placement spec
        datacenter_name = 'Datacenter'  # testbed.config['VM_DATACENTER_NAME']
        # vm_folder_name =   'kong111_166'                     #testbed.config['VM_FOLDER2_NAME']
        datastore_name = 'datastore-717'  # testbed.config['VM_DATASTORE_NAME']
        std_portgroup_name = 'VM Network'  # testbed.config['STDPORTGROUP_NAME']
        host = 'host-716'
        diskprovisioningtpye = DiskProvisioningType('eagerZeroedThick')
        if not self.placement_spec:
            # self.placement_spec = vm_placement_helper.get_placement_spec_for_resource_pool(
            #     self.client,
            #     datacenter_name,
            #     vm_folder_name,
            #     datastore_name)
            self.placement_spec = VM.PlacementSpec(host=host, datastore=datastore_name, folder='group-v3')
        # Get a standard network backing
        standard_network = network_helper.get_network_backing(
            self.client,
            std_portgroup_name,
            datacenter_name,
            Network.Type.STANDARD_PORTGROUP)

        """
        Create a basic VM.

        Using the provided PlacementSpec, create a VM with a selected Guest OS
        and provided name.

        Create a VM with the following configuration:
        * Create 2 disks and specify one of them on scsi0:0 since it's the boot disk
        * Specify 1 ethernet adapter using a Standard Portgroup backing
        * Setup for PXE install by selecting network as first boot device

        Use guest and system provided defaults for most configuration settings.
        """
        guest_os = 'CENTOS_6_64'  # testbed.config['VM_GUESTOS']
        hardware = ''
        # boot_disk = Disk.CreateSpec(type=Disk.HostBusAdapterType.SCSI,
        #                             scsi=ScsiAddressSpec(bus=0, unit=0),
        #                             new_vmdk=Disk.VmdkCreateSpec())
        data_disk = Disk.CreateSpec(new_vmdk=Disk.VmdkCreateSpec(capacity=self.cap))
        nic = Ethernet.CreateSpec(
            start_connected=True,
            backing=Ethernet.BackingSpec(
                type=Ethernet.BackingType.STANDARD_PORTGROUP,
                network=standard_network)
        )
        sata_adapt = Sata.CreateSpec()
        cpu = Cpu.UpdateSpec(count=self.cpu, cores_per_socket=1, hot_add_enabled=True, hot_remove_enabled=True)
        memory = Memory.UpdateSpec(size_mib=self.memory, hot_add_enabled=True)
        # boot_device_order = [
        #     BootDevice.EntryCreateSpec(BootDevice.Type.ETHERNET),
        #     BootDevice.EntryCreateSpec(BootDevice.Type.DISK)]
        # host1=Host.list()
        # print (host1)
        placement = VM.PlacementSpec(host=host, datastore=datastore_name, folder='group-v3')
        vm_create_spec = VM.CreateSpec(name=self.vm_name,
                                       guest_os=guest_os,
                                       cpu=cpu,
                                       memory=memory,
                                       placement=placement,
                                       disks=[data_disk],
                                       nics=[nic],
                                       sata_adapters=[sata_adapt])
        print('\n# Example: create_basic_vm: Creating a VM using spec\n-----')
        print(pp(vm_create_spec))
        print('-----')

        vm = self.client.vcenter.VM.create(vm_create_spec)

        print("create_basic_vm: Created VM '{}' ({})".format(self.vm_name, vm))

        vm_info = self.client.vcenter.VM.get(vm)
        print('vm.get({}) -> {}'.format(vm, pp(vm_info)))
        self.client.vcenter.vm.Power.start(vm)

        return vm

    def cleanup(self):
        vm = get_vm(self.client, self.vm_name)
        if vm:
            state = self.client.vcenter.vm.Power.get(vm)
            if state == Power.Info(state=Power.State.POWERED_ON):
                self.client.vcenter.vm.Power.stop(vm)
            elif state == Power.Info(state=Power.State.SUSPENDED):
                self.client.vcenter.vm.Power.start(vm)
                self.client.vcenter.vm.Power.stop(vm)
            print("Deleting VM '{}' ({})".format(self.vm_name, vm))
            self.client.vcenter.VM.delete(vm)


def main():
    session = get_unverified_session()
    client = create_vsphere_client(server='192.168.111.101', username='administrator@vsphere.local',
                                   password='GZhc20!(', session=session)
    create_basic_vm = CreateBasicVM(client=client, vm_name='test1000')
    # create_basic_vm.cleanup()
    # create_basic_vm.run()
    # update_network = UpdateNetwork(client=client, network='R740-vlan22', vm_name='test24')
    # update_network.update_network()
    # if create_basic_vm.cleardata:
    #     create_basic_vm.cleanup()


if __name__ == '__main__':
    main()
