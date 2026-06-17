package com.codepulse.repository.dto;

import com.codepulse.repository.enums.RepositoryStatus;
import lombok.*;

/**
 * Response DTO returned after submitting a repository.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RepositoryResponse {

    private Long id;
    private String repoName;
    private String owner;
    private RepositoryStatus status;
    private String message;
}
