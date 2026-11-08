use std::fmt;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Error {
    InvalidInput {
        field: &'static str,
        reason: &'static str,
    },
    NotImplemented {
        operation: &'static str,
    },
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::InvalidInput { field, reason } => write!(f, "{field}: {reason}"),
            Self::NotImplemented { operation } => write!(
                f,
                "{operation} is not implemented; add its algorithm in crates/tuloma-los/src/queries.rs"
            ),
        }
    }
}

impl std::error::Error for Error {}

pub type Result<T> = std::result::Result<T, Error>;
