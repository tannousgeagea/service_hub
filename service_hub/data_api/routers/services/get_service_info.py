import os
import time
import django
from fastapi import status
from datetime import datetime
from typing import Callable
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.routing import APIRoute

django.setup()
from django.core.exceptions import ObjectDoesNotExist
from database.models import PlantInfo, Urls, Service, MicroService

class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler
    

router = APIRouter(
    prefix="/api/v1",
    tags=["Services"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)



@router.api_route(
    "/service/metadata", methods=["GET"], tags=["Services"]
)
def get_service_metadata(response:Response):
    
    results = {}
    try:
        services = Service.objects.all()
        service_data = []
        for service in services:

            row = {
                "service_id": service.service_id,
                "service_name": service.service_name,
                "description": service.description,
            }

            service_data.append(row)
        
        results['data'] = service_data
        results['status_code'] = "ok"
        results["detail"] = "data retrieved successfully"
        results["status_description"] = "OK"
        
    except ObjectDoesNotExist as e:
        results['error'] = {
            'status_code': "non-matching-query",
            'status_description': f'Matching query was not found',
            'detail': f"matching query does not exist. {e}"
        }

        response.status_code = status.HTTP_404_NOT_FOUND
        
    except HTTPException as e:
        results['error'] = {
            "status_code": "not found",
            "status_description": "Request not Found",
            "detail": f"{e}",
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
    
    except Exception as e:
        results['error'] = {
            'status_code': 'server-error',
            "status_description": "Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return results


@router.api_route(
    "/service/{service_id}", methods=["GET"], tags=["PlantInfo"]
)
def get_service_info(response:Response, service_id:str):
    results = {}
    try:
        
        if not Service.objects.filter(service_id=service_id).exists():
            results['error'] = {
                "status_code": "not found",
                "status_description": "Request not Found",
                "detail": f"{service_id} not Found, please select a valid service_id",
            }
            
            response.status_code = status.HTTP_404_NOT_FOUND
            return results

        service = Service.objects.get(service_id=service_id)
        microservices = MicroService.objects.filter(service=service)
        services_data = []
        for microservice in microservices:
            services_data.append(
                {
                    "name": microservice.microservice_name,
                    "id": microservice.microservice_id,
                    "description": microservice.description,
                    "url": Urls.objects.get(microservice=microservice).full_url
            })
        
        results['data'] = {
            "plant_id": service.plant.plant_id,
            "plant_name": service.plant.plant_name,
            "plant_location": service.plant.plant_location,
            "services": services_data,
        }
        
        results['status_code'] = "ok"
        results["detail"] = "data retrieved successfully"
        results["status_description"] = "OK"
        
    except ObjectDoesNotExist as e:
        results['error'] = {
            'status_code': "non-matching-query",
            'status_description': f'Matching query was not found',
            'detail': f"matching query does not exist. {e}"
        }

        response.status_code = status.HTTP_404_NOT_FOUND
        
    except HTTPException as e:
        results['error'] = {
            "status_code": "not found",
            "status_description": "Request not Found",
            "detail": f"{e}",
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
    
    except Exception as e:
        results['error'] = {
            'status_code': 'server-error',
            "status_description": "Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return results



"""
                "microservices": [
                    {
                        'microservice_id': microservice.microservice_id,
                        'microservice_name': microservice.microservice_name,
                        'microservice_url': Urls.objects.get(microservice=microservice).full_url,
                    } for microservice in microservices
                    ]

"""