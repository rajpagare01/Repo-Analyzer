package com.codepulse.repository.dto;

import com.codepulse.repository.enums.AiReviewStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AiReviewStatusResponse {
    private AiReviewStatus status;
    private String failureReason;
    private Long generationTimeSeconds;
}
