"""
School Driver — solver design spike prototype (2026-08-31).

Grounded in the v1.0 BASELINE LOCKED artifacts of test-user-story-schooldriver:
  docs/requirements.md, docs/requirements/discovery.md

Implements, for the MVP scope:
  * Per-(school, shift, direction) runs (D-33, D-36: school identity is an output, not a driver attribute)
  * Selection-based eligibility (D-47: driver selected the (shift, direction))
  * Gender rule CR-21 (per-student sex match, AC-9 semantics)
  * Service-area rule CR-22 / D-43 (home zone AND school zone inside the driver's zone set)
  * Per-direction capacity D-34 / A-13
  * Same-day run compatibility CR-26 / D-37 (MIN_TURNAROUND_MINUTES = 30 config):
      - same school: raw non-overlap only (back-to-back valid, half-open per A-16)
      - different schools: B.start - A.end >= 2 * MIN_TURNAROUND_MINUTES
    Run time anchors (modeling note): to-school anchored at shift start S,
    from-school anchored at shift end E (D-39; reproduces the AC-7 fixture literally).
  * CR-19 flagged-student exclusion
  * CR-18 shortfall reporting channel (a skip decision per student/direction, never published as a plan)
  * Objective (D-21/D-45): ONE global solve minimizing total driving distance;
    additive per-stop surrogate -- to-school: leg(origin->school) once per driver-run (D-24)
    + per-student home->school; from-school: per-student school->home, no deadhead (D-39).
    All distances scaled to integers (CP-SAT integer arithmetic), SCALE = 100 (0.01 units).
  * Determinism + tie-breaks (D-45): stage 2 maximizes same-driver AM/PM continuity at
    zero distance cost; stage 3 realizes the stable lexicographic order of assignments
    via iterated fixing (cascade maximize, canonical order (school, shift, direction, student, driver)).

Verification (US-04 AC-4 meter): brute-force exhaustive enumeration on small random
instances; asserts (min distance, max continuity, lexicographic-min assignment) matches.

Usage:
  python school_solver.py --verify [--instances N] [--seed S]
  python school_solver.py --determinism
  python school_solver.py --demo            # 100/15/5/3
  python school_solver.py --scale           # NFR-01 reference-ish 500/50/10/2 (time-capped)
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import random
import sys
import time
from dataclasses import dataclass

from ortools.sat.python import cp_model

# ---------------------------------------------------------------- constants

TO_SCHOOL = 0
FROM_SCHOOL = 1
DIR_NAMES = {TO_SCHOOL: "to-school", FROM_SCHOOL: "from-school"}

SCALE = 100.0          # distance scale -> integer coefficients for CP-SAT
BIG_PENALTY = 10 ** 9  # per skipped student/direction (CR-18 report channel)


# ---------------------------------------------------------------- data model

@dataclass(frozen=True)
class School:
    sid: int
    x: float
    y: float
    zone: int


@dataclass(frozen=True)
class Shift:
    shid: int
    start: int   # minutes from midnight
    end: int


@dataclass(frozen=True)
class Student:
    pid: int
    school: int
    shift: int
    sex: int             # 0 = female, 1 = male
    home_zone: int
    sx: float
    sy: float
    flagged: bool = False  # CR-19


@dataclass(frozen=True)
class Driver:
    did: int
    sex: int
    zones: tuple          # D-43 multi-select
    cap: tuple            # (to_school_cap, from_school_cap) per direction run (D-34)
    ox: float
    oy: float
    selected: frozenset   # {(shift_id, direction)} (D-47; D-40: capability, not obligation)


@dataclass
class Run:
    rid: int
    school: int
    shift: int
    direction: int
    start: int            # anchor: to-school -> shift start S; from-school -> shift end E (D-39)
    end: int


@dataclass
class Instance:
    schools: dict
    shifts: dict
    students: list
    drivers: list
    runs: list
    turn_minutes: int = 30  # D-37 MVP value


# ---------------------------------------------------------------- geometry

def d2(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def dist_int(a, b):
    return int(round(d2(a, b) * SCALE))


# ---------------------------------------------------------------- eligibility

def eligible(inst: Instance, d: int, run: Run, s: Student) -> bool:
    """D-47 selection-based eligibility + CR-21 gender + CR-22/D-43 area."""
    drv = inst.drivers[d]
    if (run.shift, run.direction) not in drv.selected:
        return False
    if drv.sex != s.sex:                    # CR-21 / AC-9 (per-student sex match)
        return False
    sch = inst.schools[run.school]
    if s.home_zone not in drv.zones:        # CR-22 / D-43 (union-coverage reading)
        return False
    if sch.zone not in drv.zones:
        return False
    return True


def run_pair_incompatible(inst: Instance, r1: Run, r2: Run) -> bool:
    """CR-26 / D-37 static pair rule (order normalized by time)."""
    if r1.start > r2.start or (r1.start == r2.start and r1.rid > r2.rid):
        r1, r2 = r2, r1
    if r1.school == r2.school:
        # (iii) same school: only non-overlap; half-open, touching valid (A-16)
        return r1.end > r2.start
    # (ii) different schools: B.start - A.end >= 2 * T
    return r2.start - r1.end < 2 * inst.turn_minutes


# ---------------------------------------------------------------- instance gen

ZONES = 5          # D-43 predefined zones


def gen_instance(seed: int, n_students=5, n_drivers=3, n_schools=2, n_shifts=2,
                 rng_=None, jitter=0.33, dense=False):
    rng = rng_ if rng_ is not None else random.Random(seed)
    schools = {}
    for k in range(n_schools):
        schools[k] = School(k, rng.uniform(0, 100), rng.uniform(0, 100), rng.randrange(ZONES))
    shifts = {i: Shift(i, 420 + i * 300, 420 + (i + 1) * 300) for i in range(n_shifts)}
    students = []
    for i in range(n_students):
        sch = rng.randrange(n_schools)
        sh = rng.randrange(n_shifts)
        students.append(Student(
            pid=i, school=sch, shift=sh, sex=rng.randrange(2),
            home_zone=rng.randrange(ZONES),
            sx=rng.uniform(0, 100), sy=rng.uniform(0, 100),
            flagged=rng.random() < 0.2,       # CR-19
        ))
    drivers = []
    for d in range(n_drivers):
        if dense:
            zones = tuple(range(ZONES))                  # all zones
            nz_cap = (rng.randrange(3, 7), rng.randrange(3, 7))
            sel = frozenset((sh, dr) for sh in range(n_shifts)
                            for dr in (TO_SCHOOL, FROM_SCHOOL)
                            if rng.random() < 0.95)      # near-full availability
        else:
            nz = rng.randrange(1, ZONES + 1)
            zones = tuple(sorted(rng.sample(range(ZONES), nz)))
            sel = frozenset((sh, dr) for sh in range(n_shifts)
                            for dr in (TO_SCHOOL, FROM_SCHOOL)
                            if rng.random() < jitter + 0.4)
            nz_cap = (rng.randrange(2, 5), rng.randrange(2, 5))
        drivers.append(Driver(d, rng.randrange(2), zones, nz_cap,
                              rng.uniform(0, 100), rng.uniform(0, 100), sel))
    runs = []
    rid = 0
    for k in range(n_schools):
        for sh in range(n_shifts):
            for dr in (TO_SCHOOL, FROM_SCHOOL):
                S, E = shifts[sh].start, shifts[sh].end
                runs.append(Run(rid, k, sh, dr,
                                start=S if dr == TO_SCHOOL else E,
                                end=S if dr == TO_SCHOOL else E))
                rid += 1
    return Instance(schools=schools, shifts=shifts, students=students,
                    drivers=drivers, runs=runs)


# ---------------------------------------------------------------- costs (int)

def run_students(inst, run):
    return [s for s in inst.students if not s.flagged
            and s.school == run.school and s.shift == run.shift]


def leg_cost(inst, d: int, run: Run) -> int:
    """Driver positioning leg, paid ONCE per allocated driver-run (D-24, to-school only)."""
    if run.direction != TO_SCHOOL:
        return 0
    drv = inst.drivers[d]
    sch = inst.schools[run.school]
    return dist_int((drv.ox, drv.oy), (sch.x, sch.y))


def inc_cost(inst, d: int, run: Run, s: Student) -> int:
    """Per-student incremental distance (additive surrogate; scaled int)."""
    sch = inst.schools[run.school]
    if run.direction == TO_SCHOOL:
        return dist_int((s.sx, s.sy), (sch.x, sch.y))
    return dist_int((sch.x, sch.y), (s.sx, s.sy))


# ---------------------------------------------------------------- CP-SAT model

def canonical_key(inst, d, run, s):
    """Stable lexicographic order of assignments, D-45 tier 2:
    (school, shift, direction, student, driver)."""
    return (run.school, run.shift, run.direction, s.pid, d)


def build_model(inst, mode, fixes=None, dist_floor=None, cont_floor=None):
    """Build a fresh CpModel for one solve stage. Objective is NOT set here;
    the caller sets it (Minimize distance / Maximize continuity / Maximize single var)."""
    model = cp_model.CpModel()
    P = BIG_PENALTY

    x, y, z, c = {}, {}, {}, {}

    # --- variables -----------------------------------------------------
    for run in inst.runs:
        for s in run_students(inst, run):
            for d in range(len(inst.drivers)):
                if eligible(inst, d, run, s):
                    x[(d, run.rid, s.pid)] = model.NewBoolVar(
                        f"x_d{d}_r{run.rid}_s{s.pid}")
    for d in range(len(inst.drivers)):
        for run in inst.runs:
            y[(d, run.rid)] = model.NewBoolVar(f"y_d{d}_r{run.rid}")
    for s in inst.students:
        if s.flagged:
            continue
        for dr in (TO_SCHOOL, FROM_SCHOOL):
            z[(s.pid, dr)] = model.NewBoolVar(f"z_s{s.pid}_{dr}")
    for s in inst.students:
        if s.flagged:
            continue
        c[s.pid] = model.NewBoolVar(f"c_s{s.pid}")

    # --- assignment / shortfall (CR-18), capacity (D-34), y activation ----
    for run in inst.runs:
        for s in run_students(inst, run):
            xs = []
            for d in range(len(inst.drivers)):
                k = (d, run.rid, s.pid)
                if k in x:
                    xs.append(x[k])
                    model.AddImplication(x[k], y[(d, run.rid)])
            model.AddExactlyOne(xs + [z[(s.pid, run.direction)]])

    for d in range(len(inst.drivers)):
        for run in inst.runs:
            model.Add(
                sum(x[(d, run.rid, s.pid)] for s in run_students(inst, run)
                    if (d, run.rid, s.pid) in x) <= inst.drivers[d].cap[run.direction])

    # --- CR-26 pairwise compatibility (static clauses) ------------------
    for d in range(len(inst.drivers)):
        for r1, r2 in itertools.combinations(inst.runs, 2):
            if run_pair_incompatible(inst, r1, r2):
                model.Add(y[(d, r1.rid)] + y[(d, r2.rid)] <= 1)

    # --- continuity (D-45 tier 1): same driver for a student's AM+PM -----
    for s in inst.students:
        if s.flagged:
            continue
        r_to = next(r for r in inst.runs
                    if r.school == s.school and r.shift == s.shift
                    and r.direction == TO_SCHOOL)
        r_from = next(r for r in inst.runs
                      if r.school == s.school and r.shift == s.shift
                      and r.direction == FROM_SCHOOL)
        t = {}
        for d in range(len(inst.drivers)):
            k1 = (d, r_to.rid, s.pid)
            k2 = (d, r_from.rid, s.pid)
            if k1 in x and k2 in x:
                t[d] = model.NewBoolVar(f"t_d{d}_s{s.pid}")
                model.AddImplication(t[d], x[k1])
                model.AddImplication(t[d], x[k2])
                model.Add(t[d] >= x[k1] + x[k2] - 1)
        if t:
            model.AddMaxEquality(c[s.pid], list(t.values()))
        else:
            model.Add(c[s.pid] == 0)

    # --- stage-level constraints ----------------------------------------
    def dist_expr():
        terms = []
        for d in range(len(inst.drivers)):
            for run in inst.runs:
                terms.append(leg_cost(inst, d, run) * y[(d, run.rid)])
        for (d, rid, pid), xv in x.items():
            run = inst.runs[rid]
            s = inst.students[pid]
            terms.append(inc_cost(inst, d, run, s) * xv)
        for (pid, dr), zv in z.items():
            terms.append(P * zv)
        return sum(terms)

    if mode in ("continuity", "lex"):
        model.Add(dist_expr() == dist_floor)
    if mode == "lex":
        model.Add(sum(c[s.pid] for s in inst.students if not s.flagged) == cont_floor)
        for var, val in (fixes or {}).items():
            model.Add(var == val)

    return model, x, y, z, c


def solve_model(model, time_limit=60.0, seed=7, workers=4, log=False):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = seed
    solver.parameters.num_workers = workers
    solver.parameters.log_search_progress = log
    start = time.time()
    status = solver.Solve(model)
    return solver, status, time.time() - start


def full_solve(inst, time_limit=60.0, seed=7, workers=4, log=False, cascade=True):
    """3-stage exact solve: distance -> weighted lexicographic (dist, cont) -> lexicographic cascade.

    Stage A: minimize total distance (+ skip penalty).
    Stage B: minimize W*distance - continuity with W > n_students, which is
              provably equivalent to lexicographic (min distance, max continuity)
              — no distance unit is ever traded for a continuity point.
              (Faster than the dist==floor equality; the equality form
              made stage 2 time out on the 100-student demo.)
    Stage C: lexicographic cascade over the canonical assignment order (D-45 tier 2).
              Exact but O(#assignment-vars) sequential solves — used only for
              brute-force verification (small instances); skip with cascade=False
              for demo/scale runs (assignment then comes from stage B).

    Returns dict (dist, cont, skips, assign, stage times) or None if stage A
    is not solved (should not happen: all-skip is always feasible).
    """
    W = max(100000, 2 * len(inst.students) + 1)   # lexicographic weight

    def dist_expr(m, x, y, z):
        terms = []
        for d in range(len(inst.drivers)):
            for r in inst.runs:
                terms.append(leg_cost(inst, d, r) * y[(d, r.rid)])
        for (d, rid, pid), xv in x.items():
            terms.append(inc_cost(inst, d, inst.runs[rid], inst.students[pid]) * xv)
        for zv in z.values():
            terms.append(BIG_PENALTY * zv)
        return sum(terms)

    # stage A: distance
    m1, x1, y1, z1, c1 = build_model(inst, "distance")
    m1.Minimize(dist_expr(m1, x1, y1, z1))
    s1, st1, t1 = solve_model(m1, time_limit, seed, workers, log)
    if st1 not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    dist = round(s1.ObjectiveValue())            # round(): CP-SAT can return an ulp below int optimum
    skips1 = sum(int(s1.Value(zv)) for zv in z1.values())

    # stage B: weighted lexicographic (distance, continuity)
    m2, x2, y2, z2, c2 = build_model(inst, "distance")
    m2.Minimize(W * dist_expr(m2, x2, y2, z2) - sum(c2[s.pid] for s in inst.students if not s.flagged))
    s2, st2, t2 = solve_model(m2, time_limit, seed, workers, log)
    if st2 in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        objB = round(s2.ObjectiveValue())
        cont = W * dist - objB          # objB = W*dist* - cont*  ->  cont* = W*dist* - objB
    else:
        print(f"  [warning] stage-B status={s2.StatusName(st2)} — continuing "
              f"without the continuity tier", file=sys.stderr)
        cont = None

    # stage 3 (only when stage 2 resolved AND cascade requested):
    # lexicographic cascade (D-45 tier 2)
    fixes = {}
    t3 = 0.0
    if cont is not None and cascade:
        vars_by_key = {}
        for run in inst.runs:
            for s in run_students(inst, run):
                for d in range(len(inst.drivers)):
                    k = (d, run.rid, s.pid)
                    if k in x1:
                        vars_by_key[canonical_key(inst, d, run, s)] = x1[k]
        for ck in sorted(vars_by_key):
            var = vars_by_key[ck]
            m3, _, _, _, _ = build_model(inst, "lex", fixes=fixes,
                                         dist_floor=dist, cont_floor=cont)
            m3.Maximize(var)
            s3, st3, tt = solve_model(m3, time_limit, seed, workers, log)
            t3 += tt
            val = int(s3.Value(var)) if st3 in (cp_model.OPTIMAL, cp_model.FEASIBLE) else 0
            fixes[var] = val

    assign = {}
    if cascade and cont is not None:
        for run in inst.runs:
            for s in run_students(inst, run):
                for d in range(len(inst.drivers)):
                    k = (d, run.rid, s.pid)
                    if k in x1:
                        assign[k] = fixes.get(x1[k], 0)
    else:
        for run in inst.runs:
            for s in run_students(inst, run):
                for d in range(len(inst.drivers)):
                    k = (d, run.rid, s.pid)
                    if k in x1:
                        assign[k] = int(s2.Value(x2[k]))
    return {"dist": dist, "cont": cont, "skips": skips1, "assign": assign,
            "t1": t1, "t2": t2, "t3": t3, "st1": st1}


def solver_assignment_tuple(inst, assign):
    """Sorted canonical key tuple of assigned (x=1) entries — same
    representation as the brute-force enumerator."""
    out = []
    for (d, rid, pid), v in assign.items():
        if v == 1:
            run = inst.runs[rid]
            out.append(canonical_key(inst, d, run, inst.students[pid]))
    return tuple(sorted(out))


# ---------------------------------------------------------------- brute force

def brute_force(inst):
    """Exhaustive enumeration (US-04 AC-4 meter). Returns
    (dist, cont, sorted assignment tuple) — integer-scaled, or None if none.
    All-skip is always a candidate, so None never occurs in practice."""
    slots = []
    for run in inst.runs:
        for s in run_students(inst, run):
            slots.append((s, run.direction, run.rid))
    eligible_map = {}
    for (s, dr, rid) in slots:
        run = inst.runs[rid]
        eligible_map[(s.pid, dr)] = [d for d in range(len(inst.drivers))
                                     if eligible(inst, d, run, s)]

    best = None
    choices = [eligible_map[(s.pid, dr)] + [None] for (s, dr, _) in slots]

    def acceptable(state):
        used = {}
        for (s, dr, rid), d in zip(slots, state):
            if d is None:
                continue
            key = (d, rid)
            used[key] = used.get(key, 0) + 1
            if used[key] > inst.drivers[d].cap[dr]:
                return False
        for d in range(len(inst.drivers)):
            served = {rid for (s_, dr_, rid), dd in zip(slots, state) if dd == d}
            for (a, b) in itertools.combinations(sorted(served), 2):
                if run_pair_incompatible(inst, inst.runs[a], inst.runs[b]):
                    return False
        return True

    def evaluate(state):
        tot = BIG_PENALTY * sum(1 for (s, dr, rid), d in zip(slots, state) if d is None)
        # to-school positioning leg paid once per (driver, run) pair (D-24/D-39)
        for dd, rid in {(dd, rid) for (s, dr, rid), dd in zip(slots, state)
                        if dd is not None}:
            if inst.runs[rid].direction == TO_SCHOOL:
                tot += leg_cost(inst, dd, inst.runs[rid])
        for (s, dr, rid), d in zip(slots, state):
            if d is not None:
                tot += inc_cost(inst, d, inst.runs[rid], s)
        by_student = {}
        for (s, dr, rid), d in zip(slots, state):
            if d is not None:              # skipped slots never count (fix: None==None bug)
                by_student.setdefault(s.pid, {})[dr] = d
        cont = sum(1 for pid, m in by_student.items()
                   if TO_SCHOOL in m and FROM_SCHOOL in m
                   and m[TO_SCHOOL] == m[FROM_SCHOOL])
        out = []
        for (s, dr, rid), d in zip(slots, state):
            if d is not None:
                out.append(canonical_key(inst, d, inst.runs[rid], s))
        return tot, cont, tuple(sorted(out))

    for state in itertools.product(*choices):
        if not acceptable(state):
            continue
        tot, cont, out = evaluate(state)
        cand = (tot, -cont, out)   # maximize continuity among equal-distance plans (D-45)
        if best is None or cand < best:
            best = cand
    if best is None:
        return None
    return (best[0], -best[1], best[2])


# ---------------------------------------------------------------- verify

def run_verify(args):
    rng = random.Random(args.seed)
    n_ok = 0
    mismatches = []
    t0 = time.time()
    for i in range(args.instances):
        inst = gen_instance(rng.randrange(1 << 31),
                            n_students=rng.randrange(2, 5),
                            n_drivers=rng.randrange(2, 4),
                            n_schools=2, n_shifts=2)
        res = full_solve(inst, time_limit=10.0, seed=7)
        bf = brute_force(inst)
        if bf is None and res is None:
            n_ok += 1
            continue
        if res is None or bf is None:
            mismatches.append(i)
            continue
        d_ok = res["dist"] == bf[0]
        c_ok = res["cont"] == bf[1]
        a_ok = solver_assignment_tuple(inst, res["assign"]) == bf[2]
        if d_ok and c_ok and a_ok:
            n_ok += 1
        else:
            mismatches.append(i)
            print(f"instance {i}: MISMATCH dist {res['dist']} vs {bf[0]} | "
                  f"cont {res['cont']} vs {bf[1]} | assign {a_ok}")
            if args.debug:
                sol_assign = solver_assignment_tuple(inst, res["assign"])
                print("  solver assign:", sol_assign)
                print("  brute  assign:", bf[2])
                for s in inst.students:
                    print(f"  student {s.pid}: school={s.school} shift={s.shift} "
                          f"sex={s.sex} zone={s.home_zone} flagged={s.flagged} "
                          f"home=({s.sx:.1f},{s.sy:.1f})")
                for d, drv in enumerate(inst.drivers):
                    print(f"  driver {d}: sex={drv.sex} zones={drv.zones} cap={drv.cap} "
                          f"sel={sorted(drv.selected)} origin=({drv.ox:.1f},{drv.oy:.1f})")
    dt = time.time() - t0
    print(f"[verify] {args.instances} instances in {dt:.1f}s: {n_ok} exact matches, "
          f"{len(mismatches)} mismatches")
    if mismatches:
        print("  mismatching instance ids:", mismatches[:30])
        return 1
    return 0


def run_determinism(args):
    inst = gen_instance(12345, n_students=8, n_drivers=5, n_schools=3, n_shifts=2)
    r1 = full_solve(inst, time_limit=30.0, seed=7)
    r2 = full_solve(inst, time_limit=30.0, seed=7)
    h1 = hashlib.sha256(repr(solver_assignment_tuple(inst, r1["assign"])).encode()).hexdigest()[:12]
    h2 = hashlib.sha256(repr(solver_assignment_tuple(inst, r2["assign"])).encode()).hexdigest()[:12]
    same = (h1 == h2 and r1["dist"] == r2["dist"] and r1["cont"] == r2["cont"])
    print(f"[determinism] dist={r1['dist']} cont={r1['cont']} hash={h1} (unscaled {r1['dist']/SCALE:.2f})")
    print(f"[determinism] dist={r2['dist']} cont={r2['cont']} hash={h2}")
    print(f"[determinism] IDENTICAL: {same}")
    return 0 if same else 1


def run_demo(args):
    n_students, n_drivers, n_schools, n_shifts = 100, 15, 5, 3
    inst = gen_instance(20260831, n_students=n_students, n_drivers=n_drivers,
                        n_schools=n_schools, n_shifts=n_shifts, jitter=0.7)
    res = full_solve(inst, time_limit=args.time_limit, seed=7, log=args.verbose,
                     cascade=False)
    if res is None:
        print("[demo] NO SOLUTION within time limit")
        return 1
    print(f"[demo] students={n_students} drivers={n_drivers} schools={n_schools} shifts={n_shifts} (jitter=0.7)")
    print(f"[demo] total distance = {res['dist']/SCALE:.2f} | continuity = {res['cont']} | skips = {res['skips']}")
    print(f"[demo] stage times t1={res['t1']:.2f}s t2={res['t2']:.2f}s")
    return 0


def run_scale(args):
    n_students, n_drivers, n_schools, n_shifts = 500, args.scale_drivers, 10, 2
    inst = gen_instance(20260830, n_students=n_students, n_drivers=n_drivers,
                        n_schools=n_schools, n_shifts=n_shifts,
                        jitter=0.6, dense=args.dense)
    W = max(100000, 2 * len(inst.students) + 1)

    def dist_expr(m, x, y, z):
        terms = []
        for d in range(len(inst.drivers)):
            for r in inst.runs:
                terms.append(leg_cost(inst, d, r) * y[(d, r.rid)])
        for (d, rid, pid), xv in x.items():
            terms.append(inc_cost(inst, d, inst.runs[rid], inst.students[pid]) * xv)
        for zv in z.values():
            terms.append(BIG_PENALTY * zv)
        return sum(terms)

    # stage A: distance
    m, x, y, z, c = build_model(inst, "distance")
    m.Minimize(dist_expr(m, x, y, z))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.time_limit
    solver.parameters.random_seed = 7
    solver.parameters.num_workers = 8
    solver.parameters.log_search_progress = args.verbose
    t0 = time.time()
    status = solver.Solve(m)
    dt = time.time() - t0
    print(f"[scale] NFR-01 reference-ish dataset: {n_students} students / {n_drivers} drivers / "
          f"{n_schools} schools / {n_shifts} shifts")
    print(f"[scale] model size: {len(x)} assignment vars, {len(y)} run vars, {len(z)} skip vars")
    print(f"[scale] stage A status={solver.StatusName(status)} time={dt:.1f}s (limit {args.time_limit}s)")
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        distA = round(solver.ObjectiveValue())
        boundA = solver.BestObjectiveBound()
        print(f"[scale] stage A objective={distA / SCALE:.2f} (unscaled) | best_bound={boundA / SCALE:.2f} | "
              f"gap={100 * abs(distA - boundA) / max(1, abs(distA)):.4f}%")
        skips = sum(int(solver.Value(zv)) for zv in z.values())
        print(f"[scale] unassigned student-directions (CR-18 shortfall channel) = {skips}")
    if status != cp_model.OPTIMAL:
        print(f"[scale] note: stage A not proven optimal within the cap; "
              f"continuity tier not attempted (NFR-01 spirit: gap/abort reporting)")
        return 0 if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else 1
    # stage B: weighted lexicographic (distance, continuity) — fresh solve
    m2, x2, y2, z2, c2 = build_model(inst, "distance")
    m2.Minimize(W * dist_expr(m2, x2, y2, z2)
                - sum(c2[s.pid] for s in inst.students if not s.flagged))
    solver2 = cp_model.CpSolver()
    solver2.parameters.max_time_in_seconds = args.time_limit
    solver2.parameters.random_seed = 7
    solver2.parameters.num_workers = 8
    solver2.parameters.log_search_progress = args.verbose
    t0b = time.time()
    status2 = solver2.Solve(m2)
    dtb = time.time() - t0b
    print(f"[scale] stage B status={solver2.StatusName(status2)} time={dtb:.1f}s (limit {args.time_limit}s)")
    if status2 in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        objB = round(solver2.ObjectiveValue())
        cont = W * distA - objB if status2 == cp_model.OPTIMAL else None
        if status2 == cp_model.OPTIMAL:
            print(f"[scale] continuity (same-driver AM/PM students, D-45 tier 1) = {cont} of "
                  f"{sum(1 for s in inst.students if not s.flagged)}")
        boundB = solver2.BestObjectiveBound()
        print(f"[scale] stage B objective={objB / SCALE:.2f} (unscaled) | "
              f"gap={100 * abs(objB - boundB) / max(1, abs(objB)):.4f}%")
    return 0


def main():
    ap = argparse.ArgumentParser(description="School-driver solver spike prototype")
    ap.add_argument("--verify", action="store_true",
                    help="brute-force exactness verification (US-04 AC-4 meter)")
    ap.add_argument("--instances", type=int, default=120)
    ap.add_argument("--seed", type=int, default=20260831)
    ap.add_argument("--determinism", action="store_true",
                    help="D-45 determinism check (same input -> same report)")
    ap.add_argument("--demo", action="store_true", help="medium demo (100/15/5/3)")
    ap.add_argument("--scale", action="store_true",
                    help="reference-scale instance (500/50/10/2, time-capped)")
    ap.add_argument("--dense", action="store_true",
                    help="scale: feasibility-dense drivers (all zones, generous caps) — "
                         "the NFR-01-style reference test; default is a tight shortfall instance")
    ap.add_argument("--scale-drivers", type=int, default=50,
                    help="number of drivers for the --scale instance (default 50; "
                         "use ~80 with --dense for a fully feasible 500-student test)")
    ap.add_argument("--time-limit", type=float, default=240.0,
                    help="solver time cap per solve (s)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--debug", action="store_true", help="dump details on mismatches")
    args = ap.parse_args()

    if args.verify:
        sys.exit(run_verify(args))
    if args.determinism:
        sys.exit(run_determinism(args))
    if args.demo:
        sys.exit(run_demo(args))
    if args.scale:
        sys.exit(run_scale(args))
    ap.print_help()


if __name__ == "__main__":
    main()