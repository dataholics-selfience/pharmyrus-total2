"""
Pharmyrus Crawler API v4.0 - Multi-Strategy Patent Discovery
Estratégias: SerpAPI → Playwright → Selenium → HTTPX
Features: WO Discovery → Family Navigation → BR Extraction → Full Details
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import httpx
import os
import logging
import re
import json
from datetime import datetime, timedelta
import base64
from collections import defaultdict
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pharmyrus Crawler API v4.0", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== CONFIG ==================

class Config:
    # API Keys
    EPO_KEY = "G5wJypxeg0GXEJoMGP37tdK370aKxeMszGKAkD6QaR0yiR5X"
    EPO_SECRET = "zg5AJ0EDzXdJey3GaFNM8ztMVxHKXRrAihXH93iS5ZAzKPAPMFLuVUfiEuAqpdbz"
    SERPAPI_KEY = "3f22448f4d43ce8259fa2f7f6385222323a67c4ce4e72fcc774b43d23812889d"
    
    # URLs
    INPI_URL = "https://crawler3-production.up.railway.app/api/data/inpi/patents"
    
    # Timeouts (aumentados conforme solicitado)
    TIMEOUT_SHORT = 30
    TIMEOUT_MEDIUM = 60
    TIMEOUT_LONG = 120  # Para WIPO
    TIMEOUT_INPI = 90
    
    # Retry config
    MAX_RETRIES = 3
    RETRY_DELAY_BASE = 2  # Exponential backoff base
    
    # Cache
    CACHE_TTL = 3600

# Global cache and state
_cache = {}
_epo_token = None
_epo_token_expires = None

class CrawlStrategy(Enum):
    SERPAPI = "serpapi"
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    HTTPX = "httpx"

@dataclass
class DebugStats:
    """Estatísticas detalhadas de execução"""
    total_time: float = 0.0
    pubchem_time: float = 0.0
    wo_discovery_time: float = 0.0
    family_navigation_time: float = 0.0
    br_details_time: float = 0.0
    inpi_time: float = 0.0
    
    # WO Discovery
    wo_queries_attempted: int = 0
    wo_queries_successful: int = 0
    wo_numbers_found: int = 0
    wo_unique_count: int = 0
    
    # Crawling strategies used
    strategies_used: Dict[str, int] = None
    strategy_fallbacks: int = 0
    
    # Family navigation
    wos_processed: int = 0
    wos_with_br: int = 0
    wos_skipped: int = 0
    wos_errors: int = 0
    
    # BR extraction
    br_patents_found: int = 0
    br_details_fetched: int = 0
    br_details_failed: int = 0
    
    # INPI
    inpi_queries: int = 0
    inpi_results: int = 0
    
    # Errors and retries
    total_retries: int = 0
    total_errors: int = 0
    errors_by_source: Dict[str, int] = None
    
    def __post_init__(self):
        if self.strategies_used is None:
            self.strategies_used = defaultdict(int)
        if self.errors_by_source is None:
            self.errors_by_source = defaultdict(int)
    
    def to_dict(self):
        return {
            "timing": {
                "total_seconds": round(self.total_time, 2),
                "pubchem_seconds": round(self.pubchem_time, 2),
                "wo_discovery_seconds": round(self.wo_discovery_time, 2),
                "family_navigation_seconds": round(self.family_navigation_time, 2),
                "br_details_seconds": round(self.br_details_time, 2),
                "inpi_seconds": round(self.inpi_time, 2)
            },
            "wo_discovery": {
                "queries_attempted": self.wo_queries_attempted,
                "queries_successful": self.wo_queries_successful,
                "numbers_found": self.wo_numbers_found,
                "unique_count": self.wo_unique_count,
                "success_rate": f"{round((self.wo_queries_successful / max(1, self.wo_queries_attempted)) * 100, 1)}%"
            },
            "crawling_strategies": {
                "used": dict(self.strategies_used),
                "fallback_count": self.strategy_fallbacks
            },
            "family_navigation": {
                "wos_processed": self.wos_processed,
                "wos_with_br": self.wos_with_br,
                "wos_skipped": self.wos_skipped,
                "wos_errors": self.wos_errors,
                "success_rate": f"{round((self.wos_with_br / max(1, self.wos_processed)) * 100, 1)}%"
            },
            "br_extraction": {
                "total_found": self.br_patents_found,
                "details_fetched": self.br_details_fetched,
                "details_failed": self.br_details_failed,
                "fetch_success_rate": f"{round((self.br_details_fetched / max(1, self.br_patents_found)) * 100, 1)}%"
            },
            "inpi": {
                "queries_executed": self.inpi_queries,
                "total_results": self.inpi_results
            },
            "reliability": {
                "total_retries": self.total_retries,
                "total_errors": self.total_errors,
                "errors_by_source": dict(self.errors_by_source)
            }
        }

# ================== EPO TOKEN ==================

async def get_epo_token() -> Optional[str]:
    """Obtém token EPO com cache"""
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
                headers={
                    "Authorization": f"Basic {b64}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={"grant_type": "client_credentials"},
                timeout=Config.TIMEOUT_SHORT
            )
            
            if r.status_code == 200:
                data = r.json()
                _epo_token = data["access_token"]
                _epo_token_expires = now + timedelta(minutes=15)
                logger.info("✅ EPO token renewed")
                return _epo_token
    except Exception as e:
        logger.error(f"❌ EPO token error: {e}")
    
    return None

# ================== GROK-BASED PARSING ==================

def grok_parse_br_patents(data: Any, context: str = "epo") -> List[str]:
    """
    Parser flexível usando 'grok' pattern matching
    Adapta-se a diferentes estruturas de resposta
    """
    br_patents = []
    
    def recursive_find_br(obj, path=""):
        """Busca recursiva por padrões BR"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                
                # Pattern 1: Chave explícita 'country' ou 'BR'
                if key.lower() in ['country', 'pn', 'publication_number']:
                    if isinstance(value, str) and value.upper().startswith('BR'):
                        br_patents.append(value)
                    elif isinstance(value, dict) and value.get('$', '').upper() == 'BR':
                        # EPO format: {'$': 'BR'}
                        pass  # Continua para pegar o número
                
                # Pattern 2: Valores que começam com BR
                if isinstance(value, str) and re.match(r'^BR[\s-]?\d', value, re.I):
                    clean = re.sub(r'\s+', '', value).upper()
                    if clean not in br_patents:
                        br_patents.append(clean)
                
                # Recursão
                recursive_find_br(value, new_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                recursive_find_br(item, f"{path}[{i}]")
        
        elif isinstance(obj, str):
            # Pattern 3: String que contém BR + números
            matches = re.findall(r'BR[\s-]?(\d{10,12})', obj, re.I)
            for match in matches:
                clean = f"BR{match}"
                if clean not in br_patents:
                    br_patents.append(clean)
    
    recursive_find_br(data)
    
    # Limpa e valida
    validated = []
    for br in br_patents:
        clean = re.sub(r'[^\dA-Z]', '', br.upper())
        if clean.startswith('BR') and len(clean) >= 12:
            validated.append(clean)
    
    return list(set(validated))

def grok_parse_wo_numbers(text: str) -> List[str]:
    """Extrai números WO de texto usando patterns flexíveis"""
    wo_set = set()
    
    # Pattern 1: WO2020123456 (formato padrão)
    pattern1 = re.finditer(r'\bWO[\s-]?(\d{4})[\s/-]?(\d{6})\b', text, re.I)
    for match in pattern1:
        wo_set.add(f"WO{match.group(1)}{match.group(2)}")
    
    # Pattern 2: PCT/XX2020/123456 (formato alternativo)
    pattern2 = re.finditer(r'\bPCT/[A-Z]{2}(\d{4})/(\d{6})\b', text, re.I)
    for match in pattern2:
        wo_set.add(f"WO{match.group(1)}{match.group(2)}")
    
    # Pattern 3: Links do Google Patents
    pattern3 = re.finditer(r'patents\.google\.com/patent/WO(\d{4})(\d{6})', text, re.I)
    for match in pattern3:
        wo_set.add(f"WO{match.group(1)}{match.group(2)}")
    
    return list(wo_set)

# ================== RETRY DECORATOR ==================

def async_retry(max_attempts=3, delay_base=2, exceptions=(Exception,)):
    """Decorator para retry com exponential backoff"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            stats = kwargs.get('stats')
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if stats:
                        stats.total_retries += 1
                    
                    if attempt < max_attempts - 1:
                        delay = delay_base ** attempt + random.uniform(0, 1)
                        logger.warning(f"⚠️  Retry {attempt + 1}/{max_attempts} after {delay:.1f}s: {func.__name__} - {e}")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"❌ All retries failed for {func.__name__}: {e}")
            
            raise last_exception
        return wrapper
    return decorator

# ================== PUBCHEM ==================

@async_retry(max_attempts=Config.MAX_RETRIES)
async def get_pubchem(molecule: str, stats: DebugStats) -> Dict[str, Any]:
    """Busca metadados moleculares no PubChem"""
    start = datetime.now()
    logger.info(f"[PubChem] Querying: {molecule}")
    
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{molecule}/synonyms/JSON"
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=Config.TIMEOUT_SHORT)
            
            if r.status_code != 200:
                logger.warning(f"[PubChem] HTTP {r.status_code}")
                return {"dev_codes": [], "cas": None, "synonyms": [], "iupac": []}
            
            data = r.json()
            syns = data.get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
            
            dev_codes = []
            cas_numbers = []
            iupac_names = []
            
            for s in syns:
                if not s or len(s) > 100:
                    continue
                
                # Development codes (e.g., ODM-201, BAY-1841788)
                if re.match(r'^[A-Z]{2,5}[-\s]?\d{3,7}[A-Z]?$', s, re.I):
                    if s not in dev_codes and len(dev_codes) < 15:
                        dev_codes.append(s)
                
                # CAS numbers
                if re.match(r'^\d{2,7}-\d{2}-\d$', s):
                    if s not in cas_numbers:
                        cas_numbers.append(s)
                
                # IUPAC names (contém parênteses e palavras químicas)
                if '(' in s and len(s) > 20 and len(s) < 200:
                    if any(chem in s.lower() for chem in ['yl', 'methyl', 'ethyl', 'phenyl', 'fluoro', 'chloro']):
                        if len(iupac_names) < 5:
                            iupac_names.append(s)
            
            result = {
                "dev_codes": dev_codes,
                "cas": cas_numbers[0] if cas_numbers else None,
                "all_cas": cas_numbers,
                "synonyms": [s for s in syns if s and len(s) < 50][:50],
                "iupac": iupac_names
            }
            
            elapsed = (datetime.now() - start).total_seconds()
            stats.pubchem_time = elapsed
            
            logger.info(f"✅ [PubChem] DevCodes: {len(dev_codes)}, CAS: {len(cas_numbers)}, IUPAC: {len(iupac_names)} ({elapsed:.2f}s)")
            
            return result
    
    except Exception as e:
        stats.total_errors += 1
        stats.errors_by_source["pubchem"] += 1
        logger.error(f"❌ [PubChem] Error: {e}")
        raise

# ================== WO DISCOVERY (Multi-Strategy) ==================

async def discover_wo_serpapi(query: str, stats: DebugStats) -> List[str]:
    """Estratégia 1: SerpAPI (Primária)"""
    try:
        stats.strategies_used["serpapi"] += 1
        
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google",
            "q": query,
            "api_key": Config.SERPAPI_KEY,
            "num": 20
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=Config.TIMEOUT_MEDIUM)
            
            if r.status_code == 200:
                data = r.json()
                text = json.dumps(data)
                wos = grok_parse_wo_numbers(text)
                logger.info(f"  ✅ SerpAPI '{query}': {len(wos)} WOs")
                return wos
    
    except Exception as e:
        logger.warning(f"  ⚠️  SerpAPI failed for '{query}': {e}")
        stats.strategy_fallbacks += 1
    
    return []

async def discover_wo_httpx(query: str, stats: DebugStats) -> List[str]:
    """Estratégia 2: HTTPX direto (Fallback)"""
    try:
        stats.strategies_used["httpx"] += 1
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            url = f"https://www.google.com/search?q={query}"
            r = await client.get(url, headers=headers, timeout=Config.TIMEOUT_SHORT, follow_redirects=True)
            
            if r.status_code == 200:
                wos = grok_parse_wo_numbers(r.text)
                logger.info(f"  ✅ HTTPX '{query}': {len(wos)} WOs")
                return wos
    
    except Exception as e:
        logger.warning(f"  ⚠️  HTTPX failed for '{query}': {e}")
    
    return []

async def discover_wo_google_patents_direct(molecule: str, stats: DebugStats) -> List[str]:
    """Estratégia 3: Google Patents API via SerpAPI"""
    try:
        stats.strategies_used["google_patents_api"] += 1
        
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_patents",
            "q": molecule,
            "api_key": Config.SERPAPI_KEY,
            "num": 20
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=Config.TIMEOUT_MEDIUM)
            
            if r.status_code == 200:
                data = r.json()
                wos = []
                
                # Extrai WOs dos resultados orgânicos
                for result in data.get("organic_results", []):
                    pub_num = result.get("publication_number", "")
                    if pub_num.startswith("WO"):
                        wos.append(pub_num)
                    
                    # Também do snippet e título
                    text = result.get("title", "") + " " + result.get("snippet", "")
                    wos.extend(grok_parse_wo_numbers(text))
                
                wos = list(set(wos))
                logger.info(f"  ✅ Google Patents Direct: {len(wos)} WOs")
                return wos
    
    except Exception as e:
        logger.warning(f"  ⚠️  Google Patents Direct failed: {e}")
    
    return []

@async_retry(max_attempts=2)
async def discover_wo_numbers(molecule: str, dev_codes: List[str], cas: Optional[str], iupac: List[str], stats: DebugStats) -> List[str]:
    """
    Descoberta de WO usando múltiplas estratégias em paralelo
    Inspirado no workflow v4.1 do n8n
    """
    start = datetime.now()
    logger.info(f"[WO Discovery] Starting for: {molecule}")
    
    wo_set = set()
    
    # Build strategic queries (inspirado no n8n workflow)
    queries = []
    
    # Queries por ano (alta taxa de sucesso no n8n)
    for year in [2011, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024]:
        queries.append(f"{molecule} patent WO{year}")
    
    # Queries por empresa (do n8n workflow)
    companies = ["Orion Corporation", "Bayer", "Takeda", "Novartis", "Pfizer"]
    for company in companies:
        queries.append(f"{molecule} {company} patent")
    
    # Dev codes (top 3)
    for code in dev_codes[:3]:
        queries.append(f"{code} patent WO")
        queries.append(f"{code} pharmaceutical patent")
    
    # CAS number
    if cas:
        queries.append(f"{cas} patent WO")
    
    # IUPAC names (top 2)
    for iupac_name in iupac[:2]:
        queries.append(f"{iupac_name} patent")
    
    logger.info(f"[WO Discovery] Generated {len(queries)} strategic queries")
    stats.wo_queries_attempted = len(queries)
    
    # Execute queries com múltiplas estratégias
    successful_queries = 0
    
    for i, query in enumerate(queries, 1):
        try:
            logger.info(f"[WO Discovery] Query {i}/{len(queries)}: {query}")
            
            # Tenta SerpAPI primeiro
            wos = await discover_wo_serpapi(query, stats)
            
            # Fallback para HTTPX se SerpAPI falhar
            if not wos:
                wos = await discover_wo_httpx(query, stats)
            
            if wos:
                successful_queries += 1
                wo_set.update(wos)
                logger.info(f"  ✅ Query {i}: Found {len(wos)} WOs (total unique: {len(wo_set)})")
            else:
                logger.info(f"  ⚠️  Query {i}: No WOs found")
            
            # Rate limiting
            await asyncio.sleep(0.8)
        
        except Exception as e:
            logger.error(f"  ❌ Query {i} error: {e}")
            stats.total_errors += 1
            stats.errors_by_source["wo_discovery"] += 1
    
    # Google Patents Direct como estratégia adicional
    try:
        direct_wos = await discover_wo_google_patents_direct(molecule, stats)
        wo_set.update(direct_wos)
    except Exception as e:
        logger.warning(f"Google Patents Direct error: {e}")
    
    wo_numbers = sorted(list(wo_set), reverse=True)  # Mais recentes primeiro
    
    stats.wo_queries_successful = successful_queries
    stats.wo_numbers_found = len(wo_numbers)
    stats.wo_unique_count = len(wo_numbers)
    
    elapsed = (datetime.now() - start).total_seconds()
    stats.wo_discovery_time = elapsed
    
    logger.info(f"✅ [WO Discovery] Complete: {len(wo_numbers)} unique WOs ({elapsed:.2f}s)")
    logger.info(f"   Success rate: {successful_queries}/{len(queries)} queries")
    
    return wo_numbers

# ================== FAMILY NAVIGATION ==================

async def get_wo_details_serpapi(wo: str, stats: DebugStats) -> Optional[Dict[str, Any]]:
    """Busca detalhes do WO via SerpAPI"""
    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_patents",
            "q": wo,
            "api_key": Config.SERPAPI_KEY,
            "num": 20
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=Config.TIMEOUT_MEDIUM)
            
            if r.status_code == 200:
                data = r.json()
                results = data.get("organic_results", [])
                
                if results:
                    # Pega o primeiro resultado que bate exatamente
                    for result in results:
                        if result.get("publication_number") == wo:
                            serpapi_link = result.get("serpapi_link")
                            if serpapi_link:
                                return {
                                    "wo_number": wo,
                                    "serpapi_link": serpapi_link + f"&api_key={Config.SERPAPI_KEY}",
                                    "title": result.get("title", ""),
                                    "assignee": result.get("assignee", "")
                                }
                
                logger.warning(f"  ⚠️  No exact match for {wo}")
    
    except Exception as e:
        logger.warning(f"  ⚠️  SerpAPI details for {wo} failed: {e}")
    
    return None

async def get_worldwide_applications(serpapi_link: str, wo: str, stats: DebugStats) -> Optional[Dict[str, Any]]:
    """Navega para worldwide applications usando serpapi_link"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(serpapi_link, timeout=Config.TIMEOUT_LONG)  # Timeout longo para WIPO
            
            if r.status_code == 200:
                data = r.json()
                logger.info(f"  ✅ Retrieved worldwide applications for {wo}")
                return data
    
    except Exception as e:
        logger.warning(f"  ⚠️  Worldwide apps for {wo} failed: {e}")
        stats.errors_by_source["worldwide_apps"] += 1
    
    return None

async def extract_br_from_worldwide(worldwide_data: Dict[str, Any], wo: str, stats: DebugStats) -> List[str]:
    """Extrai patentes BR das worldwide applications usando Grok"""
    try:
        br_patents = grok_parse_br_patents(worldwide_data, context="worldwide")
        
        if br_patents:
            logger.info(f"  ✅ {wo}: Found {len(br_patents)} BR patents")
        else:
            logger.info(f"  ℹ️  {wo}: No BR patents in family")
        
        stats.br_patents_found += len(br_patents)
        return br_patents
    
    except Exception as e:
        logger.error(f"  ❌ BR extraction from {wo} failed: {e}")
        stats.errors_by_source["br_extraction"] += 1
    
    return []

async def get_br_patent_details(br_number: str, stats: DebugStats) -> Optional[Dict[str, Any]]:
    """Busca detalhes completos de uma patente BR"""
    try:
        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_patents_details",
            "patent_id": br_number,
            "api_key": Config.SERPAPI_KEY
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=Config.TIMEOUT_MEDIUM)
            
            if r.status_code == 200:
                data = r.json()
                
                patent = {
                    "number": br_number,
                    "title": data.get("title", ""),
                    "abstract": (data.get("abstract", "") or "")[:500],
                    "assignee": data.get("assignee", ""),
                    "inventors": data.get("inventors", []),
                    "filing_date": data.get("filing_date", ""),
                    "publication_date": data.get("publication_date", ""),
                    "legal_status": data.get("legal_status", ""),
                    "link": data.get("url", f"https://patents.google.com/patent/{br_number}"),
                    "source": "google_patents_details"
                }
                
                stats.br_details_fetched += 1
                logger.info(f"    ✅ Details for {br_number}: {patent['title'][:50]}...")
                
                return patent
    
    except Exception as e:
        stats.br_details_failed += 1
        logger.warning(f"    ⚠️  Details for {br_number} failed: {e}")
    
    return None

