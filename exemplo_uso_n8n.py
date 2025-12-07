"""
EXEMPLO - Usar SerpAPI Pool no n8n
Substitui API key fixa por pool dinâmico
"""

# ========================================
# ANTES (n8n Code Node) - Key fixa
# ========================================
'''
const apiKey = "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d";
const url = `https://serpapi.com/search.json?q=${query}&api_key=${apiKey}`;
'''

# ========================================
# DEPOIS (n8n Code Node) - Pool
# ========================================
'''
// Pegar key do pool
const poolUrl = "https://pharmyrus-api.railway.app/api/v1/serpapi/key";
const keyResp = await fetch(poolUrl);
const { key } = await keyResp.json();

// Usar key nas chamadas SerpAPI
const url = `https://serpapi.com/search.json?q=${query}&api_key=${key}`;
const response = await fetch(url);
'''

# ========================================
# MONITORAR STATUS
# ========================================
'''
const statusUrl = "https://pharmyrus-api.railway.app/api/v1/serpapi/status";
const status = await fetch(statusUrl).then(r => r.json());

console.log(`Keys disponíveis: ${status.available}`);
console.log(`Queries usadas: ${status.used_total}`);
'''

# ========================================
# PYTHON DIRETO
# ========================================
"""
import requests

# Pegar key
r = requests.get("https://pharmyrus-api.railway.app/api/v1/serpapi/key")
key = r.json()["key"]

# Usar
serpapi_url = f"https://serpapi.com/search.json?q=test&api_key={key}"
result = requests.get(serpapi_url).json()
"""
