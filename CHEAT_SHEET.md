# ⚡ Pharmyrus v4.0 - Quick Reference

## 🚀 START

```bash
# Local
python main.py

# Test
curl "http://localhost:8000/api/v1/search?molecule_name=Darolutamide"
```

## ✅ WHAT TO EXPECT (Darolutamide)

```json
{
  "molecule_info": {
    "dev_codes": [...],      // ✅ Should have 2+
    "cas_number": "..."      // ✅ Should exist
  },
  "wo_discovery": {
    "total_found": 12,       // ✅ Should be 10-15
    "queries_successful": 14 // ✅ Should be 10+/18
  },
  "family_navigation": {
    "wos_with_br": 6         // ✅ Should be 3+
  },
  "br_patents": {
    "total": 8,              // ✅ CRITICAL! Should be 6-10
    "patents": [...]
  },
  "comparison": {
    "match_rate": "100%",    // ✅ Should be 70%+
    "status": "excellent"
  }
}
```

## 🔍 DIAGNOSE PROBLEMS

### Zero WOs?
```bash
# Check SerpAPI
curl "https://serpapi.com/search.json?engine=google&q=Darolutamide+patent+WO2018&api_key=YOUR_KEY"
```
**Fix:** Check API key, quota, or force HTTPX fallback

### WOs but zero BRs?
```bash
# Check WO details
curl "https://serpapi.com/search.json?engine=google_patents&q=WO2018015433&api_key=YOUR_KEY"
```
**Fix:** Check if `serpapi_link` exists in response

### BRs but no details?
```bash
# Check BR details API
curl "https://serpapi.com/search.json?engine=google_patents_details&patent_id=BR112016028234A2&api_key=YOUR_KEY"
```
**Fix:** Increase delays (rate limiting)

## 📊 DEBUG STATS

```json
"debug": {
  "wo_discovery": {
    "success_rate": "??%"  // Should be >60%
  },
  "family_navigation": {
    "success_rate": "??%"  // Should be >40%
  },
  "br_extraction": {
    "fetch_success_rate": "??%" // Should be >70%
  },
  "reliability": {
    "errors_by_source": {...}  // Check most common errors
  }
}
```

## 🎯 TARGETS

| Metric | Target |
|--------|--------|
| WOs | 10-15 |
| WO success | 70%+ |
| BRs | 6-10 |
| Match rate | 70%+ |

## ⚙️ CONFIG

```python
# Timeouts
TIMEOUT_SHORT = 30    # Normal ops
TIMEOUT_MEDIUM = 60   # EPO, SerpAPI
TIMEOUT_LONG = 120    # WIPO (critical!)

# Retry
MAX_RETRIES = 3
RETRY_DELAY = 2^attempt + random
```

## 🔧 COMMON FIXES

**SerpAPI quota exceeded:**
- Switch to HTTPX fallback
- Increase delays
- Check quota dashboard

**WIPO timeout:**
- Already 120s (max safe)
- Check network
- Use EPO backup

**Parser fails:**
- Grok should adapt automatically
- Check if tags changed drastically
- Report for fix

## 📝 QUICK TEST

```bash
# Full test suite
python3 test_api.py

# Single molecule
curl "http://localhost:8000/api/v1/search?molecule_name=Ixazomib" | jq '.'

# Fast test (no INPI)
curl "http://localhost:8000/api/v1/search?molecule_name=Olaparib&deep_search=false"
```

## 🆘 HELP

**Send me:**
1. Molecule tested
2. Full JSON response
3. Debug section
4. Console logs

**I diagnose:**
- Where it failed
- Why it failed
- How to fix

## ✨ FEATURES

- [x] Multi-strategy crawling
- [x] 15+ WO queries
- [x] Family navigation
- [x] BR details extraction
- [x] Grok parser
- [x] Auto-retry
- [x] Long timeouts
- [x] Extensive debug
- [ ] Playwright (future)
- [ ] Selenium (future)

## 🎯 SUCCESS = 70%+ match rate!
