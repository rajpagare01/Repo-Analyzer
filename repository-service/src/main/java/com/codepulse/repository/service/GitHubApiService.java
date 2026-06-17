package com.codepulse.repository.service;

import com.codepulse.repository.entity.GitHubMetadata;
import com.codepulse.repository.entity.RepositoryEntity;
import com.codepulse.repository.repository.GitHubMetadataRepository;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Service for fetching repository metadata from the GitHub API.
 * Uses WebClient for non-blocking HTTP calls.
 */
@Service
@Slf4j
public class GitHubApiService {

    private final WebClient githubWebClient;
    private final GitHubMetadataRepository metadataRepository;

    public GitHubApiService(
            @Qualifier("githubWebClient") WebClient githubWebClient,
            GitHubMetadataRepository metadataRepository) {
        this.githubWebClient = githubWebClient;
        this.metadataRepository = metadataRepository;
    }

    /**
     * Fetch metadata from GitHub API and save it.
     * Gracefully handles failures — metadata is enrichment, not critical.
     *
     * @param repoEntity the repository entity
     * @return saved GitHubMetadata or null if fetch failed
     */
    public GitHubMetadata fetchAndSaveMetadata(RepositoryEntity repoEntity) {
        String owner = repoEntity.getOwner();
        String repoName = repoEntity.getRepoName();
        log.info("Fetching GitHub metadata for {}/{}", owner, repoName);

        try {
            JsonNode json = githubWebClient
                    .get()
                    .uri("/repos/{owner}/{repo}", owner, repoName)
                    .retrieve()
                    .onStatus(
                            status -> status.is4xxClientError() || status.is5xxServerError(),
                            response -> {
                                log.warn("GitHub API returned {}", response.statusCode());
                                return response.createException();
                            }
                    )
                    .bodyToMono(JsonNode.class)
                    .block();

            if (json == null) {
                log.warn("GitHub API returned null for {}/{}", owner, repoName);
                return null;
            }

            GitHubMetadata metadata = GitHubMetadata.builder()
                    .repository(repoEntity)
                    .stars(json.path("stargazers_count").asInt(0))
                    .forks(json.path("forks_count").asInt(0))
                    .openIssues(json.path("open_issues_count").asInt(0))
                    .defaultBranch(json.path("default_branch").asText("main"))
                    .description(json.path("description").asText(null))
                    .lastCommitDate(parseDate(json.path("pushed_at").asText(null)))
                    .build();

            return metadataRepository.save(metadata);

        } catch (Exception e) {
            log.warn("Failed to fetch GitHub metadata for {}/{}: {}", owner, repoName, e.getMessage());
            return null;
        }
    }

    /**
     * Parse ISO 8601 date from GitHub API response.
     */
    private LocalDateTime parseDate(String dateStr) {
        if (dateStr == null || dateStr.isEmpty()) {
            return null;
        }
        try {
            return LocalDateTime.parse(dateStr, DateTimeFormatter.ISO_DATE_TIME);
        } catch (Exception e) {
            log.debug("Could not parse date: {}", dateStr);
            return null;
        }
    }
}
