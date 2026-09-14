"""Models of digit similarity, fit to the class's own ratings (AS.200.313, Week 3).

Two theories of similarity meet one dataset. Tversky (1977) says similarity is a
contrast of feature sets: shared features add, distinctive features subtract,
and the two directions of a comparison can differ. Shepard (1987) says stimuli
sit in a metric space and similarity falls off exponentially with distance.
Here both read from the same table of digit features, so what differs is the
functional form, not the representation.

The module is the code; the notebook beside it is the narrative. It is written
so that the feature table can be edited in one place and everything downstream
follows.

    import digitmodels as dm
    df  = dm.load_ratings()                 # class CSV (local file, else the fixed copy on honeylab.org)
    M   = dm.rating_matrix(df)              # 10 x 10 mean ratings, NaN on the diagonal
    ctx = dm.Context(dm.DEFAULT_FEATURES)   # feature table -> distances and set counts
    fit = dm.fit(dm.MODELS["tversky"], M, ctx)
    cv  = dm.cross_validate(dm.MODELS.values(), df, ctx)

Ratings are on a 1..7 scale, 7 = extremely similar. A rating row is
(name, trial, a, b, rating, rt_ms, ts, strategy), where the screen asked
"How similar is a to b?", so a is the subject and b the referent.
"""

from __future__ import annotations

import io
import os
import warnings
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd
from scipy.optimize import minimize

DIGITS = np.arange(10)
SCALE_MIN, SCALE_MAX = 1, 7
STRATEGIES = ("magnitude", "arithmetic", "shape", "mixed")

FROZEN_URL = "https://www.honeylab.org/mmb2026/data/digit-similarity-2026.csv"   # the class CSV, copied up once
LIVE_URL = "https://mmb.honeylab.org/export.csv"        # the intake server; only read if asked for explicitly
COLUMNS = ["name", "trial", "a", "b", "rating", "rt_ms", "ts", "strategy"]

# ------------------------------------------------------------------ features --

# Each feature names the set of digits that have it. Edit or extend this table
# and every model downstream sees the change. The three magnitude thresholds
# are "thermometer" coding: the number of thresholds two digits disagree on is
# a coarse version of how far apart they are.
DEFAULT_FEATURES: dict[str, set[int]] = {
    "magnitude >= 3": {3, 4, 5, 6, 7, 8, 9},
    "magnitude >= 5": {5, 6, 7, 8, 9},
    "magnitude >= 7": {7, 8, 9},
    "even": {0, 2, 4, 6, 8},
    "prime": {2, 3, 5, 7},
    "perfect square": {0, 1, 4, 9},
    "multiple of 3": {0, 3, 6, 9},
    "power of 2": {1, 2, 4, 8},
    "closed loop in the numeral": {0, 6, 8, 9},
    "curved stroke in the numeral": {0, 2, 3, 5, 6, 8, 9},
    "straight strokes only": {1, 4, 7},
}


def feature_matrix(features: dict[str, Iterable[int]] = DEFAULT_FEATURES) -> tuple[np.ndarray, list[str]]:
    """10 x k boolean matrix and the feature names, in table order."""
    names = list(features)
    F = np.zeros((10, len(names)), dtype=bool)
    for j, name in enumerate(names):
        members = set(int(d) for d in features[name])
        bad = members - set(DIGITS.tolist())
        if bad:
            raise ValueError(f"feature {name!r} lists non-digits {sorted(bad)}")
        F[sorted(members), j] = True
    return F, names


def feature_table(features: dict[str, Iterable[int]] = DEFAULT_FEATURES) -> pd.DataFrame:
    """The feature table as a DataFrame, digits as columns, for display."""
    F, names = feature_matrix(features)
    return pd.DataFrame(F.T.astype(int), index=names, columns=[str(d) for d in DIGITS])


class Context:
    """Everything a model needs, precomputed from the feature table.

    All arrays are 10 x 10, indexed [a, b] with a the subject of the comparison.
    """

    def __init__(self, features: dict[str, Iterable[int]] = DEFAULT_FEATURES):
        self.F, self.names = feature_matrix(features)
        F = self.F.astype(float)
        self.common = F @ F.T                                   # f(A ∩ B)
        self.a_not_b = F @ (1 - F).T                            # f(A − B)
        self.b_not_a = self.a_not_b.T                           # f(B − A)
        self.d_city = self.a_not_b + self.b_not_a               # city-block on binary features
        self.d_euclid = np.sqrt(self.d_city)                    # Euclidean on binary features
        self.absdiff = np.abs(DIGITS[:, None] - DIGITS[None, :]).astype(float)
        self.mismatch = (F[:, None, :] != F[None, :, :]).astype(float)   # 10x10xk

    @property
    def k(self) -> int:
        return self.F.shape[1]


# -------------------------------------------------------------------- models --

@dataclass(frozen=True)
class Model:
    name: str
    params: tuple[str, ...]
    predict: Callable[[np.ndarray, Context], np.ndarray]    # params, ctx -> 10 x 10 rating
    p0: tuple[float, ...]
    note: str = ""
    bounds: tuple[tuple[float | None, float | None], ...] | None = None

    @property
    def n_params(self) -> int:
        return len(self.params)


def _decay(kind: str):
    if kind == "exp":
        return lambda d, c: np.exp(-c * d)
    if kind == "gauss":
        return lambda d, c: np.exp(-c * d ** 2)
    raise ValueError(kind)


