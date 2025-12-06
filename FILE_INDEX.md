# 📂 Pharmyrus v4.0 - File Index

## ARQUIVOS PRINCIPAIS

### 🚀 API Core

**main_v4.py** - API completa v4.0 (USE ESTE!)
- Multi-strategy crawling
- WO discovery robusto
- Family navigation completa
- Debug extensivo
- Auto-retry
- 🎯 **ARQUIVO PRINCIPAL**

**main_v3_backup.py** - Backup da v3.0 (para rollback)
- Mantido para segurança
- Só use se v4.0 falhar completamente

**requirements_v4.txt** - Dependências v4.0
- FastAPI, HTTPX, Pydantic
- Mesmas da v3 (sem dependências novas)

---

## 📚 DOCUMENTAÇÃO

### Para Começar Rápido

**README_v4.md** - Documentação principal
- Quick start
- O que esperar
- Como testar
- Troubleshooting
- 🎯 **LEIA PRIMEIRO!**

**CHEAT_SHEET.md** - Referência rápida
- Comandos principais
- O que verificar
- Como diagnosticar
- Targets e métricas
- 🎯 **CONSULTA RÁPIDA**

### Para Entender as Mudanças

**V3_VS_V4_COMPARISON.md** - Comparação detalhada
- O que mudou e por quê
- Antes vs Depois
- Fluxos completos
- Lições do n8n
- 🎯 **PARA ENTENDER DIFERENÇAS**

**EXECUTIVE_SUMMARY.md** - Sumário executivo
- Resumo para stakeholders
- Impacto no negócio
- Riscos e mitigações
- ROI
- 🎯 **PARA APRESENTAR**

### Para Testar

**TESTING_GUIDE_v4.md** - Guia completo de testes
- Como testar passo a passo
- O que verificar em cada etapa
- Como diagnosticar problemas
- Exemplos de respostas
- 🎯 **GUIA DE TESTES**

---

## 🛠️  SCRIPTS

**test_api.py** - Teste automatizado
```bash
python3 test_api.py
```
- Testa 5 moléculas
- Gera relatório detalhado
- Colorized output
- 🎯 **PARA VALIDAÇÃO RÁPIDA**

**deploy_v4.sh** - Script de deploy
```bash
./deploy_v4.sh [local|railway|rollback|test|compare]
```
- Deploy local ou Railway
- Rollback automático
- Teste integrado
- Comparação v3 vs v4
- 🎯 **PARA DEPLOY**

---

## 📊 QUANDO USAR CADA ARQUIVO

### Cenário 1: "Quero começar agora"
1. **README_v4.md** - Entenda o básico
2. **deploy_v4.sh local** - Rode local
3. **test_api.py** - Valide que funciona
4. **CHEAT_SHEET.md** - Referência rápida

### Cenário 2: "Quero entender o que mudou"
1. **V3_VS_V4_COMPARISON.md** - Diferenças principais
2. **README_v4.md** - Features novas
3. **main_v4.py** - Código fonte

### Cenário 3: "Quero testar antes de deploy"
1. **TESTING_GUIDE_v4.md** - Guia completo
2. **test_api.py** - Testes automatizados
3. **deploy_v4.sh test** - Teste integrado
4. **CHEAT_SHEET.md** - Debug rápido

### Cenário 4: "Quero fazer deploy"
1. **deploy_v4.sh local** - Teste local primeiro
2. **test_api.py** - Valide funcionamento
3. **deploy_v4.sh railway** - Deploy production
4. **Monitor Railway dashboard**

### Cenário 5: "Algo deu errado"
1. **CHEAT_SHEET.md** - Diagnóstico rápido
2. **TESTING_GUIDE_v4.md** - Troubleshooting detalhado
3. **deploy_v4.sh rollback** - Volta para v3
4. **Enviar debug JSON** para análise

### Cenário 6: "Quero apresentar para stakeholders"
1. **EXECUTIVE_SUMMARY.md** - Apresentação executiva
2. **V3_VS_V4_COMPARISON.md** - Detalhes técnicos
3. **test_api.py results** - Evidências

---

