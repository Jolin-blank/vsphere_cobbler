from django.db import models


# Create your models here.
class cmdb(models.Model):
    ip = models.GenericIPAddressField(unique=True)
    hostname = models.CharField(max_length=50, default='null')
    name = models.CharField(max_length=20, null=True)
    cpu = models.CharField(max_length=5, null=True)
    memory = models.CharField(max_length=5, null=True)
    cap = models.CharField(max_length=5, null=True)
    is_got_ip = models.CharField(max_length=5, default='no')
    is_set_vlan = models.CharField(max_length=5, default='no')
    dept = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=10, null=True)
    dc = models.CharField(max_length=5, null=True)
    env = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.ip

    def init_hardware(self, template):
        self.memory = hardware_template().get_cpu(template)
        self.cpu = hardware_template().get_mem(template)
        self.cap = hardware_template().get_cap(template)



class hardware_template(models.Model):
    template = models.CharField(max_length=10)  # name
    cpu = models.CharField(max_length=5)
    memory = models.CharField(max_length=5)
    capacity = models.CharField(max_length=5)  # int   #增加删除字段 #json filed  meta_data  #物理主机

    def __str__(self):
        return self.template

    # @staticmethod
    # def get_hardware_info(template):
    #     info = {"cpu": hardware_template.objects.get(template=template).cpu,
    #             "memory": hardware_template.objects.get(template=template).memory,
    #             "cap": hardware_template.objects.get(template=template).capacity}
    #     return info

    @staticmethod
    def get_cpu(template):  # 一个方法
        return hardware_template.objects.get(template=template).cpu

    @staticmethod
    def get_mem(template):
        return hardware_template.objects.get(template=template).memory

    @staticmethod
    def get_cap(template):
        return hardware_template.objects.get(template=template).capacity


