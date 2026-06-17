package com.codepulse.repository.controller;

import com.codepulse.repository.dto.*;
import com.codepulse.repository.service.RepositoryService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST controller for repository operations.
 * Provides endpoints for submitting, listing, polling status, and retrieving reports.
 */
@RestController
@RequestMapping("/api/repositories")
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:5173"})
@RequiredArgsConstructor
public class RepositoryController {

    private final RepositoryService repositoryService;

    /**
     * Submit a GitHub repository for analysis.
     * Returns immediately with PENDING status; analysis runs in the background.
     */
    @PostMapping
    public ResponseEntity<RepositoryResponse> submitRepository(
            @Valid @RequestBody RepositoryRequest request) {
        RepositoryResponse response = repositoryService.submitRepository(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * List all submitted repositories.
     */
    @GetMapping
    public ResponseEntity<List<RepositoryResponse>> getAllRepositories() {
        return ResponseEntity.ok(repositoryService.getAllRepositories());
    }

    /**
     * Poll the analysis status of a repository.
     * Use this for frontend polling while analysis is in progress.
     */
    @GetMapping("/{id}/status")
    public ResponseEntity<StatusResponse> getStatus(@PathVariable Long id) {
        return ResponseEntity.ok(repositoryService.getStatus(id));
    }

    /**
     * Get the full analysis report for a completed repository.
     * Returns 400 if analysis is not yet complete.
     */
    @GetMapping("/{id}/report")
    public ResponseEntity<ReportResponse> getReport(@PathVariable Long id) {
        return ResponseEntity.ok(repositoryService.getReport(id));
    }
}
