#!/usr/bin/env python3
"""
TESTE RÁPIDO v4.2 - Verifica se WOs estão sendo extraídos
==========================================================
Testa APENAS os 2 primeiros layers:
1. PubChem → dev codes
2. WO Discovery → extração de WOs

Uso:
    python3 test_wo_extraction.py
"""

import asyncio
import sys
sys.path.insert(0, '/home/claude/pharmyrus-api')

from main_v4_2_production import layer1_pubchem, layer2_wo_discovery, DebugStats

async def test_wo_extraction():
    print("="*70)
    print("TESTE RÁPIDO: EXTRAÇÃO DE WOs")
    print("="*70)
    print("\nTestando com: Darolutamide")
    print("Esperado: 10-15 WOs")
    print("="*70)
    
    debug = DebugStats()
    
    # Layer 1: PubChem
    print("\n🔹 LAYER 1: PubChem")
    pubchem = await layer1_pubchem("darolutamide", debug)
    
    print(f"\nDev Codes: {len(pubchem['dev_codes'])}")
    for i, code in enumerate(pubchem['dev_codes'][:5]):
        print(f"  {i+1}. {code}")
    if len(pubchem['dev_codes']) > 5:
        print(f"  ... +{len(pubchem['dev_codes']) - 5} more")
    
    print(f"\nCAS: {pubchem['cas_number']}")
    
    # Layer 2: WO Discovery
    print(f"\n🔹 LAYER 2: WO Discovery")
    wo_numbers = await layer2_wo_discovery(
        "darolutamide",
        "Nubeqa",
        pubchem['dev_codes'],
        debug
    )
    
    print(f"\n{'='*70}")
    print("RESULTADO FINAL")
    print(f"{'='*70}")
    
    if len(wo_numbers) == 0:
        print("❌ FALHA: Nenhum WO encontrado!")
        print("\nDEBUG:")
        print(f"Total requests: {len(debug.requests)}")
        print(f"Successful requests: {len([r for r in debug.requests if r.status_code == 200])}")
        print(f"Errors: {len(debug.errors)}")
        
        if debug.errors:
            print("\nERROS:")
            for err in debug.errors[:5]:
                print(f"  - {err}")
        
        return False
    
    print(f"✅ SUCESSO: {len(wo_numbers)} WOs encontrados")
    print("\nWOs extraídos:")
    for i, wo in enumerate(wo_numbers, 1):
        print(f"  {i:2d}. {wo}")
    
    print(f"\n{'='*70}")
    print("ESTATÍSTICAS")
    print(f"{'='*70}")
    print(f"Total requests HTTP: {len(debug.requests)}")
    print(f"Requests bem-sucedidos: {len([r for r in debug.requests if r.status_code == 200])}")
    print(f"Requests falhados: {len([r for r in debug.requests if r.status_code != 200])}")
    print(f"Tempo total: {sum(l.duration_seconds for l in debug.layers):.1f}s")
    
    # Verificação final
    if len(wo_numbers) >= 10:
        print("\n✅ EXCELENTE! 10+ WOs encontrados")
        return True
    elif len(wo_numbers) >= 5:
        print("\n⚠️  OK: 5+ WOs encontrados (esperado: 10+)")
        return True
    else:
        print("\n❌ BAIXO: Menos de 5 WOs encontrados")
        return False

if __name__ == "__main__":
    print("\nIniciando teste...\n")
    success = asyncio.run(test_wo_extraction())
    
    if success:
        print("\n" + "="*70)
        print("🚀 TESTE PASSOU! API está extraindo WOs corretamente.")
        print("="*70)
        print("\nPróximos passos:")
        print("1. python3 main_v4_2_production.py  # Inicia API")
        print("2. curl 'http://localhost:8000/api/v1/search?molecule_name=darolutamide&brand_name=Nubeqa'")
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ TESTE FALHOU! WOs não estão sendo extraídos.")
        print("="*70)
        print("\nVerifique:")
        print("1. SerpAPI key está correta?")
        print("2. SerpAPI tem créditos?")
        print("3. Internet está funcionando?")
        sys.exit(1)