def _distance_model(name: str, dist: str, kind: str, note: str) -> Model:
    g = _decay(kind)

    def predict(p, ctx):
        c, k, b0 = p
        return b0 + k * g(getattr(ctx, dist), c)

    # Bounds keep predictions on the 1..7 scale (b0 is the rating at infinite
    # distance, b0 + k the rating at zero distance) and stop the exponential
    # from imitating a straight line (c → 0, k → ∞).
    return Model(name, ("c", "k", "b0"), predict, (0.5, 5.0, 1.0), note,
                 bounds=((0.02, 10.0), (0.0, 6.0), (1.0, 7.0)))


def _tversky_contrast(p, ctx):
    b0, theta, alpha, beta = p
    return b0 + theta * ctx.common - alpha * ctx.a_not_b - beta * ctx.b_not_a


def _tversky_symmetric(p, ctx):
    b0, theta, alpha = p
    return b0 + theta * ctx.common - alpha * (ctx.a_not_b + ctx.b_not_a)


def _tversky_ratio(p, ctx):
    b0, k, alpha, beta = p
    num = ctx.common
    den = num + alpha * ctx.a_not_b + beta * ctx.b_not_a
    with np.errstate(invalid="ignore", divide="ignore"):
        s = np.where(den > 0, num / den, 0.0)
    return b0 + k * s


MODELS: dict[str, Model] = {
    "number line (exp)": _distance_model(
        "number line (exp)", "absdiff", "exp",
        "rating = b0 + k·exp(−c·|a−b|). Magnitude only, Shepard's decay."),
    "number line (gauss)": _distance_model(
        "number line (gauss)", "absdiff", "gauss",
        "rating = b0 + k·exp(−c·|a−b|²). Magnitude only, Gaussian decay."),
    "shepard features (city-block, exp)": _distance_model(
        "shepard features (city-block, exp)", "d_city", "exp",
        "rating = b0 + k·exp(−c·d), d = number of features the digits disagree on."),
    "shepard features (city-block, gauss)": _distance_model(
        "shepard features (city-block, gauss)", "d_city", "gauss",
        "Same distance, Gaussian decay."),
    "shepard features (euclidean, exp)": _distance_model(
        "shepard features (euclidean, exp)", "d_euclid", "exp",
        "Euclidean distance on binary features is √(city-block)."),
    "tversky symmetric": Model(
        "tversky symmetric", ("b0", "theta", "alpha"), _tversky_symmetric, (1.0, 0.5, 0.5),
        "rating = b0 + θ·f(A∩B) − α·[f(A−B) + f(B−A)]. Linear in city-block distance, plus common features."),
    "tversky": Model(
        "tversky", ("b0", "theta", "alpha", "beta"), _tversky_contrast, (1.0, 0.5, 0.5, 0.5),
        "rating = b0 + θ·f(A∩B) − α·f(A−B) − β·f(B−A). α ≠ β gives asymmetry."),
    "tversky ratio": Model(
        "tversky ratio", ("b0", "k", "alpha", "beta"), _tversky_ratio, (1.0, 5.0, 1.0, 1.0),
        "rating = b0 + k·f(A∩B) / [f(A∩B) + α·f(A−B) + β·f(B−A)]. Bounded, like the scale.",
        bounds=((1.0, 7.0), (0.0, 6.0), (0.0, 20.0), (0.0, 20.0))),
}

# The comparison ladder: each step adds one idea, and one parameter.
LADDER = [
    "number line (exp)",
    "shepard features (city-block, exp)",
    "tversky symmetric",
    "tversky",
]


# ---------------------------------------------------------------------- data --

def load_ratings(source: str | os.PathLike | None = None, since: str | None = None) -> pd.DataFrame:
    """Load the class ratings as a DataFrame with the eight CSV columns.

    source: a path, a URL, or None. None tries, in order: the MMB_RATINGS
    environment variable, ./ratings.csv, then the fixed copy of the class CSV
    on honeylab.org (which is what Colab uses). The live intake server is
    never read unless passed as the source. since="YYYY-MM-DD" drops rows
    stamped before that UTC date.
    """
    if source is None:
        env = os.environ.get("MMB_RATINGS")
        candidates = [env] if env else []
        candidates += [Path("ratings.csv"), FROZEN_URL]
        errors = []
        for cand in candidates:
            try:
                df = _read(cand)
                break
            except Exception as e:                       # noqa: BLE001 - try the next source
                errors.append(f"{cand}: {e}")
        else:
            raise FileNotFoundError("no ratings found; tried\n  " + "\n  ".join(errors)
                                    + "\nUse simulate() for a dry run.")
    else:
        df = _read(source)
    return _clean(df, since)


def _read(source) -> pd.DataFrame:
    s = str(source)
    if s.startswith("http://") or s.startswith("https://"):
        text = urllib.request.urlopen(s, timeout=15).read().decode()
        return pd.read_csv(io.StringIO(text))
    p = Path(source)
    if not p.exists():
        raise FileNotFoundError(p)
    return pd.read_csv(p)


