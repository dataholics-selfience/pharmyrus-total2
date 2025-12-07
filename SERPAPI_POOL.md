# SerpAPI Pool Manager - Pharmyrus v4.0

## 🎯 Overview

Sistema inteligente de gerenciamento de pool de API keys da SerpAPI com:

- ✅ **9 API keys** com 250 queries cada = **2.250 queries/mês**
- ✅ **Rotação automática** quando uma key atinge o limite
- ✅ **Renovação mensal** baseada em data configurável
- ✅ **Persistência de estado** em arquivo JSON
- ✅ **Thread-safe** com locks para concorrência
- ✅ **Endpoints REST** para monitoramento em tempo real

## 📊 Pool de Keys

| Instância | Email | Limite | Status Inicial |
|-----------|-------|--------|----------------|
| Instância 1 | daniel.mendes@dataholics.io | 250 | ✅ Ativa |
| Instância 2 | innovagenoi2@gmail.com | 250 | ✅ Ativa |
| Instância 3 | innovagenoi3@gmail.com | 250 | ✅ Ativa |
| Instância 4 (Keith) | innovagenoi@gmail.com | 250 | ✅ Ativa |
| Instância 5 (LG) | innovagenoi4@gmail.com | 0 | ❌ Zerada |
| Instância 6 (Keith Clínica) | innovagenoi5@gmail.com | 250 | ✅ Ativa |
| Instância 7 (Dona Deny) | innovagenoi6@gmail.com | 250 | ✅ Ativa |
| Instância 8 (JoJo) | innovagenoi7@gmail.com | 250 | ✅ Ativa |
| Instância 9 | innovagenoi7@gmail.com | 250 | ✅ Ativa |

**Total disponível inicial:** 2.000 queries (8 keys ativas × 250)

## 🚀 Quick Start

### 1. Instalação

```bash
pip install -r requirements.txt
```

### 2. Iniciar API

```bash
# Desenvolvimento
python main.py

# Produção (Railway)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. Testar Pool

```bash
# Testes básicos
python test_serpapi_pool.py

# Testes completos (inclui busca de molécula)
python test_serpapi_pool.py --full

# Customizar URL
python test_serpapi_pool.py --url https://pharmyrus-api.up.railway.app
```

## 📡 API Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "4.0.0",
  "features": {
    "serpapi_pool": true,
    "total_keys": 9,
    "total_monthly_queries": 2250
  },
  "timestamp": "2025-12-07T..."
}
```

### Pool Status (Detalhado)

```http
GET /api/v1/serpapi/status
```

**Response:**
```json
{
  "total_keys": 9,
  "total_requests_made": 42,
  "total_available_queries": 1958,
  "total_used_queries": 42,
  "total_limit": 2000,
  "usage_percentage": 2.1,
  "keys": [
    {
      "instance": "Instância 1",
      "email": "daniel.mendes@dataholics.io",
      "used": 10,
      "limit": 250,
      "remaining": 240,
      "status": "active",
      "last_used": "2025-12-07T...",
      "last_renewal": "2025-12-07T..."
    },
    // ... outras keys
  ],
  "last_check": "2025-12-07T..."
}
```

### Usage Summary (Simplificado)

```http
GET /api/v1/serpapi/usage
```

**Response:**
```json
{
  "pool_info": {
    "total_keys": 9,
    "total_limit": 2000,
    "total_available": 1958,
    "usage_percentage": 2.1
  },
  "current_status": {
    "requests_made": 42,
    "queries_used": 42,
    "queries_remaining": 1958
  },
  "health": "healthy",
  "last_check": "2025-12-07T..."
}
```

### Get Next Key (Para Testes)

```http
GET /api/v1/serpapi/key
```

**Response (Success):**
```json
{
  "success": true,
  "key": "11e7b23032aae12b0f75c06af0ad60a861e9f7ea6d53fc7ca039aed18b5e3573",
  "message": "Key obtained successfully"
}
```

**Response (All Exhausted):**
```json
{
  "success": false,
  "key": null,
  "message": "All keys exhausted - waiting for monthly renewal"
}
```

### Reset Specific Key (Dev/Testing)

```http
POST /api/v1/serpapi/reset/{key_substring}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/serpapi/reset/11e7b230
```

**Response:**
```json
{
  "success": true,
  "message": "Key 11e7b230... reset successfully",
  "key": "11e7b23032aae12b0f..."
}
```

### Reset All Keys (Dev/Testing)

```http
POST /api/v1/serpapi/reset-all
```

⚠️ **CUIDADO:** Reseta todas as keys do pool!

**Response:**
```json
{
  "success": true,
  "message": "All keys reset successfully",
  "total_keys": 9
}
```

## 🔄 Funcionamento

### 1. Rotação Automática

Quando você solicita uma key via `get_serpapi_key()`:

1. O pool verifica qual foi a última key usada
2. Busca a próxima key disponível (com queries restantes)
3. Incrementa o contador de uso
4. Persiste o estado em `serpapi_state.json`
5. Retorna a key

Se a key atingir o limite (250 queries):
- Status muda para `"exhausted"`
- Pool passa automaticamente para a próxima key

### 2. Renovação Mensal

Todas as keys têm `renewal_day: 7` (dia 7 de cada mês).

Quando o pool detecta que é dia 7 e o mês mudou:
- Reseta contador `used` para 0
- Restaura `limit` para 250
- Atualiza `last_renewal` para a data atual
- Status volta para `"active"`

### 3. Persistência

O estado é salvo em `serpapi_state.json`:

