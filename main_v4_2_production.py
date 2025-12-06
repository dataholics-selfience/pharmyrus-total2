"""
Pharmyrus API v4.2 PRODUCTION
==============================
Pipeline completo em 4 layers com debug extremo.

LAYERS:
1. PubChem → dev codes, CAS
2. WO Discovery → Extrai WOs (igual n8n)
3. Patent Family → BR, US, JP, CN, EP para cada WO
4. Patent Details → Dados completos

Author: Claude
Date: 2024-12-06
Version: 4.2
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
SERPAPI_KEY = "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d"
TIMEOUT_SHORT = 30
TIMEOUT_MEDIUM = 60
TIMEOUT_LONG = 120

# ==================== DEBUG TRACKING ====================
@dataclass
class RequestLog:
    step: str
    url: str
    params: Dict
    status_code: Optional[int] = None
    response_size: int = 0
    error: Optional[str] = None
    duration_ms: float = 0.0
    
@dataclass
class LayerStats:
    layer_name: str
    success: bool = False
    items_found: int = 0
    duration_seconds: float = 0.0
    details: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

@dataclass
class DebugStats:
    requests: List[RequestLog] = field(default_factory=list)
    layers: List[LayerStats] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

# ==================== HTTP HELPERS ====================
async def serpapi_request(
    engine: str,
    params: Dict,
    debug: DebugStats,
    step_name: str,
    timeout: int = TIMEOUT_MEDIUM
) -> Optional[Dict]:
    """Request SerpAPI com logging"""
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

# ==================== LAYER 1: PUBCHEM ====================
async def layer1_pubchem(molecule: str, debug: DebugStats) -> Dict:
    """Layer 1: Extrai dev codes e CAS do PubChem"""
    print(f"\n{'='*60}")
    print(f"LAYER 1: PUBCHEM")
    print(f"{'='*60}")
    
    layer = LayerStats(layer_name="pubchem")
    start = datetime.now()
    
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule}/synonyms/JSON"
    
    log = RequestLog(step="pubchem", url=url, params={})
    request_start = datetime.now()
    
    dev_codes = []
    cas_number = None
    synonyms_count = 0
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SHORT) as client:
            response = await client.get(url)
            log.status_code = response.status_code
            log.duration_ms = (datetime.now() - request_start).total_seconds() * 1000
            
            if response.status_code == 200:
                data = response.json()
                log.response_size = len(response.text)
                
                synonyms = data.get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
                synonyms_count = len(synonyms)
                
                dev_pattern = re.compile(r"^[A-Z]{2,5}[-\s]?\d{3,7}[A-Z]?$", re.IGNORECASE)
                cas_pattern = re.compile(r"^\d{2,7}-\d{2}-\d$")
                
                for syn in synonyms:
                    if dev_pattern.match(syn) and len(dev_codes) < 10:
                        dev_codes.append(syn)
                    if cas_pattern.match(syn) and not cas_number:
                        cas_number = syn
                
                layer.success = True
                layer.items_found = len(dev_codes)
                layer.details = {
                    "dev_codes_found": len(dev_codes),
                    "cas_found": bool(cas_number),
                    "synonyms_total": synonyms_count
                }
                
                print(f"✅ Dev codes: {len(dev_codes)}")
                print(f"✅ CAS: {cas_number or 'N/A'}")
                print(f"✅ Synonyms: {synonyms_count}")
            else:
                log.error = f"HTTP {response.status_code}"
                layer.errors.append(f"HTTP {response.status_code}")
                print(f"❌ PubChem failed: HTTP {response.status_code}")
                
    except Exception as e:
        log.error = str(e)
        log.duration_ms = (datetime.now() - request_start).total_seconds() * 1000
        layer.errors.append(str(e))
        print(f"❌ PubChem error: {e}")
    
    debug.requests.append(log)
    layer.duration_seconds = (datetime.now() - start).total_seconds()
    debug.layers.append(layer)
    
    return {
        "dev_codes": dev_codes,
        "cas_number": cas_number,
        "synonyms_count": synonyms_count
    }

# ==================== LAYER 2: WO DISCOVERY ====================
async def layer2_wo_discovery(molecule: str, brand: str, dev_codes: List[str], debug: DebugStats) -> List[str]:
    """Layer 2: Descobre WOs usando Google (igual n8n)"""
    print(f"\n{'='*60}")
    print(f"LAYER 2: WO DISCOVERY")
    print(f"{'='*60}")
    
    layer = LayerStats(layer_name="wo_discovery")
    start = datetime.now()
    
    # Build queries IGUAL ao n8n
    queries = [
        f"{molecule} patent WO2011",
        f"{molecule} patent WO2016",
        f"{molecule} patent WO2018",
        f"{molecule} Orion Corporation patent",
        f"{molecule} Bayer patent",
    ]
    
    # Add dev code queries
    for i, dev in enumerate(dev_codes[:2]):
        queries.append(f"{dev} patent WO")
    
    print(f"Total queries: {len(queries)}")
    
    wo_numbers = set()
    wo_pattern = re.compile(r"WO[\s-]?(\d{4})[\s\/]?(\d{6})", re.IGNORECASE)
    
    successful_queries = 0
    
    for i, query in enumerate(queries):
        print(f"\n  Query {i+1}/{len(queries)}: {query}")
        
        # USA engine=google (IGUAL n8n, NÃO google_patents)
        result = await serpapi_request(
            engine="google",  # ← IMPORTANTE!
            params={"q": query, "num": 10},
            debug=debug,
            step_name=f"wo_q{i+1}"
        )
        
        if result:
            successful_queries += 1
            organic = result.get("organic_results", [])
            
            # Extract WOs com regex IGUAL n8n
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
    
    layer.success = len(wo_list) > 0
    layer.items_found = len(wo_list)
    layer.details = {
        "queries_executed": len(queries),
        "queries_successful": successful_queries,
        "wo_numbers": wo_list
    }
    layer.duration_seconds = (datetime.now() - start).total_seconds()
    debug.layers.append(layer)
    
    print(f"\n✅ Total WOs found: {len(wo_list)}")
    
    return wo_list

# ==================== LAYER 3: PATENT FAMILY ====================
async def layer3_patent_family(wo_number: str, debug: DebugStats) -> Dict:
    """Layer 3: Busca família completa de patentes (BR, US, JP, CN, EP)"""
    print(f"\n  🔍 Processing WO: {wo_number}")
    
    family = {
        "wo_number": wo_number,
        "BR": [],
        "US": [],
        "JP": [],
        "CN": [],
        "EP": [],
        "other": []
    }
    
    # STEP 1: Search WO via google_patents
    result1 = await serpapi_request(
        engine="google_patents",
        params={"q": wo_number, "num": 20},
        debug=debug,
        step_name=f"family_search_{wo_number}"
    )
    
    if not result1:
        print(f"    ❌ Failed to search")
        return family
    
    # STEP 2: Get json_endpoint
    json_endpoint = result1.get("search_metadata", {}).get("json_endpoint")
    
    if not json_endpoint:
        print(f"    ❌ No json_endpoint")
        return family
    
    print(f"    ✅ Found json_endpoint")
    
    # STEP 3: Navigate to json_endpoint
    log = RequestLog(step=f"family_endpoint_{wo_number}", url=json_endpoint, params={})
    request_start = datetime.now()
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_MEDIUM) as client:
            response = await client.get(json_endpoint)
            log.status_code = response.status_code
            log.duration_ms = (datetime.now() - request_start).total_seconds() * 1000
            
            if response.status_code == 200:
                result2 = response.json()
                log.response_size = len(response.text)
                debug.requests.append(log)
                
                # STEP 4: Get serpapi_link
                organic_results = result2.get("organic_results", [])
                
                if not organic_results:
                    print(f"    ❌ No organic results")
                    return family
                
                serpapi_link = organic_results[0].get("serpapi_link")
                
                if not serpapi_link:
                    print(f"    ❌ No serpapi_link")
                    return family
                
                serpapi_link_with_key = f"{serpapi_link}&api_key={SERPAPI_KEY}"
                print(f"    ✅ Found serpapi_link")
                
                # STEP 5: Navigate to serpapi_link
                log2 = RequestLog(step=f"family_details_{wo_number}", url=serpapi_link_with_key, params={})
                request_start2 = datetime.now()
                
                response2 = await client.get(serpapi_link_with_key)
                log2.status_code = response2.status_code
                log2.duration_ms = (datetime.now() - request_start2).total_seconds() * 1000
                
                if response2.status_code == 200:
                    result3 = response2.json()
                    log2.response_size = len(response2.text)
                    debug.requests.append(log2)
                    
                    # STEP 6: Extract worldwide_applications
                    worldwide_apps = result3.get("worldwide_applications", {})
                    
                    for year, apps in worldwide_apps.items():
                        if isinstance(apps, list):
                            for app in apps:
                                doc_id = app.get("document_id", "")
                                
                                if doc_id.startswith("BR"):
                                    family["BR"].append(doc_id)
                                    print(f"    ✅ BR: {doc_id}")
                                elif doc_id.startswith("US"):
                                    family["US"].append(doc_id)
                                    print(f"    ✅ US: {doc_id}")
                                elif doc_id.startswith("JP"):
                                    family["JP"].append(doc_id)
                                    print(f"    ✅ JP: {doc_id}")
                                elif doc_id.startswith("CN"):
                                    family["CN"].append(doc_id)
                                    print(f"    ✅ CN: {doc_id}")
                                elif doc_id.startswith("EP"):
                                    family["EP"].append(doc_id)
                                    print(f"    ✅ EP: {doc_id}")
                                elif not doc_id.startswith("WO"):
                                    family["other"].append(doc_id)
                    
                    total = sum(len(v) for k, v in family.items() if k != "wo_number")
                    print(f"    Total patents: {total} (BR:{len(family['BR'])}, US:{len(family['US'])}, JP:{len(family['JP'])}, CN:{len(family['CN'])}, EP:{len(family['EP'])})")
                else:
                    log2.error = f"HTTP {response2.status_code}"
                    debug.requests.append(log2)
            else:
                log.error = f"HTTP {response.status_code}"
                debug.requests.append(log)
    
    except Exception as e:
        log.error = str(e)
        log.duration_ms = (datetime.now() - request_start).total_seconds() * 1000
        debug.requests.append(log)
        print(f"    ❌ Error: {e}")
    
    return family

# ==================== LAYER 4: PATENT DETAILS ====================
async def layer4_patent_details(patent_id: str, country: str, debug: DebugStats) -> Optional[Dict]:
    """Layer 4: Busca detalhes completos de uma patente"""
    result = await serpapi_request(
        engine="google_patents_details",
        params={"patent_id": patent_id},
        debug=debug,
        step_name=f"details_{country}_{patent_id}"
    )
    
    if not result:
        return None
    
    return {
        "number": patent_id,
        "country": country,
        "title": result.get("title", ""),
        "abstract": (result.get("abstract", "") or "")[:300],
        "assignee": result.get("assignee", ""),
        "inventors": result.get("inventors", []),
        "filing_date": result.get("filing_date", ""),
        "publication_date": result.get("publication_date", ""),
        "legal_status": result.get("legal_status", ""),
        "classifications": result.get("classifications", []),
        "link": result.get("url", f"https://patents.google.com/patent/{patent_id}"),
        "source": "google_patents"
    }

# ==================== MAIN PIPELINE ====================
async def search_patents(molecule_name: str, brand_name: str = "") -> Dict:
    """Pipeline completo em 4 layers"""
    pipeline_start = datetime.now()
    debug = DebugStats()
    
    print(f"\n{'='*60}")
    print(f"PHARMYRUS API v4.2 PRODUCTION")
    print(f"Molecule: {molecule_name}")
    print(f"Brand: {brand_name or 'N/A'}")
    print(f"{'='*60}")
    
    # ==================== LAYER 1: PUBCHEM ====================
    pubchem_data = await layer1_pubchem(molecule_name, debug)
    
    if not pubchem_data["dev_codes"] and not pubchem_data["cas_number"]:
        print("\n⚠️  WARNING: No dev codes or CAS found")
    
    # ==================== LAYER 2: WO DISCOVERY ====================
    wo_numbers = await layer2_wo_discovery(
        molecule_name,
        brand_name,
        pubchem_data["dev_codes"],
        debug
    )
    
    if not wo_numbers:
        print("\n⚠️  WARNING: No WO numbers found!")
    
    # ==================== LAYER 3: PATENT FAMILY ====================
    print(f"\n{'='*60}")
    print(f"LAYER 3: PATENT FAMILY NAVIGATION")
    print(f"{'='*60}")
    
    layer3 = LayerStats(layer_name="patent_family")
    layer3_start = datetime.now()
    
    all_families = []
    all_patents_by_country = {
        "BR": {},
        "US": {},
        "JP": {},
        "CN": {},
        "EP": {}
    }
    
    wos_processed = 0
    wos_with_patents = 0
    
    # Process first 5 WOs
    for wo in wo_numbers[:5]:
        family = await layer3_patent_family(wo, debug)
        all_families.append(family)
        
        has_patents = False
        for country in ["BR", "US", "JP", "CN", "EP"]:
            for patent_id in family[country]:
                if patent_id not in all_patents_by_country[country]:
                    all_patents_by_country[country][patent_id] = wo
                    has_patents = True
        
        if has_patents:
            wos_with_patents += 1
        
        wos_processed += 1
        await asyncio.sleep(1)  # Rate limiting
    
    layer3.success = wos_processed > 0
    layer3.items_found = sum(len(v) for v in all_patents_by_country.values())
    layer3.details = {
        "wos_processed": wos_processed,
        "wos_with_patents": wos_with_patents,
        "BR_patents": len(all_patents_by_country["BR"]),
        "US_patents": len(all_patents_by_country["US"]),
        "JP_patents": len(all_patents_by_country["JP"]),
        "CN_patents": len(all_patents_by_country["CN"]),
        "EP_patents": len(all_patents_by_country["EP"])
    }
    layer3.duration_seconds = (datetime.now() - layer3_start).total_seconds()
    debug.layers.append(layer3)
    
    print(f"\n✅ Patent Family Summary:")
    print(f"   WOs processed: {wos_processed}")
    print(f"   BR patents: {len(all_patents_by_country['BR'])}")
    print(f"   US patents: {len(all_patents_by_country['US'])}")
    print(f"   JP patents: {len(all_patents_by_country['JP'])}")
    print(f"   CN patents: {len(all_patents_by_country['CN'])}")
    print(f"   EP patents: {len(all_patents_by_country['EP'])}")
    
    # ==================== LAYER 4: PATENT DETAILS ====================
    print(f"\n{'='*60}")
    print(f"LAYER 4: PATENT DETAILS")
    print(f"{'='*60}")
    
    layer4 = LayerStats(layer_name="patent_details")
    layer4_start = datetime.now()
    
    all_patents_detailed = {
        "BR": [],
        "US": [],
        "JP": [],
        "CN": [],
        "EP": []
    }
    
    details_fetched = 0
    
    # Get details for each country (limit 10 per country)
    for country in ["BR", "US", "JP", "CN", "EP"]:
        print(f"\n{country} Patents:")
        
        for i, (patent_id, source_wo) in enumerate(list(all_patents_by_country[country].items())[:10]):
            print(f"  {i+1}/{min(10, len(all_patents_by_country[country]))}: {patent_id}")
            
            details = await layer4_patent_details(patent_id, country, debug)
            
            if details:
                details["source_wo"] = source_wo
                all_patents_detailed[country].append(details)
                details_fetched += 1
            
            await asyncio.sleep(0.5)
    
    layer4.success = details_fetched > 0
    layer4.items_found = details_fetched
    layer4.details = {
        "BR_detailed": len(all_patents_detailed["BR"]),
        "US_detailed": len(all_patents_detailed["US"]),
        "JP_detailed": len(all_patents_detailed["JP"]),
        "CN_detailed": len(all_patents_detailed["CN"]),
        "EP_detailed": len(all_patents_detailed["EP"])
    }
    layer4.duration_seconds = (datetime.now() - layer4_start).total_seconds()
    debug.layers.append(layer4)
    
    # ==================== FINAL OUTPUT ====================
    total_time = (datetime.now() - pipeline_start).total_seconds()
    
    return {
        "consulta": {
            "termo_pesquisado": molecule_name,
            "nome_comercial": brand_name,
            "data_consulta": datetime.now().isoformat(),
            "pais_alvo": ["Brasil", "Estados Unidos", "Japão", "China", "Europa"]
        },
        "molecule_info": {
            "chemical_name": molecule_name,
            "brand_name": brand_name,
            **pubchem_data
        },
        "layer1_pubchem": {
            "success": debug.layers[0].success,
            "dev_codes_found": len(pubchem_data["dev_codes"]),
            "cas_found": bool(pubchem_data["cas_number"]),
            "duration_seconds": debug.layers[0].duration_seconds
        },
        "layer2_wo_discovery": {
            "success": debug.layers[1].success,
            "wo_numbers_found": len(wo_numbers),
            "wo_numbers": wo_numbers,
            "queries_executed": debug.layers[1].details.get("queries_executed", 0),
            "queries_successful": debug.layers[1].details.get("queries_successful", 0),
            "duration_seconds": debug.layers[1].duration_seconds
        },
        "layer3_patent_family": {
            "success": debug.layers[2].success,
            "wos_processed": debug.layers[2].details["wos_processed"],
            "wos_with_patents": debug.layers[2].details["wos_with_patents"],
            "patents_by_country": {
                "BR": debug.layers[2].details["BR_patents"],
                "US": debug.layers[2].details["US_patents"],
                "JP": debug.layers[2].details["JP_patents"],
                "CN": debug.layers[2].details["CN_patents"],
                "EP": debug.layers[2].details["EP_patents"]
            },
            "duration_seconds": debug.layers[2].duration_seconds
        },
        "layer4_patent_details": {
            "success": debug.layers[3].success,
            "details_fetched": debug.layers[3].items_found,
            "by_country": debug.layers[3].details,
            "duration_seconds": debug.layers[3].duration_seconds
        },
        "patents": all_patents_detailed,
        "comparison_br": {
            "expected": 8,
            "found": len(all_patents_detailed["BR"]),
            "match_rate": f"{(min(len(all_patents_detailed['BR']), 8) / 8 * 100):.0f}%",
            "status": "Excellent" if len(all_patents_detailed["BR"]) >= 6 else "Good" if len(all_patents_detailed["BR"]) >= 4 else "Low"
        },
        "debug": {
            "http_requests": [asdict(r) for r in debug.requests],
            "layers": [asdict(l) for l in debug.layers],
            "errors": debug.errors,
            "requests_total": len(debug.requests),
            "requests_successful": len([r for r in debug.requests if r.status_code == 200])
        },
        "execution_time_seconds": round(total_time, 2),
        "timestamp": datetime.now().isoformat(),
        "api_version": "4.2-PRODUCTION"
    }

# ==================== FASTAPI ====================
app = FastAPI(title="Pharmyrus API v4.2 PRODUCTION", version="4.2.0")

@app.get("/")
async def root():
    return {
        "api": "Pharmyrus v4.2 PRODUCTION",
        "status": "online",
        "description": "4-layer pipeline: PubChem → WO Discovery → Patent Family → Details",
        "layers": ["PubChem", "WO Discovery", "Patent Family (BR/US/JP/CN/EP)", "Patent Details"],
        "endpoints": {
            "/api/v1/search": "Main search",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "4.2-PRODUCTION"}

@app.get("/api/v1/search")
async def search(
    molecule_name: str = Query(..., description="Nome da molécula"),
    brand_name: str = Query("", description="Nome comercial (opcional)")
):
    try:
        result = await search_patents(molecule_name, brand_name)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "molecule": molecule_name,
                "api_version": "4.2-PRODUCTION"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
