use crate::{buffers as b, types::*};
use numpy::{IntoPyArray, PyArray1};
use pyo3::{exceptions::PyValueError, prelude::*};
use tuloma_los::{self as core, queries as q};

/// A piecewise-linear scene retaining the original NumPy x/z objects.
#[pyclass(module = "tuloma.los")]
pub struct Scene1D {
    x: Py<PyArray1<f64>>,
    z: Py<PyArray1<f64>>,
}

impl Scene1D {
    fn with_view<R>(
        &self,
        py: Python<'_>,
        f: impl FnOnce(core::Scene1D<'_>) -> PyResult<R>,
    ) -> PyResult<R> {
        let x = b::readonly(self.x.bind(py).as_any())?;
        let z = b::readonly(self.z.bind(py).as_any())?;
        let view = core::Scene1D::new(
            x.as_slice().map_err(b::layout)?,
            z.as_slice().map_err(b::layout)?,
        )
        .map_err(b::error)?;
        f(view)
    }
}

fn segment(a: (f64, f64), b: (f64, f64)) -> core::Segment {
    core::Segment {
        a: [a.0, a.1],
        b: [b.0, b.1],
    }
}

#[pymethods]
impl Scene1D {
    #[new]
    fn new(x: &Bound<'_, PyAny>, z: &Bound<'_, PyAny>) -> PyResult<Self> {
        let xr = b::readonly(x)?;
        let zr = b::readonly(z)?;
        core::Scene1D::new(
            xr.as_slice().map_err(b::layout)?,
            zr.as_slice().map_err(b::layout)?,
        )
        .map_err(b::error)?;
        Ok(Self {
            x: x.extract::<Bound<'_, PyArray1<f64>>>()?.unbind(),
            z: z.extract::<Bound<'_, PyArray1<f64>>>()?.unbind(),
        })
    }

    #[staticmethod]
    fn from_numpy(x: &Bound<'_, PyAny>, z: &Bound<'_, PyAny>) -> PyResult<Self> {
        Self::new(x, z)
    }

    #[staticmethod]
    #[pyo3(signature = (z, *, x0=0.0, dx=1.0))]
    fn from_uniform(py: Python<'_>, z: &Bound<'_, PyAny>, x0: f64, dx: f64) -> PyResult<Self> {
        let zr = b::readonly(z)?;
        let x = q::uniform_axis(zr.as_slice().map_err(b::layout)?, x0, dx)
            .map_err(b::error)?
            .into_pyarray(py);
        Self::new(x.as_any(), z)
    }

    #[getter]
    fn x(&self, py: Python<'_>) -> Py<PyArray1<f64>> {
        self.x.clone_ref(py)
    }
    #[getter]
    fn z(&self, py: Python<'_>) -> Py<PyArray1<f64>> {
        self.z.clone_ref(py)
    }
    fn __len__(&self, py: Python<'_>) -> PyResult<usize> {
        self.with_view(py, |v| Ok(v.len()))
    }
    fn validate(&self, py: Python<'_>) -> PyResult<()> {
        self.with_view(py, |_| Ok(()))
    }

    #[pyo3(signature = (xq, *, out=None))]
    fn height<'py>(
        &self,
        py: Python<'py>,
        xq: &Bound<'py, PyAny>,
        out: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        self.with_view(py, |v| {
            b::evaluate(
                py,
                xq,
                out,
                |x| q::height(v, x),
                |x| q::heights(v, x),
                |x, y| q::heights_into(v, x, y),
            )
        })
    }

    #[pyo3(signature = (x, *, agl=0.0))]
    fn point(&self, py: Python<'_>, x: f64, agl: f64) -> PyResult<(f64, f64)> {
        self.with_view(py, |v| {
            q::point(v, x, agl).map(|p| (p[0], p[1])).map_err(b::error)
        })
    }

    #[pyo3(signature = (xa, xb, *, interior=true))]
    fn node_range(
        &self,
        py: Python<'_>,
        xa: f64,
        xb: f64,
        interior: bool,
    ) -> PyResult<(usize, usize)> {
        self.with_view(py, |v| q::node_range(v, xa, xb, interior).map_err(b::error))
    }

