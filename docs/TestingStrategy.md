# Testing Strategy

To ensure software quality, stability, and robustness, an automated test suite was developed using Python's built-in `unittest` framework.

## 1. Edge Cases & Mathematical Validation
The system is tested under extreme scenarios to verify that it handles errors gracefully rather than crashing:
- **Collinear Points:** Passing 3 points that lie exactly on the same line. Ensures the validation system catches the mathematical impossibility and raises a `ValueError`.
- **Non-Planar Points:** Passing 4 points where one deviates from the plane of the other three. The validation logic detects this deviation via the dot product and raises an error.
- **Memory Overflow:** Passing astronomical distances that threaten to exhaust system RAM (e.g., a 100,000x100,000 grid). The system intercepts this and raises a `MemoryError`.
- **Out of Bounds:** Requesting pixels located far outside the brain scan's actual dimensions. The system prevents a crash and returns a black image matrix (zeros).
- **Garbage File:** Handling corrupted CSV files that do not contain data in the expected format.

## 2. Integration & Performance
- **Direct Match:** Extracting an algorithmic slice parallel to extracting a slice directly from the raw matrix, verifying that the standard deviation between them is negligible (accounting only for interpolation smoothing).
- **Performance Test:** A comprehensive benchmark measuring actual execution times, ensuring the system processes planes at a rate significantly higher than the required threshold of 30 FPS.