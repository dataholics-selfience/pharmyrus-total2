# 🚀 PHARMYRUS API v4.2 - DEPLOY PRODUCTION

API completa para busca de patentes farmacêuticas com 4 layers:
- **Layer 1:** PubChem → Dev codes, CAS
- **Layer 2:** WO Discovery → Extrai WOs (igual n8n)
- **Layer 3:** Patent Family → BR, US, JP, CN, EP
- **Layer 4:** Patent Details → Dados completos

---

## ⚡ QUICK START (3 passos)

```bash
# 1. Configure SerpAPI key
cp .env.example .env
# Edite .env e adicione sua SERPAPI_KEY

# 2. Deploy (escolha um método)
chmod +x deploy.sh
./deploy.sh

# 3. Teste
curl http://localhost:8000/health
```

---

## 📦 ARQUIVOS DE DEPLOY

```
pharmyrus-api-v4.2/
├── main_v4_2_production.py    # API principal
├── requirements.txt            # Dependências Python
├── .env.example               # Configuração (copie para .env)
├── Dockerfile                 # Container Docker
├── docker-compose.yml         # Docker Compose
├── railway.json               # Deploy Railway
└── deploy.sh                  # Script de deploy automatizado
```

---

## 🔧 MÉTODOS DE DEPLOY

### 1️⃣ Docker (Recomendado)

```bash
# Build
docker build -t pharmyrus-api:v4.2 .

# Run
docker run -d \
  --name pharmyrus-api \
  -p 8000:8000 \
  -e SERPAPI_KEY=your_key_here \
  --restart unless-stopped \
  pharmyrus-api:v4.2

# Logs
docker logs -f pharmyrus-api
```

**OU use Docker Compose:**
```bash
docker-compose up -d
docker-compose logs -f
```

---

### 2️⃣ Railway

```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up

# Configurar variáveis
railway variables set SERPAPI_KEY=your_key_here
```

**OU use o script:**
```bash
./deploy.sh
# Escolha opção 2
```

---

### 3️⃣ Local (Python)

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar
python3 main_v4_2_production.py
```

**OU use o script:**
```bash
./deploy.sh
# Escolha opção 3
```

---

### 4️⃣ Systemd (Linux Service)

```bash
./deploy.sh
# Escolha opção 4

# Gerenciar serviço
sudo systemctl status pharmyrus
sudo systemctl restart pharmyrus
sudo journalctl -u pharmyrus -f
```

---

## 🧪 TESTES PRÉ-DEPLOY

### 1. Testar SerpAPI Keys
```bash
python3 test_multiple_keys.py
```

**Resultado esperado:**
```
✅ SUCESSO! Key funcionando encontrada
WOs encontrados: 5
```

---

### 2. Testar Extração de WOs
```bash
python3 test_wo_extraction.py
```

**Resultado esperado:**
```
✅ SUCESSO: 15 WOs encontrados
✅ EXCELENTE! 10+ WOs encontrados
```

---

### 3. Testar API Completa
```bash
# Terminal 1: Inicia API
python3 main_v4_2_production.py

# Terminal 2: Testa endpoint
curl 'http://localhost:8000/api/v1/search?molecule_name=darolutamide' | jq .
```

**Validação:**
- `layer2_wo_discovery.wo_numbers_found` ≥ 10 ✅
- `layer3_patent_family.patents_by_country.BR` ≥ 6 ✅
- `comparison_br.match_rate` ≥ 70% ✅
- `comparison_br.status` = "Excellent" ✅

---

## 📍 ENDPOINTS

### Health Check
```bash
GET http://localhost:8000/health
```

**Response:**
```json
{"status": "healthy", "version": "4.2-PRODUCTION"}
```

---

### Root
```bash
GET http://localhost:8000/
```

**Response:**
```json
{
  "api": "Pharmyrus v4.2 PRODUCTION",
  "status": "online",
  "layers": ["PubChem", "WO Discovery", "Patent Family", "Patent Details"]
}
```

---

### Search Patents
```bash
GET http://localhost:8000/api/v1/search?molecule_name=darolutamide&brand_name=Nubeqa
```

**Response:**
```json
{
  "consulta": {...},
  "molecule_info": {...},
  "layer2_wo_discovery": {
    "wo_numbers_found": 15,
    "wo_numbers": ["WO2011051540", ...]
  },
  "layer3_patent_family": {
    "patents_by_country": {"BR": 8, "US": 12, ...}
  },
  "patents": {
    "BR": [...],
    "US": [...],
    ...
  },
  "comparison_br": {
    "found": 8,
    "match_rate": "100%",
    "status": "Excellent"
  }
}
```

---

## ⚙️ CONFIGURAÇÃO

### Variáveis de Ambiente (.env)

```bash
# SerpAPI (obrigatório)
SERPAPI_KEY=your_serpapi_key_here

