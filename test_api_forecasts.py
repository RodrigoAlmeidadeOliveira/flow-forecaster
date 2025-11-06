#!/usr/bin/env python3
"""
Script de teste para verificar o endpoint /api/forecasts
"""
import requests

BASE_URL = "https://flow-forecaster.fly.dev"

# Login
print("=== LOGIN ===")
session = requests.Session()
response = session.post(f"{BASE_URL}/login", data={
    'email': 'rodrigoalmeidadeoliveira@gmail.com',
    'password': input("Digite sua senha: ")
})

if response.status_code == 200:
    print("✓ Login bem-sucedido")
else:
    print(f"✗ Erro no login: {response.status_code}")
    print(response.text[:500])
    exit(1)

# Verificar /api/forecasts
print("\n=== GET /api/forecasts ===")
response = session.get(f"{BASE_URL}/api/forecasts")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    forecasts = response.json()
    print(f"Total de forecasts retornados: {len(forecasts)}")

    if len(forecasts) == 0:
        print("⚠️ PROBLEMA: API retornou lista vazia!")
        print("Mas o banco tem 9 forecasts...")
    else:
        print("\nForecasts encontrados:")
        for f in forecasts:
            print(f"  - ID: {f['id']}, Nome: {f['name']}, Project: {f['project_id']}")
else:
    print(f"✗ Erro na API: {response.status_code}")
    print(response.text[:500])

# Verificar /api/projects
print("\n=== GET /api/projects ===")
response = session.get(f"{BASE_URL}/api/projects")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    projects = response.json()
    print(f"Total de projects retornados: {len(projects)}")
    if len(projects) > 0:
        print("\nProjects encontrados:")
        for p in projects:
            print(f"  - ID: {p['id']}, Nome: {p['name']}")
else:
    print(f"✗ Erro na API: {response.status_code}")
