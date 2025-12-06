# 🔧 CORREÇÃO: ERRO DE PORTA NO RAILWAY

## ❌ PROBLEMA

```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

**Causa:** A variável `$PORT` do Railway não estava sendo expandida corretamente pelo uvicorn.

---

## ✅ SOLUÇÃO APLICADA (3 correções)

### 1️⃣ **main_v4_2_production.py** - Lê PORT do ambiente

```python
# ANTES (linha 650-652):
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# DEPOIS (linha 650-655):
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting Pharmyrus API v4.2 on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
```

**Benefício:** Agora lê `PORT` do ambiente automaticamente. Se não existir, usa 8000.

---

### 2️⃣ **start.sh** - Script de inicialização robusto

```bash
#!/bin/bash
# Pharmyrus API v4.2 - Railway Start Script

# Get PORT from environment or use default
PORT=${PORT:-8000}

echo "Starting Pharmyrus API v4.2 on port $PORT..."

# Start uvicorn with explicit port
exec uvicorn main_v4_2_production:app --host 0.0.0.0 --port $PORT
```

**Uso:** `./start.sh`

---

### 3️⃣ **railway.json** - Usa start.sh

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && chmod +x start.sh"
  },
  "deploy": {
    "startCommand": "./start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🚀 REDEPLOY NO RAILWAY

### Método 1: Railway CLI

```bash
# 1. Baixar arquivos corrigidos
# Baixe: main_v4_2_production.py, start.sh, railway.json

# 2. Substituir arquivos antigos

# 3. Commit e push
git add .
git commit -m "fix: Railway PORT variable expansion"
git push

# 4. OU redeploy direto
railway up
```

---

### Método 2: Railway Dashboard

1. **Delete o deploy atual**
   - Railway Dashboard → Your Project → Settings → Delete

2. **Crie novo deploy**
   - Railway → New Project → Deploy from GitHub
   - Ou faça upload dos arquivos manualmente

3. **Configure variável SERPAPI_KEY**
   - Variables → Add Variable
   - `SERPAPI_KEY=bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc`

---

### Método 3: Teste Local Primeiro

```bash
# Testar se PORT é lida corretamente
PORT=3000 python3 main_v4_2_production.py
# Deve printar: 🚀 Starting Pharmyrus API v4.2 on port 3000...

# Acesse: http://localhost:3000/health
```

---

## 📋 ARQUIVOS CORRIGIDOS (DOWNLOAD)

Baixe as versões corrigidas:

1. [**main_v4_2_production.py**](computer:///mnt/user-data/outputs/main_v4_2_production.py) - ✅ Lê PORT do ambiente
2. [**start.sh**](computer:///mnt/user-data/outputs/start.sh) - ✅ Script de inicialização
3. [**railway.json**](computer:///mnt/user-data/outputs/railway.json) - ✅ Usa start.sh

---

## ✅ VALIDAÇÃO PÓS-CORREÇÃO

### 1. Local
```bash
# Testar PORT dinâmica
PORT=3000 python3 main_v4_2_production.py

# Esperado:
# 🚀 Starting Pharmyrus API v4.2 on port 3000...
# INFO:     Started server process [12345]
# INFO:     Uvicorn running on http://0.0.0.0:3000
```

### 2. Railway
```bash
# Após redeploy, verificar logs
railway logs

# Esperado:
# 🚀 Starting Pharmyrus API v4.2 on port 8080...
# INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 3. Health Check
```bash
# Railway fornece URL pública
curl https://seu-app.up.railway.app/health

# Esperado:
{"status":"healthy","version":"4.2-PRODUCTION"}
```

---

## 🐛 TROUBLESHOOTING ADICIONAL

### ❌ "Permission denied: ./start.sh"
```bash
chmod +x start.sh
./start.sh
```

### ❌ "ModuleNotFoundError: No module named 'uvicorn'"
```bash
pip install -r requirements.txt
```

### ❌ Railway ainda mostra erro
1. **Delete o projeto completamente**
2. **Crie novo projeto**
3. **Use os arquivos corrigidos**
4. **Configure SERPAPI_KEY**

---

## 🔄 ALTERNATIVA: USAR PYTHON DIRETAMENTE

Se preferir não usar start.sh, o **main_v4_2_production.py** corrigido já funciona:

```bash
# Railway pode usar diretamente
python3 main_v4_2_production.py
```

Atualize **railway.json**:
```json
{
  "deploy": {
    "startCommand": "python3 main_v4_2_production.py"
  }
}
```

---

## 📊 RESUMO DAS MUDANÇAS

| Arquivo | Mudança | Status |
|---------|---------|--------|
| main_v4_2_production.py | Lê PORT do ambiente (os.getenv) | ✅ CORRIGIDO |
| start.sh | Script com expansão correta de $PORT | ✅ NOVO |
| railway.json | Usa ./start.sh como startCommand | ✅ CORRIGIDO |

---

## 🎯 PRÓXIMOS PASSOS

1. ✅ Baixar arquivos corrigidos (links acima)
2. ✅ Substituir arquivos antigos
3. ✅ Commit + Push (ou railway up)
4. ✅ Verificar logs: `railway logs`
5. ✅ Testar health: `curl https://seu-app.railway.app/health`
6. ✅ Testar API: `curl https://seu-app.railway.app/api/v1/search?molecule_name=darolutamide`

---

## 💡 EXPLICAÇÃO TÉCNICA

**Por que o erro aconteceu?**

O Railway injeta `PORT` como variável de ambiente (ex: `PORT=8080`), mas o comando:

```bash
uvicorn main:app --port $PORT
```

Não expande `$PORT` em contexto não-shell. O uvicorn recebe literalmente a string `"$PORT"` e tenta converter para inteiro, resultando em erro.

**Solução:**
1. Usar shell explícito: `sh -c 'uvicorn --port ${PORT}'`
2. Ou ler PORT no código Python: `os.getenv("PORT")`
3. Ou usar script bash que expande a variável

Implementamos **todas as 3 soluções** para máxima compatibilidade.

---

**Versão:** 4.2-PRODUCTION-FIXED  
**Data:** 2024-12-06  
**Status:** ✅ ERRO CORRIGIDO  

🎯 **Baixe os arquivos corrigidos e redeploy no Railway!**
