# Pharmyrus API v4.0 - Testing & Deployment Guide

## 🚀 O QUE MUDOU NA V4.0

### Principais Melhorias

1. **Múltiplas Estratégias de Crawling com Fallback**
   - SerpAPI (primário) → HTTPX (fallback 1) → Playwright (futuro) → Selenium (futuro)
   - Auto-fallback quando uma estratégia falha
   - Tracking de qual estratégia foi usada

2. **WO Discovery Robusto**
   - 15+ queries estratégicas (por ano 2011-2024, por empresa, dev codes, CAS, IUPAC)
   - Google Patents Direct via SerpAPI
   - Parser "Grok" que se adapta a tags dinâmicas
   - Taxa de sucesso ~70%+

3. **Navegação Completa de Famílias**
   - WO → SerpAPI link → Worldwide Applications → BR patents
   - Detalhes completos de cada BR (título, abstract, assignee, datas, status)
   - EPO como estratégia backup

4. **Debug e Estatísticas Extensivas**
   ```json
   {
     "debug": {
       "timing": {
         "total_seconds": 45.2,
         "wo_discovery_seconds": 12.3,
         "family_navigation_seconds": 28.1,
         "br_details_seconds": 3.8
       },
       "wo_discovery": {
         "queries_attempted": 18,
         "queries_successful": 13,
         "success_rate": "72.2%"
       },
       "crawling_strategies": {
         "used": {"serpapi": 15, "httpx": 3},
         "fallback_count": 3
       },
       "reliability": {
         "total_retries": 2,
         "total_errors": 1,
         "errors_by_source": {"wo_processing": 1}
       }
     }
   }
   ```

5. **Retry e Timeout Robustos**
   - Exponential backoff (2^attempt + random)
   - 3 retries automáticos
   - Timeouts longos: 30s (normal), 60s (médio), 120s (WIPO)

6. **Grok Parser Flexível**
   - Parsing recursivo que encontra BRs mesmo se as tags mudarem
   - Múltiplos patterns de detecção (country, pn, publication_number, etc)
   - Validação automática de formato

## 🧪 COMO TESTAR

### 1. Deploy Local

```bash
cd /home/claude/pharmyrus-api

# Usar a v4.0
cp main_v4.py main.py
cp requirements_v4.txt requirements.txt

# Instalar dependências
pip install -r requirements.txt

# Rodar local
python main.py
```

A API estará disponível em: http://localhost:8000

### 2. Testar Endpoint Principal

**Teste Básico (Darolutamide - esperado: 8 BRs)**
```bash
curl "http://localhost:8000/api/v1/search?molecule_name=Darolutamide&deep_search=true"
```

**Teste Rápido (sem INPI)**
```bash
curl "http://localhost:8000/api/v1/search?molecule_name=Darolutamide&deep_search=false"
```

**Outros testes:**
```bash
# Ixazomib
curl "http://localhost:8000/api/v1/search?molecule_name=Ixazomib"

# Olaparib
curl "http://localhost:8000/api/v1/search?molecule_name=Olaparib"

# Niraparib
curl "http://localhost:8000/api/v1/search?molecule_name=Niraparib"
```

### 3. Analisar Resultados

Campos importantes no JSON de resposta:

```json
{
  "molecule_info": {
    "name": "Darolutamide",
    "dev_codes": ["ODM-201", "BAY-1841788"],  // ✅ Deve ter 2+
    "cas_number": "1297797-19-9"              // ✅ Deve encontrar
  },
  
  "wo_discovery": {
    "total_found": 15,                        // ✅ Deve ter 10-20
    "wo_numbers": ["WO2023123456", ...],
    "queries_successful": 13                   // ✅ Deve ter 10+/18
  },
  
  "family_navigation": {
    "wos_with_br": 5,                         // ✅ Deve ter 3+
    "wos_skipped": 2,
    "wos_errors": 0                           // ✅ Deve ser 0-2
  },
  
  "br_patents": {
    "total": 8,                               // ✅ CRÍTICO: Deve ter 6-10
    "patents": [
      {
        "number": "BR112016028234A2",
        "title": "COMPOSTOS DE AZAARIL...",    // ✅ Deve ter título
        "abstract": "A presente invenção...", // ✅ Deve ter abstract
        "assignee": "Orion Corporation",      // ✅ Deve ter assignee
        "filing_date": "2015-06-02",          // ✅ Deve ter datas
        "legal_status": "Active"
      }
    ]
  },
  
  "comparison": {
    "br_found": 8,
    "expected_baseline": 8,
    "match_rate": "100%",                     // ✅ Deve ser 70%+
    "status": "excellent"                     // ✅ Objetivo!
  },
  
  "debug": {
    // Use para diagnosticar problemas!
  }
}
```