```json
{
  "keys": {
    "11e7b230...": {
      "email": "daniel.mendes@dataholics.io",
      "instance": "Instância 1",
      "used": 42,
      "limit": 250,
      "renewal_day": 7,
      "last_renewal": "2025-12-07T...",
      "last_used": "2025-12-07T...",
      "status": "active"
    }
  },
  "last_used_index": 0,
  "total_requests": 42
}
```

## 💻 Uso Programático

### Python (dentro da API)

```python
from serpapi_pool import get_serpapi_key, get_serpapi_status

# Obter uma key
api_key = get_serpapi_key()
if api_key:
    # Usar key em requisição
    params = {
        "engine": "google",
        "q": "Darolutamide patent WO",
        "api_key": api_key
    }
    response = requests.get("https://serpapi.com/search.json", params=params)
else:
    # Todas as keys esgotadas
    print("Aguardando renovação mensal...")

# Verificar status
status = get_serpapi_status()
print(f"Queries disponíveis: {status['total_available_queries']}")
```

### cURL (via API REST)

```bash
# Status do pool
curl http://localhost:8000/api/v1/serpapi/status

# Resumo de uso
curl http://localhost:8000/api/v1/serpapi/usage

# Obter uma key
curl http://localhost:8000/api/v1/serpapi/key

# Resetar key específica (dev)
curl -X POST http://localhost:8000/api/v1/serpapi/reset/11e7b230

# Resetar todas (dev)
curl -X POST http://localhost:8000/api/v1/serpapi/reset-all
```

## 📈 Monitoramento

### Dashboard Recomendado

Crie um dashboard que monitore:

1. **Queries Disponíveis**: `GET /api/v1/serpapi/usage`
2. **Taxa de Uso**: `usage_percentage` do status
3. **Alertas**:
   - `< 500 queries`: ⚠️ Warning
   - `< 100 queries`: 🚨 Critical
   - `= 0 queries`: ❌ Exhausted

### Logs

O pool gera logs informativos:

```
INFO:__main__:🔑 Key fornecida: Instância 1 | Usado: 42/250 | Restante: 208
INFO:__main__:⚠️ Key esgotada: Instância 5 (LG)
INFO:__main__:🔄 Key renovada: Instância 1 (limite restaurado: 250)
ERROR:__main__:❌ TODAS AS KEYS ESGOTADAS!
```

## 🧪 Testes

### Teste Standalone

```bash
# Roda teste embutido no módulo
python serpapi_pool.py
```

**Output esperado:**
```
============================================================
TESTE DO SERPAPI POOL MANAGER
============================================================

📊 STATUS INICIAL:
Total de keys: 9
Queries disponíveis: 2000
Queries usadas: 0

🧪 SIMULANDO 10 REQUISIÇÕES:
1. Key obtida: 11e7b23032aae12b0f...
2. Key obtida: 11e7b23032aae12b0f...
...

📊 STATUS FINAL:
Total requisições: 10
Queries restantes: 1990
Uso: 0.5%

✅ Teste concluído!
```

### Teste via API

```bash
# Básico
python test_serpapi_pool.py

# Completo
python test_serpapi_pool.py --full
```

## 🔧 Configuração Avançada

### Customizar Renewal Day

Edite `serpapi_pool.py`:

```python
KEYS_POOL = [
    {
        "key": "...",
        "renewal_day": 15  # Renova dia 15 em vez de dia 7
    }
]
```

### Customizar Limite

Para testes, você pode ajustar o limite:

```python
KEYS_POOL = [
    {
        "key": "...",
        "limit": 10  # Limite de teste
    }
]
```

### Múltiplas Instâncias

O pool é **thread-safe** e persiste estado em arquivo, então múltiplas instâncias da API compartilham o mesmo pool automaticamente.

## 🚨 Troubleshooting

### "All keys exhausted"

**Causa**: Todas as 9 keys atingiram o limite de 250 queries.

**Solução**:
1. Aguarde o dia de renovação (dia 7)
2. Para desenvolvimento, use: `POST /api/v1/serpapi/reset-all`

### Key não renova automaticamente

**Causa**: O mês ainda não mudou ou ainda não chegou no `renewal_day`.

**Verificação**:
```python
from datetime import datetime
now = datetime.now()
print(f"Hoje: dia {now.day} de {now.month}")
# Renova apenas se: now.day >= renewal_day E mês diferente da last_renewal
```

### Estado corrompido

**Solução**: Delete o arquivo de estado para recomeçar:
```bash
rm serpapi_state.json
# Reinicie a API - estado será recriado
```

## 📝 Changelog

### v4.0.0 (2025-12-07)
- ✨ Implementação completa do SerpAPI Pool Manager
- ✨ 9 API keys com 2.250 queries/mês total
- ✨ Rotação automática e renovação mensal
- ✨ Endpoints REST para monitoramento
- ✨ Persistência de estado thread-safe
- ✨ Suite de testes completa
- 🔧 Integração no discover_wo() com fallback

## 🤝 Contribuindo

Para adicionar novas keys ao pool:

1. Edite `serpapi_pool.py`
2. Adicione a key em `KEYS_POOL`
3. Configure `renewal_day` apropriado
4. Delete `serpapi_state.json` para reinicializar
5. Reinicie a API

## 📞 Suporte

- 📧 Email: daniel.mendes@dataholics.io
- 🔗 Railway: https://pharmyrus-api.up.railway.app
- 📚 Docs: [QUICKSTART.md](QUICKSTART.md)

## ⚖️ License

Proprietary - Pharmyrus / Dataholics
