"""
Pharmyrus API v4.1 EXPERT
========================
Replicação EXATA do workflow n8n com debug completo.

Estratégia de navegação (4 passos):
1. WO Search via google_patents
2. Navigate to json_endpoint (worldwide apps)
3. Extract serpapi_link from first result
4. Get BR patents from worldwide_applications
5. Fetch details for each BR

Author: Claude
Date: 2024-12-06
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import httpx
import re
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import asyncio
from pydantic import BaseModel

# ==================== CONFIGURATION ====================
SERPAPI_KEY = "871b533d956978e967e7621c871d53fb448bc36e90af6389eda2aca3420236e1"
TIMEOUT_SHORT = 30
TIMEOUT_MEDIUM = 60
TIMEOUT_LONG = 120

# ==================== DEBUG TRACKING ====================
@dataclass
class RequestLog:
    """Armazena request/response de cada chamada HTTP"""
    step: str
    url: str
    params: Dict
    status_code: Optional[int] = None
    response_size: int = 0
    error: Optional[str] = None
    duration_ms: float = 0.0
    
@dataclass
class DebugStats:
    """Estatísticas detalhadas de debug"""
    requests: List[RequestLog] = field(default_factory=list)
    wo_discovery: Dict = field(default_factory=dict)
    family_navigation: Dict = field(default_factory=dict)
    br_extraction: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timing: Dict = field(default_factory=dict)

# ==================== HELPERS ====================
async def serpapi_request(
    engine: str,
    params: Dict,
    debug: DebugStats,
    step_name: str,
    timeout: int = TIMEOUT_MEDIUM
) -> Optional[Dict]:
    """Faz request para SerpAPI com logging completo"""
    url = "https://serpapi.com/search.json"
    
    full_params = {
        "engine": engine,
        "api_key": SERPAPI_KEY,
        **params
    }
    
    log = RequestLog(
        step=step_name,
        url=url,
        params={k: v for k, v in full_params.items() if k != "api_key"}
    )
    
    start = datetime.now()
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=full_params)
            
            log.status_code = response.status_code
            log.duration_ms = (datetime.now() - start).total_seconds() * 1000
            
            if response.status_code == 200:
                data = response.json()
                log.response_size = len(response.text)
                debug.requests.append(log)
                
                print(f"✅ {step_name}: {log.status_code} ({log.duration_ms:.0f}ms, {log.response_size} bytes)")
                return data
            else:
                log.error = f"HTTP {response.status_code}"
                debug.requests.append(log)
                debug.errors.append(f"{step_name}: HTTP {response.status_code}")
                print(f"❌ {step_name}: HTTP {response.status_code}")
                return None
                
    except Exception as e:
        log.error = str(e)
        log.duration_ms = (datetime.now() - start).total_seconds() * 1000
        debug.requests.append(log)
        debug.errors.append(f"{step_name}: {str(e)}")
        print(f"❌ {step_name}: {str(e)}")
        return None

async def fetch_url(url: str, debug: DebugStats, step_name: str, timeout: int = TIMEOUT_MEDIUM) -> Optional[Dict]:
    """Faz request genérico com logging"""
    log = RequestLog(step=step_name, url=url, params={})
    start = datetime.now()
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            log.status_code = response.status_code
            log.duration_ms = (datetime.now() - start).total_seconds() * 1000
            
            if response.status_code == 200:
                data = response.json()
                log.response_size = len(response.text)
                debug.requests.append(log)
                print(f"✅ {step_name}: {log.status_code} ({log.duration_ms:.0f}ms)")
                return data
            else:
                log.error = f"HTTP {response.status_code}"
                debug.requests.append(log)
                debug.errors.append(f"{step_name}: HTTP {response.status_code}")
                print(f"❌ {step_name}: HTTP {response.status_code}")
                return None
                
    except Exception as e:
        log.error = str(e)
        log.duration_ms = (datetime.now() - start).total_seconds() * 1000
        debug.requests.append(log)
        debug.errors.append(f"{step_name}: {str(e)}")
        print(f"❌ {step_name}: {str(e)}")
        return None

# ==================== PUBCHEM ====================
async def get_pubchem_data(molecule: str, debug: DebugStats) -> Dict:
    """Extrai dev codes e CAS do PubChem"""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule}/synonyms/JSON"
    
    log = RequestLog(step="pubchem", url=url, params={})
    start = datetime.now()
    
    dev_codes = []
    cas_number = None
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SHORT) as client:
            response = await client.get(url)
            log.status_code = response.status_code
            log.duration_ms = (datetime.now() - start).total_seconds() * 1000
            
            if response.status_code == 200:
                data = response.json()
                log.response_size = len(response.text)
                
                synonyms = data.get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
                
                dev_pattern = re.compile(r"^[A-Z]{2,5}[-\s]?\d{3,7}[A-Z]?$", re.IGNORECASE)
                cas_pattern = re.compile(r"^\d{2,7}-\d{2}-\d$")
                
                for syn in synonyms:
                    if dev_pattern.match(syn) and len(dev_codes) < 10:
                        dev_codes.append(syn)
                    if cas_pattern.match(syn) and not cas_number:
                        cas_number = syn
                
                print(f"✅ PubChem: {len(dev_codes)} dev codes, CAS: {cas_number or 'N/A'}")
            else:
                log.error = f"HTTP {response.status_code}"
                print(f"❌ PubChem failed: HTTP {response.status_code}")
                
    except Exception as e:
        log.error = str(e)
        log.duration_ms = (datetime.now() - start).total_seconds() * 1000
        print(f"❌ PubChem error: {e}")
    
    debug.requests.append(log)
    
    return {
        "dev_codes": dev_codes,
        "cas_number": cas_number,
        "synonyms_count": len(synonyms) if 'synonyms' in locals() else 0
    }

# ==================== WO DISCOVERY ====================
async def discover_wo_numbers(molecule: str, dev_codes: List[str], debug: DebugStats) -> List[str]:
    """Descobre números WO usando múltiplas queries"""
    print("\n=== WO DISCOVERY ===")
    
    queries = [
        f"{molecule} patent WO2011",
        f"{molecule} patent WO2016",
        f"{molecule} patent WO2018",
        f"{molecule} Orion Corporation patent",
        f"{molecule} Bayer patent",
    ]
    
    # Add dev code queries
    for dev in dev_codes[:2]:
        queries.append(f"{dev} patent WO")
    
    wo_numbers = set()
    wo_pattern = re.compile(r"WO[\s-]?(\d{4})[\s/]?(\d{6})", re.IGNORECASE)
    
    successful_queries = 0
    
    for i, query in enumerate(queries):
        print(f"  Query {i+1}/{len(queries)}: {query}")
        
        result = await serpapi_request(
            engine="google",
            params={"q": query, "num": 10},
            debug=debug,
            step_name=f"wo_discovery_q{i+1}"
        )
        
        if result:
            successful_queries += 1
            organic = result.get("organic_results", [])
            
            for item in organic:
                text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('link', '')}"
                matches = wo_pattern.findall(text)
                
                for year, num in matches:
                    wo = f"WO{year}{num}"
                    if wo not in wo_numbers:
                        wo_numbers.add(wo)
                        print(f"    ✅ Found: {wo}")
        
        await asyncio.sleep(0.5)  # Rate limiting
    
    wo_list = sorted(list(wo_numbers))
    
    debug.wo_discovery = {
        "queries_executed": len(queries),
        "queries_successful": successful_queries,
        "wo_numbers_found": len(wo_list),
        "wo_numbers": wo_list
    }
    
    print(f"\n  Total WOs found: {len(wo_list)}")
    return wo_list

# ==================== FAMILY NAVIGATION (N8N STYLE) ====================
async def navigate_to_br_patents(wo_number: str, debug: DebugStats) -> List[str]:
    """
    Navega do WO até os BRs seguindo EXATAMENTE o fluxo do n8n:
    1. Search WO via google_patents
    2. Get json_endpoint
    3. Navigate to json_endpoint
    4. Get serpapi_link from first result
    5. Navigate to serpapi_link
    6. Extract BRs from worldwide_applications
    """
    print(f"\n  🔍 Processing WO: {wo_number}")
    
    # STEP 1: Search WO via google_patents
    result1 = await serpapi_request(
        engine="google_patents",
        params={"q": wo_number, "num": 20},
        debug=debug,
        step_name=f"wo_search_{wo_number}"
    )
    
    if not result1:
        print(f"    ❌ Failed to search WO")
        return []
    
    # STEP 2: Extract json_endpoint
    json_endpoint = result1.get("search_metadata", {}).get("json_endpoint")
    
    if not json_endpoint:
        print(f"    ❌ No json_endpoint found")
        return []
    
    print(f"    ✅ Found json_endpoint")
    
    # STEP 3: Navigate to json_endpoint (worldwide applications)
    result2 = await fetch_url(
        url=json_endpoint,
        debug=debug,
        step_name=f"worldwide_apps_{wo_number}"
    )
    
    if not result2:
        print(f"    ❌ Failed to get worldwide apps")
        return []
    
    # STEP 4: Extract serpapi_link from first organic result
    organic_results = result2.get("organic_results", [])
    
    if not organic_results:
        print(f"    ❌ No organic results")
        return []
    
    serpapi_link = organic_results[0].get("serpapi_link")
    
    if not serpapi_link:
        print(f"    ❌ No serpapi_link in first result")
        return []
    
    # Add API key to serpapi_link
    serpapi_link_with_key = f"{serpapi_link}&api_key={SERPAPI_KEY}"
    print(f"    ✅ Found serpapi_link")
    
    # STEP 5: Navigate to serpapi_link (detailed patent info with worldwide_applications)
    result3 = await fetch_url(
        url=serpapi_link_with_key,
        debug=debug,
        step_name=f"patent_details_{wo_number}"
    )
    
    if not result3:
        print(f"    ❌ Failed to get patent details")
        return []
    
    # STEP 6: Extract BRs from worldwide_applications
    worldwide_apps = result3.get("worldwide_applications", {})
    
    br_patents = []
    
    for year, apps in worldwide_apps.items():
        if isinstance(apps, list):
            for app in apps:
                doc_id = app.get("document_id", "")
                if doc_id.startswith("BR"):
                    br_patents.append(doc_id)
                    print(f"    ✅ Found BR: {doc_id}")
    
    print(f"    Total BRs found: {len(br_patents)}")
    
    return br_patents

# ==================== BR DETAILS ====================
async def get_br_patent_details(br_id: str, debug: DebugStats) -> Optional[Dict]:
    """Busca detalhes completos de uma patente BR"""
    result = await serpapi_request(
        engine="google_patents_details",
        params={"patent_id": br_id},
        debug=debug,
        step_name=f"br_details_{br_id}"
    )
    
    if not result:
        return None
    
    return {
        "number": br_id,
        "title": result.get("title", ""),
        "abstract": (result.get("abstract", "") or "")[:300],
        "assignee": result.get("assignee", ""),
        "inventors": result.get("inventors", []),
        "filing_date": result.get("filing_date", ""),
        "publication_date": result.get("publication_date", ""),
        "legal_status": result.get("legal_status", ""),
        "link": result.get("url", f"https://patents.google.com/patent/{br_id}"),
        "source": "google_patents"
    }

# ==================== MAIN PIPELINE ====================
async def search_patents(molecule_name: str) -> Dict:
    """Pipeline principal de busca de patentes"""
    start_time = datetime.now()
    debug = DebugStats()
    
    print(f"\n{'='*60}")
    print(f"PHARMYRUS API v4.1 EXPERT")
    print(f"Molecule: {molecule_name}")
    print(f"{'='*60}")
    
    # 1. PubChem
    pubchem_data = await get_pubchem_data(molecule_name, debug)
    
    # 2. WO Discovery
    wo_numbers = await discover_wo_numbers(
        molecule_name,
        pubchem_data["dev_codes"],
        debug
    )
    
    if not wo_numbers:
        print("\n⚠️  WARNING: No WO numbers found!")
    
    # 3. Family Navigation
    print("\n=== FAMILY NAVIGATION ===")
    
    all_br_patents = {}
    wos_processed = 0
    wos_with_br = 0
    
    for wo in wo_numbers[:5]:  # Process first 5 WOs
        br_list = await navigate_to_br_patents(wo, debug)
        
        if br_list:
            wos_with_br += 1
            for br_id in br_list:
                if br_id not in all_br_patents:
                    all_br_patents[br_id] = wo
        
        wos_processed += 1
        await asyncio.sleep(1)  # Rate limiting between WOs
    
    debug.family_navigation = {
        "wos_processed": wos_processed,
        "wos_with_br": wos_with_br,
        "unique_br_found": len(all_br_patents)
    }
    
    # 4. BR Details
    print(f"\n=== BR DETAILS ({len(all_br_patents)} patents) ===")
    
    br_patents_detailed = []
    
    for i, (br_id, source_wo) in enumerate(list(all_br_patents.items())[:20]):
        print(f"  {i+1}/{min(20, len(all_br_patents))}: {br_id}")
        
        details = await get_br_patent_details(br_id, debug)
        
        if details:
            details["source_wo"] = source_wo
            br_patents_detailed.append(details)
        
        await asyncio.sleep(0.5)
    
    debug.br_extraction = {
        "total_br_unique": len(all_br_patents),
        "details_fetched": len(br_patents_detailed),
        "fetch_success_rate": f"{(len(br_patents_detailed) / max(1, len(all_br_patents)) * 100):.1f}%"
    }
    
    # Timing
    total_time = (datetime.now() - start_time).total_seconds()
    debug.timing = {
        "total_seconds": round(total_time, 2),
        "requests_count": len(debug.requests),
        "avg_request_ms": round(sum(r.duration_ms for r in debug.requests) / max(1, len(debug.requests)), 2)
    }
    
    # Final output
    return {
        "consulta": {
            "termo_pesquisado": molecule_name,
            "data_consulta": datetime.now().isoformat(),
            "nome_molecula": molecule_name,
            "pais_alvo": ["Brasil"]
        },
        "molecule_info": {
            "chemical_name": molecule_name,
            **pubchem_data
        },
        "wo_discovery": debug.wo_discovery,
        "family_navigation": debug.family_navigation,
        "br_extraction": debug.br_extraction,
        "br_patents": br_patents_detailed,
        "comparison": {
            "expected": 8,
            "found": len(br_patents_detailed),
            "match_rate": f"{(min(len(br_patents_detailed), 8) / 8 * 100):.0f}%",
            "status": "Excellent" if len(br_patents_detailed) >= 6 else "Good" if len(br_patents_detailed) >= 4 else "Low"
        },
        "debug": {
            "http_requests": [asdict(r) for r in debug.requests],
            "errors": debug.errors,
            "timing": debug.timing
        },
        "execution_time_seconds": total_time,
        "timestamp": datetime.now().isoformat(),
        "api_version": "4.1-EXPERT"
    }

# ==================== FASTAPI ====================
app = FastAPI(title="Pharmyrus API v4.1 EXPERT", version="4.1.0")

@app.get("/")
async def root():
    return {
        "api": "Pharmyrus v4.1 EXPERT",
        "status": "online",
        "description": "N8n workflow replication with complete debug",
        "endpoints": {
            "/api/v1/search": "Main patent search",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "4.1-EXPERT"}

@app.get("/api/v1/search")
async def search(
    molecule_name: str = Query(..., description="Nome da molécula (ex: Darolutamide)")
):
    try:
        result = await search_patents(molecule_name)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "molecule": molecule_name,
                "api_version": "4.1-EXPERT"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
