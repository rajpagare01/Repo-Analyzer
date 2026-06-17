package com.codepulse.repository.repository;

import com.codepulse.repository.entity.RepositoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * JPA repository for RepositoryEntity.
 */
@Repository
public interface RepositoryEntityRepository extends JpaRepository<RepositoryEntity, Long> {

    List<RepositoryEntity> findAllByOrderByCreatedAtDesc();
}
