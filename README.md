# 🚀 Pharmyrus Crawler API - Railway Ready

**Endpoint:** `GET /api/v1/search?molecule_name=darolutamide`

Sistema de busca de patentes com arquitetura 6-layer, 100% compatível Railway.

---

## ⚡ Deploy Railway (3 Passos)

### 1. Push GitHub
```bash
git init
git add .
git commit -m "Pharmyrus API"
git remote add origin https://github.com/SEU_USER/pharmyrus-railway.git
git push -u origin main
```

### 2. Deploy Railway
1. [railway.app](https://railway.app) → Login with GitHub
2. **New Project** → **Deploy from GitHub repo**
3. Selecione `pharmyrus-railway`
4. Aguarde build (~2 min)

### 3. Testar
```bash
curl "https://seu-dominio.railway.app/api/v1/search?molecule_name=darolutamide"
```

✅ **API no ar em < 5 minutos!**

---

## 📡 Response JSON (Genoi-compatible)

```json
{
  "consulta": {
    "termo_pesquisado": "darolutamide",
    "nome_molecula": "darolutamide"
  },
  "molecule_info": {
    "dev_codes": ["ODM-201"],
    "cas_number": "1297538-32-9"
  },
  "search_result": {
    "inpi_patents": [...],
    "total_inpi_patents": 8
  },
  "comparison_cortellis": {
    "expected": 8,
    "found": 8,
    "match_rate": "100%"
  }
}
```

---

## 🏗️ Arquitetura

1. **PubChem** → Dev codes, CAS, synonyms
2. **INPI** → 15 queries sequenciais (replica n8n)
3. **FDA** → Orange Book data

---

## 📦 Arquivos

```
pharmyrus_railway/
├── main.py           # FastAPI app
├── requirements.txt  # Dependencies
├── Procfile          # Railway start
├── railway.json      # Railway config
├── runtime.txt       # Python 3.11
├── nixpacks.toml     # Build config
└── README.md         # Este arquivo
```

---

## 💰 Custo

Railway: ~$25/mês | Cortellis: $4,167/mês | **Economia: 99.4%**

---

## 🎯 Features

✅ SEM SERP API  
✅ SEM n8n  
✅ Railway auto-deploy  
✅ INPI 15 queries  
✅ EPO token auto-renewal  
✅ Async/await  

---

## 📚 Docs

- Swagger: `https://seu-dominio.railway.app/docs`
- Health: `/health`
- Info: `/`

**Deploy now:** `railway up` 🚀
