import click
from rich.console import Console
from rich.table import Table
import odscli.sdk.token_utils as token_utils
import requests
from odscli.sdk.constants import ODS_PROTOCOL, OPTIMIZER, OPTIMIZER_CONFIG
console = Console()

@click.group('optimizer_cli')
@click.pass_context
def optimizer_cli():
    pass

# optimizer

@optimizer_cli.group('optimizer')
def optimizer():
    pass

@optimizer.command('ls')
@click.argument('model_type',
                type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']))
@click.option('--owner_id', '-o', type=str, required=True, help='Owner ID for the optimizers')
def list_optimizers(model_type, owner_id):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER}/list"
    
    params = {
        "ownerId": owner_id,
        "model_type": model_type.upper()
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        optimizer_table = Table()
        optimizer_table.add_column("Model Name")
        optimizer_table.add_column("Model Type")
        
        for optimizer in response.json():
            optimizer_table.add_row(optimizer, model_type.upper())
        
        console.print(optimizer_table)
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")

@optimizer.command('rm')
@click.argument('model_name')
@click.option('--model_type', '-t', 
              type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']), 
              required=True)
@click.option('--owner_id', '-o', type=str, required=True)
def delete_optimizer(model_name, model_type, owner_id):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER}/rm"
    
    params = {
        "ownerId": owner_id,
        "modelName": model_name,
        "model_type": model_type.upper()
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, params=params, headers=headers)
    
    if response.status_code == 200:
        console.print(f"[green]Successfully deleted optimizer {model_name}")
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")

@optimizer.command('upload')
@click.argument('model_name')
@click.option('--model_type', '-t', 
              type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']), 
              required=True)
@click.option('--owner_id', '-o', type=str, required=True)
@click.option('--file_path', '-f', type=click.Path(exists=True), required=True)
def upload_optimizer(model_name, model_type, owner_id, file_path):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER}/upload"
    
    params = {
        "modelName": model_name,
        "modelType": model_type.upper(),
        "ownerId": owner_id
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, params=params, headers=headers, files=files)
    
    if response.status_code == 200:
        console.print(f"[green]Successfully uploaded optimizer {model_name}")
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")

@optimizer.command('download')
@click.argument('model_name')
@click.option('--model_type', '-t', 
              type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']), 
              required=True)
@click.option('--owner_id', '-o', type=str, required=True)
@click.option('--output', '-out', type=click.Path(), required=True)
def download_optimizer(model_name, model_type, owner_id, output):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER}/download"
    
    params = {
        "ownerId": owner_id,
        "modelName": model_name,
        "modelType": model_type.upper()
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        with open(output, 'wb') as f:
            f.write(response.content)
        console.print(f"[green]Successfully downloaded optimizer to {output}")
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")


# Optimizer Config

@optimizer_cli.group('optimizer_config')
def optimizer_config():
    pass

@optimizer_config.command('create')
@click.argument('config_name')
@click.option('--model_type', '-t', 
              type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']), 
              required=True)
@click.option('--owner_id', '-o', type=str, required=True)
@click.option('--config_file', '-f', type=click.Path(exists=True), required=True)
def create_config(config_name, model_type, owner_id, config_file):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER_CONFIG}/"
    
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    config_data['modelType'] = model_type.upper()
    config_data['configName'] = config_name
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=config_data, headers=headers, params={"owner_id": owner_id})
    
    if response.status_code == 200:
        console.print(f"[green]Successfully created configuration {config_name}")
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")

@optimizer_config.command('ls')
@click.option('--model_type', '-t', 
              type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']), 
              required=True)
@click.option('--owner_id', '-o', type=str, required=True)
def list_configs(model_type, owner_id):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER_CONFIG}/list"
    
    params = {
        "model_type": model_type.upper(),
        "owner_id": owner_id
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        config_table = Table()
        config_table.add_column("Config Name")
        config_table.add_column("Model Type")
        
        for config in response.json():
            config_table.add_row(config, model_type.upper())
        
        console.print(config_table)
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")

@optimizer_config.command('get')
@click.argument('config_name')
@click.option('--model_type', '-t', 
              type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']), 
              required=True)
@click.option('--owner_id', '-o', type=str, required=True)
def get_config(config_name, model_type, owner_id):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER_CONFIG}/"
    
    params = {
        "config_name": config_name,
        "model_type": model_type.upper(),
        "owner_id": owner_id
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        config_data = response.json()
        console.print(json.dumps(config_data, indent=2))
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")

@optimizer_config.command('rm')
@click.argument('config_name')
@click.option('--model_type', '-t', 
              type=click.Choice(['ddpg', 'dqn', 'ppo', 'bo']), 
              required=True)
@click.option('--owner_id', '-o', type=str, required=True)
def delete_config(config_name, model_type, owner_id):
    host, user, token = token_utils.readConfig()
    url = f"{ODS_PROTOCOL}{host}{OPTIMIZER_CONFIG}/"
    
    params = {
        "config_name": config_name,
        "model_type": model_type.upper(),
        "owner_id": owner_id
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, params=params, headers=headers)
    
    if response.status_code == 200:
        console.print(f"[green]Successfully deleted configuration {config_name}")
    else:
        console.print(f"[red]Error: {response.status_code} - {response.text}")