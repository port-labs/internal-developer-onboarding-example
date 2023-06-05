import logging
from fastapi import APIRouter, Depends

from app.core import port
from app.core.config import settings
from app.schemas.webhook_schema import Webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/service", dependencies=None)
async def handle_create_service_webhook(webhook: Webhook):
    logger.info(f"Webhook body: {webhook}")

    action_type = webhook.payload['action']['trigger']
    action_identifier = webhook.payload['action']['identifier']
    properties = webhook.payload['properties']
    integrations = properties['integrations']

    run_id = webhook.context.runId

    if action_type == 'CREATE':
        logger.info(f"{action_identifier} - onboard new team")

        # Create Mesh Team and Connect it to Group
        mesh_team_entity_identifier = properties["meshTeamName"].lower().replace(
            " ", "_")
        entity_data = {
            "identifier": mesh_team_entity_identifier,
            "title": properties["meshTeamName"],
            "properties": {},
            "relations": {
                "group_name": properties["meshGroup"]
            }
        }
        create_response = port.create_entity(
            blueprint=settings.PORT_SERVICE_MESH_TEAM_BLUEPRINT, body=entity_data, run_id=run_id)
        action_status = 'SUCCESS' if 200 <= create_response.status_code <= 299 else 'FAILURE'
        message = f"Message after creating entity is {action_status}"

        # Proceed to grant this newly created team access to the Repository
        if action_status == 'SUCCESS':
            relation_items = ["services", "libraries"]
            relation_map = {"services": "service", "libraries": "library"}

            for item_type in relation_items:
                if item_type in properties.keys():

                    # Add this new team to all selected services and libraries repository
                    for entity_identifier in properties[item_type]:
                        repository_entity_data = port.get_entity(
                            blueprint=settings.PORT_REPOSITORY_BLUEPRINT, entity_id=entity_identifier)

                        # Retrieve existing mesh relations and append the new team to the existing mesh relations
                        existing_mesh_relations = repository_entity_data["relations"].get("mesh", [
                        ])
                        existing_mesh_relations.append(
                            mesh_team_entity_identifier)

                        # Update the entity data with the new property type and mesh relations
                        entity_data = {
                            "properties": {
                                "type": relation_map[item_type]
                            },
                            "relations": {
                                "mesh": existing_mesh_relations
                            }
                        }

                        # Create Snyk and SonarQube relation for each service/library repository
                        service_integrations = integrations.get(
                            entity_identifier)
                        if service_integrations:
                            entity_data["relations"].update(
                                service_integrations)

                        # Update the entity with the modified data
                        port.update_entity(blueprint=settings.PORT_REPOSITORY_BLUEPRINT,
                                           entity_id=entity_identifier, body=entity_data, run_id=run_id)

        port.update_action(run_id, message, action_status)
        return {'status': action_status}

    return {'status': 'SUCCESS'}