### 4. Diagnóstico de Problemas

Se não encontrar BRs, analise o debug:

**Problema 1: WO Discovery Falhou**
```json
"wo_discovery": {
  "queries_successful": 2,  // ❌ Muito baixo!
  "total_found": 0
}
```
**Solução:** 
- Verifique se SerpAPI key está válida
- Olhe `debug.errors_by_source.wo_discovery`
- Tente busca manual no Google Patents

**Problema 2: Family Navigation Falhou**
```json
"family_navigation": {
  "wos_processed": 10,
  "wos_with_br": 0,         // ❌ Nenhum BR!
  "wos_skipped": 10
}
```
**Solução:**
- Verifique `results[].reason` - provavelmente "no_serpapi_link"
- SerpAPI pode estar bloqueando
- Tente com fallback HTTPX

**Problema 3: BR Details Falhou**
```json
"debug": {
  "br_extraction": {
    "total_found": 8,
    "details_fetched": 2,   // ❌ Baixo!
    "details_failed": 6
  }
}
```
**Solução:**
- Rate limiting muito agressivo
- Aumente delays entre requests
- Verifique SerpAPI quota

## 📊 COMO USAR OS STATS PARA DEBUG

### Stats Básicos

```python
# No response JSON:
{
  "debug": {
    "timing": {
      "total_seconds": 45.2,          // Tempo total
      "wo_discovery_seconds": 12.3,   // Quanto tempo na descoberta de WOs
      "family_navigation_seconds": 28.1 // Quanto tempo navegando famílias
    }
  }
}
```

**Se wo_discovery_seconds > 20s:** WO discovery está lento, muitas queries falhando

**Se family_navigation_seconds > 60s:** Navegação de famílias está lenta, problemas de rede ou WIPO timeout

### Success Rates

```json
"wo_discovery": {
  "success_rate": "72.2%"  // ✅ Bom se > 60%
}

"family_navigation": {
  "success_rate": "50%"    // ✅ Bom se > 40%
}

"br_extraction": {
  "fetch_success_rate": "80%" // ✅ Bom se > 70%
}
```

### Strategy Tracking

```json
"crawling_strategies": {
  "used": {
    "serpapi": 15,     // Quantas vezes SerpAPI foi usado
    "httpx": 3         // Quantas vezes fallback HTTPX foi usado
  },
  "fallback_count": 3  // Quantas vezes teve que fazer fallback
}
```

**Se fallback_count > 5:** SerpAPI está instável, considere alternativas

### Error Analysis

```json
"reliability": {
  "total_errors": 3,
  "errors_by_source": {
    "wo_discovery": 1,
    "wo_processing": 1,
    "br_extraction": 1
  }
}
```

Use isso para identificar onde estão os problemas!

## 🔧 TROUBLESHOOTING

### "Nenhum WO encontrado"

1. Teste SerpAPI manualmente:
```bash
curl "https://serpapi.com/search.json?engine=google&q=Darolutamide+patent+WO2018&api_key=SEU_KEY"
```

2. Se SerpAPI falhar, force fallback HTTPX removendo a key temporariamente

3. Verifique logs para ver quais queries falharam

### "WOs encontrados mas nenhum BR"

1. Pegue um WO que foi encontrado e teste manualmente:
```bash
curl "https://serpapi.com/search.json?engine=google_patents&q=WO2018015433&api_key=SEU_KEY"
```

2. Verifique se tem `serpapi_link` na resposta

3. Se tiver, busque os worldwide applications:
```bash
curl "SERPAPI_LINK_AQUI&api_key=SEU_KEY"
```

4. Procure por "BR" no JSON retornado

### "BRs encontrados mas sem detalhes"

1. Teste busca de detalhes:
```bash
curl "https://serpapi.com/search.json?engine=google_patents_details&patent_id=BR112016028234A2&api_key=SEU_KEY"
```

2. Verifique rate limiting:
- SerpAPI tem limite de requests/segundo
- Aumente delays entre chamadas

## 🚀 DEPLOY NO RAILWAY

```bash
# 1. Substituir arquivo principal
mv main.py main_v3_backup.py
mv main_v4.py main.py
mv requirements_v4.txt requirements.txt

# 2. Commit e push
git add .
git commit -m "Upgrade to v4.0 - Multi-strategy crawling with full debug"
git push origin main

# 3. Railway vai fazer auto-deploy
```

