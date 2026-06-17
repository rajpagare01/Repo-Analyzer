package com.codepulse.repository.dto;

import lombok.*;

import java.util.Map;

/**
 * Response DTO for the full analysis report.
 * Includes scores, metrics, and GitHub metadata.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportResponse {

    private String repoName;
    private String owner;
    private Integer readmeScore;
    private Integer testingScore;
    private Integer structureScore;
    private Double overallScore;
    private Integer totalFiles;
    private Integer totalLines;
    
    private Double averageComplexity;
    private Integer highComplexityFunctions;
    private Integer complexityScore;
    
    private Double maintainabilityIndex;
    private Integer maintainabilityScore;
    
    private Integer dependencyCount;
    private String packageManager;
    
    private Integer longMethods;
    private Integer largeClasses;
    private Integer deepNesting;
    
    private Double qualityScore;

    private Map<String, Integer> languages;

    // GitHub metadata
    private Integer stars;
    private Integer forks;
    private Integer openIssues;
    private String defaultBranch;
    private String lastCommitDate;
    private String description;
}
