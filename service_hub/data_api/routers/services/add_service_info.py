import os
import uuid
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




description = """

Endpoint:
POST /service

Tags:

    Services

Description:
This endpoint allows you to add a new service to the system. The request must contain a plant_id and a service_name. Optional fields include service_id, description, and meta_info. If the service_id is not provided, a new unique ID will be generated.

Request Body:
The request body should be a JSON object with the following fields:

    plant_id (string, required): The unique identifier of the plant to which the service is associated.
    service_name (string, required): The name of the service being added.
    service_id (string, optional): The unique identifier for the service. If not provided, a new UUID will be generated.
    description (string, optional): A description of the service.
    meta_info (object, optional): Additional metadata related to the service.

Response:
The response will be a JSON object indicating the result of the operation. It includes a status code, status description, and a detailed message.

    Success Response:
        status_code: "ok"
        status_description: "service with service ID {service_id} successfully saved"
        detail: "success"

    Error Responses:

        Bad Request:
            status_code: "bad-request"
            status_description: "plant_id {plant_id} does not exists"
            detail: "plant_id {plant_id} does not exist; please select a valid plant_id"

        Not Found:
            status_code: "not found"
            status_description: "Request not Found"
            detail: Details of the HTTP exception encountered

        Internal Server Error:
            status_code: "server-error"
            status_description: "Internal Server Error"
            detail: Description of the encountered exception

Example Request:

json

{
  "plant_id": "12345",
  "service_name": "Irrigation",
  "description": "Automated irrigation service",
  "meta_info": {
    "frequency": "daily",
    "duration": "2 hours"
  }
}

Example Response:

    Success:

    json

{
  "status_code": "ok",
  "status_description": "service with service ID 12345 successfully saved",
  "detail": "success"
}

Error (Bad Request):

json

    {
      "error": {
        "status_code": "bad-request",
        "status_description": "plant_id 12345 does not exists",
        "detail": "plant_id 12345 does not exist; please select a valid plant_id"
      }
    }

Implementation Notes:

    The function checks if the plant_id and service_name are present in the request. If not, it raises an assertion error.
    It validates if the plant_id exists in the PlantInfo database.
    If the plant_id does not exist, a 400 Bad Request status is returned.
    A new service_id is generated if not provided.
    The service details are saved in the database.
    Appropriate error handling is in place for HTTP exceptions and general exceptions, returning 404 Not Found and 500 Internal Server Error statuses, respectively.

"""

@router.api_route(
    "/service", methods=["POST"], tags=["Services"], description=description
)
def add_new_service(response: Response, request:dict):
    results = {}
    try:
        
        
        assert 'plant_id' in request.keys(), f'key: plant_id not found'
        assert 'service_name' in request.keys(), f'key: service_name not Found'
        
        if not PlantInfo.objects.filter(plant_id=request['plant_id']).exists():
            results['error'] = {
                'status_code': "bad-request",
                'status_description': f'plant_id {request["plant_id"]} does not exists',
                'detail': f"plant_id {request['plant_id']} does not exist; please select a valid plant_id",
            }

            response.status_code = status.HTTP_400_BAD_REQUEST
            return results
            
        service_id = request.get('service_id', str(uuid.uuid4()))
        plant_info = PlantInfo.objects.get(plant_id = request['plant_id'])
        service = Service(
            plant=plant_info,
            service_id=service_id,
            service_name=request.get('service_name'),
            description=request.get('description'),
            meta_info=request.get('meta_info'),
        )
        
        service.save()
        
        results = {
            "status_code": 'ok',
            "status_description": f"service with service ID {request['plant_id']} successfully saved",
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