"""Baut die Unterseiten von vespasian-advisory.de. Aufruf: python3 _bau/seiten.py (im Repo)."""
import json, os, re, html

BASE = "https://vespasian-advisory.de"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZAEHLER = open(os.path.join(ROOT, "_bau", "zaehler.html")).read()

LEISTUNGEN = [
    ("unternehmensbewertung", "Unternehmensbewertung"),
    ("kaufpreis-check", "Kaufpreis-Check"),
    ("nachfolge-und-verkauf", "Nachfolge und Verkauf"),
    ("finanzierung-und-bankgespraech", "Finanzierung und Bankgespräch"),
    ("erbschaft-und-erbengemeinschaft", "Erbschaft und Erbengemeinschaft"),
    ("scheidung-und-pflichtteil", "Scheidung, Pflichtteil, Abfindung"),
]

INVEST = "Vespasian Invest beteiligt sich selbst an kleinen Unternehmen. Wo das bei einem Auftrag eine Rolle spielen könnte, sagen wir es Ihnen vorab und lehnen den Auftrag im Zweifel ab."


def esc(t):
    return html.escape(t, quote=True)


def plain(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t))


def liste(items):
    return '<ul class="list">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def schritte(items):
    out = '<ol class="steps">'
    for titel, text, dauer in items:
        d = f'<span class="dauer">{dauer}</span>' if dauer else ""
        out += f"<li><div><h3>{titel}</h3><p>{text}</p>{d}</div></li>"
    return out + "</ol>"


def block(titel, inhalt, grey=False, bid=""):
    i = f' id="{bid}"' if bid else ""
    g = " grey" if grey else ""
    return f'<section class="block{g}"{i}><div class="wrap split"><h2>{titel}</h2><div class="body">{inhalt}</div></div></section>'


def honorar(posten, note):
    cells = "".join(f"<div><small>{k}</small><strong>{v}</strong><p>{t}</p></div>" for k, v, t in posten)
    return f'<div class="fee">{cells}</div><p class="note">{note}</p>'


def fragen(faq):
    return '<div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faq) + "</div>"


def seite(pfad, titel, beschreibung, crumb, kicker, h1, lead, facts, inhalt, faq, service=None, preis=None):
    url = f"{BASE}/{pfad}"
    crumbs = [("Start", f"{BASE}/")]
    if pfad.startswith("leistungen/"):
        crumbs.append(("Leistungen", f"{BASE}/#leistungen"))
    crumbs.append((crumb, url))
    graph = [
        {"@type": "WebPage", "@id": url, "url": url, "name": titel, "description": beschreibung, "inLanguage": "de-DE",
         "isPartOf": {"@type": "WebSite", "url": f"{BASE}/", "name": "Vespasian Advisory"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]},
    ]
    if service:
        s = {"@type": "Service", "name": service, "description": beschreibung, "areaServed": {"@type": "Country", "name": "Deutschland"},
             "provider": {"@type": "ProfessionalService", "name": "Vespasian Advisory", "url": f"{BASE}/"}}
        if preis:
            s["offers"] = {"@type": "Offer", "priceCurrency": "EUR", "priceSpecification": {"@type": "PriceSpecification", "minPrice": preis, "priceCurrency": "EUR"}}
        graph.append(s)
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in faq]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)
    crumb_html = '<p class="crumbs">' + '<span aria-hidden="true">/</span>'.join(
        f'<a href="{u.replace(BASE, "")}">{n}</a>' if u != url else f"<span aria-current=\"page\" style=\"margin:0;color:#cfcfcf\">{n}</span>" for n, u in crumbs) + "</p>"
    facts_html = '<ul class="facts">' + "".join(f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in facts) + "</ul>" if facts else ""
    andere = "".join(f'<a href="/leistungen/{s}/">{n}<span aria-hidden="true">→</span></a>' for s, n in LEISTUNGEN if f"leistungen/{s}/" != pfad)
    andere += '<a href="/honorar/">Honorar<span aria-hidden="true">→</span></a>' if pfad != "honorar/" else ""
    andere += '<a href="/beispiel/">Beispielbericht<span aria-hidden="true">→</span></a>' if pfad != "beispiel/" else ""
    faq_block = block("Häufige Fragen.", fragen(faq), bid="fragen") if faq else ""
    doc = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(titel)}</title>
<meta name="description" content="{esc(beschreibung)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="Vespasian Advisory">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(titel)}">
<meta property="og:description" content="{esc(beschreibung)}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Vespasian Advisory. Den Wert kennen. Sicher entscheiden.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE}/og.png">
<meta name="theme-color" content="#000000">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-48.png" type="image/png" sizes="48x48">
<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">
<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/newsreader-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/hanken-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/seite.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="head"><div class="wrap">
  <a class="wordmark" href="/">Vespasian <span>Advisory</span></a>
  <nav aria-label="Hauptnavigation"><a class="navlink" href="/#leistungen">Leistungen</a><a class="navlink" href="/honorar/">Honorar</a><a class="navlink" href="/beispiel/">Beispiel</a><a class="cta" href="/#kontakt">Erstgespräch</a></nav>