def _clean(df: pd.DataFrame, since: str | None) -> pd.DataFrame:
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"ratings file lacks columns {missing}")
    df = df[COLUMNS].copy()
    df["strategy"] = df["strategy"].fillna("").astype(str)
    df["ts"] = df["ts"].astype(str)
    if since:
        df = df[df["ts"].str[:10] >= since]
    for c in ("trial", "a", "b", "rating", "rt_ms"):
        df[c] = df[c].astype(int)
    # The server already keeps the latest row per (name, trial); repeat that here
    # in case a file was concatenated by hand.
    df = df.sort_values("ts").drop_duplicates(["name", "trial"], keep="last")
    df = df[(df["a"] != df["b"]) & df["rating"].between(SCALE_MIN, SCALE_MAX)]
    return df.sort_values(["name", "trial"]).reset_index(drop=True)


def summary(df: pd.DataFrame) -> dict:
    per = df.groupby("name").size()
    return {
        "participants": int(per.size),
        "complete": int((per >= 90).sum()),
        "ratings": int(len(df)),
        "strategies": df.drop_duplicates("name")["strategy"].replace("", "none").value_counts().to_dict(),
    }


def rating_matrix(df: pd.DataFrame, names: Iterable[str] | None = None) -> np.ndarray:
    """10 x 10 mean rating, [a, b] = "how similar is a to b". NaN where unrated."""
    if names is not None:
        df = df[df["name"].isin(set(names))]
    M = np.full((10, 10), np.nan)
    g = df.groupby(["a", "b"])["rating"].mean()
    for (a, b), v in g.items():
        M[a, b] = v
    return M


def participant_matrices(df: pd.DataFrame) -> dict[str, np.ndarray]:
    return {n: rating_matrix(sub) for n, sub in df.groupby("name")}


def strategy_of(df: pd.DataFrame) -> dict[str, str]:
    """name -> self-reported strategy ('' if the survey was skipped)."""
    return df.drop_duplicates("name").set_index("name")["strategy"].to_dict()


def strategy_matrices(df: pd.DataFrame) -> dict[str, tuple[np.ndarray, int]]:
    """strategy -> (class matrix for that group, number of participants)."""
    out, by = {}, {}
    for name, strat in strategy_of(df).items():
        by.setdefault(strat or "none", []).append(name)
    for strat, names in sorted(by.items()):
        out[strat] = (rating_matrix(df, names), len(names))
    return out


def symmetrize(M: np.ndarray) -> np.ndarray:
    return (M + M.T) / 2


def offdiag(M: np.ndarray) -> np.ndarray:
    """The 90 ordered-pair entries as a vector, row-major, diagonal skipped."""
    return M[~np.eye(10, dtype=bool)]


# ------------------------------------------------------------------- fitting --

def r2(pred: np.ndarray, obs: np.ndarray) -> float:
    """Variance explained, over the entries where obs is defined."""
    mask = ~np.isnan(obs) & ~np.eye(10, dtype=bool)
    y, yhat = obs[mask], pred[mask]
    sst = np.sum((y - y.mean()) ** 2)
    return float(1 - np.sum((y - yhat) ** 2) / sst) if sst > 0 else float("nan")


def aic(sse: float, n: int, k: int) -> float:
    """Gaussian-likelihood AIC up to a constant: n·ln(SSE/n) + 2k."""
    return float(n * np.log(sse / n) + 2 * k)


@dataclass
class Fit:
    model: Model
    params: np.ndarray
    predicted: np.ndarray
    sse: float
    n: int
    r2: float

    @property
    def aic(self) -> float:
        return aic(self.sse, self.n, self.model.n_params)

    def as_dict(self) -> dict:
        d = {"model": self.model.name, "params": self.model.n_params,
             "train R²": round(self.r2, 3), "AIC": round(self.aic, 1)}
        d.update({p: round(float(v), 3) for p, v in zip(self.model.params, self.params)})
        return d


def fit(model: Model, target: np.ndarray, ctx: Context, restarts: int = 4,
        rng: np.random.Generator | None = None) -> Fit:
    """Least-squares fit of one model to a 10 x 10 target matrix.

    The loss is the summed squared error over every rated ordered pair, and the
    minimiser is Nelder–Mead from a few starting points, within the model's
    parameter bounds if it has any. This is the same machinery as the MDS
    tutorial, applied to a different objective.
    """
    rng = rng or np.random.default_rng(0)
    mask = ~np.isnan(target) & ~np.eye(10, dtype=bool)
    y = target[mask]

    def loss(p):
        return float(np.sum((model.predict(p, ctx)[mask] - y) ** 2))

    p0 = np.array(model.p0, dtype=float)
    starts = [p0] + [p0 * rng.uniform(0.3, 2.0, p0.size) for _ in range(restarts)]
    best = None
    for s in starts:
        res = minimize(loss, s, method="Nelder-Mead", bounds=model.bounds,
                       options={"maxiter": 20_000, "maxfev": 20_000, "xatol": 1e-7, "fatol": 1e-9})
        if best is None or res.fun < best.fun:
            best = res
    pred = model.predict(best.x, ctx)
    return Fit(model, best.x, pred, float(best.fun), int(mask.sum()), r2(pred, target))


def fit_all(models: Iterable[Model], target: np.ndarray, ctx: Context) -> pd.DataFrame:
    fits = [fit(m, target, ctx) for m in models]
    return pd.DataFrame([f.as_dict() for f in fits]).set_index("model")


