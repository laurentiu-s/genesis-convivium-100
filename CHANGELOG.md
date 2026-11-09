# Changelog

## v26.11.5 — publication release (2026-11-10)

Packaging of PROJECT GENESIS v26.11.5 for public release together with revision 5 of the
working paper. **The simulation logic is unchanged**: a full re-run of this repository
reproduces the reference results in `data/results_v26.11.5` exactly (see
`analysis/check_reproduction.py`).

Changed
- `src/build.py`: no hard-coded absolute path any more; builds from the folder it lives in.
- `src/part2.py`: the live dashboard (port 8771) and the Observatory file server (port 8772)
  now listen on `127.0.0.1` instead of all network interfaces. The dashboard's control
  endpoints (pause, intervene, restore checkpoint) have no authentication, so they should
  not be reachable from other machines.
- SPDX licence headers added to the Python sources.

Added
- `run_headless.py`: runs the notebook without Colab and without the live server.
- `analysis/make_figures.py`, `analysis/make_tables.py`, `analysis/check_reproduction.py`.
- `data/results_v26.11.5/`: the 13 CSV tables behind the paper, with checksums.
- `data/policy_lab_extended/`: final outcomes of the 40-seed Policy Lab (seeds 0–39).
- `figures/`, `paper/`, `observatory/`.
- `README.md`, `LICENSE`, `LICENSE-DATA-AND-TEXT.md`, `CITATION.cff`, `requirements.txt`.

Known issues (documented in the paper, Section 8; deliberately not fixed in this release so
that code and paper match)
- The coexistence index is multiplied by (1 − maximum species-conflict level of any single actor).
- Epistemic health saturates at its bounds; the biosphere index is bounded at 1.2, not 1.0.
- Persistent food shortfalls for the Gulf and Iran actors.
- The dashboard page loads two fonts from Google Fonts; offline it falls back to system fonts.
