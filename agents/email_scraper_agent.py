"""
Agente 2 — Extracción de correos de contacto.
Estrategia para cada empresa:
  1. Si ya tiene 'website', úsalo directamente.
  2. Si no, deduce candidatos de URL por nombre y verifica cuál responde.
  3. Visita /contacto, /contact, /sobre-nosotros y raíz buscando emails.
Sin APIs externas.
"""

import re
import json
import time
import requests
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
import unicodedata

CACHE_FILE = Path(__file__).resolve().parent.parent / "website_cache.json"


def _load_cache() -> dict:
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-AR,es;q=0.9",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

DOMINIOS_IGNORADOS = {
    "example.com", "domain.com", "email.com", "correo.com",
    "tudominio.com", "sentry.io", "wixpress.com", "google.com",
    "linkedin.com", "computrabajo.com.ar", "bumeran.com.ar",
    "zonajobs.com.ar", "indeed.com", "talent.com",
    # Proveedores de temas/plataformas (aparecen en el código, no son de la empresa)
    "envato.com", "themeforest.net", "wordpress.com", "wordpress.org",
    "wp.com", "squarespace.com", "shopify.com", "godaddy.com",
    "cloudflare.com", "gstatic.com", "jsdelivr.net", "googleapis.com",
    "w3.org", "schema.org", "mozilla.org",
}

# Buzones automáticos que NO son correos de contacto
NOREPLY_RE = re.compile(
    r"^(no[-_]?reply|do[-_]?not[-_]?reply|noresponder|noreply|"
    r"postmaster|mailer-daemon|abuse|root|webmaster|nobody)$", re.I
)

PALABRAS_BASURA = {
    "argentina", "s.a", "sa", "s.r.l", "srl", "ltda", "inc",
    "group", "grupo", "solutions", "soluciones", "services",
    "servicios", "consulting", "consultora", "recursos", "humanos",
    "technologies", "tecnologias", "digital", "global", "en",
    "de", "del", "la", "el", "los", "las", "y",
}


def normalizar(texto: str) -> str:
    """Quita acentos, signos y pasa a minúsculas."""
    nfkd = unicodedata.normalize("NFKD", texto)
    ascii_ = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9\s]", " ", ascii_.lower())


def generar_candidatos(company: str) -> list[str]:
    """Genera URLs candidatas a partir del nombre de empresa."""
    norm = normalizar(company)
    palabras = [p for p in norm.split() if p not in PALABRAS_BASURA and len(p) > 1]

    if not palabras:
        return []

    slug_completo = "".join(palabras)
    slug_primero  = palabras[0]
    slug_dos      = "".join(palabras[:2]) if len(palabras) >= 2 else slug_primero
    slug_guion    = "-".join(palabras[:3])

    # Probar primero los slugs MÁS específicos (nombre completo) y dejar el
    # de una sola palabra para el final: "estudioorbe" antes que "estudio",
    # así no caemos en un dominio genérico de otra empresa.
    orden = [slug_completo, slug_guion, slug_dos, slug_primero]
    slugs = list(dict.fromkeys(orden))   # dedup conservando el orden

    candidatos = []
    for slug in slugs:
        for tld in [".com.ar", ".com", ".ar"]:
            candidatos.append(f"https://www.{slug}{tld}")
            candidatos.append(f"https://{slug}{tld}")
    return candidatos


def verificar_url(url: str) -> bool:
    """Comprueba que la URL responde con 200."""
    try:
        r = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        return r.status_code < 400
    except Exception:
        return False


def buscar_website_por_nombre(company: str) -> str:
    """Deduce y verifica la URL del sitio web de una empresa (por slug del nombre)."""
    candidatos = generar_candidatos(company)
    for url in candidatos:
        if verificar_url(url):
            return url
    return ""


