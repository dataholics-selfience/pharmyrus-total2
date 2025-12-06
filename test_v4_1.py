#!/usr/bin/env python3
"""
Quick Test for Pharmyrus API v4.1 EXPERT
==========================================
Testa a API e mostra resultados coloridos no terminal.

Usage:
    python3 test_v4_1.py
"""

import requests
import json
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

API_URL = "http://localhost:8000/api/v1/search"
MOLECULE = "Darolutamide"

print(f"\n{Fore.CYAN}{'='*60}")
print(f"{Fore.CYAN}PHARMYRUS API v4.1 EXPERT - QUICK TEST")
print(f"{Fore.CYAN}{'='*60}\n")

print(f"{Fore.YELLOW}Testing molecule: {MOLECULE}")
print(f"{Fore.YELLOW}API endpoint: {API_URL}\n")

try:
    print(f"{Fore.BLUE}⏳ Making request...")
    start = datetime.now()
    
    response = requests.get(API_URL, params={"molecule_name": MOLECULE}, timeout=180)
    
    duration = (datetime.now() - start).total_seconds()
    
    if response.status_code != 200:
        print(f"{Fore.RED}❌ HTTP Error: {response.status_code}")
        print(f"{Fore.RED}{response.text}")
        exit(1)
    
    data = response.json()
    
    # Save to file
    filename = f"test_result_{MOLECULE.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"{Fore.GREEN}✅ Request completed in {duration:.1f}s")
    print(f"{Fore.GREEN}📁 Saved to: {filename}\n")
    
    # ========== RESULTS ==========
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}RESULTS")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    # Molecule Info
    mol_info = data.get("molecule_info", {})
    print(f"{Fore.MAGENTA}📊 MOLECULE INFO:")
    print(f"  Dev Codes: {len(mol_info.get('dev_codes', []))}")
    print(f"  CAS: {mol_info.get('cas_number', 'N/A')}")
    print(f"  Synonyms: {mol_info.get('synonyms_count', 0)}\n")
    
    # WO Discovery
    wo_disc = data.get("wo_discovery", {})
    print(f"{Fore.YELLOW}🔍 WO DISCOVERY:")
    print(f"  Queries Executed: {wo_disc.get('queries_executed', 0)}")
    print(f"  Queries Successful: {wo_disc.get('queries_successful', 0)}")
    print(f"  WO Numbers Found: {Fore.GREEN if wo_disc.get('wo_numbers_found', 0) >= 8 else Fore.RED}{wo_disc.get('wo_numbers_found', 0)}{Style.RESET_ALL}")
    
    wo_numbers = wo_disc.get('wo_numbers', [])
    if wo_numbers:
        print(f"  First 5 WOs: {', '.join(wo_numbers[:5])}\n")
    else:
        print(f"{Fore.RED}  ❌ No WO numbers found!\n")
    
    # Family Navigation
    fam_nav = data.get("family_navigation", {})
    print(f"{Fore.BLUE}🌐 FAMILY NAVIGATION:")
    print(f"  WOs Processed: {fam_nav.get('wos_processed', 0)}")
    print(f"  WOs with BR: {fam_nav.get('wos_with_br', 0)}")
    print(f"  Unique BRs Found: {Fore.GREEN if fam_nav.get('unique_br_found', 0) >= 6 else Fore.RED}{fam_nav.get('unique_br_found', 0)}{Style.RESET_ALL}\n")
    
    # BR Extraction
    br_ext = data.get("br_extraction", {})
    print(f"{Fore.GREEN}📄 BR EXTRACTION:")
    print(f"  Total BR Unique: {br_ext.get('total_br_unique', 0)}")
    print(f"  Details Fetched: {br_ext.get('details_fetched', 0)}")
    print(f"  Success Rate: {br_ext.get('fetch_success_rate', 'N/A')}\n")
    
    # BR Patents
    br_patents = data.get("br_patents", [])
    print(f"{Fore.MAGENTA}📋 BR PATENTS ({len(br_patents)} total):")
    
    for i, patent in enumerate(br_patents[:5], 1):
        print(f"\n  {i}. {patent.get('number', 'N/A')}")
        print(f"     Title: {patent.get('title', 'N/A')[:60]}...")
        print(f"     Assignee: {patent.get('assignee', 'N/A')}")
        print(f"     Filing: {patent.get('filing_date', 'N/A')}")
        print(f"     Source WO: {patent.get('source_wo', 'N/A')}")
    
    if len(br_patents) > 5:
        print(f"\n  ... and {len(br_patents) - 5} more\n")
    
    # Comparison
    comp = data.get("comparison", {})
    print(f"\n{Fore.CYAN}📊 COMPARISON:")
    print(f"  Expected: {comp.get('expected', 8)}")
    print(f"  Found: {Fore.GREEN if comp.get('found', 0) >= 6 else Fore.RED}{comp.get('found', 0)}{Style.RESET_ALL}")
    print(f"  Match Rate: {Fore.GREEN if int(comp.get('match_rate', '0%').rstrip('%')) >= 70 else Fore.RED}{comp.get('match_rate', 'N/A')}{Style.RESET_ALL}")
    print(f"  Status: {Fore.GREEN if comp.get('status') == 'Excellent' else Fore.YELLOW}{comp.get('status', 'N/A')}{Style.RESET_ALL}\n")
    
    # Debug
    debug = data.get("debug", {})
    errors = debug.get("errors", [])
    timing = debug.get("timing", {})
    requests_count = len(debug.get("http_requests", []))
    
    print(f"{Fore.YELLOW}🔧 DEBUG:")
    print(f"  HTTP Requests: {requests_count}")
    print(f"  Errors: {Fore.RED if errors else Fore.GREEN}{len(errors)}{Style.RESET_ALL}")
    print(f"  Total Time: {timing.get('total_seconds', 0)}s")
    print(f"  Avg Request: {timing.get('avg_request_ms', 0):.0f}ms\n")
    
    if errors:
        print(f"{Fore.RED}  Error List:")
        for err in errors[:5]:
            print(f"{Fore.RED}    - {err}")
    
    # ========== VERDICT ==========
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}VERDICT")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    br_found = len(br_patents)
    match_rate = int(comp.get('match_rate', '0%').rstrip('%'))
    
    if br_found >= 6 and match_rate >= 70:
        print(f"{Fore.GREEN}✅ EXCELLENT! API is working correctly.")
        print(f"{Fore.GREEN}   {br_found} BR patents found (target: 6+)")
        print(f"{Fore.GREEN}   Match rate: {match_rate}% (target: 70%+)")
        print(f"{Fore.GREEN}\n🚀 Ready for production deployment!")
    elif br_found >= 4:
        print(f"{Fore.YELLOW}⚠️  GOOD but could be better.")
        print(f"{Fore.YELLOW}   {br_found} BR patents found (target: 6+)")
        print(f"{Fore.YELLOW}   Match rate: {match_rate}% (target: 70%+)")
        print(f"{Fore.YELLOW}\n📋 Check debug.json for optimization opportunities.")
    else:
        print(f"{Fore.RED}❌ LOW RESULTS - Investigation needed.")
        print(f"{Fore.RED}   {br_found} BR patents found (target: 6+)")
        print(f"{Fore.RED}   Match rate: {match_rate}% (target: 70%+)")
        print(f"{Fore.RED}\n🔍 Analyze {filename} for errors.")
        
        if not wo_numbers:
            print(f"{Fore.RED}\n⚠️  No WO numbers found - check SerpAPI key and quota.")
        
        if errors:
            print(f"{Fore.RED}\n⚠️  {len(errors)} errors detected - check connectivity and API limits.")
    
    print(f"\n{Fore.CYAN}{'='*60}\n")
    
except requests.exceptions.Timeout:
    print(f"{Fore.RED}❌ Timeout - API took too long to respond")
    print(f"{Fore.RED}   Try increasing timeout or check server status")
except requests.exceptions.ConnectionError:
    print(f"{Fore.RED}❌ Connection Error - Is the API running?")
    print(f"{Fore.RED}   Try: python main.py")
except Exception as e:
    print(f"{Fore.RED}❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
