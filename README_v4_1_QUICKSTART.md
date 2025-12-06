# 🚀 Pharmyrus API v4.1 EXPERT - Quick Start

## O QUE É?

API que **replica EXATAMENTE** o workflow n8n que funciona, com debug completo de cada etapa.

## 📥 INSTALAÇÃO (3 minutos)

```bash
# 1. Salve os arquivos:
#    - main_v4_1_expert.py
#    - test_v4_1.py
#    - requirements_v4.txt (mesmo da v4.0)

# 2. Renomeie
mv main_v4_1_expert.py main.py

# 3. Instale
pip install -r requirements_v4.txt

# 4. Adicione dependência de teste
pip install colorama

# 5. Execute
python main.py
```

## 🧪 TESTE RÁPIDO

```bash
# Terminal 1: API rodando
python main.py

# Terminal 2: Teste
python3 test_v4_1.py
```

**Resultado esperado:**
```
✅ EXCELLENT! API is working correctly.
   8 BR patents found (target: 6+)
   Match rate: 100% (target: 70%+)

🚀 Ready for production deployment!
```

## 📊 ENTENDENDO O OUTPUT

### Estrutura JSON

```json
{
  "wo_discovery": {
    "wo_numbers_found": 12  // ✅ Deve ser >= 8
  },
  "family_navigation": {
    "unique_br_found": 8    // ✅ Deve ser >= 6
  },
  "br_patents": [
    {
      "number": "BR112016028234A2",
      "title": "...",
      "assignee": "Orion Corporation",
      "source_wo": "WO2015185837"
    }
  ],
  "comparison": {
    "match_rate": "100%",    // ✅ Deve ser >= 70%
    "status": "Excellent"
  },
  "debug": {
    "http_requests": [...],  // Todas as requisições HTTP
    "errors": [],            // ✅ Deve estar vazio
    "timing": {
      "total_seconds": 48.5
    }
  }
}
```

## 🔍 DEBUG - ONDE OLHAR SE FALHAR

### 1. Zero WOs encontrados?

```bash
cat test_result_*.json | jq '.debug.http_requests[] | select(.step | contains("wo_discovery"))'
```

**Possíveis causas:**
- SerpAPI key inválida ou quota esgotada
- Rate limiting (status_code: 429)

### 2. WOs encontrados mas zero BRs?

```bash
cat test_result_*.json | jq '.debug.http_requests[] | select(.step | contains("worldwide_apps"))'
```

**Possíveis causas:**
- json_endpoint não encontrado
- serpapi_link não encontrado
- Navigation path quebrou

### 3. BRs encontrados mas sem detalhes?

```bash
cat test_result_*.json | jq '.br_extraction'
```

**Possíveis causas:**
- Rate limiting (muitos requests seguidos)
- API de details temporariamente indisponível

## ⚙️ CONFIGURAÇÕES

### Ajustar timeouts

Em `main.py`, linha 22-24:

```python
TIMEOUT_SHORT = 30   # PubChem, queries rápidas
TIMEOUT_MEDIUM = 60  # SerpAPI, EPO
TIMEOUT_LONG = 120   # WIPO (como solicitado)
```

### Processar mais WOs

Em `main.py`, linha 252:

```python
for wo in wo_numbers[:5]:  # Mude de 5 para 10
```

⚠️ **Atenção:** Mais WOs = mais tempo + mais API calls

### Buscar mais detalhes de BRs

Em `main.py`, linha 275:

```python
for i, (br_id, source_wo) in enumerate(list(all_br_patents.items())[:20]):  # Mude de 20 para 50
```

## 🎯 TARGETS DE PERFORMANCE

Para **Darolutamide**:

| Métrica | Target | Excelente |
|---------|--------|-----------|
| WOs encontrados | >= 8 | >= 12 |
| BRs únicos | >= 6 | >= 8 |
| Match rate | >= 70% | >= 90% |
| Tempo total | < 90s | < 60s |
| Erros HTTP | 0 | 0 |

## 📋 CHECKLIST PRÉ-PRODUÇÃO

- [ ] `test_v4_1.py` rodou com sucesso
- [ ] Match rate >= 70%
- [ ] BRs >= 6 encontrados
- [ ] `debug.errors` está vazio
- [ ] Todos os BRs têm `title`, `assignee`, `filing_date`
- [ ] Tempo de execução < 90s

## 🚀 DEPLOY PRODUÇÃO

```bash
# Se todos os checks passaram:
git add main.py requirements_v4.txt
git commit -m "Deploy Pharmyrus API v4.1 EXPERT"
git push origin main

# Railway fará deploy automático
```

## ❓ FAQ

**P: Por que ainda usa SerpAPI?**  
R: É o que o n8n usa e funciona. Remover SerpAPI é possível mas complexo (Google bloqueia scrapers). Recomendação: validar v4.1 primeiro, otimizar depois.

**P: SerpAPI não é caro?**  
R: ~$50/mês vs Cortellis $50k/ano = 99.9% de economia. Vale MUITO a pena.

**P: E se quiser mesmo remover SerpAPI?**  
R: Possível com Playwright/Selenium, mas:
1. Muito mais complexo
2. Precisa lidar com CAPTCHAs
3. Pode quebrar com mudanças do Google
4. Recomendo como **fallback**, não primário

**P: Quantas queries SerpAPI por busca?**  
R: Para Darolutamide:
- WO discovery: ~7 queries
- Family navigation: ~15 queries (5 WOs × 3 steps)
- BR details: ~8 queries
- **Total: ~30 queries por molécula**

Com plano $50/mês = 5000 queries = ~166 moléculas/mês

## 📞 SUPORTE

Se falhar:
1. Rode `test_v4_1.py`
2. Copie o JSON gerado (`test_result_*.json`)
3. Envie com a descrição do problema

Foco especial em:
- `debug.http_requests`
- `debug.errors`
- `wo_discovery`
- `family_navigation`
