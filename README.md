# Pharmyrus API - Deploy Railway

## 🚀 DEPLOY

```bash
# Opção 1: Git
git init
git add .
git commit -m "deploy"
railway link
railway up

# Opção 2: CLI direto
railway up
```

## 📁 ARQUIVOS

- `main.py` - API FastAPI
- `serpapi_pool.py` - Pool de 9 keys SerpAPI
- `requirements.txt` - Dependências
- `Procfile` - Comando de start
- `runtime.txt` - Python 3.11

## ✅ ENDPOINTS

```
GET /health
GET /api/v1/search?molecule_name=Darolutamide
GET /api/v1/serpapi/status
GET /api/v1/serpapi/key
```

## 🔑 POOL SERPAPI

9 keys configuradas:
- 7 disponíveis (1.750 queries/mês)
- 2 zeradas (reset dia 1)
- Rotação automática
- Reset mensal

## 🧪 TESTAR

```bash
# Health
curl https://seu-app.railway.app/health

# Pool status
curl https://seu-app.railway.app/api/v1/serpapi/status

# Busca
curl "https://seu-app.railway.app/api/v1/search?molecule_name=Darolutamide"
```

## ⚙️ VARIÁVEIS (opcional)

```
PORT=8000  # Railway define automaticamente
```

Nenhuma outra variável necessária!