# Dominios que NO son el sitio de la empresa (portales, redes, agregadores)
BUSCADOR_EXCLUIR = {
    # Portales y agregadores de empleo
    "computrabajo", "linkedin", "bumeran", "zonajobs", "indeed", "talent",
    "glassdoor", "jooble", "adzuna", "getonbrd", "elempleo", "trabajando",
    "jobsora", "opcionempleo", "neuvoo", "jobtome", "careerjet", "jobatus",
    "kit-empleo", "kitempleo", "buscojobs", "empleosit", "trabajos.com",
    "lever.co", "greenhouse", "workable", "bebee", "jobrapido", "trovit",
    # Directorios / datos de empresas
    "crunchbase", "clearbit", "cuitonline", "guiaempresas", "einforma",
    # Redes sociales y buscadores
    "facebook", "instagram", "twitter", "x.com", "youtube", "tiktok",
    "wikipedia", "google", "bing", "duckduckgo", "yahoo", "mercadolibre",
}


def _host_excluido(host: str) -> bool:
    return any(b in host for b in BUSCADOR_EXCLUIR)


def _primer_dominio(links: list[str]) -> str:
    """De una lista de URLs, devuelve el primer dominio que sea de empresa
    (no portal de empleo ni red social)."""
    for href in links:
        if not href.startswith("http"):
            continue
        host = urllib.parse.urlparse(href).netloc.split(":")[0].lower()
        if host and not _host_excluido(host):
            return f"https://{host}"
    return ""


def _buscar_startpage(q: str) -> str:
    """Startpage = resultados de Google sin captcha. Motor principal."""
    r = requests.get("https://www.startpage.com/sp/search",
                     params={"query": q}, headers=HEADERS, timeout=12)
    if r.status_code != 200:
        return ""
    soup = BeautifulSoup(r.text, "html.parser")
    links = [a.get("href", "") for a in soup.select("a.result-link")]
    return _primer_dominio(links)


def _buscar_duckduckgo(q: str) -> str:
    """DuckDuckGo como respaldo. Reintenta ante el 202 (rate-limit)."""
    for intento in range(3):
        r = requests.get("https://html.duckduckgo.com/html/",
                         params={"q": q}, headers=HEADERS, timeout=12)
        if r.status_code == 200 and "result__a" in r.text:
            soup = BeautifulSoup(r.text, "html.parser")
            links = []
            for a in soup.select("a.result__a"):
                href = a.get("href", "")
                p = urllib.parse.urlparse(href)
                if "duckduckgo.com" in p.netloc and "uddg" in (p.query or ""):
                    href = urllib.parse.parse_qs(p.query).get("uddg", [""])[0]
                links.append(href)
            return _primer_dominio(links)
        time.sleep(2 + intento * 1.5)   # backoff ante 202
    return ""


def buscar_website_por_busqueda(company: str, extra: str = "") -> str:
    """
    Opción B — Busca la empresa en un buscador, detecta el link de su sitio
    y lo devuelve (descartando portales de empleo y redes sociales).
    Motores en orden: Startpage (Google sin captcha) → DuckDuckGo.
    """
    # Solo el nombre (+ país): agregar "sitio oficial" empeora los resultados
    # (trae páginas de portales en vez del sitio propio).
    q = " ".join(p for p in [company, extra] if p).strip()
    for nombre, motor in [("Startpage", _buscar_startpage),
                          ("DuckDuckGo", _buscar_duckduckgo)]:
        try:
            web = motor(q)
            if web:
                print(f"[Agente 2]   Sitio hallado vía {nombre}: {web}")
                return web
        except Exception as e:
            print(f"[Agente 2]   {nombre} falló: {e}")
    print(f"[Agente 2]   Búsqueda web sin resultado.")
    return ""


# Extensiones de archivos/assets que NO son emails reales (logo@2x.webp, etc.)
EXT_ASSETS = {
    "png", "jpg", "jpeg", "gif", "svg", "webp", "ico", "bmp", "avif",
    "js", "css", "mjs", "json", "map",
    "woff", "woff2", "ttf", "otf", "eot",
    "mp4", "webm", "mp3", "pdf",
}

# Descriptor de densidad de imágenes responsive: "...@2x.webp", "...@3x.png"
DENSIDAD_RE = re.compile(r"^\d+x\.", re.I)


