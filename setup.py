# Databricks notebook source
# MAGIC %pip install -r requirements.txt
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import os
import yaml
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import pipelines
from databricks.sdk.service.catalog import VolumeType, SecurableType, PermissionsChange, Privilege 
from databricks.sdk.service.pipelines import PipelineLibrary, NotebookLibrary
from databricks.sdk.service.apps import AppAccessControlRequest, AppPermissionLevel

# COMMAND ----------

dbutils.widgets.text("catalog", "", "Catalog")

w = WorkspaceClient()

# Create Catalog
catalog_name = dbutils.widgets.get("catalog")

if not catalog_name:
    raise ValueError("Catalog cannot be empty or None")

try:
    catalog = w.catalogs.get(catalog_name)
    print(f"Catalog {catalog_name} already exists")
except Exception as e:
    w.catalogs.create(catalog_name)
    print(f"Catalog {catalog_name} created") #assumes user owns the catalog

# Create Schema
try:
    schema = w.schemas.get(f"{catalog_name}.dino_game")
    print(f"Schema dino_game already exists")
except Exception as e:
    w.schemas.create("dino_game",catalog_name)
    print(f"Schema dino_game created")

# Create Volume
if any(v.name == "games" for v in list(w.volumes.list(catalog_name=catalog_name, schema_name="dino_game"))):
    print(f"Volume games already exists")
else:
    w.volumes.create(catalog_name, "dino_game", "games", volume_type=VolumeType.MANAGED)
    print(f"Volume dino_game created")

# Create Pipeline
pipeline_name = f"{str.lower(catalog_name)}_dino_game"

if any(
    p.name == pipeline_name
    for p in w.pipelines.list_pipelines(filter=f"name LIKE '{pipeline_name}'")
):
    print(f"Pipeline {pipeline_name} already exists")
else:
    w.pipelines.create(
        name=pipeline_name,
        catalog=catalog_name,
        target="dino_game",
        serverless=True,
        continuous=False,
        libraries=[
            PipelineLibrary(
                notebook=NotebookLibrary(
                    path="/Users/daniel.brookes@databricks.com/dbrookes-dino-game/notebooks/games_dlt"  # TODO: Improve the notebook path
                )
            )
        ],
    )
    print(f"Pipeline {pipeline_name} created")

# Create Dashboard
dashboard_template = open("./dashboard/dino_game_leaderboard.lvdash.json").read()

try:
    w.lakeview.create(
        display_name="🦖 Dino Game",
        serialized_dashboard=dashboard_template,
        parent_path=f"{os.getcwd()}/dashboard",
    )
    print("Dashboard created")
except Exception as e:
    if "already exists" in str(e):
        print("Dashboard 🦖 Dino Game already exists")
    else:
        raise e

# Create App
app_name = f"{str.lower(catalog_name)}-dino-game"

try:
    app = w.apps.get(app_name)
    print(f"App {app_name} already exists")
except:
    w.apps.create_and_wait(app_name,description="A clone of the popular Chrome Dino Game")

# Deploy App
yaml_file_path = os.path.join(os.getcwd(), 'app.yaml')

with open(yaml_file_path, 'r') as file:
    config = yaml.safe_load(file)

for env_var in config['env']:
    if env_var['name'] == 'CATALOG':
        env_var['value'] = catalog_name
        
with open(yaml_file_path, 'w') as file:
    yaml.dump(config, file, default_flow_style=False)

deployment_response = w.apps.deploy_and_wait(
    app_name = app_name,
    source_code_path = f"{os.getcwd()}",
)

if deployment_response.status.state.value == "SUCCEEDED":
  print(f"App {app_name} deployed successfully")
else:
  print(f"App {app_name} deployment failed")

# Grant permissions
app_sp = w.service_principals.get(app.service_principal_id) # the value returned is a shortform ID which isnt the same as the application_id which grants.update needs
w.grants.update(SecurableType.VOLUME, app_name, changes=[PermissionsChange(principal=app_sp.application_id, add=[Privilege.READ_VOLUME, Privilege.WRITE_VOLUME])])
# Add user permissions for all account users
w.apps.set_permissions(app_name, access_control_list=[AppAccessControlRequest(group_name='account users', permission_level=AppPermissionLevel.CAN_USE)])