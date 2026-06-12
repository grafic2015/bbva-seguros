"""
Agente 1 — Búsqueda de ofertas de trabajo.
- requests + BeautifulSoup para sitios estáticos (Computrabajo, LinkedIn, Talent.com)
- Playwright (Chromium headless) para sitios que requieren JS (Google Jobs, Indeed, ZonaJobs, Jooble, GetOnBoard, Adzuna)
"""

import re
import sys
import json
import time
import random
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import config

SEEN_FILE = Path(__file__).resolve().parent.parent / "seen_jobs.json"


def _load_seen() -> set:
    try:
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _save_seen(seen: set) -> None:
    try:
        SEEN_FILE.write_text(json.dumps(list(seen), indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
]


def _rotating_headers() -> dict:
    h = dict(HEADERS)
    h["User-Agent"] = random.choice(USER_AGENTS)
    return h


def get_soup(url: str, retries: int = 3) -> BeautifulSoup | None:
    for attempt in range(retries):
        try:
            # Delay anti-ban aleatorio entre requests
            if attempt > 0:
                time.sleep(random.uniform(3, 7))
            else:
                time.sleep(random.uniform(0.5, 2.0))
            resp = requests.get(url, headers=_rotating_headers(), timeout=14)
            resp.encoding = resp.apparent_encoding
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            print(f"[Agente 1]   Error HTTP (intento {attempt+1}/{retries}): {e}")
    return None


def get_soup_pw(page, url: str, wait_selector: str = None, wait_ms: int = 2000) -> BeautifulSoup | None:
    try:
        page.goto(url, timeout=20000, wait_until="domcontentloaded")
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=8000)
            except PWTimeout:
                pass
        else:
            time.sleep(wait_ms / 1000)
        return BeautifulSoup(page.content(), "html.parser")
    except Exception as e:
        print(f"[Agente 1]   Error Playwright: {e}")
        return None


def limpiar(texto: str) -> str:
    texto = re.sub(r"(Postulado|Vista|Nuevo|Destacado)+$", "", texto)
    texto = re.sub(r"^\d[,\.]\d", "", texto)
    return " ".join(texto.split())


def mk_job(company, title, link, source, desc="", fecha="", location=""):
    return {
        "company":     limpiar(company),
        "website":     "",
        "job_title":   limpiar(title),
        "description": desc or f"Oferta en {source}",
        "apply_url":   link,
        "source":      source,
        "fecha":       fecha,   # etiqueta de recencia ("Hoy", "Ayer", ...) si el portal la da
        "location":    location,  # ubicación de la búsqueda
    }


# Patrón de recencia que aparece en los listados (Computrabajo, etc.)
FECHA_RE = re.compile(
    r"(Hoy|Ayer|Hace\s+\d+\s+(?:minuto|hora|d[ií]a|semana|mes)\w*)", re.I
)


def extraer_fecha(texto: str) -> str:
    m = FECHA_RE.search(texto or "")
    return m.group(1) if m else ""


def es_reciente(fecha: str, dias: int = 1) -> bool:
    """True si el aviso fue publicado dentro de los últimos `dias` días."""
    if not fecha:
        return True
    f = fecha.lower()
    if "hoy" in f or ("hace" in f and ("hora" in f or "minuto" in f)):
        return True
    if dias == 1:
        return False
    if "ayer" in f and dias >= 2:
        return True
    m = re.search(r"hace\s+(\d+)\s+d[ií]a", f)
    if m and int(m.group(1)) <= dias:
        return True
    return False


