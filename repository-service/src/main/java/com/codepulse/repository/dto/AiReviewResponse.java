package com.codepulse.repository.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiReviewResponse {
    private String repositoryGrade;
    private Integer confidenceScore;
    private String executiveSummary;
    private List<String> strengths;
    private List<String> weaknesses;
    private List<Map<String, String>> securityRisks;
    private List<Map<String, String>> codeQualityRisks;
    private List<String> architectureRecommendations;
    private List<Map<String, String>> recommendations;
}
