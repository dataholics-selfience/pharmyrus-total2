#!/usr/bin/env python3
"""
TESTE RÁPIDO - Testa AMBAS as SerpAPI keys
===========================================
"""

import httpx
import asyncio
import re

# Keys encontradas no n8n
KEYS = [
    "bc20bca64032a7ac59abf330bbdeca80aa79cd72bb208059056b10fb6e33e4bc",  # INPI REAL
    "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d",  # Patent Search v4.1
]

async def test_key(key, key_name):
    print(f"\n{'='*70}")
    print(f"Testando: {key_name}")
    print(f"Key: {key[:20]}...{key[-10:]}")
    print(f"{'='*70}")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "engine": "google",
                    "q": "darolutamide patent WO2011",
                    "api_key": key,
                    "num": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                organic = data.get("organic_results", [])
                
                print(f"✅ Status: 200 OK")
                print(f"✅ Resultados: {len(organic)}")
                
                # Extract WOs
                wo_pattern = re.compile(r"WO[\s-]?(\d{4})[\s\/]?(\d{6})", re.IGNORECASE)
                found_wos = set()
                
                for item in organic:
                    text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('link', '')}"
                    matches = wo_pattern.findall(text)
                    for year, num in matches:
                        found_wos.add(f"WO{year}{num}")
                
                if found_wos:
                    print(f"✅ WOs encontrados: {len(found_wos)}")
                    for wo in sorted(found_wos)[:5]:
                        print(f"   - {wo}")
                    if len(found_wos) > 5:
                        print(f"   ... +{len(found_wos) - 5} more")
                    
                    return key, len(found_wos)
                else:
                    print(f"⚠️  Nenhum WO encontrado")
                    return None, 0
            
            elif response.status_code == 401:
                print(f"❌ 401: Key inválida")
                return None, 0
            elif response.status_code == 403:
                print(f"❌ 403: Sem créditos ou bloqueado")
                return None, 0
            elif response.status_code == 429:
                print(f"❌ 429: Rate limit")
                return None, 0
            else:
                print(f"❌ HTTP {response.status_code}")
                return None, 0
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None, 0

async def main():
    print("\n" + "="*70)
    print("TESTANDO MÚLTIPLAS SERPAPI KEYS")
    print("="*70)
    
    best_key = None
    best_count = 0
    
    for i, key in enumerate(KEYS):
        key_name = ["INPI REAL", "Patent Search v4.1"][i]
        working_key, wo_count = await test_key(key, key_name)
        
        if working_key and wo_count > best_count:
            best_key = working_key
            best_count = wo_count
        
        await asyncio.sleep(1)
    
    print(f"\n" + "="*70)
    if best_key:
        print(f"✅ SUCESSO! Key funcionando encontrada")
        print(f"="*70)
        print(f"\nKey: {best_key[:20]}...{best_key[-10:]}")
        print(f"WOs encontrados: {best_count}")
        print(f"\n📝 COPIE ESTA KEY PARA main_v4_2_production.py:")
        print(f'SERPAPI_KEY = "{best_key}"')
    else:
        print(f"❌ NENHUMA KEY FUNCIONAL")
        print(f"="*70)
        print(f"\nPossíveis causas:")
        print(f"1. Sem créditos em ambas as keys")
        print(f"2. Ambiente sem acesso à internet")
        print(f"3. SerpAPI bloqueado")
        print(f"\nVerifique: https://serpapi.com/dashboard")

if __name__ == "__main__":
    asyncio.run(main())
