# DEPLOY IMEDIATO - Pharmyrus API + SerpAPI Pool

## 🚀 DEPLOY RAILWAY (1 comando)

```bash
# Extrair e fazer deploy
tar -xzf pharmyrus-api-serpapi-pool.tar.gz
railway up
```

## ✅ PRONTO!

API rodando com:
- 9 chaves SerpAPI (250 queries cada = 2.250 total/mês)
- Rotação automática quando uma key esgota
- Reset mensal automático no dia 1

## 📊 MONITORAR

```bash
# Status do pool
curl https://SEU-APP.railway.app/api/v1/serpapi/status

# Pegar uma key
curl https://SEU-APP.railway.app/api/v1/serpapi/key
```

## 🔧 USAR NO N8N

Substituir chamadas SerpAPI fixas por:

```javascript
// Antes (hardcoded)
const API_KEY = "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d";

// Depois (pool)
const response = await fetch("https://SEU-APP.railway.app/api/v1/serpapi/key");
const { key } = await response.json();
// usar key nas chamadas SerpAPI
```

## 📁 ARQUIVOS

- `main.py` - API com pool integrado
- `serpapi_pool.py` - Gerenciador de keys
- `requirements.txt` - Dependências
- `start.sh` - Startup script

## ⚙️ KEYS NO POOL

1. daniel.mendes (250 usadas - zerada)
2. innovagenoi2 ✅
3. innovagenoi3 ✅  
4. Keith ✅
5. LG (250 usadas - zerada)
6. Keith Clínica ✅
7. Dona Deny ✅
8. JoJo ✅
9. Nova ✅

**7 keys disponíveis = 1.750 queries disponíveis**

Reset automático: dia 1 de cada mês
