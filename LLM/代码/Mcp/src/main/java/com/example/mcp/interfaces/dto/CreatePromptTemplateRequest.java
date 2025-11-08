package com.example.mcp.interfaces.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import javax.validation.constraints.NotBlank;
import java.util.Map;

/**
 * 创建提示词模板请求DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreatePromptTemplateRequest {
    
    @NotBlank(message = "Template name is required")
    private String name;
    
    private String description;
    
    @NotBlank(message = "Template content is required")
    private String content;
    
    private Map<String, String> variables;
    
    private String category;
    
    private String createdBy;
}
