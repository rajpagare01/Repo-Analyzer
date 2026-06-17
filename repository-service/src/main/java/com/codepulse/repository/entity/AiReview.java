package com.codepulse.repository.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "ai_reviews")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiReview {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "report_id", nullable = false)
    private Report report;

    @Column(nullable = false, length = 50)
    private String provider; // ollama, gemini, openai

    @Column(name = "repository_grade", nullable = false, length = 10)
    private String repositoryGrade;

    @Column(name = "confidence_score")
    private Integer confidenceScore;

    @Column(name = "executive_summary", columnDefinition = "TEXT")
    private String executiveSummary;

    @Column(name = "strengths", columnDefinition = "JSON")
    private String strengths;

    @Column(name = "weaknesses", columnDefinition = "JSON")
    private String weaknesses;

    @Column(name = "security_risks", columnDefinition = "JSON")
    private String securityRisks;

    @Column(name = "code_quality_risks", columnDefinition = "JSON")
    private String codeQualityRisks;

    @Column(name = "architecture_recommendations", columnDefinition = "JSON")
    private String architectureRecommendations;

    @Column(name = "recommendations", columnDefinition = "JSON")
    private String recommendations;

    @Column(name = "generated_at", nullable = false, updatable = false)
    private LocalDateTime generatedAt;

    @PrePersist
    protected void onCreate() {
        this.generatedAt = LocalDateTime.now();
    }
}