def emails_validos_de_html(html: str) -> list[str]:
    """Devuelve todos los emails reales del HTML, ya filtrados (sin assets/noreply/etc.)."""
    out, vistos = [], set()
    for email in EMAIL_RE.findall(html):
        email = email.lower()
        if email in vistos:
            continue
        local, dominio = email.split("@", 1)
        ext = dominio.rsplit(".", 1)[-1]
        if DENSIDAD_RE.match(dominio):          # logo@2x.webp
            continue
        if ext in EXT_ASSETS or dominio in DOMINIOS_IGNORADOS:
            continue
        if len(local) < 2:                       # local part muy corto = ruido
            continue
        if NOREPLY_RE.match(local):              # noreply@, postmaster@, etc.
            continue
        vistos.add(email)
        out.append(email)
    return out


def extraer_email_de_html(html: str, dominio_preferido: str = "") -> str:
    """
    Primer email válido del HTML. Si se pasa `dominio_preferido`, prioriza
    los correos de ESE dominio (el del propio sitio) sobre los de terceros.
    """
    emails = emails_validos_de_html(html)
    if not emails:
        return ""
    if dominio_preferido:
        for e in emails:
            if e.split("@", 1)[1].endswith(dominio_preferido):
                return e
    return emails[0]


def _get(url: str, timeout: int = 10):
    """GET robusto: si el sitio tiene el certificado SSL roto/vencido,
    reintenta sin verificarlo (muchas empresas chicas lo tienen mal)."""
    try:
        return requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.exceptions.SSLError:
        import urllib3
        urllib3.disable_warnings()
        return requests.get(url, headers=HEADERS, timeout=timeout, verify=False)


def extraer_email_de_pagina(url: str, dominio_preferido: str = "") -> str:
    """Descarga UNA página (p. ej. el aviso) y devuelve el primer email válido."""
    try:
        resp = _get(url, timeout=10)
        resp.encoding = resp.apparent_encoding
        return extraer_email_de_html(resp.text, dominio_preferido)
    except Exception as e:
        print(f"[Agente 2]   Error: {e}")
        return ""


# Palabras que delatan una página de contacto / carreras / "sumate"
LINK_KEYWORDS = (
    "contacto", "contact", "contactanos", "contacto",
    "sumate", "sumate-a", "unite", "unete", "join",
    "careers", "carrera", "carreras", "jobs", "job",
    "empleo", "empleos", "trabaja", "trabajar", "trabaja-con-nosotros",
    "nosotros", "about", "quienes-somos", "quienes",
)


def extraer_email_de_sitio(website: str) -> str:
    """
    Busca el email de contacto en el sitio de la empresa:
      1. Rutas directas comunes (/contacto, /careers, etc.).
      2. Si no hay, recorre el HOME y sigue los links que parezcan de
         contacto/carreras (ej: 'Sumate a YEL' → /sumate-a-yel/).
    """
    base = website.rstrip("/")
    base_host = urllib.parse.urlparse(base).netloc.split(":")[0]
    # Dominio del propio sitio (sin www) para priorizar sus correos
    dom_pref = base_host[4:] if base_host.startswith("www.") else base_host
    visitadas: set[str] = set()

    def probar(url: str) -> str:
        if url in visitadas:
            return ""
        visitadas.add(url)
        print(f"[Agente 2]   Visitando {url} ...")
        return extraer_email_de_pagina(url, dom_pref)

    # 1) Rutas directas comunes
    rutas = ["", "/contacto", "/contact", "/contactanos",
             "/sobre-nosotros", "/about", "/careers", "/jobs",
             "/empleos", "/trabaja-con-nosotros"]
    for ruta in rutas:
        email = probar(base + ruta)
        if email:
            return email

    # 2) Crawl del home: seguir links de contacto/carreras del mismo dominio
    try:
        r = _get(base, timeout=8)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        candidatos: list[str] = []
        for a in soup.find_all("a", href=True):
            blob = (a["href"] + " " + a.get_text(" ", strip=True)).lower()
            if any(k in blob for k in LINK_KEYWORDS):
                full = urllib.parse.urljoin(base + "/", a["href"]).split("#")[0]
                host = urllib.parse.urlparse(full).netloc.split(":")[0]
                if full.startswith("http") and host.endswith(base_host):
                    candidatos.append(full)
        for url in dict.fromkeys(candidatos):       # dedup, preserva orden
            if len(visitadas) > 16:
                break
            print(f"[Agente 2]   Siguiendo link de contacto/carreras...")
            email = probar(url)
            if email:
                return email
    except Exception as e:
        print(f"[Agente 2]   Error recorriendo el home: {e}")

    return ""