# Server
HOST=0.0.0.0
PORT=8000

# Timeouts
TIMEOUT_SHORT=30
TIMEOUT_MEDIUM=60
TIMEOUT_LONG=120
```

---

## 🔑 SerpAPI Keys

**Keys disponíveis** (encontradas no n8n):

```bash
# Key 1: INPI REAL
bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc

# Key 2: Patent Search v4.1
3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d
```

**Teste ambas com:**
```bash
python3 test_multiple_keys.py
```

---

## 📊 PERFORMANCE

### Darolutamide (benchmark):
```
Layer 1: 1-2s   → Dev codes, CAS
Layer 2: 15-20s → 15 WOs
Layer 3: 20-30s → 38 patents (BR/US/JP/CN/EP)
Layer 4: 15-25s → Detalhes completos

Total: 60-80 segundos
Requests HTTP: ~63
SerpAPI Cost: ~$0.01
```

---

## 🐛 TROUBLESHOOTING

### ❌ "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

---

### ❌ "403 Forbidden" (SerpAPI)
```bash
# Sem créditos ou key inválida
# Verifique: https://serpapi.com/dashboard
python3 test_multiple_keys.py
```

---

### ❌ "Nenhum WO encontrado"
```bash
# Verifique se a key está correta no .env
cat .env | grep SERPAPI_KEY

# Teste extração
python3 test_wo_extraction.py
```

---

### ❌ "Port 8000 already in use"
```bash
# Encontrar processo
lsof -i :8000

# Matar processo
kill -9 <PID>

# OU usar outra porta
PORT=8001 python3 main_v4_2_production.py
```

---

## 📈 MONITORAMENTO

### Logs (Docker)
```bash
docker logs -f pharmyrus-api
```

### Logs (Systemd)
```bash
sudo journalctl -u pharmyrus -f
```

### Métricas
```bash
# Total requests
curl http://localhost:8000/api/v1/search?... | jq .debug.requests_total

# Erros
curl http://localhost:8000/api/v1/search?... | jq .debug.errors

# Tempo de execução
curl http://localhost:8000/api/v1/search?... | jq .execution_time_seconds
```

---

## 🔒 SEGURANÇA

### Produção:
1. **Nunca exponha** `.env` no Git
2. Use **HTTPS** (Nginx + Let's Encrypt)
3. Configure **rate limiting**
4. Use **API keys** para autenticação
5. Monitor **logs** regularmente

### Nginx Config (exemplo):
```nginx
server {
    listen 80;
    server_name pharmyrus.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📚 DOCUMENTAÇÃO ADICIONAL

- **GUIA_COMPLETO_v4_2.md** - Documentação técnica completa
- **START_HERE_v4_2.md** - Resumo executivo
- **INDEX_v4_2.md** - Índice de todos os arquivos

---

## 🎯 CHECKLIST DE DEPLOY

- [ ] SerpAPI key configurada no `.env`
- [ ] `test_multiple_keys.py` → Key funciona ✅
- [ ] `test_wo_extraction.py` → WOs ≥ 10 ✅
- [ ] Deploy realizado (Docker/Railway/Local/Systemd)
- [ ] API acessível via HTTP
- [ ] Health check retorna 200 OK
- [ ] Endpoint `/api/v1/search` funciona
- [ ] BRs ≥ 6, match_rate ≥ 70%
- [ ] Logs sendo monitorados
- [ ] Backup do `.env` realizado

---

## 📞 SUPORTE

Se problemas persistirem após seguir este guia:

1. Compartilhe output de `test_multiple_keys.py`
2. Compartilhe output de `test_wo_extraction.py`
3. Compartilhe logs: `docker logs pharmyrus-api`
4. Compartilhe resultado JSON do endpoint

---

## 🚀 DEPLOY RÁPIDO

**1 comando para deploy Docker:**
```bash
docker run -d --name pharmyrus-api -p 8000:8000 \
  -e SERPAPI_KEY=bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc \
  pharmyrus-api:v4.2
```

**1 comando para testar:**
```bash
curl http://localhost:8000/health && \
curl 'http://localhost:8000/api/v1/search?molecule_name=darolutamide' | jq .comparison_br
```

---

**Versão:** 4.2-PRODUCTION  
**Data:** 2024-12-06  
**Status:** ✅ Pronto para deploy  
**Licença:** Proprietário (Pharmyrus)