## 📁 ESTRUTURA DE ARQUIVOS

```
pharmyrus-api/
│
├── 🚀 CORE API
│   ├── main_v4.py              # ✅ API v4.0 completa
│   ├── main_v3_backup.py       # Backup v3
│   └── requirements_v4.txt     # Dependencies
│
├── 📚 DOCS - COMEÇAR
│   ├── README_v4.md            # ✅ LEIA PRIMEIRO
│   └── CHEAT_SHEET.md          # ✅ CONSULTA RÁPIDA
│
├── 📚 DOCS - ENTENDER
│   ├── V3_VS_V4_COMPARISON.md  # Diferenças
│   └── EXECUTIVE_SUMMARY.md    # Sumário executivo
│
├── 📚 DOCS - TESTAR
│   ├── TESTING_GUIDE_v4.md     # Guia de testes
│   └── FILE_INDEX.md           # Este arquivo
│
└── 🛠️  SCRIPTS
    ├── test_api.py             # ✅ Teste automatizado
    └── deploy_v4.sh            # ✅ Deploy script
```

---

## 🎯 FLUXO RECOMENDADO

### Para Iniciantes
```
1. README_v4.md (10min)
   ↓
2. deploy_v4.sh local (5min)
   ↓
3. CHEAT_SHEET.md (bookmark para consulta)
   ↓
4. test_api.py (30min)
   ↓
5. Se OK → deploy_v4.sh railway
   ↓
6. Se Problema → TESTING_GUIDE_v4.md
```

### Para Experientes
```
1. V3_VS_V4_COMPARISON.md (5min)
   ↓
2. main_v4.py (review do código)
   ↓
3. test_api.py (validação)
   ↓
4. deploy_v4.sh railway
```

### Para Troubleshooting
```
1. CHEAT_SHEET.md (diagnóstico rápido)
   ↓
2. TESTING_GUIDE_v4.md (troubleshooting detalhado)
   ↓
3. Coletar debug JSON
   ↓
4. Enviar para análise
```

---

## 📝 CHECKLIST DE ARQUIVOS

Antes de deploy, verifique que tem todos:

- [ ] main_v4.py
- [ ] requirements_v4.txt
- [ ] README_v4.md
- [ ] CHEAT_SHEET.md
- [ ] TESTING_GUIDE_v4.md
- [ ] V3_VS_V4_COMPARISON.md
- [ ] EXECUTIVE_SUMMARY.md
- [ ] test_api.py (executável)
- [ ] deploy_v4.sh (executável)
- [ ] FILE_INDEX.md (este arquivo)

---

## 🔄 UPDATES E VERSÕES

### v4.0 (atual)
- ✅ Multi-strategy crawling
- ✅ WO discovery robusto
- ✅ Family navigation
- ✅ Debug extensivo

### v4.1 (futuro)
- [ ] Playwright integration
- [ ] Selenium fallback
- [ ] Smart caching

---

## 💡 DICAS

**Para aprender:**
- Comece pelo README_v4.md
- Use CHEAT_SHEET.md como referência
- Leia TESTING_GUIDE_v4.md antes de testar

**Para deploy:**
- Use deploy_v4.sh (automatiza tudo)
- Teste local primeiro
- Mantenha backup da v3

**Para debug:**
- CHEAT_SHEET.md tem diagnósticos rápidos
- TESTING_GUIDE_v4.md tem troubleshooting completo
- Sempre colete o debug JSON

**Para apresentar:**
- EXECUTIVE_SUMMARY.md para não-técnicos
- V3_VS_V4_COMPARISON.md para técnicos
- test_api.py results como evidência

---

## 🆘 AJUDA RÁPIDA

**"Não sei por onde começar"**
→ README_v4.md

**"Quero testar agora"**
→ deploy_v4.sh local

**"Algo não funciona"**
→ CHEAT_SHEET.md (troubleshooting)

**"Preciso apresentar"**
→ EXECUTIVE_SUMMARY.md

**"Quero entender o código"**
→ main_v4.py + V3_VS_V4_COMPARISON.md

---

*Última atualização: 2024-12-06*
*Versão: 1.0*
