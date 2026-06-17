package com.codepulse.repository.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * JPA entity representing an analysis report for a repository.
 */
@Entity
@Table(name = "reports")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Report {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "repository_id", nullable = false)
    private RepositoryEntity repository;

    @Column(name = "readme_score", nullable = false)
    private Integer readmeScore;

    @Column(name = "testing_score", nullable = false)
    private Integer testingScore;

    @Column(name = "structure_score", nullable = false)
    private Integer structureScore;

    @Column(name = "overall_score", nullable = false)
    private Double overallScore;

    @Column(name = "total_files")
    private Integer totalFiles;

    @Column(name = "total_lines")
    private Integer totalLines;

    @Column(name = "average_complexity")
    private Double averageComplexity;

    @Column(name = "high_complexity_functions")
    private Integer highComplexityFunctions;

    @Column(name = "complexity_score")
    private Integer complexityScore;

    @Column(name = "maintainability_index")
    private Double maintainabilityIndex;

    @Column(name = "maintainability_score")
    private Integer maintainabilityScore;

    @Column(name = "dependency_count")
    private Integer dependencyCount;

    @Column(name = "package_manager")
    private String packageManager;

    @Column(name = "long_methods")
    private Integer longMethods;

    @Column(name = "large_classes")
    private Integer largeClasses;

    @Column(name = "deep_nesting")
    private Integer deepNesting;

    @Column(name = "quality_score")
    private Double qualityScore;

    @Column(columnDefinition = "TEXT")
    private String languages;

    @Column(name = "generated_at", nullable = false, updatable = false)
    private LocalDateTime generatedAt;

    @PrePersist
    protected void onCreate() {
        this.generatedAt = LocalDateTime.now();
    }
}
