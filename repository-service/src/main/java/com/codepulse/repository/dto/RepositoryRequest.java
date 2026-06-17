package com.codepulse.repository.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request DTO for submitting a GitHub repository for analysis.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RepositoryRequest {

    @NotBlank(message = "Repository URL is required")
    @Pattern(
        regexp = "^https?://github\\.com/[\\w.\\-]+/[\\w.\\-]+(?:\\.git)?/?$",
        message = "Invalid GitHub repository URL format. Expected: https://github.com/owner/repo"
    )
    private String repoUrl;
}
