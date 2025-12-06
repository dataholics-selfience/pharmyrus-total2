#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  PHARMYRUS v3.0 - VERIFICAÇÃO PRÉ-DEPLOY        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# 1. Verificar número de arquivos
echo "✓ Verificando número de arquivos..."
FILE_COUNT=$(ls -1A | wc -l)
if [ "$FILE_COUNT" -eq 8 ]; then
    echo "  ✅ OK - 8 arquivos encontrados"
else
    echo "  ❌ ERRO - Esperado 8 arquivos, encontrado $FILE_COUNT"
    echo "  Arquivos encontrados:"
    ls -1A | sed 's/^/    /'
    ERRORS=$((ERRORS + 1))
fi

# 2. Verificar runtime.txt
echo ""
echo "✓ Verificando runtime.txt..."
if [ -f "runtime.txt" ]; then
    RUNTIME=$(cat runtime.txt)
    if [ "$RUNTIME" = "python-3.11" ]; then
        echo "  ✅ OK - python-3.11 (correto)"
    else
        echo "  ❌ ERRO - Conteúdo: '$RUNTIME'"
        echo "  ❌ Deveria ser: 'python-3.11'"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ❌ ERRO - runtime.txt não encontrado"
    ERRORS=$((ERRORS + 1))
fi

# 3. Verificar nixpacks.toml NÃO existe
echo ""
echo "✓ Verificando ausência de nixpacks.toml..."
if [ -f "nixpacks.toml" ]; then
    echo "  ❌ ERRO - nixpacks.toml existe (deve ser removido)"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ OK - nixpacks.toml não existe"
fi

# 4. Verificar railway.json NÃO existe
echo ""
echo "✓ Verificando ausência de railway.json..."
if [ -f "railway.json" ]; then
    echo "  ❌ ERRO - railway.json existe (deve ser removido)"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ OK - railway.json não existe"
fi

# 5. Verificar main.py existe e tem layer_statistics
echo ""
echo "✓ Verificando main.py..."
if [ -f "main.py" ]; then
    if grep -q "layer_statistics" main.py; then
        echo "  ✅ OK - main.py tem layer_statistics (v3.0)"
    else
        echo "  ❌ ERRO - main.py NÃO tem layer_statistics"
        echo "  ❌ Você está usando versão antiga do main.py"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ❌ ERRO - main.py não encontrado"
    ERRORS=$((ERRORS + 1))
fi

# 6. Verificar Procfile
echo ""
echo "✓ Verificando Procfile..."
if [ -f "Procfile" ]; then
    if grep -q "uvicorn main:app" Procfile; then
        echo "  ✅ OK - Procfile correto"
    else
        echo "  ❌ ERRO - Procfile com comando incorreto"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ❌ ERRO - Procfile não encontrado"
    ERRORS=$((ERRORS + 1))
fi

# 7. Verificar requirements.txt
echo ""
echo "✓ Verificando requirements.txt..."
if [ -f "requirements.txt" ]; then
    if grep -q "fastapi" requirements.txt; then
        echo "  ✅ OK - requirements.txt tem FastAPI"
    else
        echo "  ❌ ERRO - requirements.txt sem FastAPI"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ❌ ERRO - requirements.txt não encontrado"
    ERRORS=$((ERRORS + 1))
fi

# RESULTADO FINAL
echo ""
echo "════════════════════════════════════════════════════"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════╗"
    echo "║                                                  ║"
    echo "║      ✅ TUDO CERTO! PODE FAZER GIT PUSH         ║"
    echo "║                                                  ║"
    echo "║  Próximos passos:                                ║"
    echo "║  1. git add .                                    ║"
    echo "║  2. git commit -m 'Pharmyrus v3.0'               ║"
    echo "║  3. git push                                     ║"
    echo "║                                                  ║"
    echo "║  Build Railway vai PASSAR! ✅                   ║"
    echo "║                                                  ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo ""
    exit 0
else
    echo "╔══════════════════════════════════════════════════╗"
    echo "║                                                  ║"
    echo "║      ❌ $ERRORS ERRO(S) ENCONTRADO(S)                  ║"
    echo "║                                                  ║"
    echo "║  NÃO FAÇA GIT PUSH!                              ║"
    echo "║  Corrija os erros acima primeiro.                ║"
    echo "║                                                  ║"
    echo "║  Você provavelmente está usando o arquivo        ║"
    echo "║  ERRADO. Baixe:                                  ║"
    echo "║                                                  ║"
    echo "║  📦 pharmyrus-api-v3-FINAL.tar.gz               ║"
    echo "║                                                  ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo ""
    exit 1
fi
