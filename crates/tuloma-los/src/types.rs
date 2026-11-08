/// Coordinates in a single declared local planar frame, in metres.
pub type Point2 = [f64; 2];

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Location {
    Above,
    On,
    Below,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Visibility {
    Visible,
    Touch,
    Blocked,
    SameX,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum TouchPolicy {
    Allow,
    Block,
}

/// Codes used by the uint8 array in Python Contacts.kinds.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum ContactKind {
    Enter = 1,
    Exit = 2,
    Touch = 3,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Extremum {
    pub value: f64,
    pub point: Point2,
    pub parameter: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ClearanceExtrema {
    pub minimum: Extremum,
    pub maximum: Extremum,
}

/// Clipped endpoints and original terrain knots, ordered along A -> B.
#[derive(Clone, Debug, PartialEq)]
pub struct ClearanceProfile {
    pub parameters: Vec<f64>,
    pub clearance: Vec<f64>,
}

/// Isolated points are unique and ordered along A -> B. Overlaps are intervals
/// in t, not x; a nonempty interval contains infinitely many contact points.
#[derive(Clone, Debug, PartialEq)]
pub struct Contacts {
    pub points: Vec<Point2>,
    pub parameters: Vec<f64>,
    pub kinds: Vec<ContactKind>,
    pub overlaps: Vec<[f64; 2]>,
}

/// Arguments shared by the immediate scene queries. No plan or execution cache.
#[derive(Clone, Copy, Debug)]
pub struct Segment {
    pub a: Point2,
    pub b: Point2,
}
