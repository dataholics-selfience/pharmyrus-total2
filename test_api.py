#!/usr/bin/env python3
"""
Pharmyrus API v4.0 - Automated Testing Script
Testa a API com múltiplas moléculas e gera relatório detalhado
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List

# Configuração
API_BASE = "http://localhost:8000"  # Mude para URL do Railway se necessário
TIMEOUT = 180  # 3 minutos por molécula

# Moléculas para teste (com baseline esperado do Cortellis)
TEST_MOLECULES = [
    {"name": "Darolutamide", "expected_brs": 8, "priority": "HIGH"},
    {"name": "Ixazomib", "expected_brs": 6, "priority": "HIGH"},
    {"name": "Niraparib", "expected_brs": 5, "priority": "MEDIUM"},
    {"name": "Olaparib", "expected_brs": 7, "priority": "MEDIUM"},
    {"name": "Venetoclax", "expected_brs": 4, "priority": "LOW"},
]

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Imprime cabeçalho colorido"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

async def test_health() -> bool:
    """Testa se API está online"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API_BASE}/health", timeout=10)
            if r.status_code == 200:
                print_success("API está online!")
                data = r.json()
                print_info(f"Version: {data.get('version')}")
                print_info(f"EPO Token: {'Valid' if data.get('epo_token_valid') else 'Invalid'}")
                return True
    except Exception as e:
        print_error(f"API offline: {e}")
    return False

async def test_molecule(molecule: Dict[str, Any]) -> Dict[str, Any]:
    """Testa uma molécula e retorna resultado"""
    name = molecule["name"]
    expected = molecule["expected_brs"]
    
    print_header(f"Testing: {name}")
    print_info(f"Expected BR patents: {expected}")
    
    result = {
        "molecule": name,
        "expected_brs": expected,
        "status": "unknown",
        "execution_time": 0,
        "findings": {},
        "debug": {},
        "errors": []
    }
    
    start = datetime.now()
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_BASE}/api/v1/search"
            params = {"molecule_name": name, "deep_search": "true"}
            
            print_info(f"Calling API: {url}")
            r = await client.get(url, params=params, timeout=TIMEOUT)
            
            if r.status_code != 200:
                result["status"] = "error"
                result["errors"].append(f"HTTP {r.status_code}")
                print_error(f"HTTP {r.status_code}")
                return result
            
            data = r.json()
            elapsed = (datetime.now() - start).total_seconds()
            result["execution_time"] = elapsed
            
            # Extract key metrics
            findings = {
                "dev_codes": len(data.get("molecule_info", {}).get("dev_codes", [])),
                "cas_found": data.get("molecule_info", {}).get("cas_number") is not None,
                "wos_found": data.get("wo_discovery", {}).get("total_found", 0),
                "wos_with_br": data.get("family_navigation", {}).get("wos_with_br", 0),
                "br_patents_total": data.get("br_patents", {}).get("total", 0),
                "inpi_patents": data.get("inpi_direct", {}).get("total", 0),
                "match_rate": data.get("comparison", {}).get("match_rate", "0%")
            }
            
            result["findings"] = findings
            result["debug"] = data.get("debug", {})
            
            # Determine status
            br_found = findings["br_patents_total"]
            match_rate = float(findings["match_rate"].replace("%", ""))
            
            if br_found >= expected * 0.7:  # 70%+ do esperado
                result["status"] = "excellent"
                print_success(f"Excellent! Found {br_found}/{expected} BRs ({match_rate}%)")
            elif br_found >= expected * 0.5:  # 50%+ do esperado
                result["status"] = "good"
                print_warning(f"Good! Found {br_found}/{expected} BRs ({match_rate}%)")
            elif br_found > 0:
                result["status"] = "partial"
                print_warning(f"Partial success: {br_found}/{expected} BRs ({match_rate}%)")
            else:
                result["status"] = "failed"
                print_error(f"Failed! Found 0/{expected} BRs")
            
            # Print key metrics
            print_info(f"Execution time: {elapsed:.1f}s")
            print_info(f"Dev codes: {findings['dev_codes']}")
            print_info(f"CAS found: {findings['cas_found']}")
            print_info(f"WOs found: {findings['wos_found']}")
            print_info(f"WOs with BR: {findings['wos_with_br']}")
            print_info(f"BR patents: {findings['br_patents_total']}")
            print_info(f"INPI patents: {findings['inpi_patents']}")
            
            # Print debug summary
            debug = result["debug"]
            if debug:
                print_info("\nDebug Summary:")
                
                # Timing
                timing = debug.get("timing", {})
                print_info(f"  WO Discovery: {timing.get('wo_discovery_seconds', 0):.1f}s")
                print_info(f"  Family Navigation: {timing.get('family_navigation_seconds', 0):.1f}s")
                print_info(f"  BR Details: {timing.get('br_details_seconds', 0):.1f}s")
                
                # Success rates
                wo_disc = debug.get("wo_discovery", {})
                fam_nav = debug.get("family_navigation", {})
                br_ext = debug.get("br_extraction", {})
                
                print_info(f"  WO Discovery Success: {wo_disc.get('success_rate', 'N/A')}")
                print_info(f"  Family Navigation Success: {fam_nav.get('success_rate', 'N/A')}")
                print_info(f"  BR Details Fetch Success: {br_ext.get('fetch_success_rate', 'N/A')}")
                
                # Strategies
                strategies = debug.get("crawling_strategies", {})
                used = strategies.get("used", {})
                if used:
                    print_info(f"  Strategies used: {json.dumps(used)}")
                
                # Errors
                reliability = debug.get("reliability", {})
                errors = reliability.get("total_errors", 0)
                if errors > 0:
                    print_warning(f"  Total errors: {errors}")
                    errors_by_source = reliability.get("errors_by_source", {})
                    if errors_by_source:
                        print_warning(f"  Errors by source: {json.dumps(errors_by_source)}")
            
            return result
    
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
        print_error(f"Exception: {e}")
        return result

