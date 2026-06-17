package com.codepulse.repository.exception;

/**
 * Thrown when a repository is not found by ID.
 */
public class RepositoryNotFoundException extends RuntimeException {

    public RepositoryNotFoundException(Long id) {
        super("Repository not found with id: " + id);
    }

    public RepositoryNotFoundException(String message) {
        super(message);
    }
}
