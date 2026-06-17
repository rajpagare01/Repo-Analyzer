package com.codepulse.repository.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * JPA entity for GitHub metadata enrichment.
 * Stores stars, forks, issues, and other GitHub API data.
 */
@Entity
@Table(name = "github_metadata")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GitHubMetadata {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "repository_id", nullable = false, unique = true)
    private RepositoryEntity repository;

    @Column(nullable = false)
    @Builder.Default
    private Integer stars = 0;

    @Column(nullable = false)
    @Builder.Default
    private Integer forks = 0;

    @Column(name = "open_issues", nullable = false)
    @Builder.Default
    private Integer openIssues = 0;

    @Column(name = "default_branch", length = 100)
    private String defaultBranch;

    @Column(name = "last_commit_date")
    private LocalDateTime lastCommitDate;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "fetched_at", nullable = false, updatable = false)
    private LocalDateTime fetchedAt;

    @PrePersist
    protected void onCreate() {
        this.fetchedAt = LocalDateTime.now();
    }
}