def cross_validate(models: Iterable[Model], df: pd.DataFrame, ctx: Context,
                   n_splits: int = 20, rng: np.random.Generator | None = None) -> pd.DataFrame:
    """Split the participants in half, fit on one half's mean matrix, score on the other's.

    Returns one row per model with mean and sd of held-out R² across splits, plus
    two reference rows. "other half, as-is" uses the training half's matrix
    itself as the prediction; a model can beat it, because ten people's means
    are noisy and a model smooths that noise. "ceiling" is the split-half
    correlation r: if each half is truth plus independent noise, a perfect
    model of the truth scores R² = r on a half, so no model should sit above it.
    """
    rng = rng or np.random.default_rng(1)
    models = list(models)
    names = np.array(sorted(df["name"].unique()))
    if names.size < 4:
        raise ValueError("need at least four participants to split in half")
    scores = {m.name: [] for m in models}
    train_scores = {m.name: [] for m in models}
    asis, ceiling = [], []
    for _ in range(n_splits):
        perm = rng.permutation(names)
        half = names.size // 2
        A = rating_matrix(df, perm[:half])
        B = rating_matrix(df, perm[half:])
        asis.append(r2(A, B))
        a, b = offdiag(A), offdiag(B)
        ok = ~np.isnan(a) & ~np.isnan(b)
        ceiling.append(np.corrcoef(a[ok], b[ok])[0, 1])
        for m in models:
            f = fit(m, A, ctx, restarts=1, rng=rng)
            train_scores[m.name].append(f.r2)
            scores[m.name].append(r2(f.predicted, B))
    rows = [{"model": m.name, "params": m.n_params,
             "train R²": np.mean(train_scores[m.name]),
             "held-out R²": np.mean(scores[m.name]),
             "sd": np.std(scores[m.name])} for m in models]
    rows.append({"model": "other half, as-is", "params": 0,
                 "train R²": np.nan, "held-out R²": np.mean(asis), "sd": np.std(asis)})
    rows.append({"model": "ceiling (split-half r)", "params": 0,
                 "train R²": np.nan, "held-out R²": np.mean(ceiling), "sd": np.std(ceiling)})
    return pd.DataFrame(rows).set_index("model")


