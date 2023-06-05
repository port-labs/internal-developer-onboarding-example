# Internal Developer Portal Onboarding Example

Port is the Developer Platform meant to supercharge your DevOps and Developers, and allows you to regain control of your environment.


## Description

The following example helps internal developer teams to onboard new members into their workspace.

This example consists of a FastAPI backend, that listen for Port Action Webhook events.

For each event, the backend creates new Port Entity for `meshTeam`, assigns the team to an internal group blueprint (`mesh_group`), grants the newly created team access to the organization's services and libraries repository blueprint (`microservice`).

Finally, the backend updates Port Action run.

## Table of Contents
1. [Local Setup](#Localhost)
2. [Webhook Setup](#Webhook)
3. [Port Setup](#Port)


## Setup

### Localhost

1. Make sure that the Docker daemon is available and running
```
$ docker info
```

2. Create `.env` file with the required environment variables
```
$ cat .env

PORT_CLIENT_ID=<PORT_CLIENT_ID>
PORT_CLIENT_SECRET=<PORT_CLIENT_SECRET>
```

3. Build example's Docker image
```
$ docker build -t getport.io/port-idp-webhook-example .
```

4. Run example's Docker image with `.env`

To change the default port (`80`) to `8080` for example, replace command's flags with the following: `-p 80:8080 -e PORT="8080"`
```
$ docker run -d --name getport.io-port-idp-webhook-example -p 80:80 --env-file .env getport.io/getport.io/port-idp-webhook-example
```

5. Verify that the Docker container is up and running, and ready to listen for new webhooks:
```
$ docker logs -f getport.io-port-idp-webhook-example

...
[2023-04-18 12:17:17 +0000] [1] [INFO] Starting gunicorn 20.1.0
[2023-04-18 12:17:17 +0000] [1] [INFO] Listening at: http://0.0.0.0:80 (1)
[2023-04-18 12:17:17 +0000] [1] [INFO] Using worker: uvicorn.workers.UvicornWorker
[2023-04-18 12:17:17 +0000] [10] [INFO] Booting worker with pid: 10
...
[2023-04-18 12:17:19 +0000] [18] [INFO] Application startup complete.
```

`docker logs -f` command follows log output, and helps you also to troubleshoot future action runs.

### Webhook

1. Create public URL for your local application. 

In this tutorial, we create a new channel in [smee.getport.io](https://smee.getport.io/), and use provided `Webhook Proxy URL`. 

2. Install the Smee client:
```
$ pip install pysmee
```

3. Use installed `pysmee` client to forward the events to your localhost API URL (replace `<SMEE_WEBHOOK_PROXY_URL>`):
```
pysmee forward <SMEE_WEBHOOK_PROXY_URL> http://localhost:80/api/service
```

### Port

1. Create `mesh_group` blueprint:
```
{
  "identifier": "mesh_group",
  "title": "Mesh Group",
  "icon": "TwoUsers",
  "schema": {
    "properties": {},
    "required": []
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "relations": {}
}
```

2. Create `meshTeam` blueprint:
```
{
  "identifier": "meshTeam",
  "title": "Mesh Team",
  "icon": "TwoUsers",
  "schema": {
    "properties": {},
    "required": []
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "relations": {
    "group_name": {
      "title": "Group Name",
      "target": "mesh_group",
      "required": false,
      "many": false
    }
  }
}
```

3. Create `microservice` blueprint:
```
{
  "identifier": "microservice",
  "title": "Repository",
  "icon": "Service",
  "schema": {
    "properties": {
      "description": {
        "type": "string",
        "title": "Description"
      },
      "url": {
        "type": "string",
        "format": "url",
        "title": "URL"
      },
      "type": {
        "title": "type",
        "type": "string",
        "enum": [
          "library",
          "service"
        ],
        "enumColors": {
          "library": "blue",
          "service": "turquoise"
        }
      }
    },
    "required": []
  },
  "mirrorProperties": {
    "coverage": {
      "title": "coverage",
      "path": "sonar_qube_project.coverage"
    }
  },
  "calculationProperties": {},
  "relations": {
    "produces": {
      "title": "Produces",
      "target": "event",
      "required": false,
      "many": true
    },
    "group": {
      "title": "Group",
      "target": "gitlab_groups",
      "required": false,
      "many": false
    },
    "mesh": {
      "title": "Mesh",
      "target": "meshTeam",
      "required": false,
      "many": true
    },
    "snyk_project": {
      "title": "Snyk Project",
      "target": "snyk_projects",
      "required": false,
      "many": false
    },
    "consumes": {
      "title": "Consumes",
      "target": "event",
      "required": false,
      "many": true
    },
    "sonar_qube_project": {
      "title": "Sonar Qube Project",
      "target": "sonarCloudAnalysis",
      "required": false,
      "many": false
    }
  }
}
```

5. Follow the [Port documentation](https://docs.getport.io/build-your-software-catalog/sync-data-to-catalog/webhook/examples/) to create the necessary blueprints such as `sonarCloudAnalysis`, `snyk_projects` etc.


6. Create new actions for blueprint (replace instances of `<WEBHOOK_URL>` with your smee proxy URL):

```
[
  {
    "id": "action_wqQOtDbUc9VQM77F",
    "identifier": "onBoard",
    "title": "On Board Mesh Team",
    "userInputs": {
      "properties": {
        "meshTeamName": {
          "type": "string",
          "title": "Mesh Team Name"
        },
        "meshGroup": {
          "type": "string",
          "format": "entity",
          "blueprint": "mesh_group",
          "title": "Mesh Group"
        },
        "services": {
          "type": "array",
          "icon": "GitLab",
          "items": {
            "format": "entity",
            "blueprint": "microservice",
            "type": "string"
          },
          "title": "Services"
        },
        "libraries": {
          "type": "array",
          "items": {
            "format": "entity",
            "blueprint": "microservice",
            "type": "string"
          },
          "title": "Libraries"
        },
        "integrations": {
          "type": "object",
          "default": {
            "serviceA": {
              "snyk_project": "SNYK_PROJECT__ID",
              "sonar_qube_project": "SONAR_QUBE_PROJECT_ID"
            }
          },
          "patternProperties": {
            "^[A-Za-z0-9@_=\\-]*$": {
              "type": "object",
              "properties": {
                "snyk_project": {
                  "type": "string"
                },
                "sonar_qube_project": {
                  "type": "string"
                }
              }
            }
          }
        }
      },
      "required": []
    },
    "invocationMethod": {
      "type": "WEBHOOK",
      "url": "<WEBHOOK_URL>"
    },
    "trigger": "CREATE",
    "description": "On board your group into Organization's Developer Portal",
    "requiredApproval": false
  }
]
```

7. Run the action with some input:
```
{
  "meshTeamName": "Platforms Engineering Team",
  "meshGroup": "e_WnA2Mllw89JN87RT",
  "services": [
    "e_bvVotgt6e7fP8g4U"
  ],
  "integrations": {
    "e_bvVotgt6e7fP8g4U": {
      "snyk_project": "SNYK_PROJECT_ID",
      "sonar_qube_project": "SONAR_QUBE_PROJECT_ID"
    }
  }
}
```

8. Verify status and outcome of the action run in Port (run status in audit logs, new entities, ...).