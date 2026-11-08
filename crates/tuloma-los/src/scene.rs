use crate::{Error, Result};

/// Borrowed storage. No sorting, resampling, ownership transfer or copy.
#[derive(Clone, Copy, Debug)]
pub struct Scene1D<'a> {
    x: &'a [f64],
    z: &'a [f64],
}

impl<'a> Scene1D<'a> {
    pub fn new(x: &'a [f64], z: &'a [f64]) -> Result<Self> {
        let invalid = |field, reason| Error::InvalidInput { field, reason };
        if x.len() < 2 || x.len() != z.len() {
            return Err(invalid("x/z", "equal lengths >= 2 required"));
        }
        if !x.iter().all(|v| v.is_finite()) || !z.iter().all(|v| v.is_finite()) {
            return Err(invalid(
                "x/z",
                "finite coordinates required; NoData is unsupported",
            ));
        }
        if !x.windows(2).all(|w| w[0] < w[1]) {
            return Err(invalid("x", "strictly increasing coordinates required"));
        }
        Ok(Self { x, z })
    }

    pub fn x(&self) -> &'a [f64] {
        self.x
    }
    pub fn z(&self) -> &'a [f64] {
        self.z
    }
    pub fn len(&self) -> usize {
        self.x.len()
    }
    pub fn is_empty(&self) -> bool {
        self.x.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn constructor_borrows_the_original_slices() {
        let x = [0.0, 1.0, 3.0];
        let z = [1.0, -2.0, 4.0];
        let scene = Scene1D::new(&x, &z).unwrap();
        assert_eq!(scene.x().as_ptr(), x.as_ptr());
        assert_eq!(scene.z().as_ptr(), z.as_ptr());
    }

    #[test]
    fn invalid_storage_is_rejected_without_repair() {
        assert!(Scene1D::new(&[0.0], &[0.0]).is_err());
        assert!(Scene1D::new(&[0.0, 0.0], &[0.0, 0.0]).is_err());
        assert!(Scene1D::new(&[0.0, 1.0], &[0.0, f64::NAN]).is_err());
    }
}
