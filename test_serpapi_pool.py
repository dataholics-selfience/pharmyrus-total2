#!/usr/bin/env python3
"""
Test Script for SerpAPI Pool Manager
Testa funcionalidades do gerenciador de pool de API keys
"""

import sys
import os
import requests
import json
from time import sleep

# URL da API (ajuste conforme necessário)
BASE_URL = "http://localhost:8000"  # Para testes locais
# BASE_URL = "https://pharmyrus-api.up.railway.app"  # Para produção

def print_header(text):
    """Imprime header formatado"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_section(text):
    """Imprime seção formatada"""
    print(f"\n📌 {text}")
    print("-"*70)

def test_health():
    """Testa endpoint de health"""
    print_section("1. Testing Health Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   SerpAPI Pool: {'Enabled' if data.get('features', {}).get('serpapi_pool') else 'Disabled'}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pool_status():
    """Testa endpoint de status do pool"""
    print_section("2. Testing Pool Status Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/serpapi/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Pool Status:")
            print(f"   Total Keys: {data['total_keys']}")
            print(f"   Total Limit: {data['total_limit']}")
            print(f"   Available Queries: {data['total_available_queries']}")
            print(f"   Used Queries: {data['total_used_queries']}")
            print(f"   Usage: {data['usage_percentage']}%")
            print(f"   Total Requests: {data['total_requests_made']}")
            
            print("\n   Individual Keys:")
            for i, key_info in enumerate(data['keys'][:5], 1):  # Mostra primeiras 5
                print(f"   {i}. {key_info['instance']}")
                print(f"      Status: {key_info['status']}")
                print(f"      Used: {key_info['used']}/{key_info['limit']}")
                print(f"      Remaining: {key_info['remaining']}")
            
            if len(data['keys']) > 5:
                print(f"   ... e mais {len(data['keys']) - 5} keys")
            
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_usage_summary():
    """Testa endpoint de resumo de uso"""
    print_section("3. Testing Usage Summary Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/serpapi/usage")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Usage Summary:")
            
            pool = data['pool_info']
            print(f"   Pool Info:")
            print(f"   - Total Keys: {pool['total_keys']}")
            print(f"   - Total Limit: {pool['total_limit']}")
            print(f"   - Available: {pool['total_available']}")
            print(f"   - Usage: {pool['usage_percentage']}%")
            
            status = data['current_status']
            print(f"\n   Current Status:")
            print(f"   - Requests Made: {status['requests_made']}")
            print(f"   - Queries Used: {status['queries_used']}")
            print(f"   - Queries Remaining: {status['queries_remaining']}")
            
            print(f"\n   Health: {data['health'].upper()}")
            
            return True
        else:
            print(f"❌ Usage summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_key():
    """Testa obtenção de uma key do pool"""
    print_section("4. Testing Get Key Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/serpapi/key")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Key obtained successfully!")
                print(f"   Key: {data['key'][:20]}...")
                return True
            else:
                print(f"⚠️ {data['message']}")
                return False
        else:
            print(f"❌ Get key failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_multiple_requests():
    """Simula múltiplas requisições"""
    print_section("5. Simulating Multiple Key Requests")
    
    num_requests = 5
    print(f"   Requesting {num_requests} keys...")
    
    success_count = 0
    fail_count = 0
    
    for i in range(num_requests):
        try:
            response = requests.get(f"{BASE_URL}/api/v1/serpapi/key")
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    success_count += 1
                    print(f"   {i+1}. ✅ Key obtained: {data['key'][:20]}...")
                else:
                    fail_count += 1
                    print(f"   {i+1}. ⚠️ {data['message']}")
            else:
                fail_count += 1
                print(f"   {i+1}. ❌ HTTP {response.status_code}")
            
            sleep(0.2)  # Pequeno delay entre requisições
            
        except Exception as e:
            fail_count += 1
            print(f"   {i+1}. ❌ Error: {e}")
    
    print(f"\n   Results: {success_count} success, {fail_count} failed")
    return success_count > 0

def test_molecule_search():
    """Testa busca de molécula (usa keys do pool)"""
    print_section("6. Testing Molecule Search (Uses Pool Keys)")
    
    molecule = "Darolutamide"
    print(f"   Searching for: {molecule}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/search",
            params={"molecule_name": molecule, "deep_search": False},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search completed:")
            print(f"   WO Numbers found: {data['search_result']['total_wo_discovered']}")
            print(f"   BR from EPO: {data['search_result']['total_br_from_epo']}")
            print(f"   Execution time: {data['execution_time_seconds']}s")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print_header("PHARMYRUS API - SERPAPI POOL MANAGER TESTS")
    print(f"Base URL: {BASE_URL}\n")
    
    results = []
    
    # Teste 1: Health
    results.append(("Health Check", test_health()))
    
    # Teste 2: Pool Status
    results.append(("Pool Status", test_pool_status()))
    
    # Teste 3: Usage Summary
    results.append(("Usage Summary", test_usage_summary()))
    
    # Teste 4: Get Key
    results.append(("Get Key", test_get_key()))
    
    # Teste 5: Multiple Requests
    results.append(("Multiple Requests", test_multiple_requests()))
    
    # Teste 6: Molecule Search (opcional, mais demorado)
    if "--full" in sys.argv:
        results.append(("Molecule Search", test_molecule_search()))
    
    # Resumo
    print_header("TEST RESULTS SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*70}\n")
    
    return passed == total

if __name__ == "__main__":
    print("\n🧪 Pharmyrus API Test Suite")
    print("=" * 70)
    
    # Verifica argumentos
    if "--help" in sys.argv:
        print("\nUsage:")
        print("  python test_serpapi_pool.py           # Run basic tests")
        print("  python test_serpapi_pool.py --full    # Run all tests (including molecule search)")
        print("  python test_serpapi_pool.py --help    # Show this help")
        sys.exit(0)
    
    # Permite customizar URL
    if "--url" in sys.argv:
        idx = sys.argv.index("--url")
        if idx + 1 < len(sys.argv):
            BASE_URL = sys.argv[idx + 1]
    
    # Executa testes
    success = run_all_tests()
    
    # Exit code
    sys.exit(0 if success else 1)
