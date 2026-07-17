// fastcount/src/lib.rs
use pyo3::prelude::*;

#[pyfunction]
fn count_primes(limit: u64) -> u64 {
    let mut count = 0;
    for n in 2..limit {
        let mut d = 2;
        let mut prime = true;
        while d * d <= n {
            if n % d == 0 {
                prime = false;
                break;
            }
            d += 1;
        }
        if prime {
            count += 1;
        }
    }
    count
}

#[pyfunction]
fn collatz_lengths(values: Vec<u64>) -> Vec<u64> {
    values
        .into_iter()
        .map(|start| {
            let mut n = start;
            let mut steps = 0;
            while n != 1 {
                n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
                steps += 1;
            }
            steps
        })
        .collect()
}

#[pymodule]
fn fastcount(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(count_primes, m)?)?;
    m.add_function(wrap_pyfunction!(collatz_lengths, m)?)?;
    Ok(())
}
