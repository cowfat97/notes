package com.example.mcp.infrastructure.persistence;

import com.example.mcp.domain.model.PromptTemplate;
import com.example.mcp.domain.repository.PromptTemplateRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * 提示词模板仓库实现
 * 实现领域仓库接口，提供数据访问功能
 */
@Slf4j
@Repository
@RequiredArgsConstructor
public class PromptTemplateRepositoryImpl implements PromptTemplateRepository {
    
    private final PromptTemplateJpaRepository jpaRepository;
    
    @Override
    public PromptTemplate save(PromptTemplate template) {
        PromptTemplateEntity entity = convertToEntity(template);
        PromptTemplateEntity savedEntity = jpaRepository.save(entity);
        return convertToDomain(savedEntity);
    }
    
    @Override
    public Optional<PromptTemplate> findById(String id) {
        return jpaRepository.findById(id)
                .map(this::convertToDomain);
    }
    
    @Override
    public Optional<PromptTemplate> findByName(String name) {
        return jpaRepository.findByName(name)
                .map(this::convertToDomain);
    }
    
    @Override
    public List<PromptTemplate> findAll() {
        return jpaRepository.findAll().stream()
                .map(this::convertToDomain)
                .collect(Collectors.toList());
    }
    
    @Override
    public List<PromptTemplate> findByCategory(String category) {
        return jpaRepository.findByCategory(category).stream()
                .map(this::convertToDomain)
                .collect(Collectors.toList());
    }
    
    @Override
    public List<PromptTemplate> search(String keyword) {
        return jpaRepository.search(keyword).stream()
                .map(this::convertToDomain)
                .collect(Collectors.toList());
    }
    
    @Override
    public boolean deleteById(String id) {
        try {
            jpaRepository.deleteById(id);
            return true;
        } catch (Exception e) {
            log.error("Error deleting template with id: {}", id, e);
            return false;
        }
    }
    
    @Override
    public boolean existsById(String id) {
        return jpaRepository.existsById(id);
    }
    
    @Override
    public boolean existsByName(String name) {
        return jpaRepository.existsByName(name);
    }
    
    @Override
    public long count() {
        return jpaRepository.count();
    }
    
    /**
     * 将领域模型转换为JPA实体
     */
    private PromptTemplateEntity convertToEntity(PromptTemplate domain) {
        return PromptTemplateEntity.builder()
                .id(domain.getId())
                .name(domain.getName())
                .description(domain.getDescription())
                .content(domain.getContent())
                .variables(domain.getVariables())
                .category(domain.getCategory())
                .createdAt(domain.getCreatedAt())
                .updatedAt(domain.getUpdatedAt())
                .createdBy(domain.getCreatedBy())
                .enabled(domain.isEnabled())
                .build();
    }
    
    /**
     * 将JPA实体转换为领域模型
     */
    private PromptTemplate convertToDomain(PromptTemplateEntity entity) {
        return PromptTemplate.builder()
                .id(entity.getId())
                .name(entity.getName())
                .description(entity.getDescription())
                .content(entity.getContent())
                .variables(entity.getVariables())
                .category(entity.getCategory())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .createdBy(entity.getCreatedBy())
                .enabled(entity.isEnabled())
                .build();
    }
}