def _pasa_filtros(title: str, company: str, required_keywords: str = "") -> bool:
    """Devuelve False si el trabajo debe ser excluido por keyword o empresa.
    Usa búsqueda de palabras completas (límites de palabra) para más precisión."""
    title_l   = title.lower()
    company_l = company.lower()

    # Validar que el título contenga AL MENOS una palabra clave requerida
    if required_keywords:
        # Dividir por comas primero (frases exactas), luego por espacios
        frases = [f.strip().lower() for f in required_keywords.split(",") if f.strip()]
        if not frases:
            frases = [required_keywords.lower()]

        has_keyword = False
        for frase in frases:
            palabras = frase.split()
            # Buscar la frase exacta o palabras clave principales (> 3 caracteres)
            if len(palabras) > 1:
                # Es una frase: buscar coincidencia exacta
                if frase in title_l:
                    has_keyword = True
                    break
            else:
                # Es una palabra: buscar con límites de palabra
                palabra = palabras[0]
                if len(palabra) > 2:
                    # Usar regex con límites de palabra
                    if re.search(r'\b' + re.escape(palabra) + r'\b', title_l):
                        has_keyword = True
                        break

        if not has_keyword:
            return False

    # Palabras excluidas en el título
    for kw in (config.EXCLUDE_KEYWORDS or []):
        if kw.strip().lower() in title_l:
            return False

    # Empresas en la blacklist
    for emp in (config.BLACKLIST_COMPANIES or []):
        if emp.strip().lower() and emp.strip().lower() in company_l:
            return False

    return True


def _pasa_modalidad(title: str, desc: str) -> bool:
    """Filtra por modalidad si está configurado."""
    mod = (config.JOB_MODALITY or "").strip().lower()
    if not mod:
        return True
    texto = (title + " " + desc).lower()
    if mod == "remoto":
        return any(w in texto for w in ["remoto", "remote", "teletrabajo", "100% remoto"])
    if mod == "hibrido":
        return any(w in texto for w in ["híbrido", "hibrido", "hybrid"])
    if mod == "presencial":
        # excluir los que digan remoto
        return not any(w in texto for w in ["remoto", "remote", "teletrabajo"])
    return True