</div></header>
<main id="inhalt">
<div class="intro"><div class="wrap">
{crumb_html}
<p class="kicker">{kicker}</p>
<h1>{h1}</h1>
<p class="lead">{lead}</p>
{facts_html}
</div></div>
{inhalt}
{faq_block}
<section class="block"><div class="wrap split"><h2>Weitere Themen.</h2><div class="more">{andere}</div></div></section>
<section class="close"><div class="wrap">
<h2>Sprechen wir über Ihren Anlass.</h2>
<p>Das Erstgespräch ist kostenlos und unverbindlich. Danach wissen Sie, was eine Bewertung oder Planung in Ihrem Fall leisten kann und was sie kostet.</p>
<div class="btns"><a class="btn fill" href="/#kontakt">Erstgespräch vereinbaren <span aria-hidden="true">→</span></a><a class="btn ghost" href="tel:+4915202665878">+49 152 0266 5878</a></div>
</div></section>
</main>
<footer><div class="wrap">
<div class="links"><a href="/">Start</a><a href="/#leistungen">Leistungen</a><a href="/honorar/">Honorar</a><a href="/beispiel/">Beispielbericht</a><a href="/#impressum">Impressum</a><a href="/#datenschutz">Datenschutz</a></div>
<div class="group-strip"><a class="gs-main" href="https://vespasian-group.de">Ein Bereich der Vespasian Group <span aria-hidden="true">→</span></a><span class="gs-links"><a href="https://vespasian-immobilien.de">Vespasian Immobilien</a><a href="https://vespasian-invest.de">Vespasian Invest</a><a href="https://noctatec.de">NoctaTec</a></span></div>
<p class="bottom">© 2026 Vespasian Advisory ist eine Marke der TF Vespasian Vermögensverwaltungs-GmbH.</p>
</div></footer>
{ZAEHLER}</body>
</html>
"""
    os.makedirs(os.path.join(ROOT, pfad), exist_ok=True)
    open(os.path.join(ROOT, pfad, "index.html"), "w").write(doc)
    return url


URLS = []

# 1 Unternehmensbewertung -----------------------------------------------------------
URLS.append(seite(
    "leistungen/unternehmensbewertung/",
    "Unternehmensbewertung für Verkauf, Nachfolge und Gesellschafter | Vespasian Advisory",
    "Unternehmensbewertung nach dem Rahmen des IDW S1. Werteinschätzung oder ausführlicher Bewertungsbericht mit offengelegten Annahmen. Bundesweit, persönlich oder digital.",
    "Unternehmensbewertung", "Unternehmensbewertung",
    "Was Ihr Unternehmen wert ist, belegt und nachvollziehbar.",
    "Ob Verkauf, Nachfolge, Gesellschafterwechsel oder eine Entscheidung in der Familie. Eine Bewertung ist nur so gut wie ihre Herleitung. Wir rechnen sauber, legen jede Annahme offen und erklären das Ergebnis so, dass Sie es vertreten können.",
    [("IDW S1", "als methodischer Rahmen"), ("1 bis 6 Wochen", "je nach Format"), ("ab 1.900 €", "Werteinschätzung")],
    block("Wann eine Bewertung gebraucht wird.", liste([
        "Verkauf oder Übergabe an Familie, Mitarbeiter oder einen externen Käufer",
        "Eintritt oder Austritt eines Gesellschafters und die Frage nach der Abfindung",
        "Kauf eines Unternehmens oder einer Beteiligung",
        "Erbauseinandersetzung, Zugewinnausgleich oder Pflichtteil",
        "Gespräche mit der Bank über eine Finanzierung",
        "Eine ehrliche Standortbestimmung für die eigene Planung",
    ]))
    + block("Zwei Formate, je nach Zweck.", schritte([
        ("Werteinschätzung", "Eine begründete Bandbreite auf Basis der letzten drei Jahresabschlüsse und eines ausführlichen Gesprächs. Für die erste Orientierung und interne Entscheidungen, nicht als Gutachten gegenüber Dritten.", "Dauer etwa 1 bis 2 Wochen"),
        ("Bewertungsbericht", "Ertragswert- oder DCF-Verfahren mit bereinigten Ergebnissen, Planung, hergeleitetem Kapitalisierungszins und Sensitivitäten, plausibilisiert mit Marktmultiplikatoren. Für Verhandlungen, Mitgesellschafter, Banken und Berater.", "Dauer etwa 3 bis 6 Wochen ab vollständigen Unterlagen"),
    ]) + '<p class="note">Die Werteinschätzung wird voll angerechnet, wenn Sie danach einen Bewertungsbericht beauftragen. <a href="/beispiel/">So sieht ein Bericht aus</a>.</p>', grey=True)
    + block("So gehen wir vor.", schritte([
        ("Erstgespräch", "Wir klären Anlass, Zweck und das passende Format. Kostenlos, per Video, Telefon oder vor Ort.", "30 bis 45 Minuten"),
        ("Angebot", "Sie erhalten ein schriftliches Angebot mit Umfang, Zeitplan und Honorar.", "innerhalb von zwei Werktagen"),
        ("Unterlagen und Gespräch", "Sie schicken die Unterlagen digital. Wir sprechen mit Ihnen über Geschäftsmodell, Kunden, Personal und Pläne.", ""),
        ("Analyse", "Wir bereinigen die Ergebnisse, prüfen die Planung, leiten den Kapitalisierungszins her und rechnen Wert und Sensitivitäten.", ""),
        ("Ergebnis", "Sie erhalten den Bericht und wir besprechen ihn mit Ihnen, auf Wunsch gemeinsam mit Ihrem Steuerberater oder Anwalt.", ""),
    ]))
    + block("Was Sie bekommen.", liste([
        "Einen Bericht als PDF mit Wert oder Bandbreite",
        "Die Herleitung aller Annahmen, mit Quellen für Marktdaten",
        "Eine Sensitivitätsanalyse, die zeigt, wie stark der Wert auf Umsatz, Marge und Zins reagiert",
        "Eine Plausibilisierung mit branchenüblichen Multiplikatoren",
        "Auf Wunsch das Rechenmodell in Excel",
        "Eine Besprechung, in der Sie jede Zahl hinterfragen können",
    ]), grey=True)
    + block("Was wir von Ihnen brauchen.", liste([
        "Jahresabschlüsse der letzten drei bis fünf Jahre",
        "Aktuelle betriebswirtschaftliche Auswertung mit Summen- und Saldenliste",
        "Ihre Planung oder Ihre Erwartung für die nächsten Jahre",
        "Gesellschaftsvertrag und wesentliche Verträge mit Kunden, Lieferanten, Vermietern und Banken",
        "Vergütung der Geschäftsführung und eine Personalübersicht",
        "Anlagenverzeichnis und Angaben zu Immobilien im Betriebsvermögen",
    ]) + '<p class="note">Fehlt etwas, klären wir das im Gespräch. Wir arbeiten mit dem, was vorhanden ist, und kennzeichnen Lücken im Bericht.</p>')
    + block("Was wir bewusst nicht tun.", "<p>Wir sind keine Wirtschaftsprüfer und keine öffentlich bestellten Sachverständigen. Unsere Berichte folgen dem Rahmen des IDW S1, sind aber kein Gutachten eines Wirtschaftsprüfers. Bewertungen für das Finanzamt, etwa zur Erbschaft- oder Schenkungsteuer, erstellen wir nicht. Steuerliche Fragen klären Sie mit Ihrem Steuerberater.</p>", grey=True)
    + block("Honorar.", honorar([
        ("Werteinschätzung", "ab 1.900 €", "Bandbreite mit Kurzbericht, bei Folgeauftrag voll angerechnet"),
        ("Bewertungsbericht", "ab 4.900 €", "Ausführlicher Bericht mit Sensitivitäten und Plausibilisierung"),
    ], 'Das genaue Honorar steht vor Beginn im schriftlichen Angebot. Es hängt von Größe, Struktur und Zweck ab. <a href="/honorar/">Alle Honorare</a>')),
    [
        ("Welches Verfahren nutzen Sie?", "In der Regel das Ertragswertverfahren oder ein DCF-Verfahren im Rahmen des IDW S1. Multiplikatoren nutzen wir zur Plausibilisierung, nicht als Ersatz für die Rechnung. Hängt der Wert stark an der Person des Inhabers, sagen wir offen, wo die Methode an Grenzen stößt."),
        ("Wie genau ist das Ergebnis?", "Ein Unternehmenswert ist immer eine begründete Schätzung. Deshalb zeigen wir eine Bandbreite und wie stark der Wert auf einzelne Annahmen reagiert. Den Preis bestimmen am Ende Verhandlung und Markt."),
        ("Bleiben meine Unterlagen vertraulich?", "Ja. Auf Wunsch unterzeichnen wir vorab eine Vertraulichkeitsvereinbarung. Ihre Unterlagen nutzen wir nur für den Auftrag."),
        ("Arbeiten Sie auch digital?", "Ja, bundesweit. Unterlagen kommen digital, Gespräche führen wir per Video oder Telefon. Wo es hilft, kommen wir vor Ort."),
    ],
    service="Unternehmensbewertung", preis=1900,
))

# 2 Kaufpreis-Check ------------------------------------------------------------------
URLS.append(seite(
    "leistungen/kaufpreis-check/",
    "Kaufpreis-Check vor dem Unternehmenskauf | Vespasian Advisory",
    "Unabhängige Prüfung von Kaufpreis, Zahlen und Planannahmen vor dem Kauf eines Unternehmens oder einer Beteiligung. Mit Risiken, Fragenliste und Finanzierbarkeit.",
    "Kaufpreis-Check", "Kaufpreis-Check und wirtschaftliche Due Diligence",
    "Eine zweite Meinung, bevor Sie unterschreiben.",
    "Wer ein Unternehmen kauft, bekommt die Zahlen meist vom Verkäufer. Wir prüfen, ob der Preis zu dem passt, was das Unternehmen tatsächlich verdient, wo die Risiken liegen und ob sich der Kauf aus dem Unternehmen heraus finanzieren lässt.",
    [("1 bis 3 Wochen", "auch kurzfristig"), ("ab 2.400 €", "Honorar"), ("Käufersicht", "keine Provision vom Verkäufer")],
    block("Wann sich ein Check lohnt.", liste([
        "Sie wollen einen Betrieb, eine Praxis oder eine Beteiligung kaufen",
        "Mitarbeiter oder ein Nachfolger übernehmen das Unternehmen",
        "Es liegen Exposé und Kaufpreisvorstellung vor und Sie wollen wissen, was dahintersteht",
        "Ihre Bank verlangt eine Begründung des Kaufpreises",
    ]))
    + block("Was wir prüfen.", liste([
        "<b>Bereinigte Ergebnisse.</b> Einmaleffekte, Inhabergehalt, Mieten an Gesellschafter und alles, was nach dem Kauf anders sein wird",
        "<b>Planannahmen.</b> Ist das Wachstum im Exposé belegt oder erhofft",
        "<b>Abhängigkeiten.</b> Von einzelnen Kunden, Lieferanten oder vom bisherigen Inhaber",
        "<b>Investitionsstau und Umlaufvermögen.</b> Was nach dem Kauf zusätzlich Geld kostet",
        "<b>Finanzierbarkeit.</b> Ob Zins und Tilgung aus dem Cashflow bezahlt werden können",
        "<b>Marktvergleich.</b> Wie der Preis im Verhältnis zu üblichen Multiplikatoren liegt",
    ]), grey=True)
    + block("So gehen wir vor.", schritte([
        ("Erstgespräch", "Wir klären Vorhaben, Termin und die wichtigsten Fragen. Kostenlos.", "30 bis 45 Minuten"),
        ("Angebot", "Umfang, Zeitplan und Honorar schriftlich.", "innerhalb von zwei Werktagen"),
        ("Durchsicht", "Wir sichten die Unterlagen und schicken Ihnen eine Fragenliste für den Verkäufer.", ""),
        ("Analyse", "Bereinigung, Plausibilisierung der Planung, Risiken und Finanzierbarkeit.", ""),
        ("Ergebnis", "Bericht und Besprechung mit klarer Einschätzung zum Preis und Ihrem Verhandlungsspielraum.", ""),
    ]))
    + block("Was Sie bekommen.", liste([
        "Eine klare Einschätzung, ob der Preis plausibel, ambitioniert oder zu hoch ist, mit Bandbreite",
        "Die Risiken nach Bedeutung geordnet",
        "Eine Fragenliste für die Verhandlung",
        "Eine Rechnung zur Finanzierbarkeit des Kaufpreises",
        "Eine Besprechung, auf Wunsch mit Ihrer Bank oder Ihrem Anwalt",
    ]), grey=True)
    + block("Was wir von Ihnen brauchen.", liste([
        "Exposé und Kaufpreisvorstellung",
        "Jahresabschlüsse der letzten drei Jahre und die aktuelle betriebswirtschaftliche Auswertung",
        "Die Planung des Verkäufers, soweit vorhanden",
        "Eine Liste der wesentlichen Verträge",
        "Ihre Vorstellung zur Finanzierung",
    ]))
    + block("Was wir bewusst nicht tun.", f"<p>Eine rechtliche und steuerliche Due Diligence ersetzen wir nicht. Verträge prüft Ihr Anwalt, steuerliche Risiken Ihr Steuerberater. Wir liefern die wirtschaftliche Seite und stimmen uns gern mit beiden ab.</p><p>{INVEST}</p>", grey=True)
    + block("Honorar.", honorar([
        ("Kaufpreis-Check", "ab 2.400 €", "Prüfung, Bericht und Besprechung"),
        ("Mit Bewertungsbericht", "ab 4.900 €", "Wenn Sie zusätzlich einen eigenen Wert für die Verhandlung brauchen"),
    ], 'Das genaue Honorar steht vor Beginn im schriftlichen Angebot. <a href="/honorar/">Alle Honorare</a>')),
    [
        ("Arbeiten Sie auch für Verkäufer?", "Ja. Dann bereiten wir die Zahlen so auf, dass sie einer Prüfung durch den Käufer standhalten. In einem Verkauf arbeiten wir aber immer nur für eine Seite."),
        ("Geht es auch kurzfristig?", "Wenn ein Termin drängt, sagen Sie es im Erstgespräch. Liegen die Unterlagen vor, ist eine erste Einschätzung oft innerhalb weniger Tage möglich."),
        ("Was, wenn der Preis zu hoch ist?", "Dann sagen wir Ihnen das klar und zeigen, mit welchen Zahlen Sie nachverhandeln können. Manchmal ist die beste Empfehlung, nicht zu kaufen."),
    ],
    service="Kaufpreis-Check und wirtschaftliche Due Diligence", preis=2400,
))

# 3 Nachfolge und Verkauf -------------------------------------------------------------
URLS.append(seite(
    "leistungen/nachfolge-und-verkauf/",
    "Unternehmensnachfolge und Verkauf vorbereiten | Vespasian Advisory",
    "Vorbereitung von Nachfolge und Unternehmensverkauf mit Wertbasis, geordneten Unterlagen, Exposé und Finanzierbarkeit für den Käufer. Ohne Erfolgsprovision.",
    "Nachfolge und Verkauf", "Nachfolge und Verkauf",
    "Gut übergeben heißt früh vorbereiten.",
    "Eine Nachfolge braucht meist mehr Zeit, als man denkt. Wir schaffen eine belastbare Wertbasis, ordnen die Unterlagen und bereiten Ihr Unternehmen so vor, dass ein Käufer oder Nachfolger es versteht und finanzieren kann.",
    [("2 bis 3 Monate", "Vorbereitung"), ("ab 6.900 €", "mit Bewertungsbericht"), ("ohne Provision", "nur Honorar")],
    block("Wann Sie anfangen sollten.", liste([
        "Sie wollen in den nächsten ein bis fünf Jahren übergeben",
        "Kinder oder Mitarbeiter sollen übernehmen und alle wollen einen fairen Wert",
        "Ein Interessent hat sich gemeldet und Sie wollen vorbereitet sein",
        "Die Bank des Nachfolgers verlangt belastbare Zahlen",
    ]) + '<p class="note">Ideal sind zwei bis drei Jahre Vorlauf. Dann bleibt Zeit, Zahlen zu ordnen und die Abhängigkeit von Ihrer Person zu verringern.</p>')
    + block("So gehen wir vor.", schritte([
        ("Standort", "Ziele, Zeitplan und mögliche Wege, also Familie, Mitarbeiter oder ein externer Käufer.", "etwa 1 bis 2 Wochen"),
        ("Wertbasis", "Bewertungsbericht mit Bandbreite als Grundlage für alle Gespräche.", "etwa 3 bis 6 Wochen"),
        ("Unterlagen", "Bereinigte Zahlen, anonymes Kurzprofil, Exposé und eine geordnete Liste für den Datenraum.", "etwa 2 bis 4 Wochen"),
        ("Gespräche", "Vorbereitung der Gespräche mit Interessenten oder Nachfolger und eine Rechnung, wie der Kaufpreis finanziert werden kann.", "nach Bedarf"),
        ("Begleitung", "Zahlenfragen in der Verhandlung bis zum Notartermin.", "nach Vereinbarung"),
    ]), grey=True)
    + block("Was Sie bekommen.", liste([
        "Einen Bewertungsbericht als gemeinsame Grundlage",
        "Ein anonymes Kurzprofil und ein Exposé",
        "Eine geordnete Unterlagenliste für den Datenraum",
        "Eine Rechnung zur Finanzierbarkeit aus Sicht des Käufers",
        "Einen Zeitplan bis zur Übergabe",
    ]))
    + block("Was wir bewusst nicht tun.", f"<p>Wir sind keine Makler und nehmen keine Erfolgsprovision. Interessenten finden Sie über Ihr Netzwerk, Ihre Kammer oder Nachfolgebörsen wie nexxt-change. Wir sorgen dafür, dass Sie dann vorbereitet sind. Steuerliche Gestaltung und Verträge liegen bei Ihrem Steuerberater und Ihrem Anwalt oder Notar.</p><p>{INVEST}</p>", grey=True)
    + block("Honorar.", honorar([
        ("Vorbereitung", "ab 6.900 €", "Standort, Bewertungsbericht, Kurzprofil, Exposé und Unterlagenliste"),
        ("Begleitung", "nach Vereinbarung", "Gespräche und Verhandlung, vorab im Umfang festgelegt"),
    ], 'Das genaue Honorar steht vor Beginn im schriftlichen Angebot. <a href="/honorar/">Alle Honorare</a>')),
    [
        ("Wann sollte ich anfangen?", "Idealerweise zwei bis drei Jahre vor der Übergabe. Dann lassen sich Zahlen ordnen, Abhängigkeiten verringern und der Wert gezielt steigern."),
        ("Bekommen Sie eine Provision?", "Nein. Wir werden nur von Ihnen bezahlt, nach vereinbartem Honorar. Am Verkaufspreis verdienen wir nicht mit."),
        ("Was ist, wenn mein Kind übernimmt?", "Dann geht es um einen Wert, den beide Seiten als fair empfinden, und um eine Finanzierung, die das Unternehmen tragen kann. Die steuerliche Seite klären Sie mit Ihrem Steuerberater."),
    ],
    service="Vorbereitung von Unternehmensnachfolge und Verkauf", preis=6900,
))

# 4 Finanzierung und Bankgespräch -----------------------------------------------------
URLS.append(seite(
    "leistungen/finanzierung-und-bankgespraech/",
    "Businessplan und Unterlagen für das Bankgespräch | Vespasian Advisory",
    "Businessplan, Liquiditäts- und Kapitaldienstplanung für Kauf, Investition oder Umschuldung. Unterlagen, mit denen Sie gut vorbereitet ins Bankgespräch gehen.",
    "Finanzierung und Bankgespräch", "Finanzierung und Planung",
    "Gut vorbereitet ins Bankgespräch.",
    "Banken entscheiden nach Zahlen und nach dem Eindruck, den Ihre Planung hinterlässt. Wir erstellen Businessplan, Liquiditäts- und Kapitaldienstplanung so, dass die wichtigen Fragen beantwortet sind, bevor sie gestellt werden.",
    [("1 bis 3 Wochen", "je nach Vorhaben"), ("ab 1.900 €", "Honorar"), ("in Excel", "zum Weiterarbeiten")],
    block("Wofür Sie das brauchen.", liste([
        "Kauf eines Unternehmens oder einer Immobilie",
        "Investitionen und Wachstum",
        "Umschuldung oder Gespräche über bestehende Kredite",
        "Förderkredite, die über Ihre Hausbank beantragt werden",
        "Gründung oder Übernahme",
    ]))
    + block("So gehen wir vor.", schritte([
        ("Erstgespräch", "Vorhaben, Zeitplan und Bank. Kostenlos.", "30 bis 45 Minuten"),
        ("Angebot", "Umfang, Zeitplan und Honorar schriftlich.", "innerhalb von zwei Werktagen"),
        ("Aufnahme", "Wir übernehmen Ihre Zahlen und besprechen Annahmen zu Umsatz, Kosten und Investitionen.", ""),
        ("Planung", "Drei bis fünf Jahre mit Gewinn- und Verlustrechnung, Liquidität und Kapitaldienst, dazu ein vorsichtiges Szenario.", ""),
        ("Vorbereitung", "Kurzfassung für die Bank und eine Probe der typischen Fragen.", ""),
    ]), grey=True)
    + block("Was Sie bekommen.", liste([
        "Einen Businessplan als PDF",
        "Die Planung in Excel mit Gewinn- und Verlustrechnung, Liquidität und Kapitaldienst",
        "Die Kennzahlen, auf die Banken schauen, etwa Kapitaldienstdeckung und Eigenkapitalquote",
        "Eine Kurzfassung für das Gespräch",
        "Auf Wunsch unsere Begleitung zum Termin",
    ]))
    + block("Was wir von Ihnen brauchen.", liste([
        "Die letzten Jahresabschlüsse und die aktuelle betriebswirtschaftliche Auswertung",
        "Übersicht der bestehenden Darlehen",
        "Das Vorhaben mit Kosten, Angeboten und Zeitplan",
        "Angaben zu Eigenkapital und Sicherheiten",
    ]), grey=True)
    + block("Was wir bewusst nicht tun.", "<p>Wir vermitteln keine Kredite und erhalten keine Provision von Banken. Förderanträge stellt Ihre Hausbank. So bleibt unsere Einschätzung unabhängig.</p>")
    + block("Honorar.", honorar([
        ("Bankunterlagen", "ab 1.900 €", "Planung, Kennzahlen und Kurzfassung"),
        ("Businessplan", "ab 2.900 €", "Ausführlicher Plan für Gründung, Kauf oder größere Investitionen"),
    ], 'Das genaue Honorar steht vor Beginn im schriftlichen Angebot. <a href="/honorar/">Alle Honorare</a>'), grey=True),
    [
        ("Garantieren Sie die Finanzierung?", "Nein. Die Entscheidung trifft die Bank. Wir sorgen dafür, dass Ihre Unterlagen vollständig, schlüssig und ehrlich sind."),
        ("Begleiten Sie mich zur Bank?", "Auf Wunsch ja, persönlich oder per Video."),
        ("Kann ich die Planung später selbst fortschreiben?", "Ja. Sie bekommen das Modell in Excel, aufgebaut zum Weiterarbeiten."),
    ],
    service="Businessplan und Finanzierungsunterlagen", preis=1900,
))

# 5 Erbschaft und Erbengemeinschaft ----------------------------------------------------
URLS.append(seite(
    "leistungen/erbschaft-und-erbengemeinschaft/",
    "Erbengemeinschaft mit Unternehmen oder Immobilien | Vespasian Advisory",
    "Werte von Unternehmen und Immobilien im Nachlass, Varianten zu Übernahme und Auszahlung und deren Finanzierbarkeit. Eine gemeinsame Zahlengrundlage für alle Erben.",
    "Erbschaft und Erbengemeinschaft", "Erbschaft und Erbengemeinschaft",
    "Eine gemeinsame Zahlengrundlage für alle Erben.",
    "In Erbengemeinschaften geht es selten um Paragrafen, meist um Werte. Wir ermitteln, was Unternehmen und Immobilien im Nachlass wert sind, und rechnen durch, wer was übernehmen kann und wie sich eine Auszahlung finanzieren lässt.",
    [("2 bis 6 Wochen", "je nach Nachlass"), ("ab 2.900 €", "Honorar"), ("für alle Erben", "auf Wunsch gemeinsam")],
    block("Wann Sie uns brauchen.", liste([
        "Ein Unternehmen oder eine Beteiligung gehört zum Nachlass",
        "Immobilien sollen übernommen statt verkauft werden",
        "Ein Erbe möchte ausgezahlt werden",
        "Die Erben sind sich über Werte nicht einig",
    ]))
    + block("So gehen wir vor.", schritte([
        ("Erstgespräch", "Gern mit allen Erben gemeinsam. Kostenlos.", "45 bis 60 Minuten"),
        ("Angebot", "Umfang, Zeitplan und Honorar schriftlich.", "innerhalb von zwei Werktagen"),
        ("Bestandsaufnahme", "Eine Übersicht über Vermögen und Verbindlichkeiten im Nachlass.", ""),
        ("Bewertung", "Werte von Unternehmen und Immobilien mit Herleitung.", ""),
        ("Varianten", "Verkauf, Übernahme mit Auszahlung oder Aufteilung, jeweils mit der Frage, ob die Finanzierung trägt.", ""),
    ]), grey=True)
    + block("Was Sie bekommen.", liste([
        "Eine Vermögensübersicht des Nachlasses",
        "Werte mit nachvollziehbarer Herleitung",
        "Eine Variantenrechnung, wer was übernehmen kann",
        "Eine Rechnung zur Finanzierbarkeit einer Auszahlung",
        "Eine Grundlage, mit der Anwalt oder Notar weiterarbeiten können",
    ]))
    + block("Was wir von Ihnen brauchen.", liste([
        "Ein Nachlassverzeichnis, soweit vorhanden",
        "Grundbuchauszüge, Mietverträge und eine Mietaufstellung",
        "Jahresabschlüsse von Unternehmen im Nachlass",
        "Eine Übersicht der Darlehen",
    ]), grey=True)
    + block("Was wir bewusst nicht tun.", "<p>Wir beraten nicht rechtlich und nicht steuerlich. Wer welchen Anteil erhält und wie die Auseinandersetzung vertraglich gestaltet wird, klären Anwalt oder Notar. Erbschaftsteuer und Bewertungen für das Finanzamt sind Sache Ihres Steuerberaters.</p>")
    + block("Honorar.", honorar([
        ("Nachlass mit Immobilien", "ab 2.900 €", "Werte, Varianten und Finanzierbarkeit"),
        ("Nachlass mit Unternehmen", "ab 4.900 €", "Mit Bewertungsbericht für das Unternehmen"),
    ], 'Das genaue Honorar steht vor Beginn im schriftlichen Angebot. <a href="/honorar/">Alle Honorare</a>'), grey=True),
    [
        ("Können Sie für alle Erben gemeinsam arbeiten?", "Ja, und das ist oft der beste Weg. Ein gemeinsamer Auftrag schafft eine Zahlengrundlage, die niemand als Parteigutachten abtun muss. Wird es streitig, arbeiten wir nur noch für eine Seite."),
        ("Bewerten Sie auch Immobilien?", "Ja, mit dem Blick eines Bestandshalters auf Basis von Mieten, Zustand und Markt. Brauchen Sie ein Verkehrswertgutachten eines öffentlich bestellten Sachverständigen, sagen wir Ihnen das."),
        ("Wie viel Zeit sollten wir einplanen?", "Für einen Nachlass mit wenigen Immobilien zwei bis drei Wochen ab vollständigen Unterlagen. Mit einem Unternehmen eher vier bis sechs Wochen."),
    ],
    service="Bewertung und Variantenrechnung für Erbengemeinschaften", preis=2900,
))

# 6 Scheidung, Pflichtteil, Abfindung ---------------------------------------------------
URLS.append(seite(
    "leistungen/scheidung-und-pflichtteil/",
    "Unternehmensbewertung für Zugewinn, Pflichtteil und Abfindung | Vespasian Advisory",
    "Bewertungen von Unternehmen und Immobilien zum Stichtag für Zugewinnausgleich, Pflichtteil und Gesellschafterabfindung. Für Anwälte und ihre Mandanten.",
    "Scheidung, Pflichtteil, Abfindung", "Für Anwälte und ihre Mandanten",
    "Werte, die einer Prüfung standhalten.",
    "Beim Zugewinnausgleich, beim Pflichtteil oder bei der Abfindung eines Gesellschafters hängt viel am Wert eines Unternehmens oder einer Immobilie. Wir erstellen Bewertungen zum Stichtag, die Anwälte, Gegenseite und Gericht nachvollziehen können.",
    [("3 bis 8 Wochen", "je nach Fall"), ("ab 4.900 €", "Bewertungsbericht"), ("ab 1.900 €", "Prüfung eines Gegengutachtens")],
    block("Typische Anlässe.", liste([
        "Zugewinnausgleich, wenn ein Unternehmen oder eine Beteiligung zum Vermögen gehört",
        "Pflichtteil und Pflichtteilsergänzung",
        "Abfindung eines ausscheidenden Gesellschafters",
        "Prüfung eines Gutachtens der Gegenseite",
    ]))
    + block("So gehen wir vor.", schritte([
        ("Abstimmung mit dem Anwalt", "Stichtag, Fragestellung und Umfang. Kostenlos.", "30 bis 45 Minuten"),
        ("Angebot", "Umfang, Zeitplan und Honorar schriftlich.", "innerhalb von zwei Werktagen"),
        ("Unterlagen", "Abschlüsse rund um den Stichtag, Verträge und Angaben zum Betrieb.", ""),
        ("Bewertung", "Wert zum Stichtag mit offengelegten Annahmen und Sensitivitäten.", ""),
        ("Erläuterung", "Besprechung mit Anwalt und Mandant, auf Wunsch eine Stellungnahme zu Einwänden.", ""),
    ]), grey=True)
    + block("Was Sie bekommen.", liste([
        "Einen Bewertungsbericht zum Stichtag",
        "Offengelegte Annahmen mit Quellen",
        "Sensitivitäten, die zeigen, wo der Wert empfindlich ist",
        "Eine Erläuterung für Anwalt und Mandant",
        "Auf Wunsch eine Stellungnahme zu einem Gegengutachten",
    ]))
    + block("Was wir von Ihnen brauchen.", liste([
        "Stichtag und Fragestellung, in der Regel vom Anwalt",
        "Jahresabschlüsse vor und nach dem Stichtag",
        "Gesellschaftsvertrag mit Abfindungsregelung",
        "Unterlagen zu Immobilien im Vermögen",
    ]), grey=True)
    + block("Was wir bewusst nicht tun.", "<p>Unsere Berichte sind Parteigutachten. Wir sind keine öffentlich bestellten Sachverständigen und vertreten niemanden rechtlich. Die rechtliche Würdigung bleibt beim Anwalt.</p>")
    + block("Honorar.", honorar([
        ("Bewertungsbericht", "ab 4.900 €", "Wert zum Stichtag mit Erläuterung"),
        ("Prüfung eines Gegengutachtens", "ab 1.900 €", "Methode, Annahmen und Rechnung"),
    ], 'Das genaue Honorar steht vor Beginn im schriftlichen Angebot. <a href="/honorar/">Alle Honorare</a>'), grey=True),
    [
        ("Arbeiten Sie direkt mit Anwälten?", "Ja, das ist der Regelfall. Der Anwalt klärt Stichtag und Fragestellung, wir liefern die Bewertung."),
        ("Können Sie ein Gegengutachten prüfen?", "Ja. Wir prüfen Methode, Annahmen und Rechnung und zeigen, wo das Ergebnis angreifbar ist."),
        ("Ist das gerichtsfest?", "Kein Gutachten ist vor Einwänden sicher. Wir bauen den Bericht so auf, dass jede Zahl hergeleitet ist und Einwände gezielt beantwortet werden können. Ob ein Gericht zusätzlich einen eigenen Sachverständigen bestellt, entscheidet das Gericht."),
    ],
    service="Unternehmensbewertung für Zugewinnausgleich, Pflichtteil und Abfindung", preis=1900,
))

# Honorar -------------------------------------------------------------------------------
URLS.append(seite(
    "honorar/",
    "Honorare für Bewertung und Beratung | Vespasian Advisory",
    "Honorare von Vespasian Advisory für Unternehmensbewertung, Kaufpreis-Check, Nachfolge, Finanzierung, Erbengemeinschaft und Bewertungen für Anwälte.",
    "Honorar", "Honorar",
    "Klare Honorare, vorab vereinbart.",
    "Jeder Auftrag beginnt mit einem kostenlosen Erstgespräch. Danach erhalten Sie ein schriftliches Angebot mit Umfang, Zeitplan und Honorar. Die Beträge unten sind Untergrenzen für typische Aufträge.",
    [("kostenlos", "Erstgespräch"), ("schriftlich", "Angebot vor Beginn"), ("keine Provisionen", "von niemandem")],
    block("Honorare im Überblick.", honorar([
        ("Werteinschätzung", "ab 1.900 €", '<a href="/leistungen/unternehmensbewertung/">Unternehmensbewertung</a>, bei Folgeauftrag angerechnet'),
        ("Bewertungsbericht", "ab 4.900 €", '<a href="/leistungen/unternehmensbewertung/">Unternehmensbewertung</a> mit Sensitivitäten'),
        ("Kaufpreis-Check", "ab 2.400 €", '<a href="/leistungen/kaufpreis-check/">Prüfung vor dem Kauf</a>'),
        ("Nachfolge vorbereiten", "ab 6.900 €", '<a href="/leistungen/nachfolge-und-verkauf/">Mit Bewertungsbericht und Exposé</a>'),
        ("Bankunterlagen", "ab 1.900 €", '<a href="/leistungen/finanzierung-und-bankgespraech/">Planung und Kennzahlen</a>'),
        ("Erbengemeinschaft", "ab 2.900 €", '<a href="/leistungen/erbschaft-und-erbengemeinschaft/">Werte und Varianten</a>'),
        ("Bewertung zum Stichtag", "ab 4.900 €", '<a href="/leistungen/scheidung-und-pflichtteil/">Zugewinn, Pflichtteil, Abfindung</a>'),
        ("Prüfung eines Gegengutachtens", "ab 1.900 €", '<a href="/leistungen/scheidung-und-pflichtteil/">Methode, Annahmen, Rechnung</a>'),
    ], "Begleitung in Verhandlungen und laufende Aufgaben wie Controlling rechnen wir nach vereinbartem Umfang ab. Reisekosten fallen nur nach Absprache an."))
    + block("Wovon das Honorar abhängt.", liste([
        "Größe und Struktur des Unternehmens, etwa mehrere Gesellschaften oder Immobilien im Betriebsvermögen",
        "Vollständigkeit und Qualität der Unterlagen",
        "Zweck, also interne Entscheidung oder Bericht gegenüber Dritten oder einem Gericht",
        "Zeitdruck",
        "Anzahl der Bewertungsobjekte und Stichtage",
    ]), grey=True)
    + block("Warum wir Preise nennen.", "<p>Sie sollen vor dem ersten Gespräch einschätzen können, ob eine Zusammenarbeit für Sie in Frage kommt. Ein Bewertungsbericht eines Wirtschaftsprüfers kostet oft deutlich mehr. Unsere Berichte folgen demselben methodischen Rahmen, verzichten aber auf das, was nur ein Wirtschaftsprüfer leisten darf. Wenn Ihr Anlass genau das verlangt, sagen wir es Ihnen im Erstgespräch.</p>"),
    [
        ("Ist das Erstgespräch wirklich kostenlos?", "Ja. Es dient dazu, Anlass und Umfang zu klären. Ob Sie danach beauftragen, entscheiden Sie in Ruhe."),
        ("Kann das Honorar am Ende höher ausfallen?", "Nur wenn sich der Umfang ändert und Sie vorher zustimmen. Ohne Ihre Zustimmung bleibt es beim Angebot."),
        ("Erhalten Sie Provisionen von Dritten?", "Nein, von niemandem. Wir verkaufen keine Finanzprodukte und vermitteln keine Kredite oder Unternehmen."),
    ],
))

# Beispielbericht ------------------------------------------------------------------------
def tab(kopf, zeilen, summe=None):
    h = "<tr>" + "".join(f'<th class="{"num" if i else ""}">{k}</th>' for i, k in enumerate(kopf)) + "</tr>"
    b = "".join("<tr>" + "".join(f'<td class="{"num" if i else ""}">{c}</td>' for i, c in enumerate(z)) + "</tr>" for z in zeilen)
    if summe:
        b += '<tr class="sum">' + "".join(f'<td class="{"num" if i else ""}">{c}</td>' for i, c in enumerate(summe)) + "</tr>"
    return f'<div class="table-wrap"><table><thead>{h}</thead><tbody>{b}</tbody></table></div>'


URLS.append(seite(
    "beispiel/",
    "Beispiel eines Bewertungsberichts | Vespasian Advisory",
    "Wie ein Bewertungsbericht von Vespasian Advisory aufgebaut ist. Gliederung, Bereinigung, Ertragswert, Sensitivitäten und Plausibilisierung an einem Beispiel mit erfundenen Zahlen.",
    "Beispielbericht", "Beispiel mit erfundenen Zahlen",
    "So sieht ein Bewertungsbericht aus.",
    "Damit Sie wissen, was Sie bekommen, zeigen wir die wichtigsten Teile eines Berichts an einem erfundenen Unternehmen. Zahlen und Annahmen sind frei gewählt und gerundet.",
    [("Musterbetrieb", "Haustechnik, 24 Mitarbeitende"), ("3,2 Mio. €", "Umsatz"), ("Übergabe", "an zwei Mitarbeiter")],
    block("Gliederung des Berichts.", '<p class="tag">Beispiel, keine echten Daten</p>' + schritte([
        ("Auftrag und Zweck", "Anlass, Stichtag, Bewertungsrahmen und die Frage, die der Bericht beantwortet.", ""),
        ("Unternehmen und Markt", "Geschäftsmodell, Kunden, Personal, Wettbewerb und Abhängigkeiten.", ""),
        ("Bereinigung", "Vom Ergebnis laut Abschluss zum Ergebnis, das ein neuer Eigentümer erwarten kann.", ""),
        ("Planung", "Die nächsten Jahre, abgeglichen mit Vergangenheit und Markt.", ""),
        ("Kapitalisierungszins", "Basiszins, Risikozuschlag und Wachstum, mit Quellen.", ""),
        ("Wert, Sensitivitäten und Plausibilisierung", "Ertragswert, Bandbreite und der Abgleich mit Marktmultiplikatoren.", ""),
        ("Ergebnis und Grenzen", "Was der Wert aussagt und was nicht.", ""),
    ]))
    + block("Bereinigung der Ergebnisse.", "<p>Das Ergebnis laut Jahresabschluss ist selten das, was ein Käufer erwarten kann. Im Beispiel zahlt sich der Inhaber ein Gehalt unter Marktniveau, die Gesellschaft mietet ihre Halle beim Inhaber über Marktniveau, und 2025 gab es einen einmaligen Großauftrag.</p>" + tab(
        ["in Tsd. €", "2023", "2024", "2025"],
        [["Ergebnis vor Steuern laut Abschluss", "310", "285", "340"],
         ["Marktübliches Geschäftsführergehalt", "−40", "−40", "−45"],
         ["Miete auf Marktniveau", "+12", "+12", "+12"],
         ["Einmaliger Großauftrag", "0", "0", "−35"]],
        ["Bereinigtes Ergebnis vor Steuern", "282", "257", "272"]) + '<p class="note">Durchschnitt rund 270 Tsd. € vor Steuern. Nach Unternehmensteuern, hier vereinfacht mit 30 Prozent angesetzt, bleibt ein nachhaltiger Ertrag von rund 190 Tsd. € im Jahr.</p>', grey=True)
    + block("Vom Ertrag zum Wert.", tab(
        ["Schritt", "Wert"],
        [["Nachhaltiger Ertrag", "190 Tsd. €"],
         ["Kapitalisierungszins (Annahme für dieses Beispiel)", "11,0 %"],
         ["abzüglich Wachstum", "1,0 %"]],
        ["Ertragswert, 190 geteilt durch 10 %", "1,90 Mio. €"]) + '<p class="note">In einem echten Auftrag leiten wir den Kapitalisierungszins aus aktuellen Marktdaten her und nennen die Quellen. Hier ist er eine Annahme.</p>')
    + block("Sensitivitäten.", "<p>Kleine Änderungen bei Ertrag oder Zins verschieben den Wert deutlich. Deshalb gehört diese Tabelle in jeden Bericht.</p>" + tab(
        ["Zins nach Wachstum", "Ertrag 170", "Ertrag 190", "Ertrag 210"],
        [["9 %", "1,89 Mio. €", "2,11 Mio. €", "2,33 Mio. €"],
         ["10 %", "1,70 Mio. €", "1,90 Mio. €", "2,10 Mio. €"],
         ["11 %", "1,55 Mio. €", "1,73 Mio. €", "1,91 Mio. €"]]), grey=True)
    + block("Plausibilisierung und Ergebnis.", "<p>Zum Abgleich nehmen wir das operative Ergebnis von rund 300 Tsd. € und übliche Multiplikatoren für vergleichbare kleine Handwerksbetriebe von etwa 5,5 bis 6,5. Das ergibt 1,65 bis 1,95 Mio. € und bestätigt die Größenordnung.</p><p><b>Ergebnis im Beispiel.</b> Ein Wert von rund 1,9 Mio. € mit einer Bandbreite von 1,7 bis 2,1 Mio. €. Für die Übergabe an zwei Mitarbeiter folgt im Bericht eine Rechnung, ob der Kaufpreis aus dem Ertrag des Betriebs finanziert werden kann.</p>"),
    [
        ("Sind die Zahlen echt?", "Nein. Unternehmen, Zahlen und Annahmen sind erfunden und dienen nur der Veranschaulichung."),
        ("Wie umfangreich ist ein echter Bericht?", "Je nach Unternehmen 20 bis 40 Seiten mit Anhang. Die Werteinschätzung ist deutlich kürzer."),
        ("Bekomme ich auch die Rechnung?", "Auf Wunsch erhalten Sie das Rechenmodell in Excel, damit Sie Annahmen selbst verändern können."),
    ],
))

print("\n".join(URLS))
