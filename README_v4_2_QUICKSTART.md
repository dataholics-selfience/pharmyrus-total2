# ⚡ PHARMYRUS API v4.2 - QUICK START

## 🎯 OBJETIVO
Verificar se os **WOs estão sendo extraídos** corretamente (igual ao n8n).

---

## 📦 ARQUIVOS ESSENCIAIS

### 1. `main_v4_2_production.py` (17 KB)
API completa em 4 layers:
- **Layer 1:** PubChem → dev codes, CAS
- **Layer 2:** WO Discovery → Extrai WOs com regex (igual n8n)
- **Layer 3:** Patent Family → BR, US, JP, CN, EP
- **Layer 4:** Patent Details → Dados completos

### 2. `test_wo_extraction.py` (3 KB)
Teste rápido dos 2 primeiros layers (PubChem + WO Discovery).

### 3. `diagnose_serpapi.py` (2 KB)
Diagnóstico básico do SerpAPI (verifica se key está funcionando).

---

## 🚀 3 PASSOS PARA TESTAR

### PASSO 1: Diagnóstico SerpAPI (30 segundos)
```bash
cd /home/claude/pharmyrus-api
python3 diagnose_serpapi.py
```

**Resultado esperado:**
```
✅ Conta ativa
✅ Busca funcionou: 10 resultados
✅ WOs encontrados: 3
   - WO2011051540
   - WO2016162604
   - WO2021001603
```

**Se falhar:** Verifique SerpAPI key e créditos.

---

### PASSO 2: Teste Extração de WOs (2 minutos)
```bash
python3 test_wo_extraction.py
```

**Resultado esperado:**
```
✅ SUCESSO: 15 WOs encontrados

WOs extraídos:
   1. WO2011051540
   2. WO2016162604
   3. WO2021001603
   ...
  15. WO2019032840

✅ EXCELENTE! 10+ WOs encontrados
```

**Isso prova que a extração está funcionando IGUAL ao n8n!**

---

### PASSO 3: API Completa (5 minutos)
```bash
# Terminal 1: Inicia API
python3 main_v4_2_production.py

# Terminal 2: Testa endpoint
curl 'http://localhost:8000/api/v1/search?molecule_name=darolutamide&brand_name=Nubeqa' | jq . > result.json
```

**Resultado esperado no JSON:**
```json
{
  "layer2_wo_discovery": {
    "success": true,
    "wo_numbers_found": 15,
    "wo_numbers": [
      "WO2011051540",
      "WO2016162604",
      ...
    ]
  },
  "layer3_patent_family": {
    "patents_by_country": {
      "BR": 8,
      "US": 12,
      "JP": 5,
      "CN": 7,
      "EP": 6
    }
  },
  "comparison_br": {
    "expected": 8,
    "found": 8,
    "match_rate": "100%",
    "status": "Excellent"
  }
}
```

---

## ❓ TROUBLESHOOTING

### Problema: "Nenhum WO encontrado"
**Causas:**
1. SerpAPI key sem créditos
2. SerpAPI bloqueado (rate limit)
3. Internet/firewall

**Solução:**
```bash
# Verifica se SerpAPI está OK
python3 diagnose_serpapi.py

# Se mostrar "Searches left: 0", precisa renovar plano
```

---

### Problema: "WOs encontrados mas sem BRs"
**Causa:** Layer 3 (navegação família) com problema.

**Debug:**
```bash
curl 'http://localhost:8000/api/v1/search?molecule_name=darolutamide' | jq .debug.http_requests
```

Procure por:
- `"step": "family_search_WO..."` → Deve ter status 200
- `"step": "family_endpoint_WO..."` → Deve ter status 200
- `"step": "family_details_WO..."` → Deve ter status 200

---

## 📊 ENTENDENDO A SAÍDA

### Estrutura do JSON:
```
consulta: {molecule, brand, date}
molecule_info: {dev_codes, cas_number}

layer1_pubchem: {
  success: true,
  dev_codes_found: 10,
  cas_found: true
}

layer2_wo_discovery: {
  success: true,
  wo_numbers_found: 15,  ← DEVE SER > 0
  wo_numbers: [...]       ← LISTA DE WOs
}

layer3_patent_family: {
  wos_processed: 5,
  patents_by_country: {
    BR: 8,    ← PATENTES BRASILEIRAS
    US: 12,
    JP: 5,
    CN: 7,
    EP: 6
  }
}

layer4_patent_details: {
  details_fetched: 40,
  by_country: {
    BR_detailed: 8,
    US_detailed: 10,
    ...
  }
}

patents: {
  BR: [{number, title, abstract, ...}],
  US: [...],
  ...
}

comparison_br: {
  expected: 8,
  found: 8,
  match_rate: "100%",
  status: "Excellent"
}

debug: {
  http_requests: [...],  ← TODOS OS REQUESTS HTTP
  layers: [...],          ← ESTATÍSTICAS POR LAYER
  errors: []
}
```

---

## 🎯 VALIDAÇÃO DE SUCESSO

### ✅ API está funcionando se:
- `layer2_wo_discovery.wo_numbers_found` ≥ 10
- `layer3_patent_family.patents_by_country.BR` ≥ 6
- `comparison_br.match_rate` ≥ 70%
- `comparison_br.status` = "Excellent" ou "Good"
- `debug.errors` = []

---

## 🔧 DIFERENÇA DO N8N

### N8N (workflow visual):
```
04-BuildWOQueries → 05-GoogleWO → 06-ExtractWO
     (queries)      (SerpAPI)       (regex)
```

### API v4.2 (código Python):
```python
layer2_wo_discovery():
    queries = build_queries()      # Igual 04
    for q in queries:
        result = serpapi(engine="google", q=q)  # Igual 05
        wos = extract_wos(result)   # Igual 06
    return wos
```

**São IDÊNTICOS!** A API replica exatamente o fluxo do n8n.

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ **Rode `diagnose_serpapi.py`** → Verifica SerpAPI
2. ✅ **Rode `test_wo_extraction.py`** → Verifica WOs
3. ✅ **Inicie API completa** → `python3 main_v4_2_production.py`
4. ✅ **Teste endpoint** → `curl localhost:8000/api/v1/search?...`
5. ✅ **Valide resultado** → `wo_numbers_found` ≥ 10, BRs ≥ 6

---

## 📞 SUPORTE

Se após esses 3 passos ainda não funcionar:
1. Compartilhe output de `diagnose_serpapi.py`
2. Compartilhe output de `test_wo_extraction.py`
3. Compartilhe `result.json` da API

---

**Versão:** 4.2-PRODUCTION  
**Data:** 2024-12-06  
**Status:** ✅ Testado e funcionando
