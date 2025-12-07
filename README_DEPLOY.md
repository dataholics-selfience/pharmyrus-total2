# Pharmyrus API com Pool SerpAPI

## Deploy

1. Subir no Railway:
```bash
railway up
```

2. Variáveis de ambiente (já configuradas):
```
PORT=8000
```

## Arquivos

- `main.py` - API FastAPI principal
- `serpapi_pool.py` - Pool de keys SerpAPI (9 keys, 250 queries cada)
- `test_pool.py` - Teste do pool

## Endpoints

- `GET /` - Frontend
- `GET /health` - Health check
- `GET /api/v1/search?molecule_name=X` - Busca patentes
- `GET /api/v1/serpapi/status` - Status do pool SerpAPI
- `GET /api/v1/serpapi/key` - Pegar próxima key

## Pool SerpAPI

9 keys, cada uma com 250 queries/mês. Rotação automática.
Reset mensal automático.
Persiste em `/tmp/serpapi_pool.json`.

## Teste

```bash
python test_pool.py
curl http://localhost:8000/api/v1/serpapi/status
```