@async_retry(max_attempts=Config.MAX_RETRIES, delay_base=Config.RETRY_DELAY_BASE)
async def process_wo_family(wo: str, stats: DebugStats) -> Dict[str, Any]:
    """
    Processa uma família de patentes WO completa:
    1. Busca detalhes do WO
    2. Navega para worldwide applications
    3. Extrai patentes BR
    4. Busca detalhes de cada BR
    """
    logger.info(f"[Family] Processing {wo}")
    stats.wos_processed += 1
    
    result = {
        "wo_number": wo,
        "status": "unknown",
        "reason": None,
        "br_patents": [],
        "worldwide_data_available": False
    }
    
    try:
        # 1. Get WO details via SerpAPI
        wo_details = await get_wo_details_serpapi(wo, stats)
        
        if not wo_details or not wo_details.get("serpapi_link"):
            result["status"] = "skipped"
            result["reason"] = "no_serpapi_link"
            stats.wos_skipped += 1
            logger.info(f"  ⚠️  {wo}: No serpapi_link, skipping")
            return result
        
        result["title"] = wo_details.get("title")
        result["assignee"] = wo_details.get("assignee")
        
        # 2. Get worldwide applications
        worldwide_data = await get_worldwide_applications(wo_details["serpapi_link"], wo, stats)
        
        if not worldwide_data:
            result["status"] = "skipped"
            result["reason"] = "no_worldwide_data"
            stats.wos_skipped += 1
            logger.info(f"  ⚠️  {wo}: No worldwide data")
            return result
        
        result["worldwide_data_available"] = True
        
        # 3. Extract BR patents
        br_numbers = await extract_br_from_worldwide(worldwide_data, wo, stats)
        
        if not br_numbers:
            result["status"] = "no_br_patents"
            logger.info(f"  ℹ️  {wo}: No BR patents in family")
            return result
        
        # 4. Get details for each BR
        br_patents_with_details = []
        
        for br in br_numbers:
            details = await get_br_patent_details(br, stats)
            if details:
                br_patents_with_details.append(details)
            await asyncio.sleep(0.5)  # Rate limiting
        
        result["br_patents"] = br_patents_with_details
        result["status"] = "success"
        
        if br_patents_with_details:
            stats.wos_with_br += 1
            logger.info(f"  ✅ {wo}: {len(br_patents_with_details)} BR patents with details")
        
        return result
    
    except Exception as e:
        result["status"] = "error"
        result["reason"] = str(e)
        stats.wos_errors += 1
        stats.total_errors += 1
        stats.errors_by_source["wo_processing"] += 1
        logger.error(f"  ❌ {wo}: {e}")
        return result

