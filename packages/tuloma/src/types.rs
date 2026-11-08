use crate::buffers;
use numpy::{IntoPyArray, PyArray1, PyArray2};
use pyo3::{exceptions::PyRuntimeError, prelude::*};
use tuloma_los as core;

#[pyclass(frozen, eq, eq_int, module = "tuloma.los")]
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Location {
    Above,
    On,
    Below,
}
impl From<core::Location> for Location {
    fn from(v: core::Location) -> Self {
        match v {
            core::Location::Above => Self::Above,
            core::Location::On => Self::On,
            core::Location::Below => Self::Below,
        }
    }
}

#[pyclass(frozen, eq, eq_int, module = "tuloma.los")]
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Visibility {
    Visible,
    Touch,
    Blocked,
    SameX,
}
impl From<core::Visibility> for Visibility {
    fn from(v: core::Visibility) -> Self {
        match v {
            core::Visibility::Visible => Self::Visible,
            core::Visibility::Touch => Self::Touch,
            core::Visibility::Blocked => Self::Blocked,
            core::Visibility::SameX => Self::SameX,
        }
    }
}

#[pyclass(frozen, eq, eq_int, module = "tuloma.los")]
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum ContactKind {
    Enter = 1,
    Exit = 2,
    Touch = 3,
}

#[pyclass(frozen, module = "tuloma.los")]
pub struct ClearanceExtrema {
    pub(crate) inner: core::ClearanceExtrema,
}
#[pymethods]
impl ClearanceExtrema {
    #[getter]
    fn min_value(&self) -> f64 {
        self.inner.minimum.value
    }
    #[getter]
    fn max_value(&self) -> f64 {
        self.inner.maximum.value
    }
    #[getter]
    fn min_point(&self) -> (f64, f64) {
        let p = self.inner.minimum.point;
        (p[0], p[1])
    }
    #[getter]
    fn max_point(&self) -> (f64, f64) {
        let p = self.inner.maximum.point;
        (p[0], p[1])
    }
    #[getter]
    fn min_parameter(&self) -> f64 {
        self.inner.minimum.parameter
    }
    #[getter]
    fn max_parameter(&self) -> f64 {
        self.inner.maximum.parameter
    }
}

#[pyclass(frozen, module = "tuloma.los")]
pub struct ClearanceProfile {
    parameters: Py<PyArray1<f64>>,
    clearance: Py<PyArray1<f64>>,
}
impl ClearanceProfile {
    pub(crate) fn from_core(py: Python<'_>, result: core::ClearanceProfile) -> PyResult<Self> {
        if result.parameters.len() != result.clearance.len() {
            return Err(PyRuntimeError::new_err(
                "core returned mismatched clearance profile lengths",
            ));
        }
        Ok(Self {
            parameters: result.parameters.into_pyarray(py).unbind(),
            clearance: result.clearance.into_pyarray(py).unbind(),
        })
    }
}
#[pymethods]
impl ClearanceProfile {
    #[getter]
    fn parameters(&self, py: Python<'_>) -> Py<PyArray1<f64>> {
        self.parameters.clone_ref(py)
    }
    #[getter]
    fn clearance(&self, py: Python<'_>) -> Py<PyArray1<f64>> {
        self.clearance.clone_ref(py)
    }
}

#[pyclass(frozen, module = "tuloma.los")]
pub struct Contacts {
    points: Py<PyArray2<f64>>,
    parameters: Py<PyArray1<f64>>,
    kinds: Py<PyArray1<u8>>,
    overlaps: Py<PyArray2<f64>>,
}
impl Contacts {
    pub(crate) fn from_core(py: Python<'_>, result: core::Contacts) -> PyResult<Self> {
        if result.points.len() != result.parameters.len()
            || result.points.len() != result.kinds.len()
        {
            return Err(PyRuntimeError::new_err(
                "core returned mismatched contact lengths",
            ));
        }
        Ok(Self {
            points: buffers::matrix(py, result.points)?.unbind(),
            parameters: result.parameters.into_pyarray(py).unbind(),
            kinds: result
                .kinds
                .into_iter()
                .map(|k| k as u8)
                .collect::<Vec<_>>()
                .into_pyarray(py)
                .unbind(),
            overlaps: buffers::matrix(py, result.overlaps)?.unbind(),
        })
    }
}
#[pymethods]
impl Contacts {
    #[getter]
    fn points(&self, py: Python<'_>) -> Py<PyArray2<f64>> {
        self.points.clone_ref(py)
    }
    #[getter]
    fn parameters(&self, py: Python<'_>) -> Py<PyArray1<f64>> {
        self.parameters.clone_ref(py)
    }
    #[getter]
    fn kinds(&self, py: Python<'_>) -> Py<PyArray1<u8>> {
        self.kinds.clone_ref(py)
    }
    #[getter]
    fn overlaps(&self, py: Python<'_>) -> Py<PyArray2<f64>> {
        self.overlaps.clone_ref(py)
    }
}
