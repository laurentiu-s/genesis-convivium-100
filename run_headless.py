#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Laurentiu Stavaru
"""Run PROJECT GENESIS v26.11.5 without Google Colab and without the live dashboard server.

The script executes the code cells of the notebook in order, in a fresh Python process.
The only differences from "Runtime -> Run all" in Colab are:
  * the live HTTP dashboard (port 8771) is not started; the main world is advanced with the
    same step() function in a plain loop, which gives the same trajectory;
  * IPython's display() is replaced by a no-op.
Nothing in the simulation logic is changed.

Examples
    python run_headless.py                      # full reproduction: main run + 8-seed Policy Lab + exports
    python run_headless.py --lab-seeds 8:40 --lab-only --out out_ext   # extra Policy Lab seeds only
"""
import argparse, json, os, subprocess, sys

HEADER = '''import sys, types, time, platform
_ip = types.ModuleType("IPython"); _d = types.ModuleType("IPython.display")
_d.display = lambda *a, **k: None; _d.HTML = lambda *a, **k: None; _ip.display = _d
sys.modules.setdefault("IPython", _ip); sys.modules.setdefault("IPython.display", _d)
'''
MAIN_RUN = '''
cfg_live = Config(seed=42, use_llm=USE_COLAB_AI)
world_live = World(cfg_live); world_live._llm_budget = 24
_t0 = time.time(); w_main = run(world_live, cfg_live.years*12)
print("main run finished in", round(time.time() - _t0, 1), "s", w_main.milestones, flush=True)
Y = pd.DataFrame(w_main.yearly)
'''
FOOTER = '''
import numpy, pandas
json.dump(dict(python=platform.python_version(), numpy=numpy.__version__, pandas=pandas.__version__,
               platform=platform.platform()), open("environment.json", "w"), indent=1)
print("DONE", flush=True)
'''
LAB_ONLY_TAIL = '''
lab.to_csv("policy_lab_runs.csv", index=False); lab_yearly.to_csv("policy_lab_yearly.csv", index=False)
'''

def build_script(nb_path, lab_seeds=None, lab_only=False):
    nb = json.load(open(nb_path, encoding="utf-8"))
    parts = [HEADER]
    seen_lab = False
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        src = "".join(cell["source"])
        if "class LiveRunner" in src:                       # live dashboard cell: keep definitions, replace the server
            src = src.split("LIVE_PORT = ")[0] + ("" if lab_only else MAIN_RUN)
        elif src.lstrip().startswith("# Wait for the live century"):
            continue                                        # only prints progress of the live thread
        elif "def policy_lab(" in src:
            seen_lab = True
            if lab_seeds:
                a, b = lab_seeds
                assert "POLICY_SEEDS = range(8)" in src
                src = src.replace("POLICY_SEEDS = range(8)", f"POLICY_SEEDS = range({a}, {b})")
            if lab_only:
                src += LAB_ONLY_TAIL
        elif seen_lab and lab_only:
            continue                                        # symmetric-world check and final export need the main run
        parts.append(f"# ---- notebook cell {i}\n{src}\nprint('cell {i} ok', flush=True)\n")
    parts.append(FOOTER)
    return "\n".join(parts)

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--notebook", default=os.path.join(here, "PROJECT_GENESIS_v26.11.5.ipynb"))
    ap.add_argument("--out", default="run_output", help="working directory for outputs")
    ap.add_argument("--lab-seeds", default=None, help="A:B -> Policy Lab seeds range(A, B); default 0:8 as in the notebook")
    ap.add_argument("--lab-only", action="store_true", help="skip the seed-42 main run and the final export; write Policy Lab CSVs only")
    a = ap.parse_args()
    seeds = tuple(int(x) for x in a.lab_seeds.split(":")) if a.lab_seeds else None
    os.makedirs(a.out, exist_ok=True)
    script = os.path.join(a.out, "_genesis_headless_generated.py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(build_script(a.notebook, seeds, a.lab_only))
    sys.exit(subprocess.call([sys.executable, os.path.basename(script)], cwd=a.out))

if __name__ == "__main__":
    main()
