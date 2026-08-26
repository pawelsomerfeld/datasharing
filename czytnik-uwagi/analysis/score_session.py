#!/usr/bin/env python3
"""Przelicza wskaźniki z logu sesji Czytnika Uwagi.

Niezależna implementacja tych samych wzorów, które liczy przeglądarka —
rozbieżność między tym skryptem a polem `metrics` w pliku JSON oznacza
błąd po jednej ze stron i jest celowym mechanizmem kontrolnym.

    python3 score_session.py sesja.json              # jedna sesja
    python3 score_session.py --norms katalog/        # percentyle, osobno dla każdej formy

Tylko biblioteka standardowa.
"""

import argparse
import cmath
import glob
import json
import math
import os
import signal
import statistics as st
import sys

# Bez tego przepuszczenie wyniku przez `head` albo `less` kończy się
# śladem stosu zamiast cichym urwaniem.
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):        # Windows nie ma SIGPIPE
    pass

# Kategorie sondy poza treścią tekstu. Stare klucze (mw-aware / mw-unaware)
# zostają, żeby pliki sprzed przebudowy sondy nadal się liczyły.
OFF_TASK = {"mw", "task-rel", "external", "blank", "mw-aware", "mw-unaware"}
PROBE_CATS = {"on-task": "probe_on_task", "mw": "probe_mind_wandering",
              "task-rel": "probe_task_related", "external": "probe_external",
              "blank": "probe_blank"}
PREMATURE_MS_PER_CHAR = 12.0
SLOW_BAND = (0.03, 0.07)


# --------------------------------------------------------------------- #
# narzędzia statystyczne
# --------------------------------------------------------------------- #

def ols(X, y):
    """Najmniejsze kwadraty przez równania normalne (macierze 3x3)."""
    k = len(X[0])
    A = [[sum(X[i][a] * X[i][b] for i in range(len(X))) for b in range(k)] for a in range(k)]
    b = [sum(X[i][a] * y[i] for i in range(len(X))) for a in range(k)]
    for c in range(k):                                    # eliminacja Gaussa
        p = max(range(c, k), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        b[c], b[p] = b[p], b[c]
        if abs(A[c][c]) < 1e-12:
            return [0.0] * k
        for r in range(k):
            if r == c:
                continue
            f = A[r][c] / A[c][c]
            for j in range(c, k):
                A[r][j] -= f * A[c][j]
            b[r] -= f * b[c]
    return [b[i] / A[i][i] for i in range(k)]


def residualize(items):
    """Reszty z regresji: czas linii ~ liczba znaków + pozycja w sesji.

    `items` to pary (pozycja w pełnej sesji, linia). Pozycja musi być
    globalna: linia zatrzymana nie wchodzi do serii czasów czytania, ale
    czas sesji i tak zajmuje, więc kolejne linie są dalej w czasie, niż
    wynikałoby z numeracji po odfiltrowaniu."""
    X = [[1.0, float(l["chars"]), float(pos)] for pos, l in items]
    y = [float(l["rt"]) for _, l in items]
    w = ols(X, y)
    return [y[i] - sum(w[j] * X[i][j] for j in range(3)) for i in range(len(y))]


def ex_gaussian(xs):
    """Estymacja metodą momentów. tau to składowa wykładnicza (ogon).

    Bez prawostronnej skośności estymator nie ma rozwiązania — zwracamy
    None, nie zero. Zero czytałoby się jak bardzo dobry wynik."""
    m, s = st.fmean(xs), st.pstdev(xs)
    if s == 0:
        return m, 0.0, None, 0.0
    skew = st.fmean([(x - m) ** 3 for x in xs]) / s ** 3
    if skew <= 0.01:
        return m, s, None, skew
    tau = s * (skew / 2) ** (1 / 3)
    return m - tau, math.sqrt(max(s * s - tau * tau, 0.0)), tau, skew


def quantile(a, p):
    """Kwantyl z interpolacją liniową."""
    if not a:
        return None
    x = sorted(a)
    h = (len(x) - 1) * p
    lo = math.floor(h)
    return x[lo] + (h - lo) * (x[min(lo + 1, len(x) - 1)] - x[lo])


def band_power(x, dt_s, lo, hi):
    """Względna moc w paśmie [lo, hi] Hz. Nierównomierne próbkowanie
    zastąpione średnim odstępem — wynik jest przybliżeniem."""
    n = len(x)
    if n < 16 or dt_s <= 0:
        return None
    m = st.fmean(x)
    c = [v - m for v in x]
    band = total = 0.0
    for k in range(1, n // 2 + 1):
        acc = sum(c[t] * cmath.exp(-2j * math.pi * k * t / n) for t in range(n))
        p = abs(acc) ** 2 / n
        total += p
        if lo <= k / (n * dt_s) <= hi:
            band += p
    return band / total if total else None


def z(p):
    """Odwrotna dystrybuanta normalna (Acklam)."""
    a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2,
         1.383577518672690e2, -3.066479806614716e1, 2.506628277459239]
    b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2,
         6.680131188771972e1, -1.328068155288572e1]
    c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838,
         -2.549732539343734, 4.374664141464968, 2.938163982698783]
    d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996, 3.754408661907416]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - pl:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q, r = p - 0.5, (p - 0.5) ** 2
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