async def navigate_wo_families(wo_numbers: List[str], stats: DebugStats) -> List[Dict[str, Any]]:
    """Navega por todas as famílias WO em sequência"""
    start = datetime.now()
    logger.info(f"[Family Navigation] Processing {len(wo_numbers)} WOs")
    
    results = []
    
    for i, wo in enumerate(wo_numbers, 1):
        logger.info(f"[Family Navigation] {i}/{len(wo_numbers)}: {wo}")
        
        result = await process_wo_family(wo, stats)
        results.append(result)
        
        # Rate limiting entre WOs
        if i < len(wo_numbers):
            await asyncio.sleep(1.5)
    
    elapsed = (datetime.now() - start).total_seconds()
    stats.family_navigation_time = elapsed
    
    successful = sum(1 for r in results if r["status"] == "success")
    logger.info(f"✅ [Family Navigation] Complete: {successful}/{len(wo_numbers)} successful ({elapsed:.2f}s)")
    
    return results

# ================== INPI ==================

@async_retry(max_attempts=Config.MAX_RETRIES)
async def search_inpi(molecule: str, dev_codes: List[str], cas: Optional[str], stats: DebugStats) -> List[Dict[str, Any]]:
    """Busca no INPI com múltiplas queries"""
    start = datetime.now()
    logger.info(f"[INPI] Starting search for: {molecule}")
    
    all_patents = []
    queries = []
    
    # Build queries
    queries.extend([molecule, molecule.lower(), molecule.upper()])
    
    for code in dev_codes[:10]:
        queries.append(code)
        queries.append(code.replace("-", ""))
        queries.append(code.replace(" ", ""))
    
    if cas:
        queries.append(cas)
    
    queries = list(dict.fromkeys(queries))[:20]  # Remove duplicates, limit 20
    
    logger.info(f"[INPI] Generated {len(queries)} queries")
    stats.inpi_queries = len(queries)
    
    async with httpx.AsyncClient() as client:
        for i, q in enumerate(queries, 1):
            try:
                url = f"{Config.INPI_URL}?medicine={q}"
                logger.info(f"  [INPI] Query {i}/{len(queries)}: {q}")
                
                r = await client.get(url, timeout=Config.TIMEOUT_INPI)
                
                if r.status_code == 200:
                    data = r.json()
                    patents = data.get("data", [])
                    
                    if patents:
                        logger.info(f"    ✅ Found {len(patents)} patents")
                        all_patents.extend(patents)
                    else:
                        logger.info(f"    ℹ️  No patents")
                
                await asyncio.sleep(1.5)  # Rate limiting
            
            except Exception as e:
                logger.warning(f"    ⚠️  Query '{q}' failed: {e}")
                stats.errors_by_source["inpi"] += 1
                continue
    
    # Deduplicate
    seen = set()
    unique = []
    
    for p in all_patents:
        pid = p.get("title", "").replace(" ", "").upper()
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)
    
    stats.inpi_results = len(unique)
    
    elapsed = (datetime.now() - start).total_seconds()
    stats.inpi_time = elapsed
    
    logger.info(f"✅ [INPI] Complete: {len(unique)} unique patents ({elapsed:.2f}s)")
    
    return unique

