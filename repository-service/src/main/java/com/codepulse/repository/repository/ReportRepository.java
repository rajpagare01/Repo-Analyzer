package com.codepulse.repository.repository;

import com.codepulse.repository.entity.Report;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * JPA repository for Report entity.
 */
@Repository
public interface ReportRepository extends JpaRepository<Report, Long> {

    Optional<Report> findByRepositoryId(Long repositoryId);
}
