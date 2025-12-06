#!/usr/bin/env python3
"""
DIAGNÓSTICO SERPAPI - Testa se a chave está funcionando
========================================================
"""

import httpx
import asyncio
import json

SERPAPI_KEY = "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d"

async def test_serpapi():
    print("="*70)
    print("DIAGNÓSTICO SERPAPI")
    print("="*70)
    
    # Test: Google search (o que importa)
    print("\n🔹 Test: Busca Google (darolutamide patent WO2011)...")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                "https://serpapi.com/search.json",
                params={
                    "engine": "google",
                    "q": "darolutamide patent WO2011",
                    "api_key": SERPAPI_KEY,
                    "num": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                organic = data.get("organic_results", [])
                print(f"✅ Busca funcionou: {len(organic)} resultados")
                
                if len(organic) > 0:
                    print(f"\n   Primeiro resultado:")
                    print(f"   Title: {organic[0].get('title', 'N/A')[:70]}...")
                    
                    # Check for WO numbers
                    import re
                    wo_pattern = re.compile(r"WO[\s-]?(\d{4})[\s\/]?(\d{6})", re.IGNORECASE)
                    
                    found_wos = []
                    for item in organic:
                        text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('link', '')}"
                        matches = wo_pattern.findall(text)
                        for year, num in matches:
                            wo = f"WO{year}{num}"
                            if wo not in found_wos:
                                found_wos.append(wo)
                    
                    if found_wos:
                        print(f"\n   ✅ WOs encontrados: {len(found_wos)}")
                        for wo in found_wos[:8]:
                            print(f"      - {wo}")
                        if len(found_wos) > 8:
                            print(f"      ... +{len(found_wos) - 8} more")
                    else:
                        print(f"\n   ⚠️  Nenhum WO encontrado nesta query")
                
                return len(found_wos) > 0 if found_wos else False
            elif response.status_code == 401:
                print(f"❌ Erro: API Key inválida (401)")
                return False
            elif response.status_code == 403:
                print(f"❌ Erro: Sem créditos ou acesso negado (403)")
                print(f"\n   Verifique: https://serpapi.com/dashboard")
                return False
            elif response.status_code == 429:
                print(f"❌ Erro: Rate limit atingido (429)")
                print(f"\n   Aguarde alguns minutos e tente novamente")
                return False
            else:
                print(f"❌ Erro: HTTP {response.status_code}")
                print(response.text[:300])
                return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("\nIniciando diagnóstico...\n")
    success = asyncio.run(test_serpapi())
    
    if success:
        print("\n" + "="*70)
        print("✅ SERPAPI FUNCIONANDO!")
        print("="*70)
        print("\nAgora rode: python3 test_wo_extraction.py")
    else:
        print("\n" + "="*70)
        print("❌ SERPAPI COM PROBLEMAS")
        print("="*70)
        print("\nVerifique:")
        print("1. SerpAPI key está correta?")
        print("2. Tem créditos disponíveis?")
        print("3. Internet funcionando?")
