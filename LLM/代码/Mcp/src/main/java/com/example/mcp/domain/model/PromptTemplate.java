package com.example.mcp.domain.model;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 提示词模板领域模型
 * 表示一个可重用的提示词模板
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class PromptTemplate {
    
    /**
     * 模板ID
     */
    private String id;
    
    /**
     * 模板名称
     */
    private String name;
    
    /**
     * 模板描述
     */
    private String description;
    
    /**
     * 模板内容
     */
    private String content;
    
    /**
     * 模板变量
     */
    private Map<String, String> variables;
    
    /**
     * 模板分类
     */
    private String category;
    
    /**
     * 创建时间
     */
    private LocalDateTime createdAt;
    
    /**
     * 更新时间
     */
    private LocalDateTime updatedAt;
    
    /**
     * 创建者
     */
    private String createdBy;
    
    /**
     * 是否启用
     */
    private boolean enabled;
    
    /**
     * 验证模板是否有效
     */
    public boolean isValid() {
        return name != null && !name.trim().isEmpty() 
                && content != null && !content.trim().isEmpty();
    }
    
    /**
     * 渲染模板内容
     * 将模板中的变量替换为实际值
     */
    public String render(Map<String, String> values) {
        if (content == null) {
            return "";
        }
        
        String rendered = content;
        if (values != null) {
            for (Map.Entry<String, String> entry : values.entrySet()) {
                String placeholder = "{{" + entry.getKey() + "}}";
                rendered = rendered.replace(placeholder, entry.getValue());
            }
        }
        
        return rendered;
    }
    
    /**
     * 获取模板中的变量列表
     */
    public java.util.Set<String> getVariableNames() {
        if (content == null) {
            return java.util.Collections.emptySet();
        }
        
        java.util.Set<String> variables = new java.util.HashSet<>();
        java.util.regex.Pattern pattern = java.util.regex.Pattern.compile("\\{\\{([^}]+)\\}\\}");
        java.util.regex.Matcher matcher = pattern.matcher(content);
        
        while (matcher.find()) {
            variables.add(matcher.group(1).trim());
        }
        
        return variables;
    }
    
    /**
     * 更新模板内容
     */
    public void updateContent(String newContent) {
        this.content = newContent;
        this.updatedAt = LocalDateTime.now();
    }
    
    /**
     * 启用模板
     */
    public void enable() {
        this.enabled = true;
        this.updatedAt = LocalDateTime.now();
    }
    
    /**
     * 禁用模板
     */
    public void disable() {
        this.enabled = false;
        this.updatedAt = LocalDateTime.now();
    }
}