def split_half_reliability(df: pd.DataFrame, n_splits: int = 200,
                           rng: np.random.Generator | None = None) -> float:
    """Mean correlation between the class matrices of two random halves of the class."""
    rng = rng or np.random.default_rng(2)
    names = np.array(sorted(df["name"].unique()))
    rs = []
    for _ in range(n_splits):
        perm = rng.permutation(names)
        A, B = rating_matrix(df, perm[:names.size // 2]), rating_matrix(df, perm[names.size // 2:])
        a, b = offdiag(A), offdiag(B)
        ok = ~np.isnan(a) & ~np.isnan(b)
        rs.append(np.corrcoef(a[ok], b[ok])[0, 1])
    return float(np.mean(rs))


def feature_weights(target: np.ndarray, ctx: Context) -> pd.DataFrame:
    """Which features carry the similarity judgement?

    Ordinary least squares of the rating on one indicator per feature: 1 when
    the two digits disagree on it. A large negative weight means disagreeing on
    that feature costs a lot of similarity. With ~11 features and 90 ratings
    this is descriptive, not a test.
    """
    mask = ~np.isnan(target) & ~np.eye(10, dtype=bool)
    X = np.column_stack([np.ones(mask.sum()), ctx.mismatch[mask]])
    w, *_ = np.linalg.lstsq(X, target[mask], rcond=None)
    pred = np.full((10, 10), np.nan)
    pred[mask] = X @ w
    out = pd.DataFrame({"weight": w[1:]}, index=ctx.names).sort_values("weight")
    out.attrs["intercept"] = float(w[0])
    out.attrs["r2"] = r2(pred, target)
    return out


# ----------------------------------------------------------------- asymmetry --

def asymmetry_table(M: np.ndarray) -> pd.DataFrame:
    """One row per unordered pair: S(a→b), S(b→a) and their difference."""
    rows = []
    for a in DIGITS:
        for b in DIGITS:
            if a < b:
                rows.append({"a": a, "b": b, "S(a→b)": M[a, b], "S(b→a)": M[b, a],
                             "diff": M[a, b] - M[b, a]})
    return pd.DataFrame(rows)


def prototype_scores(M: np.ndarray) -> pd.Series:
    """For each digit p, mean over x of S(x→p) − S(p→x).

    Tversky: the variant is more similar to the prototype than the prototype
    is to the variant. A positive score means other digits are judged more
    similar *to* p than p is to them, so p is acting as a reference point.
    """
    diff = M.T - M                         # [p, x] = S(x→p) − S(p→x)
    return pd.Series(np.nanmean(diff, axis=1), index=[str(d) for d in DIGITS], name="prototype score")


def asymmetry_test(df: pd.DataFrame, n_perm: int = 1000,
                   rng: np.random.Generator | None = None) -> dict:
    """Permutation test of the largest |prototype score|.

    Null: order carries no information, so each participant's two ratings of
    a pair are exchangeable. Swap them at random within participant, recompute
    the class matrix, and see how often chance beats the observed maximum.
    """
    rng = rng or np.random.default_rng(3)
    M = rating_matrix(df)
    observed = prototype_scores(M).abs().max()
    key = df[["name", "a", "b"]].copy()
    lo, hi = np.minimum(key["a"], key["b"]), np.maximum(key["a"], key["b"])
    pair_id = key["name"].astype("category").cat.codes.to_numpy() * 100 + lo.to_numpy() * 10 + hi.to_numpy()
    a, b, r = df["a"].to_numpy(), df["b"].to_numpy(), df["rating"].to_numpy(float)
    count = 0
    for _ in range(n_perm):
        flip = rng.random(pair_id.max() + 1) < 0.5
        sw = flip[pair_id]
        aa, bb = np.where(sw, b, a), np.where(sw, a, b)
        Mp = np.full((10, 10), np.nan)
        sums = np.zeros((10, 10)); cnt = np.zeros((10, 10))
        np.add.at(sums, (aa, bb), r); np.add.at(cnt, (aa, bb), 1)
        with np.errstate(invalid="ignore"):
            Mp = np.where(cnt > 0, sums / cnt, np.nan)
        if prototype_scores(Mp).abs().max() >= observed:
            count += 1
    return {"max |prototype score|": float(observed), "p": (count + 1) / (n_perm + 1)}


# --------------------------------------------------- dissimilarity and MDS --

def to_dissimilarity(M: np.ndarray, how: str = "linear") -> np.ndarray:
    """Turn mean similarity into a dissimilarity matrix, diagonal 0.

    "linear": d = 7 − s.  "log": d = −ln(s / 7), which is what Shepard's law
    implies if s ∝ exp(−d). The two disagree about the far end of the scale.
    """
    S = symmetrize(M).copy()
    np.fill_diagonal(S, SCALE_MAX)
    if how == "linear":
        D = SCALE_MAX - S
    elif how == "log":
        D = -np.log(S / SCALE_MAX)
    else:
        raise ValueError(how)
    np.fill_diagonal(D, 0.0)
    return D


def triangle_violations(D: np.ndarray, tol: float = 1e-9) -> tuple[int, int]:
    """(violations, triples): how often d(i,k) > d(i,j) + d(j,k) over ordered triples."""
    n = D.shape[0]
    v = t = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    t += 1
                    if D[i, k] > D[i, j] + D[j, k] + tol:
                        v += 1
    return v, t


def classical_mds(D: np.ndarray, dims: int = 2) -> tuple[np.ndarray, np.ndarray]:
    """Torgerson's classical MDS: coordinates (n x dims) and all eigenvalues (for a scree plot)."""
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    vals, vecs = np.linalg.eigh(B)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    X = vecs[:, :dims] * np.sqrt(np.clip(vals[:dims], 0, None))
    return X, vals


def nonmetric_mds(D: np.ndarray, dims: int = 2, seed: int = 0) -> tuple[np.ndarray, float]:
    """Kruskal's non-metric MDS via scikit-learn; returns coordinates and stress."""
    from sklearn.manifold import MDS
    m = MDS(n_components=dims, metric=False, dissimilarity="precomputed",
            random_state=seed, n_init=8, normalized_stress="auto")
    X = m.fit_transform(D)
    return X, float(m.stress_)


# ------------------------------------------------------------ response time --

def distance_effect(df: pd.DataFrame) -> pd.DataFrame:
    """Median response time per participant, averaged, as a function of |a − b|.

    Moyer & Landauer (1967): comparing two digits is faster when they are
    farther apart in magnitude. If it shows up here, it is evidence that the
    magnitude axis of the map is real, from a source other than the ratings.
    """
    d = df[df["rt_ms"] > 0].copy()
    d["absdiff"] = (d["a"] - d["b"]).abs()
    per = d.groupby(["name", "absdiff"])["rt_ms"].median().reset_index()
    return per.groupby("absdiff")["rt_ms"].agg(["mean", "sem", "count"])


# ---------------------------------------------------------------- simulation --

def simulate(n_participants: int = 20, features: dict[str, Iterable[int]] = DEFAULT_FEATURES,
             noise: float = 0.6, asymmetry: float = 0.4, rng: np.random.Generator | None = None,
             ts: str = "2026-09-08T14:00:00+00:00") -> pd.DataFrame:
    """A class that never met: ratings from a known mixture of the two theories.

    Each simulated student blends a number-line term with a Tversky contrast on
    the feature table; the blend depends on their (assigned) strategy, and the
    contrast is asymmetric by `asymmetry` (α − β), which makes feature-rich
    digits act as reference points, as Tversky predicts for prototypes.
    Ratings are rounded to the 1..7 scale with Gaussian
    noise; the default noise gives each simulated student about the
    order-to-order consistency the real class showed. Response times carry a small distance effect. The output has the
    same columns as the class CSV, so every function here accepts it.
    """
    rng = rng or np.random.default_rng(2026)
    ctx = Context(features)
    strategies = rng.choice(STRATEGIES, size=n_participants, p=[0.4, 0.2, 0.2, 0.2])
    weight = {"magnitude": 0.85, "arithmetic": 0.45, "shape": 0.25, "mixed": 0.55}
    line = np.exp(-0.45 * ctx.absdiff)
    contrast = 0.35 * ctx.common - (0.25 + asymmetry / 2) * ctx.a_not_b - (0.25 - asymmetry / 2) * ctx.b_not_a
    contrast = (contrast - contrast.min()) / (contrast.max() - contrast.min())
    rows = []
    pairs = [(a, b) for a in DIGITS for b in DIGITS if a != b]
    for i in range(n_participants):
        name = f"Sim {i:02d}"
        w = weight[strategies[i]]
        base = w * line + (1 - w) * contrast
        mu = SCALE_MIN + (SCALE_MAX - SCALE_MIN) * base
        order = rng.permutation(len(pairs))
        for trial, idx in enumerate(order, start=1):
            a, b = pairs[idx]
            rating = int(np.clip(np.rint(mu[a, b] + rng.normal(0, noise)), SCALE_MIN, SCALE_MAX))
            rt = int(max(300, rng.normal(1500 - 45 * abs(a - b), 250)))
            rows.append({"name": name, "trial": trial, "a": int(a), "b": int(b), "rating": rating,
                         "rt_ms": rt, "ts": ts, "strategy": strategies[i]})
    return pd.DataFrame(rows, columns=COLUMNS)


# ------------------------------------------------------------------ data QA --

def order_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """One row per student: does their rating of (a, b) predict their rating of (b, a)?

    Every student rated every pair in both orders, so the two orders are a
    built-in repeat. A student who is answering the question should agree
    with themselves; one who is pressing keys will not.
    """
    iu = np.triu_indices(10, 1)
    rows = []
    for name, P in participant_matrices(df).items():
        x, y = P[iu], P.T[iu]
        ok = ~np.isnan(x) & ~np.isnan(y)
        sub = df[df["name"] == name]
        rows.append({"name": name,
                     "ratings": len(sub),
                     "order r": np.corrcoef(x[ok], y[ok])[0, 1] if ok.sum() > 2 else np.nan,
                     "levels used": sub["rating"].nunique(),
                     "median rt (ms)": sub["rt_ms"].median(),
                     "strategy": sub["strategy"].iloc[0] or "none"})
    return pd.DataFrame(rows).set_index("name").sort_values("order r")


def exclude(df: pd.DataFrame, names: Iterable[str]) -> pd.DataFrame:
    """The ratings without the named students."""
    names = set(names)
    return df[~df["name"].isin(names)].reset_index(drop=True)


# ---------------------------------------------------------------- subgroups --

def student_vectors(df: pd.DataFrame) -> pd.DataFrame:
    """One row per student, one column per unordered pair: their mean rating of it."""
    iu = np.triu_indices(10, 1)
    cols = [f"{a}-{b}" for a, b in zip(*iu)]
    return pd.DataFrame({name: symmetrize(P)[iu] for name, P in participant_matrices(df).items()},
                        index=cols).T


def student_correlations(df: pd.DataFrame, order: Iterable[str] | None = None) -> pd.DataFrame:
    """Student-by-student correlation of the rating vectors, in the given row order."""
    V = student_vectors(df)
    if order is not None:
        V = V.loc[list(order)]
    return V.T.corr()


def split_test(df: pd.DataFrame, group_a: Iterable[str], group_b: Iterable[str],
               n_shuffles: int = 1000, rng: np.random.Generator | None = None) -> tuple[float, np.ndarray]:
    """How different are two groups' class matrices, compared with random splits of the same sizes?

    Returns the correlation between the two groups' matrices and the same
    correlation for n_shuffles random splits. If the groups are real, the
    observed value sits below the shuffled ones.
    """
    rng = rng or np.random.default_rng(5)
    iu = np.triu_indices(10, 1)
    group_a, group_b = list(group_a), list(group_b)

    def corr(A, B):
        a, b = symmetrize(rating_matrix(df, A))[iu], symmetrize(rating_matrix(df, B))[iu]
        ok = ~np.isnan(a) & ~np.isnan(b)
        return float(np.corrcoef(a[ok], b[ok])[0, 1])

    observed = corr(group_a, group_b)
    everyone = np.array(group_a + group_b)
    null = []
    for _ in range(n_shuffles):
        p = rng.permutation(everyone)
        null.append(corr(p[:len(group_a)], p[len(group_a):]))
    return observed, np.array(null)


# --------------------------------------------------- weighted feature models --

def feature_design(ctx: Context, common: bool = False) -> np.ndarray:
    """Predictors for the 90 ordered pairs: an intercept, then one column per feature.

    Each distinctive column is 1 when the two digits disagree on that feature.
    With common=True there is also one column per feature that is 1 when
    both digits have it. That second set is Tversky's common-features term,
    now with its own weight per feature; without it, this is a city-block
    distance with a weight per feature.
    """
    mask = ~np.eye(10, dtype=bool)
    F = ctx.F.astype(float)
    cols = [np.ones(mask.sum()), ctx.mismatch[mask]]
    if common:
        both = (F[:, None, :] * F[None, :, :])[mask]
        cols.append(both)
    return np.column_stack(cols)


def fit_features(M: np.ndarray, ctx: Context, common: bool = False) -> dict:
    """Least-squares fit of the weighted feature model to a 10 x 10 target matrix."""
    mask = ~np.isnan(M) & ~np.eye(10, dtype=bool)
    X = feature_design(ctx, common)[offdiag(np.where(mask, 1.0, np.nan)) == 1.0]
    w, *_ = np.linalg.lstsq(X, M[mask], rcond=None)
    pred = np.full((10, 10), np.nan)
    pred[~np.eye(10, dtype=bool)] = feature_design(ctx, common) @ w
    labels = ["intercept"] + [f"differ: {n}" for n in ctx.names]
    if common:
        labels += [f"both: {n}" for n in ctx.names]
    sse = float(np.nansum((pred - M) ** 2))
    return {"weights": pd.Series(w, index=labels), "predicted": pred, "r2": r2(pred, M),
            "aic": aic(sse, int(mask.sum()), X.shape[1]), "k": X.shape[1] - 1}


def features_cv(df: pd.DataFrame, features: dict[str, Iterable[int]], common: bool = False,
                n_splits: int = 30, rng: np.random.Generator | None = None) -> dict:
    """Train and held-out R² of the weighted feature model, fit on half the students, scored on the rest."""
    rng = rng or np.random.default_rng(6)
    ctx = Context(features)
    names = np.array(sorted(df["name"].unique()))
    full = fit_features(rating_matrix(df), ctx, common)
    held = []
    for _ in range(n_splits):
        p = rng.permutation(names)
        half = names.size // 2
        f = fit_features(rating_matrix(df, p[:half]), ctx, common)
        held.append(r2(f["predicted"], rating_matrix(df, p[half:])))
    return {"k": full["k"], "train R²": full["r2"], "AIC": full["aic"],
            "held-out R²": float(np.mean(held)), "sd": float(np.std(held))}


def feature_gain(df: pd.DataFrame, base: dict[str, Iterable[int]], name: str, members: Iterable[int],
                 common: bool = False, n_splits: int = 30, rng: np.random.Generator | None = None) -> dict:
    """What one extra feature buys: change in AIC (down is better) and in held-out R² (up is better)."""
    rng = rng or np.random.default_rng(6)
    before = features_cv(df, base, common, n_splits, np.random.default_rng(6))
    after = features_cv(df, {**base, name: set(members)}, common, n_splits, np.random.default_rng(6))
    return {"feature": name, "members": sorted(set(members)),
            "ΔAIC": after["AIC"] - before["AIC"], "Δheld-out R²": after["held-out R²"] - before["held-out R²"]}


def random_feature_null(df: pd.DataFrame, base: dict[str, Iterable[int]], n_random: int = 100,
                        common: bool = False, n_splits: int = 12,
                        rng: np.random.Generator | None = None) -> pd.DataFrame:
    """The same gains for made-up features: random subsets of three to five digits.

    A real feature should do better than most of these. Many will not.
    """
    rng = rng or np.random.default_rng(7)
    rows = []
    for i in range(n_random):
        size = int(rng.integers(3, 6))
        members = set(int(d) for d in rng.choice(DIGITS, size, replace=False))
        rows.append(feature_gain(df, base, f"random {i}", members, common, n_splits, rng))
    return pd.DataFrame(rows)


def similarity_by_difference(df: pd.DataFrame, names: Iterable[str] | None = None) -> pd.Series:
    """Mean similarity of the pairs at each magnitude difference 1..9."""
    S = symmetrize(rating_matrix(df, names))
    iu = np.triu_indices(10, 1)
    d = np.abs(DIGITS[iu[0]] - DIGITS[iu[1]])
    return pd.Series(S[iu]).groupby(d).mean().rename("mean similarity").rename_axis("|a − b|")


# ------------------------------------------------------- hypothesis matrices --

def partition_hypothesis(members: Iterable[int]) -> np.ndarray:
    """Similarity 1 for two digits on the same side of a split, 0 otherwise."""
    F = np.isin(DIGITS, list(members))
    return (F[:, None] == F[None, :]).astype(float)


def feature_hypothesis(features: dict[str, Iterable[int]]) -> np.ndarray:
    """Similarity 1 minus the share of features the digits disagree on."""
    ctx = Context(features)
    return 1 - ctx.d_city / ctx.k


def hypothesis_matrices() -> dict[str, np.ndarray]:
    """The 10 x 10 similarity matrix each single idea would produce, on a 0..1 scale.

    These are what a rating matrix looks like when one hypothesis alone
    drives it. Compare them with the class matrix by eye, then by
    correlation: the same move, on brain data, is representational
    similarity analysis.
    """
    H = {"number line": 1 - Context().absdiff / 9}
    for name, members in [("odd / even", {0, 2, 4, 6, 8}),
                          ("small / large", {0, 1, 2, 3, 4}),
                          ("prime", {2, 3, 5, 7}),
                          ("multiple of 3", {0, 3, 6, 9}),
                          ("closed loop", {0, 6, 8, 9}),
                          ("straight strokes only", {1, 4, 7})]:
        H[name] = partition_hypothesis(members)
    shape = {k: v for k, v in DEFAULT_FEATURES.items() if "numeral" in k or "straight" in k}
    H["numeral shape (3 features)"] = feature_hypothesis(shape)
    return H


def hypothesis_fit(M: np.ndarray, hypotheses: dict[str, np.ndarray]) -> pd.Series:
    """Correlation of each hypothesis matrix with a data matrix, over the 45 pairs."""
    iu = np.triu_indices(10, 1)
    data = symmetrize(M)[iu]
    ok = ~np.isnan(data)
    out = {}
    for name, H in hypotheses.items():
        h = H[iu]
        out[name] = float(np.corrcoef(h[ok], data[ok])[0, 1]) if h[ok].std() > 0 else float("nan")
    return pd.Series(out, name="r with the data")


# ------------------------------------------------------------------ indscal --

@dataclass
class IndscalFit:
    """A shared map plus one weight per person per axis (Carroll & Chang, 1970).

    X is the group space (10 x dims), scaled so every axis has unit sum of
    squares; W is the weight table (people x dims): person k's own map is X
    with axis m stretched by sqrt(W[k, m]). names lists the people in W's row
    order; r is, per person, the correlation between the distances their
    stretched map implies and their observed dissimilarities (a correlation,
    not R², because the fit is on double-centred squared dissimilarities and
    one person's 45 ratings carry an arbitrary additive constant); loss is the
    total squared error on the scalar-product matrices that was minimised.
    """
    X: np.ndarray
    W: np.ndarray
    names: list[str]
    r: np.ndarray
    loss: float

    def person_map(self, name: str) -> np.ndarray:
        return self.X * np.sqrt(self.W[self.names.index(name)])

    def weights(self) -> pd.DataFrame:
        cols = [f"dim{m + 1}" for m in range(self.X.shape[1])]
        out = pd.DataFrame(self.W, index=self.names, columns=cols)
        out["r"] = self.r
        return out


def _double_center(D2: np.ndarray) -> np.ndarray:
    n = D2.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    return -0.5 * J @ D2 @ J


def indscal(mats: dict[str, np.ndarray], dims: int = 2, how: str = "linear",
            restarts: int = 3, rng: np.random.Generator | None = None) -> IndscalFit:
    """Fit INDSCAL to one similarity matrix per person.

    The model says everybody shares one map, and people differ only in how
    much they stretch each of its axes: for person k the squared distance
    between digits i and j is Σ_m W[k, m]·(X[i, m] − X[j, m])². The fit
    minimises, over X and non-negative W, the squared error between each
    person's double-centred squared-dissimilarity matrix and X·diag(W[k])·Xᵀ,
    which is Carroll and Chang's objective. L-BFGS from the classical-MDS
    solution of the pooled matrix, plus a few random restarts.

    Unlike plain MDS, the axes are not free to rotate: the weights pin them.
    So the axes INDSCAL returns are the ones people actually differ on, which
    is what makes it an individual-differences method and not just a map.
    """
    from scipy.optimize import minimize as _minimize
    rng = rng or np.random.default_rng(4)
    names = list(mats)
    B = np.stack([_double_center(to_dissimilarity(mats[k], how) ** 2) for k in names])   # people x 10 x 10
    n, p = B.shape[1], len(names)

    def unpack(v):
        return v[:n * dims].reshape(n, dims), v[n * dims:].reshape(p, dims)

    def loss_grad(v):
        X, W = unpack(v)
        gX = np.zeros_like(X); gW = np.zeros_like(W); total = 0.0
        for k in range(p):
            R = B[k] - (X * W[k]) @ X.T
            total += np.sum(R ** 2)
            gX += -4 * R @ (X * W[k])
            gW[k] = -2 * np.einsum("im,ij,jm->m", X, R, X)
        return total, np.concatenate([gX.ravel(), gW.ravel()])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)          # the all-NaN diagonal
        pooled = np.nanmean(np.stack([mats[k] for k in names]), axis=0)
    X0, _ = classical_mds(to_dissimilarity(pooled, how), dims)
    starts = [np.concatenate([X0.ravel(), np.ones(p * dims)])]
    for _ in range(restarts):
        starts.append(np.concatenate([(X0 + rng.normal(0, 0.3 * X0.std(), X0.shape)).ravel(),
                                      rng.uniform(0.5, 1.5, p * dims)]))
    bounds = [(None, None)] * (n * dims) + [(0.0, None)] * (p * dims)
    best = None
    for s in starts:
        res = _minimize(loss_grad, s, jac=True, method="L-BFGS-B", bounds=bounds,
                        options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-8})
        if best is None or res.fun < best.fun:
            best = res
    X, W = unpack(best.x)
    scale = np.sqrt(np.sum(X ** 2, axis=0))
    scale[scale == 0] = 1.0
    X, W = X / scale, W * scale ** 2                         # unit axes; weights carry the size
    order = np.argsort(W.sum(axis=0))[::-1]                  # most-used axis first
    X, W = X[:, order], W[:, order]
    rs = []
    for k, name in enumerate(names):
        d = offdiag(to_dissimilarity(mats[name], how))
        dh = offdiag(np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2 * W[k]).sum(-1)))
        rs.append(float(np.corrcoef(d, dh)[0, 1]) if dh.std() > 0 else 0.0)
    return IndscalFit(X, W, names, np.array(rs), float(best.fun))


