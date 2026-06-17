package com.codepulse.repository.repository;

import com.codepulse.repository.entity.GitHubMetadata;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * JPA repository for GitHubMetadata entity.
 */
@Repository
public interface GitHubMetadataRepository extends JpaRepository<GitHubMetadata, Long> {

    Optional<GitHubMetadata> findByRepositoryId(Long repositoryId);
}
