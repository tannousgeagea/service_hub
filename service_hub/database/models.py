import uuid
from django.db import models

# Create your models here.
# Create your models here.
class PlantInfo(models.Model):
    plant_id = models.CharField(max_length=255)
    plant_name = models.CharField(max_length=255)
    plant_location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'plant_info'
        verbose_name_plural = 'Plant Information'    


    def __str__(self):
        return f"{self.plant_name}"


class Service(models.Model):
    plant = models.ForeignKey(PlantInfo, on_delete=models.CASCADE)
    service_id = models.CharField(max_length=255, default=uuid.uuid4)
    service_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'service'
        verbose_name_plural = 'Service'
        
    def __str__(self) -> str:
        return f'{self.service_name} at {self.plant}'
    
class MicroService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    microservice_id = models.CharField(max_length=255, default=uuid.uuid4)
    microservice_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    port = models.IntegerField(default=8000)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'microservice'
        verbose_name_plural = 'MicroService'
        
    def __str__(self) -> str:
        return f"{self.microservice_name} in {self.service}"
    
    
class Urls(models.Model):
    microservice = models.OneToOneField(MicroService, on_delete=models.CASCADE)
    url_id = models.UUIDField(default=uuid.uuid4, max_length=255)
    url_name = models.CharField(max_length=255)
    url_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'urls'
        verbose_name_plural = 'Urls'
        
    def __str__(self) -> str:
        return f"{self.url_name} for {self.microservice}"
    
    @property
    def full_url(self):
        plant_info = self.microservice.service.plant
        if not 'base_url' in plant_info.meta_info.keys():
            return f'key: host not defined in plant meta info, please define host in plant meta info: {plant_info}'
          
        return f"{self.microservice.service.plant.meta_info['base_url']}:{self.microservice.port}{self.url_path}"
    