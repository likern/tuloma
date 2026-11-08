use numpy::{IntoPyArray, PyArray1, PyArray2, PyReadonlyArray1, PyReadwriteArray1};
use pyo3::{
    exceptions::{PyRuntimeError, PyTypeError, PyValueError},
    prelude::*,
    types::{PyFloat, PyInt},
};
use tuloma_los as core;

pub fn error(error: core::Error) -> PyErr {
    match error {
        core::Error::NotImplemented { .. } => {
            pyo3::exceptions::PyNotImplementedError::new_err(error.to_string())
        }
        core::Error::InvalidInput { .. } => PyValueError::new_err(error.to_string()),
    }
}

pub fn layout(_: numpy::AsSliceError) -> PyErr {
    PyValueError::new_err(
        "aligned contiguous native-endian float64 storage required; no implicit copy",
    )
}

pub fn readonly<'py>(value: &Bound<'py, PyAny>) -> PyResult<PyReadonlyArray1<'py, f64>> {
    if !value.is_exact_instance_of::<PyArray1<f64>>() {
        return Err(PyTypeError::new_err(
            "expected an exact numpy.ndarray; subclasses and array-like coercion are unsupported",
        ));
    }
    let array: PyReadonlyArray1<'py, f64> = value.extract()?;
    array.as_slice().map_err(layout)?;
    Ok(array)
}

pub fn readwrite<'py>(value: &Bound<'py, PyAny>) -> PyResult<PyReadwriteArray1<'py, f64>> {
    if !value.is_exact_instance_of::<PyArray1<f64>>() {
        return Err(PyTypeError::new_err("out must be an exact numpy.ndarray"));
    }
    let mut array: PyReadwriteArray1<'py, f64> = value.extract()?;
    array.as_slice_mut().map_err(layout)?;
    Ok(array)
}

pub enum Input<'py> {
    Scalar(f64),
    Array(PyReadonlyArray1<'py, f64>),
}

impl<'py> Input<'py> {
    pub fn parse(value: &Bound<'py, PyAny>) -> PyResult<Self> {
        if value.is_instance_of::<PyFloat>() || value.is_instance_of::<PyInt>() {
            return Ok(Self::Scalar(value.extract()?));
        }
        Ok(Self::Array(readonly(value)?))
    }
}

/// Dispatch/storage glue only; all numerical work belongs in the supplied core functions.
pub fn evaluate<'py>(
    py: Python<'py>,
    value: &Bound<'py, PyAny>,
    out: Option<&Bound<'py, PyAny>>,
    scalar: impl FnOnce(f64) -> core::Result<f64>,
    batch: impl FnOnce(&[f64]) -> core::Result<Vec<f64>>,
    into: impl FnOnce(&[f64], &mut [f64]) -> core::Result<()>,
) -> PyResult<Py<PyAny>> {
    match Input::parse(value)? {
        Input::Scalar(x) => {
            if out.is_some() {
                return Err(PyTypeError::new_err("out requires an array input"));
            }
            Ok(scalar(x)
                .map_err(error)?
                .into_pyobject(py)?
                .into_any()
                .unbind())
        }
        Input::Array(array) => {
            let input = array.as_slice().map_err(layout)?;
            if let Some(out) = out {
                let mut output = readwrite(out)?;
                let data = output.as_slice_mut().map_err(layout)?;
                if data.len() != input.len() {
                    return Err(PyValueError::new_err("out length must match input"));
                }
                into(input, data).map_err(error)?;
                Ok(out.clone().unbind())
            } else {
                let result = batch(input).map_err(error)?;
                if result.len() != input.len() {
                    return Err(PyRuntimeError::new_err(
                        "core returned the wrong output length",
                    ));
                }
                Ok(result.into_pyarray(py).into_any().unbind())
            }
        }
    }
}

/// Vec::into_flattened and into_pyarray transfer the original allocation.
pub fn matrix<'py, const C: usize>(
    py: Python<'py>,
    rows: Vec<[f64; C]>,
) -> PyResult<Bound<'py, PyArray2<f64>>> {
    let len = rows.len();
    let array = numpy::ndarray::Array2::from_shape_vec((len, C), rows.into_flattened())
        .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    Ok(array.into_pyarray(py))
}