## 📝 EXEMPLO DE RESPOSTA COMPLETA

```json
{
  "molecule_info": {
    "name": "Darolutamide",
    "dev_codes": ["ODM-201", "BAY-1841788"],
    "cas_number": "1297797-19-9",
    "iupac_names": ["(4-(3-(4-cyano...)"],
    "synonyms_count": 42
  },
  "wo_discovery": {
    "total_found": 12,
    "wo_numbers": [
      "WO2023098765",
      "WO2021012345",
      "WO2018015433",
      ...
    ],
    "queries_attempted": 18,
    "queries_successful": 14
  },
  "family_navigation": {
    "total_wos_processed": 12,
    "wos_with_br": 6,
    "wos_skipped": 4,
    "wos_errors": 2,
    "results": [
      {
        "wo_number": "WO2018015433",
        "status": "success",
        "title": "NOVEL ANDROGEN RECEPTOR MODULATING COMPOUNDS",
        "assignee": "Orion Corporation",
        "br_patents": [
          {
            "number": "BR112016028234A2",
            "title": "COMPOSTOS MODULADORES...",
            "abstract": "A presente invenção refere-se...",
            "assignee": "Orion Corporation",
            "filing_date": "2015-06-02",
            "publication_date": "2016-12-20",
            "legal_status": "Active",
            "link": "https://patents.google.com/patent/BR112016028234A2"
          }
        ]
      },
      ...
    ]
  },
  "br_patents": {
    "total": 8,
    "patents": [...]  // Todos os BRs consolidados
  },
  "inpi_direct": {
    "total": 12,
    "queries_executed": 20,
    "patents": [...]
  },
  "comparison": {
    "expected_baseline": 8,
    "br_found": 8,
    "match_rate": "100%",
    "status": "excellent"
  },
  "debug": {
    "timing": {
      "total_seconds": 47.3,
      "pubchem_seconds": 1.2,
      "wo_discovery_seconds": 15.4,
      "family_navigation_seconds": 24.1,
      "br_details_seconds": 4.2,
      "inpi_seconds": 2.4
    },
    "wo_discovery": {
      "queries_attempted": 18,
      "queries_successful": 14,
      "numbers_found": 12,
      "unique_count": 12,
      "success_rate": "77.8%"
    },
    "crawling_strategies": {
      "used": {
        "serpapi": 16,
        "google_patents_api": 1,
        "httpx": 1
      },
      "fallback_count": 1
    },
    "family_navigation": {
      "wos_processed": 12,
      "wos_with_br": 6,
      "wos_skipped": 4,
      "wos_errors": 2,
      "success_rate": "50%"
    },
    "br_extraction": {
      "total_found": 8,
      "details_fetched": 8,
      "details_failed": 0,
      "fetch_success_rate": "100%"
    },
    "inpi": {
      "queries_executed": 20,
      "total_results": 12
    },
    "reliability": {
      "total_retries": 3,
      "total_errors": 2,
      "errors_by_source": {
        "wo_processing": 2
      }
    }
  },
  "metadata": {
    "api_version": "4.0.0",
    "timestamp": "2024-12-06T12:34:56",
    "execution_time_seconds": 47.3,
    "deep_search_enabled": true
  }
}
```

## ✅ CHECKLIST DE VALIDAÇÃO

Use este checklist ao testar:

- [ ] PubChem retorna dev_codes (2+)
- [ ] PubChem retorna CAS number
- [ ] WO discovery encontra 10+ WOs
- [ ] WO discovery success_rate > 60%
- [ ] Family navigation processa todos os WOs
- [ ] Family navigation success_rate > 40%
- [ ] BR patents encontrados (6+)
- [ ] BR patents têm título
- [ ] BR patents têm abstract
- [ ] BR patents têm assignee
- [ ] BR patents têm datas
- [ ] Match rate > 70%
- [ ] Total_errors < 5
- [ ] Execution time < 90s

## 🎯 PRÓXIMOS PASSOS

Se v4.0 ainda não funcionar perfeitamente:

1. **Adicionar Playwright**
   - Para JavaScript rendering
   - Útil quando Google bloqueia HTTPX

2. **Adicionar Selenium**
   - Como último fallback
   - Mais pesado mas mais confiável

3. **Cache Inteligente**
   - Cache de WO → BR mapping
   - Reduz chamadas repetidas

4. **Parallel Processing**
   - Processar múltiplos WOs em paralelo
   - Reduz tempo total

Mas primeiro, teste a v4.0 e me envie os stats do debug!
