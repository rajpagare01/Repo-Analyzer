package com.codepulse.repository.controller;

import com.codepulse.repository.dto.*;
import com.codepulse.repository.service.AiReviewService;
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
    private final AiReviewService aiReviewService;

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

    /**
     * Start generating an AI review for a completed repository.
     * Returns 202 Accepted immediately.
     */
    @PostMapping("/{id}/ai-review")
    public ResponseEntity<java.util.Map<String, String>> startAiReview(@PathVariable Long id) {
        aiReviewService.generateReviewInBackground(id);
        java.util.Map<String, String> response = new java.util.HashMap<>();
        response.put("status", "GENERATING");
        response.put("message", "AI review generation started");
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(response);
    }

    /**
     * Get the polling status of an AI review.
     */
    @GetMapping("/{id}/ai-review/status")
    public ResponseEntity<AiReviewStatusResponse> getAiReviewStatus(@PathVariable Long id) {
        ReportResponse report = repositoryService.getReport(id);
        return ResponseEntity.ok(AiReviewStatusResponse.builder()
                .status(report.getAiReviewStatus())
                .failureReason(report.getAiReviewFailureReason())
                .generationTimeSeconds(report.getAiReviewGenerationTimeSeconds())
                .build());
    }

    /**
     * Get a completed AI review for a repository.
     */
    @GetMapping("/{id}/ai-review")
    public ResponseEntity<AiReviewResponse> getAiReview(@PathVariable Long id) {
        return ResponseEntity.ok(aiReviewService.getReview(id));
    }

    /**
     * Generate and download PDF report.
     */
    @GetMapping(value = "/{id}/pdf-report", produces = org.springframework.http.MediaType.APPLICATION_PDF_VALUE)
    public ResponseEntity<byte[]> downloadPdfReport(@PathVariable Long id) {
        byte[] pdfBytes = aiReviewService.generatePdfReport(id);
        org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
        headers.setContentType(org.springframework.http.MediaType.APPLICATION_PDF);
        headers.setContentDispositionFormData("attachment", "CodePulse_Report.pdf");
        return new ResponseEntity<>(pdfBytes, headers, HttpStatus.OK);
    }
}