def extract_emails(jobs: list[dict]) -> list[dict]:
    results = []
    cache = _load_cache()

    for job in jobs:
        company   = job.get("company", "desconocida")
        website   = job.get("website", "").strip()
        apply_url = job.get("apply_url", "").strip()
        cache_key = normalizar(company)[:50]

        print(f"\n[Agente 2] Procesando: {company}")

        # Cache hit: ya conocemos el email de esta empresa
        if cache_key in cache and cache[cache_key].get("email"):
            cached = cache[cache_key]
            job["email"]   = cached["email"]
            job["website"] = cached.get("website", website)
            print(f"[Agente 2]   Cache hit: {cached['email']}")
            results.append(job)
            continue

        # Recuperar website cacheado si no lo tiene el job
        if not website and cache_key in cache and cache[cache_key].get("website"):
            website = cache[cache_key]["website"]
            job["website"] = website

        email = ""

        # 1) Entrar al aviso mismo y buscar el email en la descripción.
        #    Funciona en boards que publican el correo (GetOnBoard, sitios propios).
        #    Los grandes portales (Computrabajo, LinkedIn, Bumeran) lo ocultan → 0 acá.
        if apply_url:
            print(f"[Agente 2]   Leyendo el aviso: {apply_url[:70]}...")
            email = extraer_email_de_pagina(apply_url)
            if email:
                print(f"[Agente 2]   Email en el aviso: {email}")

        # 2) Si el aviso no tenía email, ir al sitio web de la empresa.
        if not email:
            if not website:
                # Opción B: buscar el sitio oficial en la web (DuckDuckGo)
                print(f"[Agente 2]   Sin email en el aviso. Buscando sitio oficial en la web...")
                website = buscar_website_por_busqueda(company, extra="Argentina")
                # Fallback: deducir el dominio por el slug del nombre
                if not website:
                    print(f"[Agente 2]   Sin resultado web. Deduciendo por nombre...")
                    website = buscar_website_por_nombre(company)
                if website:
                    print(f"[Agente 2]   Website encontrado: {website}")
                    job["website"] = website
            if website:
                email = extraer_email_de_sitio(website)
                if email:
                    print(f"[Agente 2]   Email en el sitio: {email}")
                else:
                    print(f"[Agente 2]   Sin email en {website}")
            else:
                print(f"[Agente 2]   No se pudo determinar el website.")

        job["email"] = email
        # Actualizar caché con lo que encontramos (aunque sea vacío, para no reintentar sitios que no tienen)
        cache[cache_key] = {"website": job.get("website", ""), "email": email}
        results.append(job)

    _save_cache(cache)
    con_email = sum(1 for j in results if j.get("email"))
    print(f"\n[Agente 2] Correos encontrados: {con_email}/{len(results)}")

    # Deduplicar por email + job_title para evitar envíos repetidos
    seen = set()
    deduped = []
    duplicados = 0
    for j in results:
        clave = (j.get("email", "").strip().lower(), j.get("job_title", "").strip().lower())
        if clave not in seen:
            seen.add(clave)
            deduped.append(j)
        else:
            duplicados += 1
            email = j.get("email", "?")
            empresa = j.get("company", "?")
            print(f"[Agente 2]   ↷ Duplicado omitido: {email} ({empresa})")

    if duplicados > 0:
        print(f"\n[Agente 2] ✓ Deduplicación: eliminados {duplicados} duplicado(s) ({len(results)} → {len(deduped)} únicos)")

    return deduped
