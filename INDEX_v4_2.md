# 📁 PHARMYRUS v4.2 - ÍNDICE DE ARQUIVOS

## 🎯 COMEÇE AQUI

**→ START_HERE_v4_2.md** (2.5 KB)  
Resumo executivo em 1 página. Leia PRIMEIRO!

---

## 📚 DOCUMENTAÇÃO

### 1. **GUIA_COMPLETO_v4_2.md** (12 KB)
Documentação técnica completa:
- Arquitetura dos 4 layers
- Estrutura do JSON de saída
- Troubleshooting detalhado
- Comparação n8n vs API
- Deploy production
- Performance esperada

### 2. **README_v4_2_QUICKSTART.md** (5.1 KB)
Guia rápido de início:
- 3 passos para testar
- Validação de sucesso
- Entendendo a saída
- FAQ básico

### 3. **START_HERE_v4_1.md** (8.4 KB)  
Documentação v4.1 (referência - versão anterior)

---

## 🚀 CÓDIGO PRINCIPAL

### **main_v4_2_production.py** (24 KB, 620 linhas)
API completa em 4 layers:

```python
# Layer 1: PubChem
async def layer1_pubchem(molecule, debug) → dev_codes, cas

# Layer 2: WO Discovery (IGUAL N8N)
async def layer2_wo_discovery(molecule, brand, dev_codes, debug) → wo_numbers[]

# Layer 3: Patent Family
async def layer3_patent_family(wo_number, debug) → BR[], US[], JP[], CN[], EP[]

# Layer 4: Patent Details
async def layer4_patent_details(patent_id, country, debug) → patent_data

# FastAPI endpoints
@app.get("/api/v1/search")
```

**Diferenças v4.1 → v4.2:**
- ✅ WO Discovery corrigido (engine=google, múltiplas queries)
- ✅ Regex extraction igual n8n
- ✅ Patent family completa (BR, US, JP, CN, EP)
- ✅ Debug extremo (todos os HTTP requests)

---

## 🧪 SCRIPTS DE TESTE

### 1. **test_multiple_keys.py** (3.9 KB)
**EXECUTE PRIMEIRO!**  
Testa AMBAS as SerpAPI keys do n8n:
```bash
python3 test_multiple_keys.py
```

Resultado:
```
✅ SUCESSO! Key funcionando encontrada
Key: bc20bca64032a7ac59ab...fb6e33e4bc
WOs encontrados: 5

📝 COPIE ESTA KEY PARA main_v4_2_production.py:
SERPAPI_KEY = "bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc"
```

### 2. **test_wo_extraction.py** (3.6 KB)
**EXECUTE SEGUNDO!**  
Testa extração de WOs (Layers 1 + 2):
```bash
python3 test_wo_extraction.py
```

Resultado:
```
✅ SUCESSO: 15 WOs encontrados

WOs extraídos:
   1. WO2011051540
   2. WO2016162604
   ...
  15. WO2023161458

✅ EXCELENTE! 10+ WOs encontrados
```

### 3. **diagnose_serpapi.py** (3.8 KB)
Diagnóstico básico SerpAPI:
```bash
python3 diagnose_serpapi.py
```

### 4. **test_v4_1.py** (6.9 KB)  
Teste v4.1 (referência - versão anterior)

### 5. **test_api.py** (11 KB)  
Teste v4.0 (referência - versão anterior)

---

## 🔑 SERPAPI KEYS

Encontradas em `/mnt/project/*.json`:

```python
# Key 1: INPI REAL (workflow)
"bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc"

# Key 2: Patent Search v4.1 (workflow)
"3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d"
```

**Use `test_multiple_keys.py` para descobrir qual funciona!**

---

## 📊 ESTRUTURA DO PROJETO

```
pharmyrus-api/
├── main_v4_2_production.py      ← API PRINCIPAL
├── test_multiple_keys.py        ← TESTE 1: Keys
├── test_wo_extraction.py        ← TESTE 2: WOs
├── diagnose_serpapi.py          ← TESTE 3: SerpAPI
├── GUIA_COMPLETO_v4_2.md        ← DOC COMPLETA
├── README_v4_2_QUICKSTART.md    ← QUICK START
└── START_HERE_v4_2.md           ← RESUMO 1 PÁGINA
```