# --------------------------------------------------------------------- #
# wskaźniki
# --------------------------------------------------------------------- #

def score(session):
    lines = session["lines"]
    probes = session.get("probes", [])
    quiz = session.get("quiz", [])
    # Zdarzenia z bloku próbnego odcinamy tak samo jak jego linie.
    all_events = session.get("events", [])
    t0m = next((e["t"] for e in all_events if e["type"] == "measured-start"), 0)
    events = [e for e in all_events if e.get("t", 0) >= t0m]
    if any(l.get("rt") is None for l in lines):
        bad = [l["passage"] + "/" + str(l["n"]) for l in lines if l.get("rt") is None]
        sys.exit("log niekompletny — brak czasu dla linii: " + ", ".join(bad))
    # Czas linii zatrzymanej jest narzucony przez zadanie, nie wybrany —
    # nie wolno go liczyć jako czasu czytania.
    read_pairs = [(i, l) for i, l in enumerate(lines) if not l.get("held")]
    read = [l for _, l in read_pairs]
    rt = [float(l["rt"]) for l in read]
    res = residualize(read_pairs)
    # Reszty w indeksacji pełnej listy, z None na liniach zatrzymanych.
    res_full, it = [], iter(res)
    for l in lines:
        res_full.append(None if l.get("held") else next(it))

    mu, sigma, tau, skew = ex_gaussian(rt)
    out = {
        "form": session.get("meta", {}).get("form", "?"),
        "code": session.get("meta", {}).get("code"),
        "salience": session.get("meta", {}).get("salience"),
        "notif_set": session.get("meta", {}).get("notifSet"),
        "dist_mode": session.get("meta", {}).get("distMode"),
        "n_lines": len(lines),
        "mu": mu, "sigma": sigma, "tau": tau, "skew": skew,
        # Odporny odpowiednik tau: górna połowa rozkładu reszt względem
        # mediany tempa. Nie degeneruje się i nie zależy od szybkości czytania.
        "tail_ratio": (quantile(res, 0.9) - quantile(res, 0.5)) / (st.median(rt) or 1),
        "cv": st.pstdev(res) / st.fmean(rt),
        "slow_band": band_power(res, st.fmean(rt) / 1000, *SLOW_BAND),
    }

    # wykrywanie bezsensu — trafienie także wtedy, gdy reakcja padła linię później
    hits = misses = fa = cr = 0
    lat = []
    for i, l in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        same = nxt and nxt["passage"] == l["passage"]
        if l["anomaly"]:
            if l["flagged"]:
                hits += 1
                lat.append(l["flagRt"])
            elif same and nxt["flagged"]:
                hits += 1
                lat.append(l["rt"] + nxt["flagRt"])
            else:
                misses += 1
    for i, l in enumerate(lines):
        if l["anomaly"]:
            continue
        prev = lines[i - 1] if i else None
        if prev and prev["anomaly"] and not prev["flagged"]:
            continue                                       # opóźnione trafienie
        fa += 1 if l["flagged"] else 0
        cr += 0 if l["flagged"] else 1
    out.update(hits=hits, misses=misses, false_alarms=fa,
               dprime=z((hits + .5) / (hits + misses + 1)) - z((fa + .5) / (fa + cr + 1)),
               detect_latency=st.median(lat) if lat else None)

    # sondy myśli
    out["off_task_rate"] = (sum(p["key"] in OFF_TASK for p in probes) / len(probes)) if probes else None
    for key, name in PROBE_CATS.items():
        out[name] = (sum(p["key"] == key for p in probes) / len(probes)) if probes else None
    absv = [p["absorption"] for p in probes if isinstance(p.get("absorption"), (int, float))]
    out["absorption"] = st.fmean(absv) if absv else None

    def pre_probe_sd(want_mw):
        vals = []
        for p in probes:
            if (p["key"] in OFF_TASK) != want_mw:
                continue
            w = [v for v in res_full[max(0, p["lineIdx"] - 3): p["lineIdx"] + 1] if v is not None]
            if len(w) >= 3:
                vals.append(st.pstdev(w))
        return st.fmean(vals) if vals else None

    a, b_ = pre_probe_sd(True), pre_probe_sd(False)
    out["pre_probe_sd_ratio"] = (a / b_) if (a and b_) else None

    # dystraktory
    base = [res_full[i] for i, l in enumerate(lines)
            if not l["distractor"] and not l["anomaly"] and not l.get("held")]
    hit_d = [res_full[i] for i, l in enumerate(lines) if l["distractor"] and not l.get("held")]
    out["distractor_cost"] = (st.fmean(hit_d) - st.fmean(base)) if hit_d and base else None
    out["distractor_lag"] = [
        (st.fmean(v) - st.fmean(base)) if (v := [res_full[i] for i, l in enumerate(lines)
         if i >= g and not l.get("held") and lines[i - g]["distractor"]
         and lines[i - g]["passage"] == l["passage"]]) else None
        for g in (1, 2, 3)]
    # --- habituacja ---
    # Uśrednienie kosztu po wszystkich ekspozycjach gubi to, co w
    # rozpraszalności najciekawsze: sprawny filtr przestaje reagować na
    # bodziec, który okazał się nieistotny, więc koszt kolejnych zakłóceń
    # maleje. Płaski albo rosnący przebieg to inny obraz niż sam wysoki
    # koszt średni.
    mode = session.get("meta", {}).get("distMode")
    seq, kinds = [], []
    for i, l in enumerate(lines):
        if not l["distractor"] or l.get("held") or res_full[i] is None:
            continue
        seq.append(res_full[i] - st.fmean(base))
        slot = l.get("distSlot", -1)
        is_tz = bool(l.get("teaser")) and (mode == "ciekawostki" or (mode == "oba" and slot % 2 == 0))
        kinds.append("ciekawostka" if is_tz else "powiadomienie")
    out["distractor_cost_sequence"] = [round(v) for v in seq]
    if len(seq) >= 4:
        xs = list(range(len(seq)))
        mx, my = st.fmean(xs), st.fmean(seq)
        den = sum((x - mx) ** 2 for x in xs)
        out["habituation_slope"] = (sum((x - mx) * (seq[i] - my) for i, x in enumerate(xs)) / den) if den else None
    else:
        out["habituation_slope"] = None
    for kind, name in (("ciekawostka", "distractor_cost_teaser"),
                       ("powiadomienie", "distractor_cost_notification")):
        v = [c for c, k in zip(seq, kinds) if k == kind]
        out[name] = st.fmean(v) if v else None

    out["distractor_clicks"] = sum(e["type"] == "distractor-click" for e in events)
    # Najazd kursorem na powiadomienie: orientacja uwagi bez kliknięcia.
    shown_n = sum(e["type"] == "distractor-on" for e in events)
    hov = [e["ms"] for e in events if e["type"] == "distractor-hover" and "ms" in e]
    out["distractors_shown"] = shown_n
    planned = (session.get("metrics") or {}).get("distractorsPlanned")
    out["distractors_planned"] = planned
    out["distractors_delivered"] = (shown_n / planned) if planned else None
    out["distractor_hover_rate"] = (len(hov) / shown_n) if shown_n else None
    out["distractor_hover_ms"] = st.median(hov) if hov else None

    # pozostałe
    out["regressions"] = sum(e["type"] == "regression" for e in events)
    out["premature"] = sum(1 for l in read if l["rt"] / l["chars"] < PREMATURE_MS_PER_CHAR)

    # --- ciekawostki i kontaminacja źródła ---
    # Wskaźnik przynęty rozdziela „nie zapamiętałem tekstu" (błąd rozłożony
    # po opcjach) od „zapamiętałem dystraktor zamiast tekstu" (błąd skupiony
    # na przynęcie) — to dwie zupełnie różne porażki.
    tz = session.get("teasers", [])
    opened = sum(1 for t in tz if t.get("opened"))
    hov = [t["hoverMs"] for t in tz if t.get("hoverMs") is not None]
    out["teasers_shown"] = len(tz)
    out["teasers_opened"] = opened
    out["teaser_open_rate"] = (opened / len(tz)) if tz else None
    out["teaser_dwell_ms"] = sum(t.get("dwellMs") or 0 for t in tz)
    out["teaser_hover_ms"] = st.median(hov) if hov else None

    lure_qs = [q for q in quiz if "lureOpt" in q]
    clean_qs = [q for q in quiz if "lureOpt" not in q]
    lure_errs = [q for q in lure_qs if not q["correct"]]
    out["lure_questions"] = len(lure_qs)
    out["lure_rate"] = (sum(1 for q in lure_qs if q.get("pickedLure")) / len(lure_qs)) if lure_qs else None
    out["lure_share_of_errors"] = (sum(1 for q in lure_errs if q.get("pickedLure")) / len(lure_errs)) if lure_errs else None
    acc_lure = (sum(q["correct"] for q in lure_qs) / len(lure_qs)) if lure_qs else None
    acc_clean = (sum(q["correct"] for q in clean_qs) / len(clean_qs)) if clean_qs else None
    out["comprehension_lure"] = acc_lure
    out["comprehension_clean"] = acc_clean
    out["lure_cost"] = (acc_clean - acc_lure) if (acc_lure is not None and acc_clean is not None) else None

    # --- hamowanie reakcji na liniach zatrzymanych ---
    held = [l for l in lines if l.get("held")]
    presses = [l.get("holdPresses", 0) for l in held]
    firsts = [l["holdFirstMs"] for l in held if l.get("holdFirstMs") is not None]
    out["hold_lines"] = len(held)
    out["hold_commission"] = (sum(1 for x in presses if x) / len(held)) if held else None
    out["hold_presses"] = sum(presses)
    out["hold_first_ms"] = st.median(firsts) if firsts else None
    tol = [l["holdFirstMs"] / l["holdMs"] for l in held
           if l.get("holdFirstMs") is not None and l.get("holdMs")]
    out["hold_tolerance"] = st.median(tol) if tol else None

    # --- korekta po błędzie: zwolnienie na linii po błędzie ---
    post = []
    for i, l in enumerate(lines):
        is_err = (l.get("held") and l.get("holdPresses", 0) > 0) \
              or (not l.get("held") and not l["anomaly"] and l["flagged"])
        if not is_err or i + 1 >= len(lines):
            continue
        nxt = lines[i + 1]
        if not nxt.get("held") and res_full[i + 1] is not None and nxt["passage"] == l["passage"]:
            post.append(res_full[i + 1])
    out["post_error_n"] = len(post)
    out["post_error_slowing"] = (st.fmean(post) - st.fmean(res)) if post else None

    # --- spadek czujności: nachylenie tempa względem pozycji w sesji ---
    idx = [i for i, l in enumerate(lines) if not l.get("held")]
    if len(idx) >= 20:
        ys = [l["rt"] / l["chars"] for l in read]
        mx, my = st.fmean(idx), st.fmean(ys)
        den = sum((x - mx) ** 2 for x in idx)
        out["vigilance_slope"] = (sum((x - mx) * (ys[i] - my) for i, x in enumerate(idx)) / den * 10) if den else None
    else:
        out["vigilance_slope"] = None
    out["blur_count"] = sum(e["type"] == "window-blur" for e in events)
    out["comprehension"] = (sum(q["correct"] for q in quiz) / len(quiz)) if quiz else None
    tot = sum(rt)
    out["wpm"] = sum(l["words"] for l in read) / (tot / 60000) if tot else None
    return out


