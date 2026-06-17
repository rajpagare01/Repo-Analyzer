package com.codepulse.repository;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * CodePulse AI — Repository Service
 * 
 * Main entry point for the Spring Boot application.
 * Enables async processing for background repository analysis.
 */
@SpringBootApplication
@EnableAsync
public class CodePulseApplication {

    public static void main(String[] args) {
        SpringApplication.run(CodePulseApplication.class, args);
    }
}
