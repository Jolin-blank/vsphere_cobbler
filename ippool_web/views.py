from django.shortcuts import render
from django.http import HttpResponse, request
from vmware.vapi.vsphere.client import create_vsphere_client
import json
from .models import cmdb
from .models import hardware_template
from .vsphere import create_vm
from django.core import serializers
from .tasks import update_switch

search = 'gzhc.local'


def test_post(requset):
    if requset.method == 'POST':
        body = requset.body
        print(body)
        tmp = json.loads(body)
        print(tmp)
        return HttpResponse(json.dumps(tmp))


def get_template(requset):
    if requset.method == 'GET':
        template_list = hardware_template.objects.all()
        data = serializers.serialize("json", template_list)
        print(data)
        return HttpResponse(data)


def index(request):
    return render(request, 'index.html')


def ip_index(request):
    return render(request, 'ip_hostname.html')


def addip(request):
    if request.method == 'GET':
        ip = request.GET.get('ip')
        ipaddr = cmdb(ip=ip)
        ipaddr.save()
        return HttpResponse(ip)


def rec_hostname(request):
    if request.method == 'GET':
        hostname = request.GET.get('hostname')
        type1 = request.GET.get('type')
        dept = request.GET.get('dept')
        env = request.GET.get('env')
        dc = request.GET.get('dc')
        cpu = request.GET.get('cpu')
        mem = request.GET.get('memory')
        cap = request.GET.get('cap')
        if env != 'uat':
            host_info = cmdb.objects.filter(hostname='null', ip__contains='.22.')[0]
        else:
            host_info = cmdb.objects.filter(hostname='null', ip__contains=".111.")[0]
        host = host_info.ip.split('.')[-1]
        host_info.cpu = cpu + 'C'
        host_info.memory = mem + 'G'
        host_info.cap = cap + 'G'
        host_info.type = type1
        host_info.dept = dept
        host_info.env = env
        host_info.dc = dc
        host_info.hostname = hostname + host + '.' + type1 + '.' + dc + '.' + dept + '.' + env + '.' + search
        host_info.name = hostname + host
        host_info.save()
        create_vm(hostname+host, int(cpu), int(mem), int(cap))
        return HttpResponse(host_info.ip)


def rec_template1(request):
    if request.method == 'GET':
        hostname = request.GET.get('hostname')
        template = request.GET.get('template')
        cpu = int(hardware_template().get_cpu(template)[:-1])
        mem = int(hardware_template().get_mem(template)[:-1])
        cap = int(hardware_template().get_cap(template)[:-1])
        host_info = cmdb.objects.filter(hostname='null')[0]
        host_info.init_hardware(template)
        host = host_info.ip.split('.')[-1]
        host_info.hostname = hostname + host + search
        host_info.name = hostname + host
        host_info.save()
        create_vm(hostname + host, cpu, mem, cap)
        return HttpResponse(host_info.ip)


def rec_template(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        hostname = body.get('name')
        template = body.get('template')
        cpu = int(hardware_template().get_cpu(template)[:-1])
        mem = int(hardware_template().get_mem(template)[:-1])
        cap = int(hardware_template().get_cap(template)[:-1])
        host_info = cmdb.objects.filter(hostname='null')[0]
        host_info.init_hardware(template)
        host = host_info.ip.split('.')[-1]
        host_info.hostname = hostname + host + search
        host_info.name = hostname + host
        host_info.save()
        create_vm(hostname + host, cpu, mem, cap)
        return HttpResponse(host_info.ip)


def rec_ip_hostname(request):
    if request.method == 'GET':
        ip = request.GET.get('ip')
        hostname = request.GET.get('hostname')
        type1 = request.GET.get('type')
        dept = request.GET.get('dept')
        env = request.GET.get('env')
        dc = request.GET.get('dc')
        cpu = request.GET.get('cpu')
        mem = request.GET.get('memory')
        cap = request.GET.get('cap')
        host = ip.split('.')[-1]
        host_info = cmdb()
        host_info.ip = ip
        host_info.cpu = cpu + 'C'
        host_info.memory = mem + 'G'
        host_info.cap = cap + 'G'
        host_info.type = type1
        host_info.dept = dept
        host_info.env = env
        host_info.dc = dc
        host_info.hostname = hostname + host + '.' + type1 + '.' + dc + '.' + dept + '.' + env + '.' + search
        host_info.hostname = hostname + host + search
        host_info.save()
        # create_vm(hostname+host, int(cpu), mem, cap)
        return HttpResponse(host_info.ip)


def ip_hostname(request):
    secret_key = request.META.get('HTTP_SECRET_KEY')
    if secret_key == 'cWuk67eNk':
        if request.method == 'GET':
            cpu = request.GET.get('cpu')
            memory = request.GET.get('memory')
            cap = request.GET.get('cap')
            ip_host = cmdb.objects.filter(is_got_ip='no', cpu=cpu, memory=memory, cap=cap)[0]
            ip_host.is_got_ip = 'yes'
            info = ip_host.ip + ':' + ip_host.hostname
            ip_host.save()
            if ip_host.ip.split('.')[-2] == '22':
                switch = 'R740-vlan22'
                update_switch.delay(ip_host.name, switch)
            return HttpResponse(info)
    else:
        return HttpResponse('do you have secret_key?')