def indscal_distances(fit: IndscalFit, name: str) -> np.ndarray:
    """The 10 x 10 distance matrix INDSCAL predicts for one person."""
    Xk = fit.person_map(name)
    return np.sqrt(((Xk[:, None, :] - Xk[None, :, :]) ** 2).sum(-1))


# ------------------------------------------------------------------ plotting --

def plot_matrix(M: np.ndarray, ax=None, title: str = "", vmin=SCALE_MIN, vmax=SCALE_MAX, cmap="Blues"):
    """Heat map of a 10 x 10 matrix, rows = subject digit, columns = referent digit."""
    import matplotlib.pyplot as plt
    ax = ax or plt.gca()
    im = ax.imshow(M, vmin=vmin, vmax=vmax, cmap=cmap)
    ax.set_xticks(DIGITS); ax.set_yticks(DIGITS)
    ax.set_xlabel("referent  b"); ax.set_ylabel("subject  a")
    ax.set_title(title)
    return im


def plot_map(X: np.ndarray, ax=None, title: str = "", color_by: Iterable[int] | None = None):
    """Scatter the ten digits at MDS coordinates, labelled."""
    import matplotlib.pyplot as plt
    ax = ax or plt.gca()
    c = list(color_by) if color_by is not None else ["#1a5276"] * 10
    ax.scatter(X[:, 0], X[:, 1], s=420, c=c, alpha=0.15, edgecolors="none")
    for d in DIGITS:
        ax.text(X[d, 0], X[d, 1], str(d), ha="center", va="center", fontsize=16, fontweight="bold")
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title)
    return ax
