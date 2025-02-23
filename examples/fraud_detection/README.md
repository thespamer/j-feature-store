# Exemplo de Detecção de Fraude em Cartão de Crédito

Este exemplo demonstra como utilizar o Feature Store para implementar um sistema de detecção de fraude em tempo real para transações de cartão de crédito.

## Visão Geral

O sistema implementa três padrões principais de fraude:

1. **Múltiplas Transações Pequenas Seguidas de Uma Grande**
   - Fraudadores frequentemente testam cartões com pequenas transações antes de fazer uma grande compra
   - O sistema detecta sequências de 3-7 transações pequenas (€1-€20) seguidas de uma grande (€500-€2000)

2. **Transações em Diferentes Países em Curto Período**
   - Detecta uso do cartão em diferentes países em um intervalo curto de tempo
   - Alerta quando há 2-4 transações em países diferentes dentro de 1 hora

3. **Tentativas Repetidas com Pequenas Variações**
   - Identifica tentativas repetidas de transação com pequenas variações no valor
   - Comum em ataques automatizados que tentam encontrar limites de aprovação

## Componentes

### 1. Transaction Simulator (`transaction_simulator.py`)
- Gera dados sintéticos de transações
- Simula tanto transações legítimas quanto fraudulentas
- Útil para testes e desenvolvimento

### 2. Feature Engineering (`feature_engineering.py`)
- Calcula features em tempo real para cada transação
- Utiliza histórico de transações do cartão
- Features incluem:
  - Contagens de transações
  - Estatísticas de valores
  - Padrões geográficos
  - Velocidade de transações

### 3. Fraud Detector (`fraud_detector.py`)
- Serviço de detecção em tempo real
- Combina modelo ML com regras de negócio
- Fornece scores de risco e explicações

## Como Usar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o simulador para gerar dados:
```bash
python transaction_simulator.py
```

3. Execute o detector de fraude:
```bash
python fraud_detector.py
```

## Features Calculadas

- `tx_count_1h`: Número de transações na última hora
- `total_amount_1h`: Valor total de transações na última hora
- `avg_amount_1h`: Valor médio das transações
- `std_amount_1h`: Desvio padrão dos valores
- `unique_countries_1h`: Número de países únicos
- `unique_merchants_1h`: Número de comerciantes únicos
- `amount_velocity`: Velocidade de mudança nos valores
- `small_tx_ratio`: Proporção de transações pequenas
- `country_change_ratio`: Taxa de mudança de países
- `small_amount_variations`: Detecção de variações pequenas nos valores

## Níveis de Risco

- **Alto**: Score > 0.8 ou padrões de alto risco detectados
- **Médio**: Score > 0.5
- **Baixo**: Score > 0.2
- **Seguro**: Score ≤ 0.2

## Integração com Feature Store

O sistema utiliza o Feature Store para:
1. Armazenar histórico de transações
2. Calcular features em tempo real
3. Armazenar resultados de análises
4. Treinar e atualizar modelos

## Considerações de Segurança

- O sistema implementa detecção de múltiplos padrões de fraude
- Utiliza tanto regras baseadas em conhecimento quanto ML
- Fornece explicações detalhadas para cada alerta
- Permite ajuste fino dos limiares de risco
- Mantém histórico completo para auditoria
