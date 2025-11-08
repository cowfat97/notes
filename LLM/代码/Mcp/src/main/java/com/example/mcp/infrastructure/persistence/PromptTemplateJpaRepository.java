package com.example.mcp.infrastructure.persistence;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 提示词模板JPA仓库接口
 * 提供数据库访问方法
 */
@Repository
public interface PromptTemplateJpaRepository extends JpaRepository<PromptTemplateEntity, String> {
    
    /**
     * 根据名称查找模板
     */
    Optional<PromptTemplateEntity> findByName(String name);
    
    /**
     * 根据分类查找模板
     */
    List<PromptTemplateEntity> findByCategory(String category);
    
    /**
     * 根据名称检查是否存在
     */
    boolean existsByName(String name);
    
    /**
     * 搜索模板（按名称或描述）
     */
    @Query("SELECT p FROM PromptTemplateEntity p WHERE " +
           "LOWER(p.name) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           "LOWER(p.description) LIKE LOWER(CONCAT('%', :keyword, '%')) OR " +
           "LOWER(p.content) LIKE LOWER(CONCAT('%', :keyword, '%'))")
    List<PromptTemplateEntity> search(@Param("keyword") String keyword);
    
    /**
     * 查找启用的模板
     */
    List<PromptTemplateEntity> findByEnabledTrue();
    
    /**
     * 根据分类和启用状态查找模板
     */
    List<PromptTemplateEntity> findByCategoryAndEnabledTrue(String category);
}