LABELS = {
    "n_lines": "linii", "mu": "mu (ms)", "sigma": "sigma (ms)", "tau": "tau (ms)",
    "tail_ratio": "ogon odporny", "skew": "skośność czasów",
    "cv": "wsp. zmienności", "slow_band": "moc 0,03-0,07 Hz", "dprime": "d' bezsens",
    "hits": "trafienia", "misses": "przeoczenia", "false_alarms": "fałszywe alarmy",
    "detect_latency": "opóźn. wykrycia (ms)", "off_task_rate": "uwaga poza tekstem",
    "probe_on_task": "sondy: przy tekście", "probe_mind_wandering": "sondy: gdzie indziej",
    "probe_task_related": "sondy: przy badaniu", "probe_external": "sondy: bodziec zewn.",
    "probe_blank": "sondy: pustka", "absorption": "wciągnięcie (1-5)",
    "habituation_slope": "habituacja (ms/eksp.)",
    "distractor_cost_teaser": "koszt: ciekawostka (ms)",
    "distractor_cost_notification": "koszt: powiadomienie (ms)",
    "distractors_shown": "powiadomień", "distractors_planned": "zaplanowanych",
    "distractors_delivered": "dostarczonych", "distractor_hover_rate": "najazd kursorem",
    "distractor_hover_ms": "czas do najazdu (ms)",
    "pre_probe_sd_ratio": "rozrzut przed sondą (x)", "distractor_cost": "koszt powiad. (ms)",
    "distractor_lag": "powrót do tempa (ms)", "distractor_clicks": "kliknięcia",
    "teasers_shown": "ciekawostek", "teaser_open_rate": "otwartych",
    "teaser_dwell_ms": "czas w ciekawostkach (ms)", "teaser_hover_ms": "czas do spojrzenia (ms)",
    "lure_questions": "pytań z przynętą", "lure_rate": "przynęta w odpowiedzi",
    "lure_share_of_errors": "przynęty wśród błędów", "comprehension_lure": "rozumienie: z przynętą",
    "comprehension_clean": "rozumienie: bez przynęty", "lure_cost": "koszt kontaminacji",
    "hold_lines": "linii zatrzymanych", "hold_commission": "błędy komisji",
    "hold_presses": "naciśnięć w oknie", "hold_first_ms": "czas 1. naciśnięcia (ms)",
    "hold_tolerance": "tolerancja czekania", "post_error_slowing": "korekta po błędzie (ms)",
    "post_error_n": "błędów do korekty", "vigilance_slope": "spadek czujności",
    "regressions": "powroty", "premature": "przejścia przedwczesne",
    "blur_count": "wyjścia poza okno", "comprehension": "rozumienie", "wpm": "słów/min",
}


