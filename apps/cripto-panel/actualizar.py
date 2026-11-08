#!/usr/bin/env python3
"""Descarga velas públicas de Bitget (sin claves) para el panel de cripto.

Escribe un JSON por par en la carpeta indicada, listo para guardarse en la
base de datos del panel (colección "market", un documento por par).

    python3 actualizar.py SALIDA_DIR
"""
import json, os, sys, time, urllib.request

PARES = ["XRPUSDT", "BTCUSDT"]
API = "https://api.bitget.com/api/v2/spot/market"

def get(path):
    with urllib.request.urlopen(API + path, timeout=30) as r:
        d = json.load(r)
    if d.get("code") != "00000":
        raise RuntimeError(d)
    return d["data"]

def velas(par, gran, limite):
    rows = get(f"/candles?symbol={par}&granularity={gran}&limit={limite}")
    # [ts_ms, open, high, low, close, vol_base, ...] -> [ts_s, o, h, l, c]
    out = [[int(r[0]) // 1000] + [float(x) for x in r[1:5]] for r in rows]
    return sorted(out)

def main(dst):
    os.makedirs(dst, exist_ok=True)
    for par in PARES:
        t = get(f"/tickers?symbol={par}")[0]
        doc = {
            "symbol": par,
            "price": float(t["lastPr"]),
            "high24h": float(t["high24h"]),
            "low24h": float(t["low24h"]),
            "change24h": float(t["change24h"]),
            "updatedAt": int(time.time()),
            "d1": velas(par, "1day", 365),
            "h4": velas(par, "4h", 180),
        }
        with open(os.path.join(dst, par + ".json"), "w") as f:
            json.dump(doc, f, separators=(",", ":"))
        print(par, doc["price"], len(doc["d1"]), len(doc["h4"]))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "datos")
