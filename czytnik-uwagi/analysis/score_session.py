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

MW_KEYS = {"mw-aware", "mw-unaware", "blank"}
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


def residualize(lines):
    """Reszty z regresji: czas linii ~ liczba znaków + pozycja w sesji."""
    X = [[1.0, float(l["chars"]), float(i)] for i, l in enumerate(lines)]
    y = [float(l["rt"]) for l in lines]
    w = ols(X, y)
    return [y[i] - sum(w[j] * X[i][j] for j in range(3)) for i in range(len(y))]


def ex_gaussian(xs):
    """Estymacja metodą momentów. tau to składowa wykładnicza (ogon)."""
    m, s = st.fmean(xs), st.pstdev(xs)
    if s == 0:
        return m, 0.0, 0.0
    skew = st.fmean([(x - m) ** 3 for x in xs]) / s ** 3
    if skew <= 0.01:
        return m, s, 0.0
    tau = s * (skew / 2) ** (1 / 3)
    return m - tau, math.sqrt(max(s * s - tau * tau, 0.0)), tau


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
    events = session.get("events", [])
    if any(l.get("rt") is None for l in lines):
        bad = [l["passage"] + "/" + str(l["n"]) for l in lines if l.get("rt") is None]
        sys.exit("log niekompletny — brak czasu dla linii: " + ", ".join(bad))
    rt = [float(l["rt"]) for l in lines]
    res = residualize(lines)

    mu, sigma, tau = ex_gaussian(rt)
    out = {
        "form": session.get("meta", {}).get("form", "?"),
        "n_lines": len(lines),
        "mu": mu, "sigma": sigma, "tau": tau,
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
    out["mw_rate"] = (sum(p["key"] in MW_KEYS for p in probes) / len(probes)) if probes else None

    def pre_probe_sd(want_mw):
        vals = []
        for p in probes:
            if (p["key"] in MW_KEYS) != want_mw:
                continue
            w = res[max(0, p["lineIdx"] - 3): p["lineIdx"] + 1]
            if len(w) >= 3:
                vals.append(st.pstdev(w))
        return st.fmean(vals) if vals else None

    a, b_ = pre_probe_sd(True), pre_probe_sd(False)
    out["pre_probe_sd_ratio"] = (a / b_) if (a and b_) else None

    # dystraktory
    base = [res[i] for i, l in enumerate(lines) if not l["distractor"] and not l["anomaly"]]
    hit_d = [res[i] for i, l in enumerate(lines) if l["distractor"]]
    out["distractor_cost"] = (st.fmean(hit_d) - st.fmean(base)) if hit_d and base else None
    out["distractor_lag"] = [
        (st.fmean(v) - st.fmean(base)) if (v := [res[i] for i, l in enumerate(lines)
         if i >= g and lines[i - g]["distractor"] and lines[i - g]["passage"] == l["passage"]]) else None
        for g in (1, 2, 3)]
    out["distractor_clicks"] = sum(e["type"] == "distractor-click" for e in events)

    # pozostałe
    out["regressions"] = sum(e["type"] == "regression" for e in events)
    out["premature"] = sum(1 for l in lines if l["rt"] / l["chars"] < PREMATURE_MS_PER_CHAR)
    out["blur_count"] = sum(e["type"] == "window-blur" for e in events)
    out["comprehension"] = (sum(q["correct"] for q in quiz) / len(quiz)) if quiz else None
    tot = sum(rt)
    out["wpm"] = sum(l["words"] for l in lines) / (tot / 60000) if tot else None
    return out


LABELS = {
    "n_lines": "linii", "mu": "mu (ms)", "sigma": "sigma (ms)", "tau": "tau (ms)",
    "cv": "wsp. zmienności", "slow_band": "moc 0,03-0,07 Hz", "dprime": "d' bezsens",
    "hits": "trafienia", "misses": "przeoczenia", "false_alarms": "fałszywe alarmy",
    "detect_latency": "opóźn. wykrycia (ms)", "mw_rate": "odsetek odpływania",
    "pre_probe_sd_ratio": "rozrzut przed sondą (x)", "distractor_cost": "koszt powiad. (ms)",
    "distractor_lag": "powrót do tempa (ms)", "distractor_clicks": "kliknięcia",
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
    pairs = [("tau", "tau"), ("cv", "cv"), ("dprime", "dprime"),
             ("slow_band", "slowBand"), ("comprehension", "comprehension"), ("wpm", "wpm")]
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
    print(f"# {args.path}  ·  forma {mine['form']}\n")
    for k, lab in LABELS.items():
        print(f"{lab:<26}{show(mine.get(k)):>14}")
    bad = check_against_browser(sess, mine)
    print("\nkontrola zgodności z przeglądarką:", "OK" if not bad else "ROZBIEŻNOŚCI")
    for line in bad:
        print(line)


if __name__ == "__main__":
    main()