def show(v):
    if v is None:
        return "—"
    if isinstance(v, list):
        return " · ".join(show(x) for x in v)
    if isinstance(v, float):
        return f"{v:.3f}" if abs(v) < 10 else f"{v:.1f}"
    return str(v)


def check_against_browser(sess, mine):
    """Porównuje z wartościami policzonymi w przeglądarce."""
    pairs = [("tau", "tau"), ("tail_ratio", "tailRatio"), ("cv", "cv"), ("dprime", "dprime"),
             ("slow_band", "slowBand"), ("comprehension", "comprehension"), ("wpm", "wpm"),
             ("off_task_rate", "offTaskRate"), ("absorption", "absorption"),
             ("distractor_hover_rate", "distractorHoverRate"),
             ("hold_commission", "holdCommission"), ("hold_tolerance", "holdTolerance"),
             ("post_error_slowing", "postErrorSlowing"), ("vigilance_slope", "vigilanceSlope"),
             ("lure_rate", "lureRate"), ("teaser_open_rate", "teaserOpenRate"),
             ("lure_cost", "lureCost"), ("habituation_slope", "habituationSlope")]
    bad = []
    for py, js in pairs:
        a, b_ = mine.get(py), sess.get("metrics", {}).get(js)
        if a is None or b_ is None:
            continue
        if abs(a - b_) > max(1e-6, abs(b_) * 1e-6):
            bad.append(f"  {py}: python={a:.6f} przeglądarka={b_:.6f}")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="plik JSON sesji albo katalog przy --norms")
    ap.add_argument("--norms", action="store_true", help="policz percentyle dla wszystkich sesji w katalogu")
    ap.add_argument("--json", action="store_true", help="wypisz surowy JSON zamiast tabeli")
    args = ap.parse_args()

    if args.norms:
        files = sorted(glob.glob(os.path.join(args.path, "*.json")))
        if not files:
            sys.exit(f"brak plików .json w {args.path}")
        rows = [score(json.load(open(f, encoding="utf-8"))) for f in files]
        by_form = {}
        for r in rows:
            by_form.setdefault(r["form"], []).append(r)

        # Normy liczy się osobno dla każdej formy. Zlanie ich w jedną tabelę
        # zakłada równoważność form, której nikt jeszcze nie wykazał.
        print(f"# {len(rows)} sesji z {args.path}")
        if len(by_form) > 1:
            print("# formy rozdzielone: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(by_form.items())))
        for form, group in sorted(by_form.items()):
            print(f"\n## Forma {form} — {len(group)} sesji")
            if len(group) < 30:
                print("   (próba za mała na normy; percentyle wyłącznie poglądowe)")
            print(f"{'wskaźnik':<26}{'n':>4}{'P10':>10}{'P25':>10}{'mediana':>10}{'P75':>10}{'P90':>10}")
            print("-" * 80)
            for k in LABELS:
                vals = sorted(r[k] for r in group if isinstance(r.get(k), (int, float)))
                if len(vals) < 2:
                    continue
                q = lambda p: vals[min(len(vals) - 1, int(round(p * (len(vals) - 1))))]
                print(f"{LABELS[k]:<26}{len(vals):>4}" +
                      "".join(f"{show(q(p)):>10}" for p in (.10, .25, .50, .75, .90)))
        return

    sess = json.load(open(args.path, encoding="utf-8"))
    mine = score(sess)
    if args.json:
        print(json.dumps(mine, ensure_ascii=False, indent=2))
        return
    head = f"# {args.path}  ·  forma {mine['form']}"
    if mine.get("code"):
        head += f"  ·  kod {mine['code']}"
    if mine.get("dist_mode"):
        head += f"  ·  dystraktor: {mine['dist_mode']}"
    if mine.get("salience"):
        head += f"  ·  natarczywość: {mine['salience']}"
    print(head + "\n")
    if mine.get("tau") is None:
        print("uwaga: tau nieokreślone (rozkład bez prawostronnej skośności) — czytaj ogon odporny\n")
    for k, lab in LABELS.items():
        print(f"{lab:<26}{show(mine.get(k)):>14}")
    bad = check_against_browser(sess, mine)
    print("\nkontrola zgodności z przeglądarką:", "OK" if not bad else "ROZBIEŻNOŚCI")
    for line in bad:
        print(line)


if __name__ == "__main__":
    main()
