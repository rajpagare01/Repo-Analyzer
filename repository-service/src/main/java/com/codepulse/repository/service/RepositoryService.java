package com.codepulse.repository.service;

import com.codepulse.repository.dto.*;
import com.codepulse.repository.entity.*;
import com.codepulse.repository.enums.RepositoryStatus;
import com.codepulse.repository.exception.AnalysisException;
import com.codepulse.repository.exception.RepositoryNotFoundException;
import com.codepulse.repository.repository.*;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Core service handling repository submission, async analysis orchestration,
 * and report retrieval.
 */
@Service
@Slf4j
public class RepositoryService {

    private static final Pattern GITHUB_URL_PATTERN = Pattern.compile(
            "https?://github\\.com/([\\w.\\-]+)/([\\w.\\-]+?)(?:\\.git)?/?$"
    );

    private final RepositoryEntityRepository repositoryRepo;
    private final ReportRepository reportRepo;
    private final GitHubMetadataRepository metadataRepo;
    private final AnalysisClientService analysisClient;
    private final GitHubApiService gitHubApiService;
    private final ObjectMapper objectMapper;

    public RepositoryService(
            RepositoryEntityRepository repositoryRepo,
            ReportRepository reportRepo,
            GitHubMetadataRepository metadataRepo,
            AnalysisClientService analysisClient,
            GitHubApiService gitHubApiService,
            ObjectMapper objectMapper) {
        this.repositoryRepo = repositoryRepo;
        this.reportRepo = reportRepo;
        this.metadataRepo = metadataRepo;
        this.analysisClient = analysisClient;
        this.gitHubApiService = gitHubApiService;
        this.objectMapper = objectMapper;
    }

    /**
     * Submit a repository for analysis.
     * Saves the entity with PENDING status and triggers async analysis.
     *
     * @param request the repository submission request
     * @return response with repository ID and status
     */
    @Transactional
    public RepositoryResponse submitRepository(RepositoryRequest request) {
        String repoUrl = request.getRepoUrl().trim();

        // Parse owner and repo name from URL
        Matcher matcher = GITHUB_URL_PATTERN.matcher(repoUrl);
        if (!matcher.matches()) {
            throw new IllegalArgumentException("Invalid GitHub URL format: " + repoUrl);
        }

        String owner = matcher.group(1);
        String repoName = matcher.group(2);

        // Save repository entity
        RepositoryEntity entity = RepositoryEntity.builder()
                .repoUrl(repoUrl)
                .repoName(repoName)
                .owner(owner)
                .status(RepositoryStatus.PENDING)
                .build();

        entity = repositoryRepo.save(entity);
        log.info("Repository submitted: {}/{} (id={})", owner, repoName, entity.getId());

        // Trigger async analysis
        analyzeInBackground(entity.getId());

        return RepositoryResponse.builder()
                .id(entity.getId())
                .repoName(repoName)
                .owner(owner)
                .status(RepositoryStatus.PENDING)
                .message("Repository submitted successfully. Analysis in progress.")
                .build();
    }

    /**
     * Background analysis task.
     * Updates status to ANALYZING, fetches GitHub metadata, calls Python service,
     * saves report, and updates status to COMPLETED (or FAILED on error).
     */
    @Async("analysisExecutor")
    public void analyzeInBackground(Long repoId) {
        log.info("Starting background analysis for repository id={}", repoId);

        RepositoryEntity entity = repositoryRepo.findById(repoId)
                .orElseThrow(() -> new RepositoryNotFoundException(repoId));

        try {
            // Update status to ANALYZING
            entity.setStatus(RepositoryStatus.ANALYZING);
            repositoryRepo.save(entity);

            // Fetch GitHub metadata (non-critical — failure is OK)
            gitHubApiService.fetchAndSaveMetadata(entity);

            // Call Python analysis service
            AnalysisResponse analysis = analysisClient.analyzeRepository(entity.getRepoUrl());

            // Convert languages map to JSON string for storage
            String languagesJson = null;
            if (analysis.getLanguages() != null && !analysis.getLanguages().isEmpty()) {
                languagesJson = objectMapper.writeValueAsString(analysis.getLanguages());
            }

            // Save report
            Report report = Report.builder()
                    .repository(entity)
                    .readmeScore(analysis.getReadmeScore())
                    .testingScore(analysis.getTestingScore())
                    .structureScore(analysis.getStructureScore())
                    .overallScore(analysis.getOverallScore())
                    .totalFiles(analysis.getTotalFiles())
                    .totalLines(analysis.getTotalLines())
                    .averageComplexity(analysis.getAverageComplexity())
                    .highComplexityFunctions(analysis.getHighComplexityFunctions())
                    .complexityScore(analysis.getComplexityScore())
                    .maintainabilityIndex(analysis.getMaintainabilityIndex())
                    .maintainabilityScore(analysis.getMaintainabilityScore())
                    .dependencyCount(analysis.getDependencyCount())
                    .packageManager(analysis.getPackageManager())
                    .longMethods(analysis.getLongMethods())
                    .largeClasses(analysis.getLargeClasses())
                    .deepNesting(analysis.getDeepNesting())
                    .qualityScore(analysis.getQualityScore())
                    .securityScore(analysis.getSecurityScore())
                    .hardcodedPasswords(analysis.getHardcodedPasswords())
                    .apiKeys(analysis.getApiKeys())
                    .awsKeys(analysis.getAwsKeys())
                    .jwtSecrets(analysis.getJwtSecrets())
                    .databaseCredentials(analysis.getDatabaseCredentials())
                    .dangerousConfigs(analysis.getDangerousConfigs())
                    .sensitiveVariables(analysis.getSensitiveVariables())
                    .privateKeys(analysis.getPrivateKeys())
                    .riskLevel(analysis.getRiskLevel())
                    .securityFindings(analysis.getSecurityFindings())
                    .vulnerableDependencies(analysis.getVulnerableDependencies())
                    .languages(languagesJson)
                    .build();

            reportRepo.save(report);

            // Update status to COMPLETED
            entity.setStatus(RepositoryStatus.COMPLETED);
            repositoryRepo.save(entity);

            log.info("Analysis completed for repository id={}, overall score={}",
                    repoId, analysis.getOverallScore());

        } catch (Exception e) {
            log.error("Analysis failed for repository id={}: {}", repoId, e.getMessage());
            entity.setStatus(RepositoryStatus.FAILED);
            repositoryRepo.save(entity);
        }
    }

