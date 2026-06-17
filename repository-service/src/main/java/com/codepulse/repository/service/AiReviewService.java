package com.codepulse.repository.service;

import com.codepulse.repository.dto.AiReviewResponse;
import com.codepulse.repository.entity.AiReview;
import com.codepulse.repository.entity.Report;
import com.codepulse.repository.repository.AiReviewRepository;
import com.codepulse.repository.repository.ReportRepository;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class AiReviewService {

    private final AiReviewRepository aiReviewRepository;
    private final ReportRepository reportRepository;
    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    @Value("${analysis.service.url:http://localhost:5000}")
    private String analysisServiceUrl;

    public AiReviewResponse getOrGenerateReview(Long reportId) {
        Optional<AiReview> existingReview = aiReviewRepository.findByReportId(reportId);
        
        if (existingReview.isPresent()) {
            log.info("Returning cached AI review for report {}", reportId);
            return mapToDto(existingReview.get());
        }

        log.info("Generating new AI review for report {}", reportId);
        Report report = reportRepository.findById(reportId)
                .orElseThrow(() -> new RuntimeException("Report not found"));

        Map<String, Object> metrics = new HashMap<>();
        metrics.put("qualityScore", report.getQualityScore());
        metrics.put("securityScore", report.getSecurityScore());
        metrics.put("readmeScore", report.getReadmeScore());
        metrics.put("testingScore", report.getTestingScore());
        metrics.put("structureScore", report.getStructureScore());
        metrics.put("maintainabilityScore", report.getMaintainabilityScore());
        metrics.put("complexityScore", report.getComplexityScore());
        metrics.put("longMethods", report.getLongMethods());
        metrics.put("largeClasses", report.getLargeClasses());
        metrics.put("deepNesting", report.getDeepNesting());
        metrics.put("dependencyCount", report.getDependencyCount());
        metrics.put("hardcodedPasswords", report.getHardcodedPasswords());
        metrics.put("apiKeys", report.getApiKeys());
        metrics.put("awsKeys", report.getAwsKeys());
        metrics.put("jwtSecrets", report.getJwtSecrets());
        metrics.put("databaseCredentials", report.getDatabaseCredentials());
        metrics.put("privateKeys", report.getPrivateKeys());

        try {
            String aiResponseStr = webClient.post()
                    .uri(analysisServiceUrl + "/api/v1/ai-review")
                    .bodyValue(metrics)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            AiReviewResponse responseDto = objectMapper.readValue(aiResponseStr, AiReviewResponse.class);
            
            AiReview aiReview = AiReview.builder()
                    .report(report)
                    .provider("ollama") // Configured in python mostly, hardcoded here as generic provider cache info
                    .repositoryGrade(responseDto.getRepositoryGrade())
                    .confidenceScore(responseDto.getConfidenceScore())
                    .executiveSummary(responseDto.getExecutiveSummary())
                    .strengths(objectMapper.writeValueAsString(responseDto.getStrengths()))
                    .weaknesses(objectMapper.writeValueAsString(responseDto.getWeaknesses()))
                    .securityRisks(objectMapper.writeValueAsString(responseDto.getSecurityRisks()))
                    .codeQualityRisks(objectMapper.writeValueAsString(responseDto.getCodeQualityRisks()))
                    .architectureRecommendations(objectMapper.writeValueAsString(responseDto.getArchitectureRecommendations()))
                    .recommendations(objectMapper.writeValueAsString(responseDto.getRecommendations()))
                    .build();

            aiReviewRepository.save(aiReview);
            return responseDto;

        } catch (Exception e) {
            log.error("Failed to generate AI review", e);
            throw new RuntimeException("AI Review Generation Failed: " + e.getMessage());
        }
    }

    private AiReviewResponse mapToDto(AiReview aiReview) {
        try {
            return AiReviewResponse.builder()
                    .repositoryGrade(aiReview.getRepositoryGrade())
                    .confidenceScore(aiReview.getConfidenceScore())
                    .executiveSummary(aiReview.getExecutiveSummary())
                    .strengths(objectMapper.readValue(aiReview.getStrengths(), new TypeReference<List<String>>() {}))
                    .weaknesses(objectMapper.readValue(aiReview.getWeaknesses(), new TypeReference<List<String>>() {}))
                    .securityRisks(objectMapper.readValue(aiReview.getSecurityRisks(), new TypeReference<List<Map<String, String>>>() {}))
                    .codeQualityRisks(objectMapper.readValue(aiReview.getCodeQualityRisks(), new TypeReference<List<Map<String, String>>>() {}))
                    .architectureRecommendations(objectMapper.readValue(aiReview.getArchitectureRecommendations(), new TypeReference<List<String>>() {}))
                    .recommendations(objectMapper.readValue(aiReview.getRecommendations(), new TypeReference<List<Map<String, String>>>() {}))
                    .build();
        } catch (JsonProcessingException e) {
            log.error("Failed to parse AI review JSON", e);
            throw new RuntimeException("Error parsing cached AI review");
        }
    }

    public byte[] generatePdfReport(Long reportId) {
        AiReviewResponse review = getOrGenerateReview(reportId);
        
        Report report = reportRepository.findById(reportId)
                .orElseThrow(() -> new RuntimeException("Report not found"));

        Map<String, Object> metrics = new HashMap<>();
        metrics.put("qualityScore", report.getQualityScore());
        metrics.put("securityScore", report.getSecurityScore());
        metrics.put("maintainabilityScore", report.getMaintainabilityScore());
        metrics.put("dependencyCount", report.getDependencyCount());

        Map<String, Object> payload = new HashMap<>();
        payload.put("metrics", metrics);
        payload.put("review", review);

        try {
            return webClient.post()
                    .uri(analysisServiceUrl + "/api/v1/pdf-report")
                    .bodyValue(payload)
                    .retrieve()
                    .bodyToMono(byte[].class)
                    .block();
        } catch (Exception e) {
            log.error("Failed to generate PDF report", e);
            throw new RuntimeException("PDF Generation Failed: " + e.getMessage());
        }
    }
}
