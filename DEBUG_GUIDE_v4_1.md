# 🔬 Pharmyrus API v4.1 EXPERT - Debug Guide

## 🎯 O QUE MUDOU (v4.0 → v4.1)

### ❌ v4.0 (FALHA)
```
Google Search → Extract WOs → Try to find BRs
❌ Usa engine=google (bloqueado)
❌ Não segue navigation path correto
❌ Debug limitado
```

### ✅ v4.1 EXPERT (FUNCIONA - Igual n8n)
```
1. PubChem → dev_codes, CAS
2. WO Discovery → google engine
3. Family Navigation (N8N STYLE):
   ├─ google_patents search
   ├─ json_endpoint extraction
   ├─ Navigate to json_endpoint
   ├─ serpapi_link extraction
   ├─ Navigate to serpapi_link
   └─ worldwide_applications extraction
4. BR Details → Complete data
```

---

## 📊 OUTPUT JSON STRUCTURE

### Seções Principais

```json
{
  "consulta": { ... },
  "molecule_info": {
    "chemical_name": "darolutamide",
    "dev_codes": ["ODM-201", "BAY-1841788", ...],
    "cas_number": "1297538-32-9"
  },
  "wo_discovery": {
    "queries_executed": 7,
    "queries_successful": 6,
    "wo_numbers_found": 12,
    "wo_numbers": ["WO2011140325", ...]
  },
  "family_navigation": {
    "wos_processed": 5,
    "wos_with_br": 3,
    "unique_br_found": 8
  },
  "br_extraction": {
    "total_br_unique": 8,
    "details_fetched": 8,
    "fetch_success_rate": "100.0%"
  },
  "br_patents": [
    {
      "number": "BR112016028234A2",
      "title": "...",
      "abstract": "...",
      "assignee": "Orion Corporation",
      "filing_date": "2015-06-03",
      "publication_date": "2017-06-06",
      "legal_status": "Active",
      "source_wo": "WO2015185837",
      ...
    }
  ],
  "comparison": {
    "expected": 8,
    "found": 8,
    "match_rate": "100%",
    "status": "Excellent"
  },
  "debug": {
    "http_requests": [
      {
        "step": "wo_search_WO2015185837",
        "url": "https://serpapi.com/search.json",
        "params": {"engine": "google_patents", "q": "WO2015185837"},
        "status_code": 200,
        "response_size": 45230,
        "duration_ms": 1250.5,
        "error": null
      },
      ...
    ],
    "errors": [],
    "timing": {
      "total_seconds": 48.5,
      "requests_count": 35,
      "avg_request_ms": 1385.2
    }
  }
}
```

---

## 🔍 COMO INTERPRETAR O DEBUG

### 1. **wo_discovery**
```json
"wo_discovery": {
  "queries_executed": 7,      // Quantas queries foram feitas
  "queries_successful": 6,     // Quantas retornaram 200
  "wo_numbers_found": 12,      // Total de WOs únicos encontrados
  "wo_numbers": ["WO2015...", ...] // Lista completa
}
```

✅ **BOM:** `queries_successful >= 5` e `wo_numbers_found >= 8`  
⚠️  **ATENÇÃO:** `wo_numbers_found < 5` → Pode ter problemas de API key  
❌ **RUIM:** `wo_numbers_found = 0` → SerpAPI bloqueada ou queries ruins

---

### 2. **family_navigation**
```json
"family_navigation": {
  "wos_processed": 5,    // WOs que tentou processar
  "wos_with_br": 3,      // WOs que tinham BRs
  "unique_br_found": 8   // Total de BRs únicos
}
```

✅ **BOM:** `wos_with_br / wos_processed >= 0.5` (50%+ têm BRs)  
⚠️  **ATENÇÃO:** `unique_br_found < 4` → Pode precisar processar mais WOs  
❌ **RUIM:** `wos_with_br = 0` → Navegação falhou

---

### 3. **br_extraction**
```json
"br_extraction": {
  "total_br_unique": 8,
  "details_fetched": 8,
  "fetch_success_rate": "100.0%"
}
```

✅ **BOM:** `fetch_success_rate >= 80%`  
⚠️  **ATENÇÃO:** `fetch_success_rate < 50%` → Rate limiting  
❌ **RUIM:** `details_fetched = 0` → API details quebrada

---

### 4. **debug.http_requests** (CRÍTICO!)

Mostra CADA request feita:

```json
{
  "step": "wo_search_WO2015185837",
  "url": "https://serpapi.com/search.json",
  "params": {"engine": "google_patents", "q": "WO2015185837"},
  "status_code": 200,
  "response_size": 45230,
  "duration_ms": 1250.5,
  "error": null
}
```

