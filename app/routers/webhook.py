import logging
from fastapi import APIRouter, Depends

# from mappings import ACTION_ID_TO_CLASS_MAPPING
# from api.deps import verify_webhook
from app.core import port
from app.core.config import settings
from app.schemas.webhook_schema import Webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

ACTION_ID_TO_CLASS_MAPPING = {}

@router.post("/service", dependencies=None)
async def handle_create_service_webhook(webhook: Webhook):
    logger.info(f"Webhook body: {webhook}")
    action_type = webhook.payload['action']['trigger']
    action_identifier = webhook.payload['action']['identifier']
    properties = webhook.payload['properties']
    run_id = webhook.context.runId

    if action_type == 'CREATE':
        logger.info(f"{action_identifier} - onboard new team")

        ## Create Mesh Team and Connect it to Group
        entity_data = {
            "title": properties["meshTeamName"],
            "properties": {},
            "relations": {
                "maya_group": properties["meshGroup"]
            }
        }
        create_response = port.create_entity(blueprint=settings.PORT_SERVICE_MESH_TEAM_BLUEPRINT, body=entity_data, run_id=run_id)
        action_status = 'SUCCESS' if 200 <= create_response.status_code <= 299 else 'FAILURE'
        message = f"Message after creating entity is {action_status}"

        ## Proceed to grant this newly created team access to the Repository
        if action_status == 'SUCCESS':
            mesh_team_entity_identifier = create_response.json()["entity"]["identifier"]

            ## Update the mesh service relation
            for service in properties["services"]:
                existing_mesh_relations = port.get_entity(blueprint=settings.PORT_REPOSITORY_BLUEPRINT, entity_id=service)["relations"]["mesh"]
                existing_mesh_relations.append(mesh_team_entity_identifier)
                entity_data = {
                    "properties": {
                        "type": "service"
                    },
                    "relations": {
                        "mesh": existing_mesh_relations
                    }
                }
                port.update_entity(blueprint=settings.PORT_REPOSITORY_BLUEPRINT, entity_id=service, body=entity_data)

            ## Update the mesh library relation
            for library in properties["libraries"]:
                existing_mesh_relations = port.get_entity(blueprint=settings.PORT_REPOSITORY_BLUEPRINT, entity_id=library)["relations"]["mesh"]
                existing_mesh_relations.append(mesh_team_entity_identifier)

                entity_data = {
                    "properties": {
                        "type": "library"
                    },
                    "relations": {
                        "mesh": existing_mesh_relations
                    }
                }
                port.update_entity(blueprint=settings.PORT_REPOSITORY_BLUEPRINT, entity_id=service, body=entity_data)

        port.update_action(run_id, message, action_status)
        return {'status': 'SUCCESS'}

    return {'status': 'SUCCESS'}