    #[pyo3(signature = (point, *, atol=0.0))]
    fn locate(&self, py: Python<'_>, point: (f64, f64), atol: f64) -> PyResult<Location> {
        self.with_view(py, |v| {
            q::locate(v, [point.0, point.1], atol)
                .map(Into::into)
                .map_err(b::error)
        })
    }

    #[pyo3(signature = (a, b, *, touch="allow", atol=0.0))]
    fn visible(
        &self,
        py: Python<'_>,
        a: (f64, f64),
        b: (f64, f64),
        touch: &str,
        atol: f64,
    ) -> PyResult<bool> {
        let policy = match touch {
            "allow" => core::TouchPolicy::Allow,
            "block" => core::TouchPolicy::Block,
            _ => return Err(PyValueError::new_err("touch must be 'allow' or 'block'")),
        };
        self.with_view(py, |v| {
            q::visible(v, segment(a, b), policy, atol).map_err(b::error)
        })
    }

    #[pyo3(signature = (a, b, *, atol=0.0))]
    fn classify(
        &self,
        py: Python<'_>,
        a: (f64, f64),
        b: (f64, f64),
        atol: f64,
    ) -> PyResult<Visibility> {
        self.with_view(py, |v| {
            q::classify(v, segment(a, b), atol)
                .map(Into::into)
                .map_err(b::error)
        })
    }

    #[pyo3(signature = (a, b, xq, *, out=None))]
    fn clearance_at<'py>(
        &self,
        py: Python<'py>,
        a: (f64, f64),
        b: (f64, f64),
        xq: &Bound<'py, PyAny>,
        out: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        self.with_view(py, |v| {
            b::evaluate(
                py,
                xq,
                out,
                |x| q::clearance_at(v, segment(a, b), x),
                |x| q::clearances(v, segment(a, b), x),
                |x, y| q::clearances_into(v, segment(a, b), x, y),
            )
        })
    }

    fn clearance_profile(
        &self,
        py: Python<'_>,
        a: (f64, f64),
        b: (f64, f64),
    ) -> PyResult<ClearanceProfile> {
        self.with_view(py, |v| {
            ClearanceProfile::from_core(
                py,
                q::clearance_profile(v, segment(a, b)).map_err(b::error)?,
            )
        })
    }
    fn clearance_extrema(
        &self,
        py: Python<'_>,
        a: (f64, f64),
        b: (f64, f64),
    ) -> PyResult<ClearanceExtrema> {
        self.with_view(py, |v| {
            Ok(ClearanceExtrema {
                inner: q::clearance_extrema(v, segment(a, b)).map_err(b::error)?,
            })
        })
    }
    #[pyo3(signature = (a, b, *, endpoints=false))]
    fn intersections(
        &self,
        py: Python<'_>,
        a: (f64, f64),
        b: (f64, f64),
        endpoints: bool,
    ) -> PyResult<Contacts> {
        self.with_view(py, |v| {
            Contacts::from_core(
                py,
                q::intersections(v, segment(a, b), endpoints).map_err(b::error)?,
            )
        })
    }
    fn below_intervals<'py>(
        &self,
        py: Python<'py>,
        a: (f64, f64),
        b: (f64, f64),
    ) -> PyResult<Bound<'py, numpy::PyArray2<f64>>> {
        self.with_view(py, |v| {
            b::matrix(py, q::below_intervals(v, segment(a, b)).map_err(b::error)?)
        })
    }
    #[pyo3(signature = (a, b, *, endpoints=false))]
    fn first_intersection(
        &self,
        py: Python<'_>,
        a: (f64, f64),
        b: (f64, f64),
        endpoints: bool,
    ) -> PyResult<Option<(f64, f64)>> {
        self.with_view(py, |v| {
            q::first_intersection(v, segment(a, b), endpoints)
                .map(|p| p.map(|p| (p[0], p[1])))
                .map_err(b::error)
        })
    }
}
