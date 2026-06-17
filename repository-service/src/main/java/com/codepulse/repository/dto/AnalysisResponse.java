package com.codepulse.repository.dto;

import lombok.*;

import java.util.Map;

/**
 * DTO for deserializing the Python analysis service response.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AnalysisResponse {

    private Integer readmeScore;
    private Integer testingScore;
    private Integer structureScore;
    private Double overallScore;
    private Integer totalFiles;
    private Integer totalLines;
    private Map<String, Integer> languages;
}
