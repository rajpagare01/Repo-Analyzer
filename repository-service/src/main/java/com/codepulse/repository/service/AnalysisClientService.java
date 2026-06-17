package com.codepulse.repository.service;

import com.codepulse.repository.dto.AnalysisResponse;
import com.codepulse.repository.exception.AnalysisException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.util.Map;

/**
 * Client service for communicating with the Python analysis service.
 * Uses WebClient for non-blocking HTTP calls.
 */
@Service
@Slf4j
public class AnalysisClientService {

    private final WebClient analysisWebClient;

    public AnalysisClientService(@Qualifier("analysisWebClient") WebClient analysisWebClient) {
        this.analysisWebClient = analysisWebClient;
    }

    /**
     * Calls the Python analysis service to analyze a repository.
     *
     * @param repoUrl the GitHub repository URL
     * @return AnalysisResponse with scores and metrics
     * @throws AnalysisException if the analysis service fails or is unreachable
     */
    public AnalysisResponse analyzeRepository(String repoUrl) {
        log.info("Calling analysis service for: {}", repoUrl);

        try {
            AnalysisResponse response = analysisWebClient
                    .post()
                    .uri("/analyze")
                    .bodyValue(Map.of("repoUrl", repoUrl))
                    .retrieve()
                    .onStatus(
                            status -> status.is4xxClientError() || status.is5xxServerError(),
                            clientResponse -> clientResponse.bodyToMono(String.class)
                                    .map(body -> new AnalysisException(
                                            "Analysis service error (" + clientResponse.statusCode() + "): " + body))
                    )
                    .bodyToMono(AnalysisResponse.class)
                    .block();

            if (response == null) {
                throw new AnalysisException("Analysis service returned null response");
            }

            log.info("Analysis complete. Overall score: {}", response.getOverallScore());
            return response;

        } catch (WebClientResponseException e) {
            log.error("Analysis service HTTP error: {} - {}", e.getStatusCode(), e.getResponseBodyAsString());
            throw new AnalysisException("Analysis service returned error: " + e.getMessage(), e);
        } catch (AnalysisException e) {
            throw e;
        } catch (Exception e) {
            log.error("Failed to communicate with analysis service: {}", e.getMessage());
            throw new AnalysisException("Analysis service is unavailable: " + e.getMessage(), e);
        }
    }
}
