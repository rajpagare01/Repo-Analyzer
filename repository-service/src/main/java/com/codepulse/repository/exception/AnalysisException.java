package com.codepulse.repository.exception;

/**
 * Thrown when the analysis service fails or is unreachable.
 */
public class AnalysisException extends RuntimeException {

    public AnalysisException(String message) {
        super(message);
    }

    public AnalysisException(String message, Throwable cause) {
        super(message, cause);
    }
}