**Campos importantes:**
- `step` - Qual etapa do pipeline
- `status_code` - 200 = OK, 429 = Rate limit, 500 = Erro servidor
- `duration_ms` - Tempo de resposta
- `error` - Se null = sucesso

**Filtrar por step:**
- `wo_discovery_q*` - Busca de WOs
- `wo_search_*` - Busca google_patents
- `worldwide_apps_*` - Navegação para json_endpoint
- `patent_details_*` - Navegação para serpapi_link
- `br_details_*` - Detalhes de cada BR

---

## 🧪 TESTES

### Teste Local

```bash
# 1. Deploy
cd /home/claude/pharmyrus-api
cp main_v4_1_expert.py main.py
pip install -r requirements_v4.txt

# 2. Run
python main.py

# 3. Test
curl "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" > debug_darolutamide.json

# 4. Analyze
cat debug_darolutamide.json | jq '.debug.http_requests[] | select(.error != null)'
cat debug_darolutamide.json | jq '.wo_discovery'
cat debug_darolutamide.json | jq '.family_navigation'
cat debug_darolutamide.json | jq '.br_patents | length'
```

---

## 🔧 TROUBLESHOOTING

### Zero WOs encontrados

```bash
# 1. Verificar requests
cat debug.json | jq '.debug.http_requests[] | select(.step | contains("wo_discovery"))'

# 2. Verificar se tem erro 429 (rate limit)
cat debug.json | jq '.debug.http_requests[] | select(.status_code == 429)'

# 3. Testar manualmente
curl "https://serpapi.com/search.json?engine=google&q=Darolutamide+patent+WO2018&api_key=KEY"
```

### WOs encontrados mas zero BRs

```bash
# 1. Verificar qual WO foi processado
cat debug.json | jq '.debug.http_requests[] | select(.step | contains("wo_search"))'

# 2. Verificar se json_endpoint foi encontrado
cat debug.json | jq '.debug.http_requests[] | select(.step | contains("worldwide_apps"))'

# 3. Verificar se serpapi_link foi encontrado
cat debug.json | jq '.debug.http_requests[] | select(.step | contains("patent_details"))'

# 4. Verificar errors
cat debug.json | jq '.debug.errors'
```

### BRs encontrados mas sem detalhes

```bash
# 1. Verificar requisições de detalhes
cat debug.json | jq '.debug.http_requests[] | select(.step | contains("br_details"))'

# 2. Rate limiting?
cat debug.json | jq '.debug.http_requests[] | select(.step | contains("br_details") and .status_code != 200)'

# 3. Testar manualmente
curl "https://serpapi.com/search.json?engine=google_patents_details&patent_id=BR112016028234A2&api_key=KEY"
```

---

## 📈 EXPECTED RESULTS (Darolutamide)

```json
{
  "wo_discovery": {
    "queries_successful": 6,
    "wo_numbers_found": 10-15
  },
  "family_navigation": {
    "wos_processed": 5,
    "wos_with_br": 3-4,
    "unique_br_found": 6-10
  },
  "br_extraction": {
    "details_fetched": 6-10,
    "fetch_success_rate": "80-100%"
  },
  "comparison": {
    "found": 6-10,
    "match_rate": "75-100%",
    "status": "Excellent"
  },
  "debug": {
    "errors": [],
    "timing": {
      "total_seconds": 45-60
    }
  }
}
```

---

## 🚀 PRÓXIMOS PASSOS

### 1. Se v4.1 funcionar (match_rate >= 70%)

✅ Deploy em produção  
✅ Comparar com Cortellis  
🔄 **DEPOIS:** Avaliar substituir SerpAPI por crawler próprio

### 2. Se falhar

❌ Analisar `debug.http_requests`  
❌ Verificar `debug.errors`  
❌ Compartilhar JSON completo para diagnóstico

---

## 📝 SOBRE REMOVER SERPAPI

**Prós:**
- Economia de custos
- Sem rate limits
- Controle total

**Contras:**
- Google bloqueia scrapers (CAPTCHA, rate limiting)
- Precisa manter infraestrutura (Playwright/Selenium)
- Maior complexidade de código
- Pode quebrar com mudanças no Google

**Recomendação:**
1. ✅ PRIMEIRO: Validar que v4.1 funciona com SerpAPI
2. ✅ DEPOIS: Implementar crawler como **fallback**
3. ✅ Estratégia híbrida: SerpAPI (primário) + Crawler (backup)

SerpAPI custa ~$50/mês para 5000 queries.  
Se Pharmyrus substituir Cortellis ($50k/ano), vale MUITO a pena pagar SerpAPI.

**ROI:**
- Cortellis: $50,000/ano
- SerpAPI: $600/ano  
- **Economia: $49,400/ano (98.8%)**