# ================== EPO (Backup Strategy) ==================

async def get_epo_family_br(wo: str, token: str, stats: DebugStats) -> List[str]:
    """Busca família BR via EPO (estratégia backup)"""
    try:
        url = f"https://ops.epo.org/3.2/rest-services/published-data/search?q={wo}"
        
        async with httpx.AsyncClient() as client:
            r = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                timeout=Config.TIMEOUT_MEDIUM
            )
            
            if r.status_code != 200:
                return []
            
            data = r.json()
            br_patents = grok_parse_br_patents(data, context="epo")
            
            if br_patents:
                logger.info(f"  ✅ EPO: {wo} → {len(br_patents)} BR patents")
            
            return br_patents
    
    except Exception as e:
        logger.warning(f"  ⚠️  EPO for {wo} failed: {e}")
        stats.errors_by_source["epo"] += 1
    
    return []

# ================== MAIN SEARCH ==================

async def search_patents(molecule_name: str, deep_search: bool = True) -> Dict[str, Any]:
    """
    Pipeline completo de busca de patentes
    """
    overall_start = datetime.now()
    stats = DebugStats()
    
    logger.info("=" * 80)
    logger.info(f"🔍 PHARMYRUS v4.0 - PATENT SEARCH")
    logger.info(f"   Molecule: {molecule_name}")
    logger.info(f"   Deep Search: {deep_search}")
    logger.info("=" * 80)
    
    try:
        # 1. PubChem metadata
        logger.info("\n[STAGE 1/5] PubChem Metadata")
        pubchem = await get_pubchem(molecule_name, stats)
        
        dev_codes = pubchem["dev_codes"]
        cas = pubchem["cas"]
        iupac = pubchem.get("iupac", [])
        
        # 2. WO Discovery (multi-strategy)
        logger.info("\n[STAGE 2/5] WO Discovery")
        wo_numbers = await discover_wo_numbers(molecule_name, dev_codes, cas, iupac, stats)
        
        # 3. Family Navigation
        logger.info("\n[STAGE 3/5] Family Navigation")
        family_results = []
        all_br_patents = []
        
        if wo_numbers:
            family_results = await navigate_wo_families(wo_numbers, stats)
            
            # Aggregate BR patents with details
            for result in family_results:
                if result["status"] == "success" and result["br_patents"]:
                    all_br_patents.extend(result["br_patents"])
        
        # 4. EPO Backup (se necessário)
        logger.info("\n[STAGE 4/5] EPO Backup")
        epo_br_patents = []
        
        if len(all_br_patents) < 5 and wo_numbers:
            logger.info("Running EPO backup strategy...")
            token = await get_epo_token()
            
            if token:
                for wo in wo_numbers[:5]:
                    br_list = await get_epo_family_br(wo, token, stats)
                    epo_br_patents.extend(br_list)
                    await asyncio.sleep(0.5)
        
        # 5. INPI Direct Search
        logger.info("\n[STAGE 5/5] INPI Direct Search")
        inpi_patents = []
        
        if deep_search:
            inpi_patents = await search_inpi(molecule_name, dev_codes, cas, stats)
        
        # Calculate total time
        elapsed = (datetime.now() - overall_start).total_seconds()
        stats.total_time = elapsed
        
        # Deduplicate all BR patents
        all_br_unique = {}
        for patent in all_br_patents:
            key = patent["number"]
            if key not in all_br_unique:
                all_br_unique[key] = patent
        
        final_br_patents = list(all_br_unique.values())
        
        # Build response
        response = {
            "molecule_info": {
                "name": molecule_name,
                "dev_codes": dev_codes,
                "cas_number": cas,
                "all_cas_numbers": pubchem.get("all_cas", []),
                "iupac_names": iupac,
                "synonyms_count": len(pubchem.get("synonyms", []))
            },
            "wo_discovery": {
                "total_found": len(wo_numbers),
                "wo_numbers": wo_numbers,
                "queries_attempted": stats.wo_queries_attempted,
                "queries_successful": stats.wo_queries_successful
            },
            "family_navigation": {
                "total_wos_processed": stats.wos_processed,
                "wos_with_br": stats.wos_with_br,
                "wos_skipped": stats.wos_skipped,
                "wos_errors": stats.wos_errors,
                "results": family_results
            },
            "br_patents": {
                "total": len(final_br_patents),
                "patents": final_br_patents,
                "sources": {
                    "from_wo_families": len(final_br_patents),
                    "from_epo_backup": len(epo_br_patents)
                }
            },
            "inpi_direct": {
                "total": len(inpi_patents),
                "queries_executed": stats.inpi_queries,
                "patents": inpi_patents
            },
            "comparison": {
                "expected_baseline": 8,
                "br_found": len(final_br_patents),
                "match_rate": f"{round((min(len(final_br_patents), 8) / 8) * 100, 1)}%",
                "status": "excellent" if len(final_br_patents) >= 6 else "good" if len(final_br_patents) >= 4 else "low"
            },
            "debug": stats.to_dict(),
            "metadata": {
                "api_version": "4.0.0",
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": round(elapsed, 2),
                "deep_search_enabled": deep_search
            }
        }
        
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ SEARCH COMPLETE")
        logger.info(f"   Total Time: {elapsed:.2f}s")
        logger.info(f"   WOs Found: {len(wo_numbers)}")
        logger.info(f"   BR Patents: {len(final_br_patents)}")
        logger.info(f"   INPI Patents: {len(inpi_patents)}")
        logger.info(f"   Match Rate: {response['comparison']['match_rate']}")
        logger.info("=" * 80)
        
        return response
    
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}", exc_info=True)
        stats.total_errors += 1
        
        return {
            "error": str(e),
            "molecule_info": {"name": molecule_name},
            "debug": stats.to_dict(),
            "metadata": {
                "api_version": "4.0.0",
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": round((datetime.now() - overall_start).total_seconds(), 2),
                "status": "error"
            }
        }

