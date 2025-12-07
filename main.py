"""
Pharmyrus Crawler API v3.0 - Railway Production
GET /api/v1/search?molecule_name=Darolutamide
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
import asyncio
import httpx
import os
import logging
import re
from datetime import datetime, timedelta
import base64
from serpapi_pool import get_key, status as pool_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pharmyrus Crawler API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Config:
    EPO_KEY = "G5wJypxeg0GXEJoMGP37tdK370aKxeMszGKAkD6QaR0yiR5X"
    EPO_SECRET = "zg5AJ0EDzXdJey3GaFNM8ztMVxHKXRrAihXH93iS5ZAzKPAPMFLuVUfiEuAqpdbz"
    INPI_URL = "https://crawler3-production.up.railway.app/api/data/inpi/patents"
    TIMEOUT = 30
    TIMEOUT_INPI = 60
    CACHE_TTL = 3600

_cache = {}
_epo_token = None
_epo_token_expires = None

async def get_epo_token() -> Optional[str]:
    global _epo_token, _epo_token_expires
    now = datetime.now()
    if _epo_token and _epo_token_expires and now < _epo_token_expires:
        return _epo_token
    try:
        creds = f"{Config.EPO_KEY}:{Config.EPO_SECRET}"
        b64 = base64.b64encode(creds.encode()).decode()
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://ops.epo.org/3.2/auth/accesstoken",
                headers={"Authorization": f"Basic {b64}", "Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": "client_credentials"},
                timeout=Config.TIMEOUT
            )
            if r.status_code == 200:
                data = r.json()
                _epo_token = data["access_token"]
                _epo_token_expires = now + timedelta(minutes=15)
                logger.info("✅ EPO token renewed")
                return _epo_token
    except Exception as e:
        logger.error(f"EPO error: {e}")
    return None

async def get_pubchem(molecule: str) -> Dict[str, Any]:
    logger.info(f"[PubChem] {molecule}")
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule}/synonyms/JSON"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=Config.TIMEOUT)
            if r.status_code != 200:
                return {"dev_codes": [], "cas": None, "synonyms": []}
            data = r.json()
            syns = data.get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
            dev_codes = []
            cas = None
            for s in syns:
                if not s or len(s) > 20:
                    continue
                if re.match(r'^[A-Z]{2,5}[-\s]?\d{3,7}[A-Z]?$', s, re.I):
                    if s not in dev_codes:
                        dev_codes.append(s)
                if re.match(r'^\d{2,7}-\d{2}-\d$', s):
                    cas = s
            return {"dev_codes": dev_codes[:10], "cas": cas, "synonyms": [s for s in syns if s and len(s) < 50][:50]}
    except Exception as e:
        logger.error(f"[PubChem] Error: {e}")
        return {"dev_codes": [], "cas": None, "synonyms": []}

async def discover_wo(molecule: str, dev_codes: List[str]) -> List[str]:
    logger.info(f"[WO] {molecule}")
    wo_set = set()
    wo_pattern = re.compile(r'WO[\s-]?(\d{4})[\s/]?(\d{6})', re.I)
    queries = [f"{molecule} patent WO", f"{molecule} WO2011", f"{molecule} WO2018", f"{molecule} WO2020"]
    for code in dev_codes[:2]:
        queries.append(f"{code} patent WO")
    try:
        async with httpx.AsyncClient() as client:
            for q in queries:
                try:
                    r = await client.get(f"https://www.google.com/search?q={q}", headers={"User-Agent": "Mozilla/5.0"}, timeout=Config.TIMEOUT, follow_redirects=True)
                    matches = wo_pattern.findall(r.text)
                    for m in matches:
                        wo_set.add(f"WO{m[0]}{m[1]}")
                    await asyncio.sleep(0.5)
                except:
                    continue
    except Exception as e:
        logger.error(f"[WO] Error: {e}")
    result = list(wo_set)[:20]
    logger.info(f"[WO] Found {len(result)}")
    return result

async def get_epo_family(wo: str, token: str) -> List[str]:
    logger.info(f"[EPO] {wo}")
    try:
        url = f"https://ops.epo.org/3.2/rest-services/published-data/search?q={wo}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}, timeout=Config.TIMEOUT)
            if r.status_code != 200:
                return []
            data = r.json()
            br_list = []
            try:
                results = data.get("ops:world-patent-data", {}).get("ops:biblio-search", {}).get("ops:search-result", {})
                refs = results.get("ops:publication-reference", [])
                if not isinstance(refs, list):
                    refs = [refs]
                for ref in refs:
                    doc = ref.get("document-id", {})
                    country = doc.get("country", {}).get("$", "")
                    number = doc.get("doc-number", {}).get("$", "")
                    if country == "BR" and number:
                        br_list.append(f"{country}{number}")
            except:
                pass
            return br_list
    except Exception as e:
        logger.error(f"[EPO] Error: {e}")
        return []

async def search_inpi(molecule: str, dev_codes: List[str], cas: Optional[str]) -> List[Dict[str, Any]]:
    logger.info(f"[INPI] {molecule}")
    all_patents = []
    queries = [molecule, molecule.lower(), molecule.upper()]
    for code in dev_codes[:8]:
        queries.append(code)
        queries.append(code.replace("-", ""))
    if cas:
        queries.append(cas)
    queries = queries[:15]
    try:
        async with httpx.AsyncClient() as client:
            for i, q in enumerate(queries, 1):
                try:
                    url = f"{Config.INPI_URL}?medicine={q}"
                    r = await client.get(url, timeout=Config.TIMEOUT_INPI)
                    if r.status_code == 200:
                        data = r.json()
                        patents = data.get("data", [])
                        if patents:
                            logger.info(f"[INPI] Q{i} '{q}': {len(patents)}")
                            all_patents.extend(patents)
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"[INPI] Q'{q}' failed: {e}")
                    continue
    except Exception as e:
        logger.error(f"[INPI] Error: {e}")
    seen = set()
    unique = []
    for p in all_patents:
        pid = p.get("title", "").replace(" ", "")
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)
    logger.info(f"[INPI] Unique: {len(unique)}")
    return unique

async def get_fda(molecule: str) -> List[Dict[str, Any]]:
    try:
        url = f"https://api.fda.gov/drug/ndc.json?search=generic_name:{molecule}&limit=5"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=Config.TIMEOUT)
            if r.status_code == 200:
                return r.json().get("results", [])
    except:
        pass
    return []

async def search_patents(molecule: str, deep_search: bool = True) -> Dict[str, Any]:
    start = datetime.now()
    logger.info(f"🔍 SEARCH: {molecule} (deep={deep_search})")
    pubchem = await get_pubchem(molecule)
    dev_codes = pubchem["dev_codes"]
    cas = pubchem["cas"]
    wo_numbers = await discover_wo(molecule, dev_codes)
    epo_token = await get_epo_token()
    br_from_epo = []
    if epo_token and wo_numbers:
        for wo in wo_numbers[:5]:
            br_list = await get_epo_family(wo, epo_token)
            br_from_epo.extend(br_list)
            await asyncio.sleep(0.5)
    inpi_patents = []
    if deep_search:
        inpi_patents = await search_inpi(molecule, dev_codes, cas)
    fda_data = await get_fda(molecule)
    elapsed = (datetime.now() - start).total_seconds()
    result = {
        "molecule_info": {"name": molecule, "dev_codes": dev_codes, "cas_number": cas, "synonyms_count": len(pubchem.get("synonyms", []))},
        "search_result": {"wo_numbers": wo_numbers, "total_wo_discovered": len(wo_numbers), "br_from_epo": br_from_epo, "total_br_from_epo": len(br_from_epo), "inpi_patents": inpi_patents, "total_inpi_patents": len(inpi_patents)},
        "orange_book_entries": fda_data,
        "execution_time_seconds": round(elapsed, 2),
        "timestamp": datetime.now().isoformat(),
        "api_version": "3.0.0"
    }
    logger.info(f"✅ Done {elapsed:.2f}s | WOs:{len(wo_numbers)} BRs:{len(inpi_patents)}")
    return result

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/api/v1/serpapi/status")
async def serpapi_status():
    """Status do pool de API keys da SerpAPI"""
    return JSONResponse(content=pool_status())

@app.get("/api/v1/serpapi/key")
async def serpapi_key():
    """Retorna próxima key disponível do pool"""
    key = get_key()
    return {"key": key[:20] + "..." if key else None, "available": key is not None}

@app.get("/api/v1/search")
async def search(molecule_name: str = Query(...), deep_search: bool = Query(True)):
    try:
        cache_key = f"{molecule_name}_{deep_search}"
        if cache_key in _cache:
            cached_time = _cache[cache_key].get("cached_at")
            if cached_time and (datetime.now() - cached_time).seconds < Config.CACHE_TTL:
                logger.info(f"✅ Cache HIT: {molecule_name}")
                return JSONResponse(content=_cache[cache_key]["data"])
        result = await search_patents(molecule_name, deep_search)
        _cache[cache_key] = {"data": result, "cached_at": datetime.now()}
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup():
    logger.info("🚀 Pharmyrus v3.0 starting...")
    token = await get_epo_token()
    if token:
        logger.info("✅ EPO ready")
    logger.info("✅ API ready!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
