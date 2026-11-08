//! Algorithm implementation seams. Do not add a Python reference fallback.
//! See docs/los-api.md for mathematical semantics and output ordering.

use crate::*;

macro_rules! pending {
    ($name:literal) => {
        Err(Error::NotImplemented { operation: $name })
    };
}

pub fn uniform_axis(_z: &[f64], _x0: f64, _dx: f64) -> Result<Vec<f64>> {
    pending!("Scene1D.from_uniform")
}
pub fn height(_scene: Scene1D<'_>, _x: f64) -> Result<f64> {
    pending!("Scene1D.height")
}
pub fn heights(_scene: Scene1D<'_>, _x: &[f64]) -> Result<Vec<f64>> {
    pending!("Scene1D.height")
}
pub fn heights_into(_scene: Scene1D<'_>, _x: &[f64], _out: &mut [f64]) -> Result<()> {
    pending!("Scene1D.height")
}
pub fn point(_scene: Scene1D<'_>, _x: f64, _agl: f64) -> Result<Point2> {
    pending!("Scene1D.point")
}
pub fn node_range(
    _scene: Scene1D<'_>,
    _xa: f64,
    _xb: f64,
    _interior: bool,
) -> Result<(usize, usize)> {
    pending!("Scene1D.node_range")
}
pub fn locate(_scene: Scene1D<'_>, _point: Point2, _atol: f64) -> Result<Location> {
    pending!("Scene1D.locate")
}
pub fn visible(
    _scene: Scene1D<'_>,
    _segment: Segment,
    _touch: TouchPolicy,
    _atol: f64,
) -> Result<bool> {
    pending!("Scene1D.visible")
}
pub fn classify(_scene: Scene1D<'_>, _segment: Segment, _atol: f64) -> Result<Visibility> {
    pending!("Scene1D.classify")
}
pub fn clearance_at(_scene: Scene1D<'_>, _segment: Segment, _x: f64) -> Result<f64> {
    pending!("Scene1D.clearance_at")
}
pub fn clearances(_scene: Scene1D<'_>, _segment: Segment, _x: &[f64]) -> Result<Vec<f64>> {
    pending!("Scene1D.clearance_at")
}
pub fn clearances_into(
    _scene: Scene1D<'_>,
    _segment: Segment,
    _x: &[f64],
    _out: &mut [f64],
) -> Result<()> {
    pending!("Scene1D.clearance_at")
}
pub fn clearance_profile(_scene: Scene1D<'_>, _segment: Segment) -> Result<ClearanceProfile> {
    pending!("Scene1D.clearance_profile")
}
pub fn clearance_extrema(_scene: Scene1D<'_>, _segment: Segment) -> Result<ClearanceExtrema> {
    pending!("Scene1D.clearance_extrema")
}
pub fn intersections(_scene: Scene1D<'_>, _segment: Segment, _endpoints: bool) -> Result<Contacts> {
    pending!("Scene1D.intersections")
}
pub fn below_intervals(_scene: Scene1D<'_>, _segment: Segment) -> Result<Vec<[f64; 2]>> {
    pending!("Scene1D.below_intervals")
}
pub fn first_intersection(
    _scene: Scene1D<'_>,
    _segment: Segment,
    _endpoints: bool,
) -> Result<Option<Point2>> {
    pending!("Scene1D.first_intersection")
}
pub fn lerp(_left: f64, _right: f64, _t: f64) -> Result<f64> {
    pending!("lerp")
}
pub fn lerps(_left: f64, _right: f64, _t: &[f64]) -> Result<Vec<f64>> {
    pending!("lerp")
}
pub fn lerps_into(_left: f64, _right: f64, _t: &[f64], _out: &mut [f64]) -> Result<()> {
    pending!("lerp")
}
pub fn line_height(_segment: Segment, _x: f64) -> Result<f64> {
    pending!("line_height")
}
pub fn line_heights(_segment: Segment, _x: &[f64]) -> Result<Vec<f64>> {
    pending!("line_height")
}
pub fn line_heights_into(_segment: Segment, _x: &[f64], _out: &mut [f64]) -> Result<()> {
    pending!("line_height")
}
pub fn segment_point(_segment: Segment, _t: f64) -> Result<Point2> {
    pending!("segment_points")
}
pub fn segment_points(_segment: Segment, _t: &[f64]) -> Result<Vec<Point2>> {
    pending!("segment_points")
}
pub fn segment_points_into(_segment: Segment, _t: &[f64], _out: &mut [f64]) -> Result<()> {
    pending!("segment_points")
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn no_fabricated_geometric_answer() {
        let scene = Scene1D::new(&[0.0, 1.0], &[0.0, 0.0]).unwrap();
        assert!(matches!(
            height(scene, 0.5),
            Err(Error::NotImplemented { .. })
        ));
        assert!(matches!(
            lerp(0.0, 1.0, 0.5),
            Err(Error::NotImplemented { .. })
        ));
    }
}
