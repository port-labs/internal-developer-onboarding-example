import logging
import json
import requests
from typing import Union, Literal

from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_port_api_token():
    """
    Get a Port API access token
    This function uses CLIENT_ID and CLIENT_SECRET from config
    """

    credentials = {'clientId': settings.PORT_CLIENT_ID, 'clientSecret': settings.PORT_CLIENT_SECRET}

    token_response = requests.post(f"{settings.PORT_API_URL}/auth/access_token", json=credentials)

    return token_response.json()['accessToken']


def create_entity(blueprint: str, body: dict, run_id: str):
    """
    Create new entity for blueprint in Port
    """

    token = get_port_api_token()
    headers = {
        'Authorization': f"Bearer {token}"
    }

    logger.info(f"create entity with: {json.dumps(body)}")
    response = requests.post(f"{settings.PORT_API_URL}/blueprints/{blueprint}/entities?run_id={run_id}",
                             json=body, headers=headers)
    logger.info(f"create entity response - status: {response.status_code}, body: {json.dumps(response.json())}")

    return response 

def get_entity(blueprint: str, entity_id: str):
    """
    Get existing entity for blueprint in Port
    """

    token = get_port_api_token()
    headers = {
        'Authorization': f"Bearer {token}"
    }

    logger.info(f"get entity with: {entity_id}")
    response = requests.get(f"{settings.PORT_API_URL}/blueprints/{blueprint}/entities/{entity_id}", headers=headers)

    logger.info(f"get entity response - status: {response.status_code}, body: {json.dumps(response.json())}")

    return response.json()["entity"]


def update_action(run_id: str, message: str, status: Union[Literal['FAILURE'], Literal['SUCCESS']]):
    """
    Reports to Port on the status of an action run
    """

    token = get_port_api_token()
    headers = {
        'Authorization': f"Bearer {token}"
    }
    body = {
        'status': status,
        'message': {
            'message': message
        }
    }

    logger.info(f"update action with: {json.dumps(body)}")
    response = requests.patch(f"{settings.PORT_API_URL}/actions/runs/{run_id}", json=body, headers=headers)
    logger.info(f"update action response - status: {response.status_code}, body: {json.dumps(response.json())}")

    return response.status_code

def update_entity(blueprint: str, entity_id: str, body: dict):
    """
    Updates an entity in Port
    """

    token = get_port_api_token()
    headers = {
        'Authorization': f"Bearer {token}"
    }

    logger.info(f"update action with: {json.dumps(body)}")
    response = requests.patch(f"{settings.PORT_API_URL}/blueprints/{blueprint}/entities/{entity_id}", json=body, headers=headers)
    logger.info(f"update entity response - status: {response.status_code}, body: {json.dumps(response.json())}")

    return response