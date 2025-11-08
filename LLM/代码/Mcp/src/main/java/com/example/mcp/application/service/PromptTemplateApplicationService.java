package com.example.mcp.application.service;

import com.example.mcp.domain.model.PromptTemplate;
import com.example.mcp.domain.repository.PromptTemplateRepository;
import com.example.mcp.domain.service.PromptTemplateService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 提示词模板应用服务
 * 协调领域服务，处理提示词模板的业务流程
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class PromptTemplateApplicationService implements PromptTemplateService {
    
    private final PromptTemplateRepository promptTemplateRepository;
    
    @Override
    public PromptTemplate createTemplate(PromptTemplate template) {
        log.info("Creating prompt template: {}", template.getName());
        
        // 验证模板
        if (!template.isValid()) {
            throw new IllegalArgumentException("Invalid template data");
        }
        
        // 检查名称是否已存在
        if (promptTemplateRepository.existsByName(template.getName())) {
            throw new IllegalArgumentException("Template name already exists: " + template.getName());
        }
        
        // 设置ID和创建时间
        template.setId(UUID.randomUUID().toString());
        template.setCreatedAt(LocalDateTime.now());
        template.setUpdatedAt(LocalDateTime.now());
        
        return promptTemplateRepository.save(template);
    }
    
    @Override
    public PromptTemplate updateTemplate(PromptTemplate template) {
        log.info("Updating prompt template: {}", template.getId());
        
        // 验证模板
        if (!template.isValid()) {
            throw new IllegalArgumentException("Invalid template data");
        }
        
        // 检查模板是否存在
        if (!promptTemplateRepository.existsById(template.getId())) {
            throw new IllegalArgumentException("Template not found: " + template.getId());
        }
        
        // 检查名称冲突（排除自己）
        PromptTemplate existing = promptTemplateRepository.findById(template.getId()).orElse(null);
        if (existing != null && !existing.getName().equals(template.getName())) {
            if (promptTemplateRepository.existsByName(template.getName())) {
                throw new IllegalArgumentException("Template name already exists: " + template.getName());
            }
        }
        
        template.setUpdatedAt(LocalDateTime.now());
        return promptTemplateRepository.save(template);
    }
    
    @Override
    public boolean deleteTemplate(String templateId) {
        log.info("Deleting prompt template: {}", templateId);
        
        if (!promptTemplateRepository.existsById(templateId)) {
            return false;
        }
        
        return promptTemplateRepository.deleteById(templateId);
    }
    
    @Override
    public PromptTemplate getTemplateById(String templateId) {
        return promptTemplateRepository.findById(templateId).orElse(null);
    }
    
    @Override
    public PromptTemplate getTemplateByName(String name) {
        return promptTemplateRepository.findByName(name).orElse(null);
    }
    
    @Override
    public List<PromptTemplate> getAllTemplates() {
        return promptTemplateRepository.findAll();
    }
    
    @Override
    public List<PromptTemplate> getTemplatesByCategory(String category) {
        return promptTemplateRepository.findByCategory(category);
    }
    
    @Override
    public List<PromptTemplate> searchTemplates(String keyword) {
        return promptTemplateRepository.search(keyword);
    }
    
    @Override
    public String renderTemplate(String templateId, Map<String, String> variables) {
        PromptTemplate template = getTemplateById(templateId);
        if (template == null) {
            throw new IllegalArgumentException("Template not found: " + templateId);
        }
        
        return renderTemplate(template, variables);
    }
    
    @Override
    public String renderTemplate(PromptTemplate template, Map<String, String> variables) {
        if (template == null) {
            throw new IllegalArgumentException("Template cannot be null");
        }
        
        if (!template.isEnabled()) {
            throw new IllegalStateException("Template is disabled: " + template.getId());
        }
        
        return template.render(variables);
    }
    
    @Override
    public boolean enableTemplate(String templateId) {
        PromptTemplate template = getTemplateById(templateId);
        if (template == null) {
            return false;
        }
        
        template.enable();
        promptTemplateRepository.save(template);
        return true;
    }
    
    @Override
    public boolean disableTemplate(String templateId) {
        PromptTemplate template = getTemplateById(templateId);
        if (template == null) {
            return false;
        }
        
        template.disable();
        promptTemplateRepository.save(template);
        return true;
    }
}