    /**
     * Get the analysis status of a repository.
     */
    public StatusResponse getStatus(Long id) {
        RepositoryEntity entity = repositoryRepo.findById(id)
                .orElseThrow(() -> new RepositoryNotFoundException(id));

        return StatusResponse.builder()
                .id(entity.getId())
                .repoName(entity.getRepoName())
                .status(entity.getStatus())
                .build();
    }

    /**
     * Get the full analysis report for a repository.
     */
    public ReportResponse getReport(Long id) {
        RepositoryEntity entity = repositoryRepo.findById(id)
                .orElseThrow(() -> new RepositoryNotFoundException(id));

        if (entity.getStatus() != RepositoryStatus.COMPLETED) {
            throw new AnalysisException(
                    "Report not ready. Current status: " + entity.getStatus());
        }

        Report report = reportRepo.findByRepositoryId(id)
                .orElseThrow(() -> new RepositoryNotFoundException(
                        "Report not found for repository id: " + id));

        // Parse languages JSON
        Map<String, Integer> languages = null;
        if (report.getLanguages() != null) {
            try {
                languages = objectMapper.readValue(
                        report.getLanguages(),
                        new TypeReference<Map<String, Integer>>() {}
                );
            } catch (Exception e) {
                log.warn("Failed to parse languages JSON: {}", e.getMessage());
            }
        }

        // Fetch GitHub metadata (may be null)
        GitHubMetadata metadata = metadataRepo.findByRepositoryId(id).orElse(null);

        ReportResponse.ReportResponseBuilder responseBuilder = ReportResponse.builder()
                .repoName(entity.getRepoName())
                .owner(entity.getOwner())
                .readmeScore(report.getReadmeScore())
                .testingScore(report.getTestingScore())
                .structureScore(report.getStructureScore())
                .overallScore(report.getOverallScore())
                .totalFiles(report.getTotalFiles())
                .totalLines(report.getTotalLines())
                .averageComplexity(report.getAverageComplexity())
                .highComplexityFunctions(report.getHighComplexityFunctions())
                .complexityScore(report.getComplexityScore())
                .maintainabilityIndex(report.getMaintainabilityIndex())
                .maintainabilityScore(report.getMaintainabilityScore())
                .dependencyCount(report.getDependencyCount())
                .packageManager(report.getPackageManager())
                .longMethods(report.getLongMethods())
                .largeClasses(report.getLargeClasses())
                .deepNesting(report.getDeepNesting())
                .qualityScore(report.getQualityScore())
                .securityScore(report.getSecurityScore())
                .hardcodedPasswords(report.getHardcodedPasswords())
                .apiKeys(report.getApiKeys())
                .awsKeys(report.getAwsKeys())
                .jwtSecrets(report.getJwtSecrets())
                .databaseCredentials(report.getDatabaseCredentials())
                .dangerousConfigs(report.getDangerousConfigs())
                .sensitiveVariables(report.getSensitiveVariables())
                .privateKeys(report.getPrivateKeys())
                .riskLevel(report.getRiskLevel())
                .securityFindings(report.getSecurityFindings())
                .vulnerableDependencies(report.getVulnerableDependencies())
                .languages(languages)
                .aiReviewStatus(report.getAiReviewStatus())
                .aiReviewFailureReason(report.getAiReviewFailureReason())
                .aiReviewGenerationTimeSeconds(report.getAiReviewGenerationTimeSeconds());

        if (metadata != null) {
            responseBuilder
                    .stars(metadata.getStars())
                    .forks(metadata.getForks())
                    .openIssues(metadata.getOpenIssues())
                    .defaultBranch(metadata.getDefaultBranch())
                    .lastCommitDate(metadata.getLastCommitDate() != null
                            ? metadata.getLastCommitDate().toString() : null)
                    .description(metadata.getDescription());
        }

        return responseBuilder.build();
    }

    /**
     * Get all submitted repositories ordered by creation date.
     */
    public List<RepositoryResponse> getAllRepositories() {
        return repositoryRepo.findAllByOrderByCreatedAtDesc().stream()
                .map(entity -> RepositoryResponse.builder()
                        .id(entity.getId())
                        .repoName(entity.getRepoName())
                        .owner(entity.getOwner())
                        .status(entity.getStatus())
                        .build())
                .collect(Collectors.toList());
    }
}
