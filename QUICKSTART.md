# ⚡ QUICKSTART

## 1️⃣ GitHub
```bash
git init && git add . && git commit -m "Pharmyrus API"
git remote add origin https://github.com/SEU_USER/pharmyrus-railway.git
git push -u origin main
```

## 2️⃣ Railway
[railway.app](https://railway.app) → New Project → Deploy from GitHub → Selecione repo → Aguarde

## 3️⃣ Testar
```bash
curl "https://SEU-DOMINIO.railway.app/api/v1/search?molecule_name=darolutamide"
```

✅ Pronto! API online em 5 minutos.

---

## 📋 Endpoints

- `GET /` - API info
- `GET /health` - Health check  
- `GET /api/v1/search?molecule_name=X` - ⭐ Busca
- `GET /docs` - Swagger

---

## 🎯 Response Format

```json
{
  "molecule_info": { "dev_codes": [...], "cas_number": "..." },
  "search_result": { "inpi_patents": [...], "total_inpi_patents": 8 },
  "comparison_cortellis": { "found": 8, "match_rate": "100%" }
}
```

Deploy: `railway up` 🚀
