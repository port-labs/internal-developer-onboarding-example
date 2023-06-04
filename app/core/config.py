from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "port-idp-onboarding-example"

    VERIFY_WEBHOOK: bool = False

    PORT_API_URL: str = "https://api.getport.io/v1"
    PORT_SERVICE_MESH_TEAM_BLUEPRINT: str = "meshTeam"
    PORT_SERVICE_MESH_GROUP_BLUEPRINT: str = "mesh_group"
    PORT_REPOSITORY_BLUEPRINT: str = "microservice"

    PORT_CLIENT_ID: str
    PORT_CLIENT_SECRET: str

    class Config:
        case_sensitive = True

settings = Settings()
