"""Геометрическая видимость на кусочно-линейном профиле."""
import numpy as np

X = np.array([0, 11, 23, 33, 40, 43, 53, 63, 73, 80, 91, 100], dtype=float)
Z = np.array([6, 2, 0, 3, 12, 5, 1, 0, 3, 6, 3, 8], dtype=float)


def _heights(z):
    heights = np.asarray(z, dtype=float)
    if heights.shape != X.shape or not np.all(np.isfinite(heights)):
        raise ValueError("Для каждого узла требуется конечная высота.")
    return heights


def profile_los(x_a, x_b, h_a=0, h_b=0, *, z=Z, atol=1e-9):
    """Проверить точную видимость и найти части отрезка под рельефом."""
    if not (X[0] <= x_a <= X[-1] and X[0] <= x_b <= X[-1]):
        raise ValueError("Точки должны лежать в пределах профиля.")
    if not (0 <= h_a < np.inf and 0 <= h_b < np.inf):
        raise ValueError("Высоты должны быть конечными и неотрицательными.")
    heights = _heights(z)

    a = float(np.interp(x_a, X, heights) + h_a)
    b = float(np.interp(x_b, X, heights) + h_b)
    result = {"a": [x_a, a], "b": [x_b, b], "kind": "visible",
              "x_peak": None, "peak_z": None, "excess": None,
              "ground": [a - h_a, b - h_b], "below": []}
    if x_a == x_b:
        return {**result, "kind": "same"}

    left, right = sorted((x_a, x_b))
    inside = (X > left) & (X < right)
    xs, zs = X[inside], heights[inside]
    if not xs.size:
        if h_a == h_b == 0:
            result["kind"] = "touch"
        return result

    line = a + (b - a) * ((xs - x_a) / (x_b - x_a))
    excess = zs - line
    k = int(np.argmax(excess))
    peak = float(excess[k])
    if peak > atol:
        kind = "blocked"
        endpoint_gaps = (-h_a, -h_b) if x_a < x_b else (-h_b, -h_a)
        result["below"] = _below_intervals(
            [left, *xs.tolist(), right], [endpoint_gaps[0], *excess.tolist(), endpoint_gaps[1]]
        )
    elif peak >= -atol:
        kind = "touch"
    else:
        kind = "visible"
    return {**result, "kind": kind, "x_peak": float(xs[k]),
            "peak_z": float(zs[k]), "excess": peak}


def _below_intervals(xs, gaps):
    spans = []
    for left, right, gap_left, gap_right in zip(xs, xs[1:], gaps, gaps[1:]):
        if gap_left <= 0 and gap_right <= 0:
            continue
        if gap_left <= 0:
            left += (right - left) * (-gap_left) / (gap_right - gap_left)
        elif gap_right <= 0:
            right = left + (right - left) * gap_left / (gap_left - gap_right)
        if spans and spans[-1][1] == left:
            spans[-1][1] = right
        else:
            spans.append([left, right])
    return spans


def compare_profile_los(x_a, x_b, h_a=0, h_b=0, step=25, *, z=Z, atol=1e-9):
    """Сравнить узлы ломаной с отсчётами через step метров от A."""
    if not np.isfinite(step) or step <= 0:
        raise ValueError("Шаг должен быть конечным и положительным.")
    heights = _heights(z)
    exact = profile_los(x_a, x_b, h_a, h_b, z=heights, atol=atol)
    distance = abs(x_b - x_a)
    if distance > 10_000 * step:
        raise ValueError("В опыте допускается до 10 000 отсчётов.")

    if not distance:
        return {"exact": exact, "sampled": "same", "samples": []}

    direction = np.sign(x_b - x_a)
    xs = x_a + direction * np.arange(step, distance, step)
    xs = xs[(xs > min(x_a, x_b)) & (xs < max(x_a, x_b))]
    if not xs.size:
        return {"exact": exact, "sampled": "empty", "samples": []}

    zs = np.interp(xs, X, heights)
    a, b = exact["a"][1], exact["b"][1]
    line = a + (b - a) * ((xs - x_a) / (x_b - x_a))
    peak = float(np.max(zs - line))
    sampled = "blocked" if peak > atol else "touch" if peak >= -atol else "visible"
    return {"exact": exact, "sampled": sampled,
            "samples": np.column_stack((xs, zs)).tolist()}


if __name__ == "__main__":
    print(profile_los(0, 80))
