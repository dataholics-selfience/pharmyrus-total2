# 📚 Pharmyrus API v4.1 EXPERT - Índice Completo

## 🎯 ARQUIVOS PRINCIPAIS (Obrigatórios)

### 1. `main_v4_1_expert.py` (17 KB)
**O QUE É:** API completa v4.1 EXPERT  
**USA PARA:** Deploy em produção  
**COMO USAR:**
```bash
mv main_v4_1_expert.py main.py
python main.py
```

### 2. `requirements_v4.txt` (87 bytes)
**O QUE É:** Dependências Python  
**USA PARA:** Instalação  
**COMO USAR:**
```bash
pip install -r requirements_v4.txt
```

### 3. `test_v4_1.py` (7 KB)
**O QUE É:** Script de teste com output colorido  
**USA PARA:** Validar se API está funcionando  
**COMO USAR:**
```bash
python3 test_v4_1.py
```
**RESULTADO ESPERADO:**
```
✅ EXCELLENT! API is working correctly.
   8 BR patents found (target: 6+)
   Match rate: 100% (target: 70%+)
```

---

## 📖 DOCUMENTAÇÃO (Leitura Recomendada)

### 4. `README_v4_1_QUICKSTART.md` (5 KB)
**O QUE É:** Guia rápido de instalação e uso  
**USA PARA:** Começar rápido  
**LÊ PRIMEIRO:** ⭐ Este aqui!  
**TEMPO:** 5 minutos

**SEÇÕES:**
- Instalação em 3 minutos
- Teste rápido
- Entendendo o output JSON
- Debug básico
- FAQ

---

### 5. `DEBUG_GUIDE_v4_1.md` (8 KB)
**O QUE É:** Guia completo de debug  
**USA PARA:** Diagnosticar problemas  
**LÊ QUANDO:** Algo falhou ou match_rate < 70%

**SEÇÕES:**
- Estrutura do JSON debug
- Como interpretar cada seção
- Troubleshooting step-by-step
- Filtros jq para análise
- Targets de performance

---

### 6. `N8N_VS_API_COMPARISON.md` (10 KB)
**O QUE É:** Comparação visual n8n workflow vs API  
**USA PARA:** Entender EXATAMENTE o que foi replicado  
**LÊ QUANDO:** Quer entender o funcionamento interno

**SEÇÕES:**
- Fluxo completo lado-a-lado
- 3 passos críticos de navegação
- Validação de equivalência
- Vantagens da API v4.1

---

## 📦 ARQUIVOS ANTERIORES (Referência)

### 7. `main_v4.py` (40 KB)
**O QUE É:** API v4.0 (versão anterior)  
**USA PARA:** Referência/comparação  
**STATUS:** ❌ Não usar em produção (falha em navegação)

### 8. `test_api.py` (11 KB)
**O QUE É:** Suite de testes para v4.0  
**USA PARA:** Referência  
**STATUS:** Compatível com v4.1 mas `test_v4_1.py` é melhor

### 9. `deploy_v4.sh` (7 KB)
**O QUE É:** Script de deploy automatizado  
**USA PARA:** Deploy Railway  
**COMO USAR:**
```bash
chmod +x deploy_v4.sh
./deploy_v4.sh railway
```

---

## 📁 ESTRUTURA DE DIRETÓRIOS

```
pharmyrus-api/
├── main_v4_1_expert.py          ← API principal (USE ESTE!)
├── main_v4.py                   ← v4.0 (referência)
├── requirements_v4.txt          ← Dependências
├── test_v4_1.py                 ← Teste rápido (USE ESTE!)
├── test_api.py                  ← Teste v4.0 (referência)
├── deploy_v4.sh                 ← Deploy script
├── README_v4_1_QUICKSTART.md    ← ⭐ Leia primeiro!
├── DEBUG_GUIDE_v4_1.md          ← Debug completo
└── N8N_VS_API_COMPARISON.md     ← Comparação técnica
```

---

## 🚀 GUIA DE INÍCIO RÁPIDO

### 1ª vez usando (15 minutos)

```bash
# 1. Baixe todos os arquivos principais:
#    - main_v4_1_expert.py
#    - requirements_v4.txt
#    - test_v4_1.py

# 2. Leia a documentação:
cat README_v4_1_QUICKSTART.md

# 3. Setup:
mv main_v4_1_expert.py main.py
pip install -r requirements_v4.txt
pip install colorama  # Para teste colorido

# 4. Execute:
python main.py  # Terminal 1

# 5. Teste:
python3 test_v4_1.py  # Terminal 2

# 6. Analise resultado:
#    - Se ✅ EXCELLENT → deploy em produção
#    - Se ⚠️ GOOD → otimizar
#    - Se ❌ LOW → ler DEBUG_GUIDE_v4_1.md
```

