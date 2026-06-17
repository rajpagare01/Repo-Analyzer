package com.codepulse.repository.dto;

import com.codepulse.repository.enums.RepositoryStatus;
import lombok.*;

/**
 * Lightweight response DTO for status polling.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StatusResponse {

    private Long id;
    private String repoName;
    private RepositoryStatus status;
}
