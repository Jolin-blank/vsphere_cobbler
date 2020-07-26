from __future__ import absolute_import, unicode_literals

from celery import shared_task
from .vsphere import *
from samples.vsphere.vcenter.vm.create.create_basic_vm import UpdateNetwork


@shared_task
def update_switch(name, network):
    client = create_client()
    network = UpdateNetwork(client, name, network)
    network.update_network()
