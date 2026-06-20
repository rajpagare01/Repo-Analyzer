package com.codepulse.repository.config;

import io.netty.channel.ChannelOption;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;

/**
 * WebClient configuration providing named beans for inter-service communication.
 */
@Configuration
public class WebClientConfig {

    @Value("${codepulse.analysis-service.url:http://localhost:5000}")
    private String analysisServiceUrl;

    @Value("${codepulse.github-api.url:https://api.github.com}")
    private String githubApiUrl;

    @Bean(name = "analysisWebClient")
    public WebClient analysisWebClient(WebClient.Builder builder) {
        HttpClient httpClient = HttpClient.create()
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
                .responseTimeout(Duration.ofSeconds(900));

        return builder
                .baseUrl(analysisServiceUrl)
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }

    @Bean(name = "githubWebClient")
    public WebClient githubWebClient(WebClient.Builder builder) {
        HttpClient httpClient = HttpClient.create()
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5000)
                .responseTimeout(Duration.ofSeconds(30));

        return builder
                .baseUrl(githubApiUrl)
                .defaultHeader("Accept", "application/vnd.github.v3+json")
                .defaultHeader("User-Agent", "CodePulse-AI")
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }
}
