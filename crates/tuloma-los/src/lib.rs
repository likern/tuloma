//! Independent Rust contracts for a local metric piecewise-linear 1.5D scene.
//!
//! Constructors validate storage. Every geometric query intentionally returns
//! [`Error::NotImplemented`]; implement the algorithms in [`queries`].

mod error;
pub mod queries;
mod scene;
mod types;

pub use error::{Error, Result};
pub use scene::Scene1D;
pub use types::*;

/// This scaffold must not be advertised as a working geometric engine.
pub const ALGORITHMS_IMPLEMENTED: bool = false;
