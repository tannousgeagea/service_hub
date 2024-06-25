from django.contrib import admin

from django.contrib import admin
from .models import PlantInfo, Service, MicroService, Urls


class UrlInline(admin.TabularInline):
    model = Urls
    extra = 0


@admin.register(PlantInfo)
class PlantInfoAdmin(admin.ModelAdmin):
    list_display = ('plant_id', 'plant_name', 'plant_location', 'created_at')
    search_fields = ('plant_name', 'plant_location')
    list_filter = ('created_at',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_id', 'service_name', 'plant', 'created_at')
    search_fields = ('service_name', 'plant__plant_name')
    list_filter = ('created_at', 'plant')

@admin.register(MicroService)
class MicroServiceAdmin(admin.ModelAdmin):
    list_display = ('microservice_id', 'microservice_name', 'service', 'port', 'created_at')
    search_fields = ('microservice_name', 'service__service_name')
    list_filter = ('created_at', 'service')
    inlines = [
        UrlInline
    ]
    
@admin.register(Urls)
class UrlsAdmin(admin.ModelAdmin):
    list_display = ('url_id', 'url_name', 'url_path', 'microservice', 'created_at')
    list_filter = ('microservice', 'created_at')

# Alternatively, you can use admin.site.register if you prefer not to use the @admin.register decorator:
# admin.site.register(PlantInfo, PlantInfoAdmin)
# admin.site.register(Service, ServiceAdmin)
# admin.site.register(MicroService, MicroServiceAdmin)