def _score_gemini(title: str, company: str, desc: str) -> tuple[int, str]:
    """Desactivado temporalmente por petición del usuario para ahorrar cuota de API."""
    return -1, ""
    try:
        import requests as req
        prompt = (
            f"Evaluá del 1 al 10 qué tan relevante es esta oferta para un técnico de soporte IT "
            f"con experiencia en Windows, Microsoft 365, Intune y redes.\n"
            f"Puesto: {title}\nEmpresa: {company}\nDescripción: {desc[:300]}\n"
            f"Respondé EXACTAMENTE en este formato: [SCORE]|[JUSTIFICACION_CORTA]\n"
            f"Ejemplo: 8|Requiere Intune y soporte Windows, hace match perfecto."
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        resp = req.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        parts = text.split('|', 1)
        score = max(1, min(10, int(re.search(r'\d+', parts[0]).group())))
        reason = parts[1].strip() if len(parts) > 1 else ""
        return score, reason
    except Exception:
        return -1, ""


# ── Scrapers estáticos ────────────────────────────────────────────────────────

def search_computrabajo(kw, loc, n):
    jobs = []
    q    = kw.replace(" ", "+")
    city = loc.split(",")[0].strip().replace(" ", "+")
    page = 1
    while len(jobs) < n:
        url  = f"https://www.computrabajo.com.ar/ofertas-de-trabajo/?q={q}&l={city}&p={page}"
        soup = get_soup(url)
        if not soup:
            break
        items = soup.select("article[data-id]") or soup.select(".js-o-listItems article")
        if not items:
            break
        for a in items:
            t = a.find("h2") or a.find("a", class_="js-o-link")
            c = a.find(class_="dFlex fc_base") or a.find("p", class_="fs16")
            l = a.find("a", href=True)
            title   = t.get_text(strip=True) if t else ""
            company = c.get_text(strip=True) if c else ""
            link    = l["href"] if l else ""
            fecha   = extraer_fecha(a.get_text(" ", strip=True))
            if link and not link.startswith("http"):
                link = "https://www.computrabajo.com.ar" + link
            if title:
                jobs.append(mk_job(company, title, link, "Computrabajo", fecha=fecha))
        page += 1
        if page > 3:  # máximo 3 páginas
            break
    return jobs[:n]


def search_linkedin(kw, loc, n):
    jobs = []
    q = kw.replace(" ", "%20")
    l = loc.replace(" ", "%20")
    start = 0
    while len(jobs) < n:
        url  = f"https://www.linkedin.com/jobs/search/?keywords={q}&location={l}&f_TPR=r604800&start={start}"
        soup = get_soup(url)
        if not soup:
            break
        cards = soup.select(".jobs-search__results-list li") or soup.select("li[class*='job']")
        if not cards:
            break
        for card in cards:
            t = card.find("h3") or card.find("a", class_="job-search-card__title-link")
            c = card.find("h4") or card.find(class_="job-search-card__company-name")
            lk = card.find("a", href=True)
            title   = t.get_text(strip=True) if t else ""
            company = c.get_text(strip=True) if c else ""
            link    = lk["href"] if lk else ""
            if title:
                jobs.append(mk_job(company, title, link, "LinkedIn"))
        start += 25
        if start >= 50:  # máximo 2 páginas (25 por página)
            break
    return jobs[:n]


def search_talent(kw, loc, n):
    jobs = []
    q    = kw.replace(" ", "+")
    city = loc.split(",")[0].strip().replace(" ", "+")
    page = 1
    while len(jobs) < n:
        url  = f"https://ar.talent.com/jobs?k={q}&l={city}&p={page}"
        soup = get_soup(url)
        if not soup:
            break
        cards = soup.select("[class*='card']") or soup.select("article")
        if not cards:
            break
        for card in cards:
            t   = card.find("h2") or card.find("h3") or card.find(class_=re.compile(r"title", re.I))
            c   = card.find(class_=re.compile(r"company|employer", re.I))
            l_e = card.find("a", href=True)
            title   = t.get_text(strip=True) if t   else ""
            company = c.get_text(strip=True) if c   else ""
            link    = l_e["href"]            if l_e else ""
            if link and not link.startswith("http"):
                link = "https://ar.talent.com" + link
            if title:
                jobs.append(mk_job(company, title, link, "Talent.com"))
        page += 1
        if page > 3:  # máximo 3 páginas
            break
    return jobs[:n]


# ── Scrapers con Playwright ───────────────────────────────────────────────────

def search_bumeran(kw, loc, n, days=None):
    """Intercepta la API interna de Bumeran con expect_response (paginado)."""
    jobs = []
    kw_slug = kw.lower().replace(" ", "-")
    is_hoy  = (days == 1) if days is not None else getattr(config, "JOB_SOLO_HOY", False)
    prefix  = "empleos-publicacion-hoy-busqueda" if is_hoy else "empleos-busqueda"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(
            user_agent=HEADERS["User-Agent"], locale="es-AR",
            viewport={"width": 1280, "height": 800},
        )
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        p = ctx.new_page()
        try:
            for page_num in range(1, 4):   # hasta 3 páginas
                if page_num == 1:
                    url = f"https://www.bumeran.com.ar/{prefix}-{kw_slug}.html"
                else:
                    url = f"https://www.bumeran.com.ar/{prefix}-{kw_slug}-pagina-{page_num}.html"
                try:
                    with p.expect_response("**/searchV2**", timeout=20000) as resp_info:
                        p.goto(url, timeout=25000, wait_until="domcontentloaded")
                    data  = resp_info.value.json()
                    items = data.get("content") or data.get("avisos") or []
                    if not items:
                        break
                    for aviso in items:
                        title   = aviso.get("titulo", "")
                        empresa = aviso.get("empresa") or {}
                        company = empresa.get("nombre", "") if isinstance(empresa, dict) else str(empresa)
                        link    = f"https://www.bumeran.com.ar{aviso.get('postulacionUrl', aviso.get('url', ''))}"
                        if title:
                            jobs.append(mk_job(company, title, link, "Bumeran"))
                    if len(jobs) >= n:
                        break
                except Exception as e:
                    print(f"[Agente 1]   Bumeran p{page_num} error: {e}")
                    break
        finally:
            browser.close()
    return jobs[:n]


def search_google_jobs(page, kw, loc, n):
    jobs = []
    q    = f"{kw} empleos {loc}".replace(" ", "+")
    soup = get_soup_pw(page, f"https://www.google.com/search?q={q}&ibp=htl;jobs&gl=ar&hl=es",
                       wait_selector="[jsname='MZnM8e']", wait_ms=3000)
    if not soup:
        return jobs
    for card in (soup.select("[jsname='MZnM8e']") or soup.select("[class*='iFjolb']") or soup.select("[data-jlid]"))[:n]:
        t = card.find(class_=re.compile(r"title|puesto|BjJfJf", re.I)) or card.find("h3") or card.find("div", {"role": "heading"})
        c = card.find(class_=re.compile(r"company|employer|vNEEBe", re.I))
        l = card.find("a", href=True)
        title   = t.get_text(strip=True) if t else ""
        company = c.get_text(strip=True) if c else ""
        link    = l["href"] if l else f"https://www.google.com/search?q={q}&ibp=htl;jobs"
        if title:
            jobs.append(mk_job(company, title, link, "Google Jobs"))
    return jobs


def search_indeed(page, kw, loc, n, days=None):
    jobs = []
    q = kw.replace(" ", "+")
    l = loc.split(",")[0].strip().replace(" ", "+")
    is_hoy   = (days == 1) if days is not None else getattr(config, "JOB_SOLO_HOY", False)
    recencia = f"&fromage={days}" if days is not None else ("&fromage=1" if is_hoy else "")
    start = 0
    while len(jobs) < n:
        url  = f"https://ar.indeed.com/jobs?q={q}&l={l}{recencia}&start={start}"
        soup = get_soup_pw(page, url, wait_selector=".job_seen_beacon", wait_ms=3000)
        if not soup:
            break
        cards = soup.select(".job_seen_beacon") or soup.select(".tapItem") or soup.select("article")
        if not cards:
            break
        for card in cards:
            t = card.find("h2") or card.find(class_=re.compile(r"jobTitle", re.I))
            c = (card.select_one('[data-testid="company-name"]')
                 or card.find(class_=re.compile(r"companyName", re.I)))
            lk = card.find("a", href=True)
            title   = t.get_text(strip=True) if t else ""
            company = c.get_text(strip=True) if c else ""
            link    = lk["href"] if lk else ""
            if link and not link.startswith("http"):
                link = "https://ar.indeed.com" + link
            if title:
                jobs.append(mk_job(company, title, link, "Indeed"))
        start += 10
        if start >= 20:  # máximo 3 páginas
            break
    return jobs[:n]


def search_zonajobs(kw, loc, n, days=None):
    """ZonaJobs usa la misma API que Bumeran — intercepción de red (paginado)."""
    jobs = []
    kw_slug = kw.lower().replace(" ", "-")
    is_hoy  = (days == 1) if days is not None else getattr(config, "JOB_SOLO_HOY", False)
    prefix  = "empleos-publicacion-hoy-busqueda" if is_hoy else "empleos-busqueda"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = browser.new_context(user_agent=HEADERS["User-Agent"], locale="es-AR",
                                   viewport={"width": 1280, "height": 800})
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        p = ctx.new_page()
        try:
            for page_num in range(1, 4):   # hasta 3 páginas
                if page_num == 1:
                    url = f"https://www.zonajobs.com.ar/{prefix}-{kw_slug}.html"
                else:
                    url = f"https://www.zonajobs.com.ar/{prefix}-{kw_slug}-pagina-{page_num}.html"
                try:
                    with p.expect_response("**/searchV2**", timeout=20000) as resp_info:
                        p.goto(url, timeout=25000, wait_until="domcontentloaded")
                    data  = resp_info.value.json()
                    items = data.get("content") or []
                    if not items:
                        break
                    for aviso in items:
                        title   = aviso.get("titulo", "")
                        empresa = aviso.get("empresa") or {}
                        company = empresa.get("nombre", "") if isinstance(empresa, dict) else str(empresa)
                        link    = f"https://www.zonajobs.com.ar{aviso.get('postulacionUrl', aviso.get('url', ''))}"
                        if title:
                            jobs.append(mk_job(company, title, link, "ZonaJobs"))
                    if len(jobs) >= n:
                        break
                except Exception as e:
                    print(f"[Agente 1]   ZonaJobs p{page_num} error: {e}")
                    break
        finally:
            browser.close()
    return jobs[:n]


def search_jooble(page, kw, loc, n):
    jobs = []
    kw_slug  = kw.lower().replace(" ", "-")
    loc_slug = loc.split(",")[0].strip().lower().replace(" ", "-")
    soup = get_soup_pw(page, f"https://ar.jooble.org/trabajo-{kw_slug}/{loc_slug}",
                       wait_selector="article", wait_ms=3000)
    if not soup:
        return jobs
    for card in (soup.select("article") or soup.select("[class*='vacancy']"))[:n]:
        t = card.find("h2") or card.find("h3")
        c = card.find(class_=re.compile(r"company|employer", re.I))
        l = card.find("a", href=True)
        title   = t.get_text(strip=True) if t else ""
        company = c.get_text(strip=True) if c else ""
        link    = l["href"] if l else ""
        if link and not link.startswith("http"):
            link = "https://ar.jooble.org" + link
        if title:
            jobs.append(mk_job(company, title, link, "Jooble"))
    return jobs


def search_getonboard(page, kw, n):
    """GetOnBoard: 18 cards encontradas, solo necesita selectores correctos."""
    jobs = []
    q = kw.replace(" ", "+")
    soup = get_soup_pw(page, f"https://www.getonbrd.com/jobs?query={q}",
                       wait_selector="[class*='job']", wait_ms=3000)
    if not soup:
        return jobs
    # Selector real del diagnóstico: 18 cards con clase que contiene 'job'
    cards = soup.select("[class*='JobLi']") or soup.select("[class*='job-li']") or \
            soup.select("ul[class*='jobs'] li") or soup.select("[class*='job']")
    for card in cards[:n]:
        # Título: primer enlace o h2/h3
        t = card.find("h2") or card.find("h3") or card.find("a", href=True)
        # Empresa: span o div con nombre de empresa
        c = card.find("span", class_=re.compile(r"company|employer|org", re.I)) or \
            card.find("div", class_=re.compile(r"company|employer", re.I))
        l = card.find("a", href=True)
        title   = t.get_text(strip=True)   if t else ""
        company = c.get_text(strip=True)   if c else ""
        link    = l["href"]                if l else ""
        if link and not link.startswith("http"):
            link = "https://www.getonbrd.com" + link
        if title and len(title) > 3:
            jobs.append(mk_job(company, title, link, "GetOnBoard"))
    return jobs


def search_adzuna(page, kw, loc, n):
    jobs = []
    q    = kw.replace(" ", "+")
    city = loc.split(",")[0].strip().lower().replace(" ", "-")
    soup = get_soup_pw(page, f"https://www.adzuna.com.ar/search?q={q}&loc={city}",
                       wait_selector="article", wait_ms=3000)
    if not soup:
        return jobs
    for card in (soup.select("article") or soup.select("[class*='result']"))[:n]:
        t = card.find("h2") or card.find("h3")
        c = card.find(class_=re.compile(r"company|employer", re.I))
        l = card.find("a", href=True)
        title   = t.get_text(strip=True) if t else ""
        company = c.get_text(strip=True) if c else ""
        link    = l["href"] if l else ""
        if link and not link.startswith("http"):
            link = "https://www.adzuna.com.ar" + link
        if title:
            jobs.append(mk_job(company, title, link, "Adzuna"))
    return jobs


def search_google_maps(page, kw, loc, n):
    jobs = []
    import urllib.parse
    import time
    q = urllib.parse.quote_plus(f"{kw} en {loc}")
    url = f"https://www.google.com/maps/search/{q}/"
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(5)
        
        for _ in range(4):
            page.mouse.wheel(0, 1200)
            time.sleep(1.5)
            
        links = page.locator("a[href*='/maps/place/']").all()
        for link in links[:n]:
            company = link.get_attribute('aria-label')
            href = link.get_attribute('href')
            if company:
                title = f"Candidatura Espontánea - {kw}"
                jobs.append(mk_job(company, title, href, "Google Maps", desc="Extraído de Google Maps para contacto espontáneo."))
    except Exception as e:
        print(f"[Agente 1]   Error en Google Maps: {e}")
        
    return jobs


# ── Orquestador ───────────────────────────────────────────────────────────────

def search_jobs(keywords: str | None = None, location: str | None = None, max_results: int | None = None, days: int | None = None) -> list[dict]:
    kw  = keywords    or config.JOB_KEYWORDS
    loc = location    or config.JOB_LOCATION
    n_total = max_results or config.JOB_MAX_RESULTS

    # Detectar múltiples ubicaciones separadas por "y", "Y" o coma ","
    raw_locs = [l.strip() for l in re.split(r'(?i)\s+y\s+|\s*,\s*', loc) if l.strip()]
    
    # Manejar caso especial para evitar separar "capital" y "federal" si usaron una coma
    locations = []
    i = 0
    while i < len(raw_locs):
        curr = raw_locs[i]
        if i + 1 < len(raw_locs) and (
            (curr.lower() == "capital" and raw_locs[i+1].lower() == "federal") or
            (curr.lower() == "federal" and raw_locs[i+1].lower() == "capital")
        ):
            locations.append("Capital Federal")
            i += 2
        else:
            locations.append(curr)
            i += 1

    print(f"[Agente 1] Buscando: {kw} en {locations} (últimos {days or 'todos'} días)")

    # 10 portales activos: Computrabajo, LinkedIn, Bumeran, ZonaJobs,
    # Indeed, Google Jobs, Jooble, GetOnBoard, Adzuna, Talent.com
    n   = max(n_total // 10 + 2, 5)
    jobs = []

    for current_loc in locations:
        print(f"[Agente 1] >>> Iniciando sub-búsqueda para la ubicación: '{current_loc}'")

        # ── Con Playwright propio (API interception) ──
        api_fuentes = [
            ("Computrabajo", lambda: search_computrabajo(kw, current_loc, n)),
            ("LinkedIn",     lambda: search_linkedin(kw, current_loc, n)),
            ("Bumeran",      lambda: search_bumeran(kw, current_loc, n, days)),
            ("ZonaJobs",     lambda: search_zonajobs(kw, current_loc, n, days)),
        ]
        for nombre, fn in api_fuentes:
            print(f"[Agente 1] [{current_loc}] Buscando en {nombre}...")
            try:
                r = fn()
                # Agregar ubicación a cada resultado
                for job in r:
                    job["location"] = current_loc
                jobs.extend(r)
                print(f"[Agente 1] [{current_loc}]   -> {len(r)} ofertas obtenidas")
            except Exception as e:
                print(f"[Agente 1] [{current_loc}]   -> Error: {e}")

        # ── Playwright compartido (HTML scraping) ──
        pw_fuentes = [
            ("Indeed",      lambda p: search_indeed(p, kw, current_loc, n, days)),
            ("Google Jobs", lambda p: search_google_jobs(p, kw, current_loc, n)),
            ("Jooble",      lambda p: search_jooble(p, kw, current_loc, n)),
            ("GetOnBoard",  lambda p: search_getonboard(p, kw, n)),
            ("Adzuna",      lambda p: search_adzuna(p, kw, current_loc, n)),
            ("Talent.com",  lambda p: search_talent(kw, current_loc, n)),
            ("Google Maps", lambda p: search_google_maps(p, kw, current_loc, n)),
        ]

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
            ctx     = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                locale="es-AR",
                viewport={"width": 1280, "height": 800},
            )
            ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page = ctx.new_page()

            for nombre, fn in pw_fuentes:
                print(f"[Agente 1] [{current_loc}] Buscando en {nombre}...")
                try:
                    r = fn(page)
                    # Agregar ubicación a cada resultado
                    for job in r:
                        job["location"] = current_loc
                    jobs.extend(r)
                    print(f"[Agente 1] [{current_loc}]   -> {len(r)} ofertas obtenidas")
                except Exception as e:
                    print(f"[Agente 1] [{current_loc}]   -> Error: {e}")

            browser.close()

    # Deduplicar resultados consolidados de todas las ubicaciones
    seen, unique = set(), []
    for j in jobs:
        key = (j["job_title"].lower()[:60], j["company"].lower()[:40])
        if key not in seen:
            seen.add(key)
            unique.append(j)

    # Filtrar por palabras clave, excluidas, blacklist y modalidad
    before = len(unique)
    unique = [
        j for j in unique
        if _pasa_filtros(j.get("job_title", ""), j.get("company", ""), kw)
        and _pasa_modalidad(j.get("job_title", ""), j.get("description", ""))
    ]
    if len(unique) < before:
        print(f"[Agente 1] Filtros: {before - len(unique)} ofertas excluidas, quedan {len(unique)}")

    # Filtro "solo hoy" (o N días) donde el portal expone la fecha
    is_hoy = (days == 1) if days is not None else getattr(config, "JOB_SOLO_HOY", False)
    if is_hoy or (days is not None and days < 30):
        antes = len(unique)
        dias_filtro = days if days is not None else (1 if is_hoy else 30)
        unique = [j for j in unique if es_reciente(j.get("fecha", ""), dias_filtro)]
        print(f"[Agente 1] Filtro {dias_filtro} días: {len(unique)}/{antes} avisos")

    # Deduplicación histórica: omitir ofertas ya vistas en búsquedas anteriores
    seen = _load_seen()
    antes_hist = len(unique)
    unique = [j for j in unique if not j.get("apply_url") or j["apply_url"] not in seen]
    repetidos = antes_hist - len(unique)
    if repetidos:
        print(f"[Agente 1] {repetidos} ofertas ya vistas en búsquedas anteriores, omitidas.")

    result = unique[:n_total]

    # Puntaje de relevancia con Gemini (solo si hay API key)
    if getattr(config, "GEMINI_API_KEY", ""):
        print(f"[Agente 1] Calculando puntaje de relevancia con Gemini para {len(result)} ofertas...")
        for j in result:
            if j.get("score") is None:
                score, reason = _score_gemini(
                    j.get("job_title", ""), j.get("company", ""), j.get("description", "")
                )
                j["score"] = score
                j["match_reason"] = reason
        # Ordenar por puntaje descendente
        result.sort(key=lambda x: x.get("score", 0), reverse=True)
        print(f"[Agente 1] Puntajes asignados. Top: {result[0].get('job_title')} ({result[0].get('score')}/10)" if result else "")

    # Guardar URLs nuevas para futuras búsquedas
    seen.update(j["apply_url"] for j in result if j.get("apply_url"))
    _save_seen(seen)

    print(f"[Agente 1] Total consolidado: {len(result)} ofertas únicas.")
    return result
