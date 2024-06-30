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
from database.models import PlantInfo

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
    tags=["PlantInfo"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)


@router.api_route(
    "/plant/add", methods=["POST"], tags=["PlantInfo"]
)
def add_new_plant(response: Response, request:dict):
    results = {}
    try:
        
        assert 'plant_id' in request.keys(), f'key: plant_id not Found'
        assert 'plant_name' in request.keys(), f'key: plant_name not Found'
        assert 'plant_location' in request.keys(), f'key: plant_location not Found'
        
        if PlantInfo.objects.filter(plant_id=request['plant_id']).exists():
            results['error'] = {
                'status_code': "bad-request",
                'status_description': f'plant_id {request["plant_id"]} already exists',
                'detail': f"plant_id {request['plant_id']} already exists",
            }

            response.status_code = status.HTTP_400_BAD_REQUEST
            return results
            
        
        plant_info = PlantInfo(
            plant_id = request['plant_id'],
            plant_name = request['plant_name'],
            plant_location = request['plant_location'],
            meta_info = request.get('meta_info')
        )
        
        plant_info.save()
        results = {
            "status_code": 'ok',
            "status_description": f"plant_id {request['plant_id']} successfully saved",
            "detail": "success"
        }
        
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