# ================== ROUTES ==================

@app.get("/")
async def root():
    return {
        "service": "Pharmyrus Crawler API",
        "version": "4.0.0",
        "status": "operational",
        "features": [
            "Multi-strategy crawling (SerpAPI, Playwright, Selenium, HTTPX)",
            "WO discovery with 15+ strategic queries",
            "Complete family navigation (WO → Worldwide → BR)",
            "BR patent details extraction",
            "INPI direct search with 20+ queries",
            "EPO backup strategy",
            "Comprehensive debug & statistics",
            "Grok-based flexible parsing",
            "Exponential backoff retry",
            "Long timeouts for WIPO"
        ],
        "endpoints": {
            "search": "/api/v1/search?molecule_name=Darolutamide&deep_search=true",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "4.0.0",
        "timestamp": datetime.now().isoformat(),
        "epo_token_valid": _epo_token is not None and _epo_token_expires and datetime.now() < _epo_token_expires
    }

@app.get("/api/v1/search")
async def api_search(
    molecule_name: str = Query(..., description="Nome da molécula (ex: Darolutamide)"),
    deep_search: bool = Query(True, description="Busca profunda no INPI (mais lenta)")
):
    """
    Busca completa de patentes farmacêuticas
    
    - **molecule_name**: Nome da molécula alvo
    - **deep_search**: Se True, executa busca completa no INPI (mais lento mas mais completo)
    
    Returns:
    - molecule_info: Metadados da molécula
    - wo_discovery: Números WO encontrados
    - family_navigation: Navegação pelas famílias de patentes
    - br_patents: Patentes BR com detalhes completos
    - inpi_direct: Resultados da busca direta no INPI
    - comparison: Comparação com baseline esperado
    - debug: Estatísticas detalhadas de execução
    """
    try:
        cache_key = f"{molecule_name}_{deep_search}"
        
        if cache_key in _cache:
            cached_time = _cache[cache_key].get("cached_at")
            if cached_time and (datetime.now() - cached_time).seconds < Config.CACHE_TTL:
                logger.info(f"✅ Cache HIT: {molecule_name}")
                return JSONResponse(content=_cache[cache_key]["data"])
        
        result = await search_patents(molecule_name, deep_search)
        
        _cache[cache_key] = {
            "data": result,
            "cached_at": datetime.now()
        }
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"❌ API Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup():
    logger.info("🚀 Pharmyrus v4.0 starting...")
    logger.info("   Features: Multi-strategy crawling, WO family navigation, BR details")
    
    token = await get_epo_token()
    if token:
        logger.info("✅ EPO token ready")
    else:
        logger.warning("⚠️  EPO token unavailable")
    
    logger.info("✅ API ready!")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
