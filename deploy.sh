#!/bin/bash
# Pharmyrus API v4.2 - Deploy Script

set -e

echo "======================================"
echo "PHARMYRUS API v4.2 - DEPLOY"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado"
    echo "Copiando .env.example para .env..."
    cp .env.example .env
    echo "✅ Por favor, edite o arquivo .env com suas configurações"
    exit 1
fi

# Load environment variables
source .env

# Check SerpAPI key
if [ -z "$SERPAPI_KEY" ]; then
    echo "❌ SERPAPI_KEY não configurada no .env"
    exit 1
fi

echo ""
echo "Escolha o método de deploy:"
echo "1. Docker"
echo "2. Railway"
echo "3. Local (Python)"
echo "4. Systemd (Linux service)"
echo ""
read -p "Opção: " option

case $option in
    1)
        echo ""
        echo "🐳 DEPLOY DOCKER"
        echo "======================================"
        
        # Build image
        echo "Building Docker image..."
        docker build -t pharmyrus-api:v4.2 .
        
        # Stop existing container
        echo "Stopping existing container..."
        docker stop pharmyrus-api 2>/dev/null || true
        docker rm pharmyrus-api 2>/dev/null || true
        
        # Run container
        echo "Starting container..."
        docker run -d \
            --name pharmyrus-api \
            -p 8000:8000 \
            -e SERPAPI_KEY=$SERPAPI_KEY \
            --restart unless-stopped \
            pharmyrus-api:v4.2
        
        echo ""
        echo "✅ Deploy concluído!"
        echo "API rodando em: http://localhost:8000"
        echo "Health check: http://localhost:8000/health"
        echo ""
        echo "Para ver logs: docker logs -f pharmyrus-api"
        ;;
        
    2)
        echo ""
        echo "🚂 DEPLOY RAILWAY"
        echo "======================================"
        
        # Check Railway CLI
        if ! command -v railway &> /dev/null; then
            echo "❌ Railway CLI não encontrado"
            echo "Instale com: npm i -g @railway/cli"
            exit 1
        fi
        
        # Login
        echo "Fazendo login no Railway..."
        railway login
        
        # Link project or create new
        echo "Linking to Railway project..."
        railway link || railway init
        
        # Set environment variables
        echo "Configurando variáveis de ambiente..."
        railway variables set SERPAPI_KEY=$SERPAPI_KEY
        
        # Deploy
        echo "Deploying to Railway..."
        railway up
        
        echo ""
        echo "✅ Deploy concluído!"
        echo "Acesse: railway open"
        ;;
        
    3)
        echo ""
        echo "🐍 DEPLOY LOCAL"
        echo "======================================"
        
        # Install dependencies
        echo "Instalando dependências..."
        pip install -r requirements.txt
        
        # Run API
        echo "Iniciando API..."
        echo ""
        echo "✅ API iniciando..."
        echo "Acesse: http://localhost:8000"
        echo "Para parar: Ctrl+C"
        echo ""
        python3 main_v4_2_production.py
        ;;
        
    4)
        echo ""
        echo "⚙️  DEPLOY SYSTEMD"
        echo "======================================"
        
        # Get current directory
        CURRENT_DIR=$(pwd)
        
        # Create systemd service file
        echo "Criando arquivo de serviço..."
        sudo tee /etc/systemd/system/pharmyrus.service > /dev/null <<EOF
[Unit]
Description=Pharmyrus API v4.2
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="SERPAPI_KEY=$SERPAPI_KEY"
ExecStart=$(which python3) $CURRENT_DIR/main_v4_2_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        # Reload systemd
        echo "Recarregando systemd..."
        sudo systemctl daemon-reload
        
        # Enable and start service
        echo "Habilitando serviço..."
        sudo systemctl enable pharmyrus
        
        echo "Iniciando serviço..."
        sudo systemctl start pharmyrus
        
        echo ""
        echo "✅ Deploy concluído!"
        echo ""
        echo "Comandos úteis:"
        echo "  Status:  sudo systemctl status pharmyrus"
        echo "  Logs:    sudo journalctl -u pharmyrus -f"
        echo "  Restart: sudo systemctl restart pharmyrus"
        echo "  Stop:    sudo systemctl stop pharmyrus"
        ;;
        
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

echo ""
echo "======================================"
echo "TESTE A API:"
echo "======================================"
echo "curl http://localhost:8000/health"
echo ""
echo "curl 'http://localhost:8000/api/v1/search?molecule_name=darolutamide&brand_name=Nubeqa' | jq ."
echo ""