### Já usou antes (2 minutos)

```bash
# Deploy direto
mv main_v4_1_expert.py main.py
python main.py

# Teste
curl "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" | jq
```

---

## 🎯 ROADMAP DE LEITURA

### Nível 1: Usuário
1. `README_v4_1_QUICKSTART.md` - Começar
2. Rodar `test_v4_1.py` - Validar
3. Deploy - Produção

### Nível 2: Troubleshooter
1. `DEBUG_GUIDE_v4_1.md` - Debug completo
2. Analisar JSON debug
3. Filtros jq para diagnóstico

### Nível 3: Developer
1. `N8N_VS_API_COMPARISON.md` - Entender arquitetura
2. `main_v4_1_expert.py` - Código fonte
3. Modificar/otimizar

---

## 📊 MATRIZ DE DECISÃO

| Situação | Arquivo | Ação |
|----------|---------|------|
| Primeira vez | README_v4_1_QUICKSTART.md | Ler completo |
| match_rate < 70% | DEBUG_GUIDE_v4_1.md | Diagnosticar |
| Quer entender como funciona | N8N_VS_API_COMPARISON.md | Estudar fluxo |
| Produção OK, quer otimizar | main_v4_1_expert.py | Modificar código |
| Deploy Railway | deploy_v4.sh | Executar |

---

## ⚡ COMANDOS ÚTEIS

### Instalação
```bash
pip install -r requirements_v4.txt
pip install colorama
```

### Execução
```bash
# Local
python main.py

# Background
nohup python main.py > api.log 2>&1 &
```

### Testes
```bash
# Teste completo
python3 test_v4_1.py

# Teste manual
curl "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" | jq

# Apenas match rate
curl -s "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" | jq '.comparison'
```

### Debug
```bash
# Ver todos os requests HTTP
curl -s "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" | jq '.debug.http_requests'

# Ver apenas erros
curl -s "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" | jq '.debug.errors'

# Ver WOs encontrados
curl -s "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" | jq '.wo_discovery'

# Ver BRs encontrados
curl -s "http://localhost:8000/api/v1/search?molecule_name=Darolutamide" | jq '.br_patents | length'
```

---

## 📞 SUPORTE

### Problemas Comuns

**❌ Zero WOs encontrados**
→ Leia: `DEBUG_GUIDE_v4_1.md` seção "Zero WOs encontrados"

**❌ WOs encontrados mas zero BRs**
→ Leia: `DEBUG_GUIDE_v4_1.md` seção "WOs encontrados mas zero BRs"

**❌ BRs encontrados mas sem detalhes**
→ Leia: `DEBUG_GUIDE_v4_1.md` seção "BRs encontrados mas sem detalhes"

### Enviar Diagnóstico

Se nada resolver:
1. Execute `python3 test_v4_1.py`
2. Copie o arquivo `test_result_darolutamide_*.json`
3. Envie junto com descrição do problema

Foco em:
- `debug.http_requests` (todas as requisições)
- `debug.errors` (erros detectados)
- `wo_discovery` (quantos WOs)
- `family_navigation` (quantos BRs)

---

## 🎓 GLOSSÁRIO

**WO** - World patent (WIPO)  
**BR** - Brazilian patent (INPI)  
**SerpAPI** - Search Engine Results Page API  
**json_endpoint** - URL retornada por SerpAPI para worldwide apps  
**serpapi_link** - URL retornada por SerpAPI para detalhes da patente  
**worldwide_applications** - Família de patentes em vários países  
**match_rate** - % de cobertura vs Cortellis  

---

## ✅ CHECKLIST PRÉ-DEPLOY

- [ ] Baixou `main_v4_1_expert.py`
- [ ] Baixou `requirements_v4.txt`
- [ ] Baixou `test_v4_1.py`
- [ ] Leu `README_v4_1_QUICKSTART.md`
- [ ] Instalou dependências
- [ ] Executou `test_v4_1.py`
- [ ] Match rate >= 70%
- [ ] Debug errors vazio
- [ ] BRs >= 6 encontrados

Se todos ✅ → **PRONTO PARA PRODUÇÃO!** 🚀
