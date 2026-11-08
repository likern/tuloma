"""Runs unchanged in native Python and in Pyodide's browser/Node runtime."""
import numpy as np
from tuloma import los
from tuloma import _los

x = np.array([0., 1., 3.], dtype=np.float64)
z = np.array([1., -2., 4.], dtype=np.float64)
scene = los.Scene1D(x, z)
assert scene.x is x and scene.z is z
assert scene.x.ctypes.data == x.ctypes.data
assert len(scene) == 3
scene.validate()
assert not los.ALGORITHMS_IMPLEMENTED
assert _los.__file__.endswith(".so"), _los.__file__

a, b = (0., 2.), (3., 5.)
calls = [lambda: scene.height(0.5), lambda: scene.visible(a, b),
         lambda: scene.intersections(a, b), lambda: los.lerp(0., 1., 0.5)]
for call in calls:
    try:
        call()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("geometry placeholder returned a fabricated answer")
result = {"ok": True, "module": _los.__file__, "numpy": np.__version__,
          "algorithms_implemented": los.ALGORITHMS_IMPLEMENTED}
print("TULOMA_NATIVE_SMOKE_OK", result)