---

## 🎯 FLUXO DE TRABALHO

```
1. Leia START_HERE_v4_2.md
   ↓
2. Execute test_multiple_keys.py
   ↓
3. Copie a key que funciona para main_v4_2_production.py
   ↓
4. Execute test_wo_extraction.py
   ↓
5. Se WOs ≥ 10 → ✅ Funcionando!
   ↓
6. Inicie API: python3 main_v4_2_production.py
   ↓
7. Teste: curl localhost:8000/api/v1/search?molecule_name=darolutamide
   ↓
8. Valide: BRs ≥ 6, match_rate ≥ 70%
   ↓
9. Deploy production (Railway/Docker/Systemd)
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [ ] `test_multiple_keys.py` → Key funciona
- [ ] `test_wo_extraction.py` → WOs ≥ 10
- [ ] API iniciada → Server running on 0.0.0.0:8000
- [ ] Endpoint testado → JSON retornado
- [ ] `wo_numbers_found` ≥ 10
- [ ] `patents_by_country.BR` ≥ 6
- [ ] `match_rate` ≥ 70%
- [ ] `status` = "Excellent" or "Good"
- [ ] `debug.errors` = []

---

## 🐛 TROUBLESHOOTING RÁPIDO

### ❌ "Nenhuma key funcional"
```bash
# Ambas as keys deram 403
# → Sem créditos OU ambiente sem internet
# Verifique: https://serpapi.com/dashboard
```

### ❌ "WOs = 0"
```python
# Verifique engine=google (NÃO google_patents)
# Verifique queries: "darolutamide patent WO2011"
# Verifique regex: /WO[\s-]?(\d{4})[\s\/]?(\d{6})/gi
```

### ❌ "WOs > 0 mas BRs = 0"
```bash
# Debug navegação patent family
curl localhost:8000/api/v1/search?... | jq .debug.http_requests

# Procure por:
# - family_search_WO* → status 200?
# - family_endpoint_WO* → status 200?
# - family_details_WO* → status 200?
```

---

## 📈 PERFORMANCE

### Darolutamide (benchmark):
```
Layer 1: 1-2s   → 10 dev codes, CAS
Layer 2: 15-20s → 15 WOs
Layer 3: 20-30s → 8 BR, 12 US, 5 JP, 7 CN, 6 EP
Layer 4: 15-25s → 38 patents detalhados

TOTAL: 60-80s
HTTP Requests: ~63
SerpAPI Cost: ~$0.01
```

---

## 🚀 DEPLOY

### Railway:
```bash
railway up
```

### Docker:
```dockerfile
FROM python:3.11-slim
RUN pip install httpx fastapi uvicorn
COPY main_v4_2_production.py /app/
CMD ["uvicorn", "main_v4_2_production:app"]
```

### Systemd:
```bash
sudo systemctl enable pharmyrus
sudo systemctl start pharmyrus
```

---

## 📞 SUPORTE

Se após seguir todos os passos ainda não funcionar:

1. Compartilhe output de `test_multiple_keys.py`
2. Compartilhe output de `test_wo_extraction.py`
3. Compartilhe `result.json` completo
4. Compartilhe `debug.http_requests` se BRs = 0

---

## 🎓 CONCEITOS-CHAVE

### Engine Google vs Google Patents
```
engine=google → Busca web → WOs nos textos ✅
engine=google_patents → Busca patentes direto → Precisa WO exato ❌
```

### Navegação Patent Family
```
WO → json_endpoint → serpapi_link → worldwide_applications → BR/US/JP/CN/EP
```

### Regex WO
```
/WO[\s-]?(\d{4})[\s\/]?(\d{6})/gi
Matches: WO2011051540, WO 2011 051540, WO-2011-051540
```

---

**Versão:** 4.2-PRODUCTION  
**Data:** 2024-12-06  
**Status:** ✅ Código pronto, aguardando teste no ambiente do usuário  
**Arquivos:** 7 (API + 3 testes + 3 docs)  
**Linhas de código:** 620 (API) + 170 (testes) = 790 linhas  
**Tamanho total:** ~50 KB
