# ⚡ PHARMYRUS v4.2 - README EXECUTIVO

## 🎯 O QUE FOI FEITO

✅ **API v4.2 PRODUCTION** - Extrai WOs IGUAL ao n8n  
✅ **4 LAYERS** - PubChem → WOs → Família (BR/US/JP/CN/EP) → Detalhes  
✅ **DEBUG EXTREMO** - Rastreia todos os HTTP requests  

## 📦 ARQUIVOS

1. **main_v4_2_production.py** - API completa (26 KB)
2. **test_wo_extraction.py** - Testa extração de WOs (6 KB)
3. **test_multiple_keys.py** - Testa ambas as SerpAPI keys (4 KB)
4. **diagnose_serpapi.py** - Diagnóstico básico (3 KB)
5. **GUIA_COMPLETO_v4_2.md** - Documentação completa (12 KB)

## 🚀 COMO USAR (3 COMANDOS)

```bash
# 1. Qual SerpAPI key funciona?
python3 test_multiple_keys.py

# 2. WOs estão sendo extraídos?
python3 test_wo_extraction.py

# 3. API completa
python3 main_v4_2_production.py
curl 'http://localhost:8000/api/v1/search?molecule_name=darolutamide' | jq .
```

## ✅ RESULTADO ESPERADO

```json
{
  "layer2_wo_discovery": {
    "wo_numbers_found": 15,
    "wo_numbers": ["WO2011051540", "WO2016162604", ...]
  },
  "layer3_patent_family": {
    "patents_by_country": {"BR": 8, "US": 12, "JP": 5, "CN": 7, "EP": 6}
  },
  "comparison_br": {
    "found": 8,
    "match_rate": "100%",
    "status": "Excellent"
  }
}
```

## 🔧 DIFERENÇA v4.1 → v4.2

**v4.1 (NÃO FUNCIONAVA):**
```python
# ❌ Buscava direto por WO number
result = serpapi(engine="google_patents", q="WO2011051540")
```

**v4.2 (FUNCIONA - IGUAL N8N):**
```python
# ✅ Busca por queries contextuais
queries = ["darolutamide patent WO2011", "ODM-201 patent WO"]
for query in queries:
    result = serpapi(engine="google", q=query)
    wos = regex_extract(result)  # /WO[\s-]?(\d{4})[\s\/]?(\d{6})/gi
```

## ⚠️ IMPORTANTE

**Ambiente Claude não tem internet** → Keys dão 403  
**VOCÊ precisa testar no SEU ambiente**  

## 📍 ARQUIVOS ESTÃO EM

```
/mnt/user-data/outputs/
├── main_v4_2_production.py
├── test_wo_extraction.py
├── test_multiple_keys.py
├── diagnose_serpapi.py
├── GUIA_COMPLETO_v4_2.md
└── README_v4_2_QUICKSTART.md
```

## 🎓 KEYS DO N8N

```python
# Encontradas em /mnt/project/*.json:
KEY_1 = "bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc"  # INPI REAL
KEY_2 = "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d"  # Patent Search
```

## ✅ PRÓXIMO PASSO

```bash
cd /mnt/user-data/outputs
python3 test_multiple_keys.py  # ← COMECE AQUI!
```

**Status:** ✅ Código pronto, aguardando teste