def generate_report(results: List[Dict[str, Any]]):
    """Gera relatório final"""
    print_header("FINAL REPORT")
    
    total = len(results)
    excellent = sum(1 for r in results if r["status"] == "excellent")
    good = sum(1 for r in results if r["status"] == "good")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] == "failed")
    errors = sum(1 for r in results if r["status"] == "error")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print(f"  Total tests: {total}")
    print_success(f"Excellent: {excellent} ({excellent/total*100:.1f}%)")
    print_success(f"Good: {good} ({good/total*100:.1f}%)")
    print_warning(f"Partial: {partial} ({partial/total*100:.1f}%)")
    print_error(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print_error(f"Errors: {errors} ({errors/total*100:.1f}%)")
    
    print(f"\n{Colors.BOLD}Detailed Results:{Colors.END}")
    for r in results:
        status_icon = {
            "excellent": "✅",
            "good": "✅",
            "partial": "⚠️ ",
            "failed": "❌",
            "error": "❌"
        }.get(r["status"], "❓")
        
        print(f"\n{status_icon} {r['molecule']}:")
        print(f"   Status: {r['status']}")
        print(f"   Time: {r['execution_time']:.1f}s")
        
        findings = r.get("findings", {})
        if findings:
            print(f"   BRs found: {findings.get('br_patents_total', 0)}/{r['expected_brs']}")
            print(f"   Match rate: {findings.get('match_rate', 'N/A')}")
            print(f"   WOs found: {findings.get('wos_found', 0)}")
            print(f"   WOs with BR: {findings.get('wos_with_br', 0)}")
        
        if r.get("errors"):
            print_error(f"   Errors: {', '.join(r['errors'])}")
    
    # Recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
    
    avg_time = sum(r["execution_time"] for r in results) / max(1, total)
    if avg_time > 90:
        print_warning(f"Average execution time is high ({avg_time:.1f}s). Consider optimizing.")
    
    if failed + errors > total * 0.3:
        print_error("High failure rate! Check debug output for common issues.")
    
    if excellent + good >= total * 0.7:
        print_success("API is performing well! 🎉")
    
    # Save report to file
    report_file = f"pharmyrus_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print_info(f"\nFull report saved to: {report_file}")

async def main():
    """Main test runner"""
    print_header("PHARMYRUS API v4.0 - AUTOMATED TESTING")
    
    # Check API health
    if not await test_health():
        print_error("API is not responding. Make sure it's running!")
        return
    
    # Run tests
    results = []
    for molecule in TEST_MOLECULES:
        result = await test_molecule(molecule)
        results.append(result)
        await asyncio.sleep(2)  # Delay entre testes
    
    # Generate report
    generate_report(results)
    
    print_header("TESTING COMPLETE")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_error("\n\nTesting interrupted by user")
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
