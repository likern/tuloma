"""Test bindings/storage and deliberate absence of algorithms, not LOS answers."""
import gc
import weakref

import numpy as np
import pytest
from tuloma import los


@pytest.fixture
def arrays():
    return np.array([0., 1., 3.]), np.array([1., -2., 4.])


def test_constructor_keeps_exact_numpy_objects(arrays):
    x, z = arrays
    scene = los.Scene1D(x, z)
    assert scene.x is x and scene.z is z
    assert scene.x.ctypes.data == x.ctypes.data
    assert scene.z.ctypes.data == z.ctypes.data
    assert len(scene) == 3
    assert scene.validate() is None
    z[1] = 7.
    assert scene.z[1] == 7.
    assert los.Scene1D.from_numpy(x, z).z is z


def test_scene_retains_numpy_owner(arrays):
    x, z = arrays
    ref = weakref.ref(z)
    scene = los.Scene1D(x, z)
    del arrays, z
    gc.collect()
    assert ref() is scene.z


@pytest.mark.parametrize("bad", [
    [0., 1., 3.], np.arange(3, dtype=np.float32), np.arange(3, dtype=">f8"),
    np.arange(3.).reshape(1, 3), np.ma.array(np.arange(3.), mask=[0, 1, 0]),
])
def test_no_array_like_dtype_rank_or_mask_coercion(bad):
    with pytest.raises((TypeError, ValueError)):
        los.Scene1D(bad, np.zeros(3))


@pytest.mark.parametrize("bad", [np.arange(6.)[::2], np.arange(3.)[::-1]])
def test_noncontiguous_is_not_packed(bad):
    with pytest.raises(ValueError):
        los.Scene1D(bad, np.zeros(3))


def test_unaligned_storage_rejected():
    bad = np.ndarray((3,), dtype=np.float64, buffer=np.zeros(25, dtype=np.uint8), offset=1)
    with pytest.raises(ValueError):
        los.Scene1D(bad, np.zeros(3))


@pytest.mark.parametrize("x,z", [([0.], [0.]), ([0., 0.], [0., 1.]),
                                  ([0., 1.], [0.]), ([0., 1.], [0., np.nan])])
def test_constructor_validates_storage(x, z):
    with pytest.raises(ValueError):
        los.Scene1D(np.array(x), np.array(z))


def test_external_edits_are_revalidated(arrays):
    x, z = arrays
    scene = los.Scene1D(x, z)
    z[0] = np.nan
    with pytest.raises(ValueError):
        scene.validate()
    with pytest.raises(ValueError):
        scene.height(0.5)


def pending_calls(scene):
    a, b = (0., 2.), (3., 5.)
    q = np.array([0.2, 0.5])
    return [
        lambda: scene.height(0.5), lambda: scene.height(q),
        lambda: scene.height(q, out=np.empty_like(q)),
        lambda: scene.point(0.5, agl=1.), lambda: scene.node_range(0., 3.),
        lambda: scene.locate(a), lambda: scene.visible(a, b),
        lambda: scene.classify(a, b), lambda: scene.clearance_at(a, b, 0.5),
        lambda: scene.clearance_at(a, b, q),
        lambda: scene.clearance_at(a, b, q, out=np.empty_like(q)),
        lambda: scene.clearance_profile(a, b), lambda: scene.clearance_extrema(a, b),
        lambda: scene.intersections(a, b), lambda: scene.below_intervals(a, b),
        lambda: scene.first_intersection(a, b),
        lambda: los.Scene1D.from_uniform(np.zeros(3)),
        lambda: los.lerp(0., 1., 0.5), lambda: los.lerp(0., 1., q),
        lambda: los.lerp(0., 1., q, out=np.empty_like(q)),
        lambda: los.line_height(a, b, 0.5), lambda: los.line_height(a, b, q),
        lambda: los.line_height(a, b, q, out=np.empty_like(q)),
        lambda: los.segment_points(a, b, 0.5), lambda: los.segment_points(a, b, q),
        lambda: los.segment_points(a, b, q, out=np.empty((2, 2))),
    ]


def test_all_geometric_entrypoints_are_explicit_placeholders(arrays):
    assert los.ALGORITHMS_IMPLEMENTED is False
    scene = los.Scene1D(*arrays)
    for call in pending_calls(scene):
        with pytest.raises(NotImplementedError, match="crates/tuloma-los/src/queries.rs"):
            call()


def test_pending_into_does_not_write_fake_results(arrays):
    scene = los.Scene1D(*arrays)
    out = np.array([123., 456.])
    with pytest.raises(NotImplementedError):
        scene.height(np.array([0., 1.]), out=out)
    np.testing.assert_array_equal(out, [123., 456.])


def test_out_alias_is_rejected_before_creating_mutable_reference(arrays):
    x, z = arrays
    scene = los.Scene1D(x, z)
    with pytest.raises((TypeError, ValueError, RuntimeError)):
        scene.height(x, out=z)


def test_out_layout_and_shape_are_checked(arrays):
    scene = los.Scene1D(*arrays)
    for out in (np.empty(1), np.empty(4)[::2]):
        with pytest.raises(ValueError):
            scene.height(np.array([0., 1.]), out=out)
    out = np.empty(2)
    out.flags.writeable = False
    with pytest.raises((TypeError, ValueError, RuntimeError)):
        scene.height(np.array([0., 1.]), out=out)


def test_public_result_types_and_enum_codes():
    assert int(los.ContactKind.Enter) == 1
    assert int(los.ContactKind.Exit) == 2
    assert int(los.ContactKind.Touch) == 3
    for name in ("Scene1D", "Contacts", "ClearanceProfile", "ClearanceExtrema", "Visibility", "Location"):
        assert getattr(los, name).__module__ == "tuloma.los"
