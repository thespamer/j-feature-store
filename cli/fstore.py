#!/usr/bin/env python
import click
import requests
import json
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

console = Console()

def get_api_url() -> str:
    return "http://localhost:8000"

@click.group()
def cli():
    """Feature Store CLI - Gerencie suas features via linha de comando."""
    pass

@cli.group()
def features():
    """Comandos relacionados a features."""
    pass

@cli.group()
def groups():
    """Comandos relacionados a grupos de features."""
    pass

@features.command()
@click.option('--name', required=True, help='Nome da feature')
@click.option('--type', required=True, help='Tipo da feature (numerical/categorical/temporal)')
@click.option('--entity-id', required=True, help='ID da entidade')
@click.option('--description', help='Descrição da feature')
@click.option('--group-id', help='ID do grupo da feature')
def create(name: str, type: str, entity_id: str, description: str = None, group_id: str = None):
    """Criar uma nova feature."""
    data = {
        "name": name,
        "type": type,
        "entity_id": entity_id,
        "description": description,
        "feature_group_id": group_id
    }
    
    response = requests.post(f"{get_api_url()}/api/v1/features", json=data)
    if response.status_code == 200:
        feature = response.json()
        console.print("[green]Feature criada com sucesso![/green]")
        _display_feature(feature)
    else:
        console.print(f"[red]Erro ao criar feature: {response.text}[/red]")

@features.command()
@click.option('--entity-id', help='Filtrar por entity_id')
def list(entity_id: str = None):
    """Listar features."""
    params = {"entity_id": entity_id} if entity_id else {}
    response = requests.get(f"{get_api_url()}/api/v1/features", params=params)
    
    if response.status_code == 200:
        features = response.json()
        table = Table(title="Features")
        table.add_column("ID")
        table.add_column("Nome")
        table.add_column("Tipo")
        table.add_column("Entidade")
        table.add_column("Grupo")
        
        for feature in features:
            table.add_row(
                feature["id"],
                feature["name"],
                feature["type"],
                feature["entity_id"],
                feature.get("feature_group_id", "-")
            )
        
        console.print(table)
    else:
        console.print(f"[red]Erro ao listar features: {response.text}[/red]")

@features.command()
@click.argument('feature_id')
def show(feature_id: str):
    """Mostrar detalhes de uma feature."""
    response = requests.get(f"{get_api_url()}/api/v1/features/{feature_id}")
    
    if response.status_code == 200:
        feature = response.json()
        _display_feature(feature)
    else:
        console.print(f"[red]Erro ao buscar feature: {response.text}[/red]")

@features.command()
@click.argument('feature_id')
@click.argument('entity_id')
@click.argument('value', type=float)
def store_value(feature_id: str, entity_id: str, value: float):
    """Armazenar um valor para uma feature."""
    data = {
        "entity_id": entity_id,
        "value": value
    }
    
    response = requests.post(
        f"{get_api_url()}/api/v1/features/{feature_id}/values",
        json=data
    )
    
    if response.status_code == 200:
        console.print("[green]Valor armazenado com sucesso![/green]")
    else:
        console.print(f"[red]Erro ao armazenar valor: {response.text}[/red]")

def _display_feature(feature: Dict[str, Any]):
    """Exibir detalhes de uma feature."""
    table = Table(title=f"Feature: {feature['name']}")
    table.add_column("Campo")
    table.add_column("Valor")
    
    for key, value in feature.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, indent=2)
        table.add_row(key, str(value))
    
    console.print(table)

if __name__ == '__main__':
    cli()
