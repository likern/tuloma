//! Python/NumPy storage and error translation; no LOS algorithm lives here.
use pyo3::prelude::*;
use tuloma_los::{self as core, queries as q};

mod buffers;
mod scene;
mod types;

#[pyfunction]
#[pyo3(signature = (left, right, t, *, out=None))]
fn lerp<'py>(
    py: Python<'py>,
    left: f64,
    right: f64,
    t: &Bound<'py, PyAny>,
    out: Option<&Bound<'py, PyAny>>,
) -> PyResult<Py<PyAny>> {
    buffers::evaluate(
        py,
        t,
        out,
        |t| q::lerp(left, right, t),
        |t| q::lerps(left, right, t),
        |t, y| q::lerps_into(left, right, t, y),
    )
}

#[pyfunction]
#[pyo3(signature = (a, b, xq, *, out=None))]
fn line_height<'py>(
    py: Python<'py>,
    a: (f64, f64),
    b: (f64, f64),
    xq: &Bound<'py, PyAny>,
    out: Option<&Bound<'py, PyAny>>,
) -> PyResult<Py<PyAny>> {
    let s = core::Segment {
        a: [a.0, a.1],
        b: [b.0, b.1],
    };
    buffers::evaluate(
        py,
        xq,
        out,
        |x| q::line_height(s, x),
        |x| q::line_heights(s, x),
        |x, y| q::line_heights_into(s, x, y),
    )
}

#[pyfunction]
#[pyo3(signature = (a, b, t, *, out=None))]
fn segment_points<'py>(
    py: Python<'py>,
    a: (f64, f64),
    b: (f64, f64),
    t: &Bound<'py, PyAny>,
    out: Option<&Bound<'py, PyAny>>,
) -> PyResult<Py<PyAny>> {
    let s = core::Segment {
        a: [a.0, a.1],
        b: [b.0, b.1],
    };
    match buffers::Input::parse(t)? {
        buffers::Input::Scalar(t) => {
            if out.is_some() {
                return Err(pyo3::exceptions::PyTypeError::new_err(
                    "out requires array t",
                ));
            }
            let p = q::segment_point(s, t).map_err(buffers::error)?;
            Ok((p[0], p[1]).into_pyobject(py)?.into_any().unbind())
        }
        buffers::Input::Array(t) => {
            let ts = t.as_slice().map_err(buffers::layout)?;
            if let Some(out) = out {
                use numpy::{PyArray2, PyReadwriteArray2};
                if !out.is_exact_instance_of::<PyArray2<f64>>() {
                    return Err(pyo3::exceptions::PyTypeError::new_err(
                        "out must be an exact rank-2 ndarray",
                    ));
                }
                let mut array: PyReadwriteArray2<'_, f64> = out.extract()?;
                use numpy::PyUntypedArrayMethods;
                if !array.is_c_contiguous() || array.shape() != [ts.len(), 2] {
                    return Err(pyo3::exceptions::PyValueError::new_err(
                        "out must have C layout and shape (len(t), 2)",
                    ));
                }
                q::segment_points_into(s, ts, array.as_slice_mut().map_err(buffers::layout)?)
                    .map_err(buffers::error)?;
                Ok(out.clone().unbind())
            } else {
                let points = q::segment_points(s, ts).map_err(buffers::error)?;
                if points.len() != ts.len() {
                    return Err(pyo3::exceptions::PyRuntimeError::new_err(
                        "core returned wrong point count",
                    ));
                }
                Ok(buffers::matrix(py, points)?.into_any().unbind())
            }
        }
    }
}

#[pymodule(gil_used = true)]
fn _los(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("ALGORITHMS_IMPLEMENTED", core::ALGORITHMS_IMPLEMENTED)?;
    m.add_class::<scene::Scene1D>()?;
    m.add_class::<types::Location>()?;
    m.add_class::<types::Visibility>()?;
    m.add_class::<types::ContactKind>()?;
    m.add_class::<types::ClearanceExtrema>()?;
    m.add_class::<types::ClearanceProfile>()?;
    m.add_class::<types::Contacts>()?;
    m.add_function(wrap_pyfunction!(lerp, m)?)?;
    m.add_function(wrap_pyfunction!(line_height, m)?)?;
    m.add_function(wrap_pyfunction!(segment_points, m)?)?;
    Ok(())
}
