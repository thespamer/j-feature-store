#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando suite de testes...${NC}"

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Verificar formatação e estilo
echo -e "\n${YELLOW}Verificando formatação com black...${NC}"
black --check backend/
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro na formatação do código${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Verificando imports com isort...${NC}"
isort --check-only backend/
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro na ordenação dos imports${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Verificando estilo com flake8...${NC}"
flake8 backend/
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro nas regras de estilo${NC}"
    exit 1
fi

# Verificar tipos
echo -e "\n${YELLOW}Verificando tipos com mypy...${NC}"
mypy backend/
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro na verificação de tipos${NC}"
    exit 1
fi

# Testes unitários
echo -e "\n${YELLOW}Executando testes unitários...${NC}"
pytest backend/tests/unit -v --cov=backend/app --cov-report=term-missing
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha nos testes unitários${NC}"
    exit 1
fi

# Testes de integração
echo -e "\n${YELLOW}Executando testes de integração...${NC}"
pytest backend/tests/integration -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha nos testes de integração${NC}"
    exit 1
fi

# Testes E2E
echo -e "\n${YELLOW}Executando testes E2E...${NC}"
docker compose -f docker-compose.yml -f e2e/docker-compose.e2e.yml up --build e2e-tests
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha nos testes E2E${NC}"
    exit 1
fi

# Testes de Performance
echo -e "\n${YELLOW}Executando testes de performance...${NC}"
locust -f backend/tests/locustfile.py --headless -u 100 -r 10 --run-time 1m
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha nos testes de performance${NC}"
    exit 1
fi

# Testes de Segurança
echo -e "\n${YELLOW}Executando testes de segurança...${NC}"
pytest backend/tests/security -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Falha nos testes de segurança${NC}"
    exit 1
fi

echo -e "\n${GREEN}Todos os testes passaram com sucesso!${NC}"
