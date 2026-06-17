package com.codepulse.repository.repository;

import com.codepulse.repository.entity.AiReview;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AiReviewRepository extends JpaRepository<AiReview, Long> {
    Optional<AiReview> findByReportId(Long reportId);
}
