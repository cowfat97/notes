package com.example.mcp.interfaces.controller;

import com.example.mcp.application.service.PromptTemplateApplicationService;
import com.example.mcp.domain.model.PromptTemplate;
import com.example.mcp.interfaces.dto.CreatePromptTemplateRequest;
import com.example.mcp.interfaces.dto.UpdatePromptTemplateRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 提示词模板控制器
 * 提供提示词模板的REST API接口
 */
@Slf4j
@RestController
@RequestMapping("/api/prompt-templates")
@RequiredArgsConstructor
public class PromptTemplateController {
    
    private final PromptTemplateApplicationService promptTemplateService;
    
    /**
     * 创建提示词模板
     */
    @PostMapping
    public ResponseEntity<PromptTemplate> createTemplate(@RequestBody CreatePromptTemplateRequest request) {
        try {
            PromptTemplate template = PromptTemplate.builder()
                    .name(request.getName())
                    .description(request.getDescription())
                    .content(request.getContent())
                    .variables(request.getVariables())
                    .category(request.getCategory())
                    .createdBy(request.getCreatedBy())
                    .enabled(true)
                    .build();
            
            PromptTemplate created = promptTemplateService.createTemplate(template);
            return ResponseEntity.ok(created);
            
        } catch (Exception e) {
            log.error("Error creating prompt template", e);
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 更新提示词模板
     */
    @PutMapping("/{id}")
    public ResponseEntity<PromptTemplate> updateTemplate(@PathVariable String id, 
                                                       @RequestBody UpdatePromptTemplateRequest request) {
        try {
            PromptTemplate existing = promptTemplateService.getTemplateById(id);
            if (existing == null) {
                return ResponseEntity.notFound().build();
            }
            
            PromptTemplate updated = PromptTemplate.builder()
                    .id(id)
                    .name(request.getName() != null ? request.getName() : existing.getName())
                    .description(request.getDescription() != null ? request.getDescription() : existing.getDescription())
                    .content(request.getContent() != null ? request.getContent() : existing.getContent())
                    .variables(request.getVariables() != null ? request.getVariables() : existing.getVariables())
                    .category(request.getCategory() != null ? request.getCategory() : existing.getCategory())
                    .createdAt(existing.getCreatedAt())
                    .createdBy(existing.getCreatedBy())
                    .enabled(request.isEnabled())
                    .build();
            
            PromptTemplate result = promptTemplateService.updateTemplate(updated);
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            log.error("Error updating prompt template", e);
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 删除提示词模板
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTemplate(@PathVariable String id) {
        try {
            boolean deleted = promptTemplateService.deleteTemplate(id);
            return deleted ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("Error deleting prompt template", e);
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 获取提示词模板
     */
    @GetMapping("/{id}")
    public ResponseEntity<PromptTemplate> getTemplate(@PathVariable String id) {
        PromptTemplate template = promptTemplateService.getTemplateById(id);
        return template != null ? ResponseEntity.ok(template) : ResponseEntity.notFound().build();
    }
    
    /**
     * 获取所有提示词模板
     */
    @GetMapping
    public ResponseEntity<List<PromptTemplate>> getAllTemplates() {
        List<PromptTemplate> templates = promptTemplateService.getAllTemplates();
        return ResponseEntity.ok(templates);
    }
    
    /**
     * 根据分类获取提示词模板
     */
    @GetMapping("/category/{category}")
    public ResponseEntity<List<PromptTemplate>> getTemplatesByCategory(@PathVariable String category) {
        List<PromptTemplate> templates = promptTemplateService.getTemplatesByCategory(category);
        return ResponseEntity.ok(templates);
    }
    
    /**
     * 搜索提示词模板
     */
    @GetMapping("/search")
    public ResponseEntity<List<PromptTemplate>> searchTemplates(@RequestParam String keyword) {
        List<PromptTemplate> templates = promptTemplateService.searchTemplates(keyword);
        return ResponseEntity.ok(templates);
    }
    
    /**
     * 渲染提示词模板
     */
    @PostMapping("/{id}/render")
    public ResponseEntity<Map<String, String>> renderTemplate(@PathVariable String id, 
                                                            @RequestBody Map<String, String> variables) {
        try {
            String rendered = promptTemplateService.renderTemplate(id, variables);
            Map<String, String> response = new HashMap<>();
            response.put("rendered", rendered);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Error rendering template", e);
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 启用提示词模板
     */
    @PostMapping("/{id}/enable")
    public ResponseEntity<Void> enableTemplate(@PathVariable String id) {
        boolean success = promptTemplateService.enableTemplate(id);
        return success ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }
    
    /**
     * 禁用提示词模板
     */
    @PostMapping("/{id}/disable")
    public ResponseEntity<Void> disableTemplate(@PathVariable String id) {
        boolean success = promptTemplateService.disableTemplate(id);
        return success ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }
}
