package com.example.mcp.interfaces.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.Map;

/**
 * 更新提示词模板请求DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdatePromptTemplateRequest {
    
    private String name;
    
    private String description;
    
    private String content;
    
    private Map<String, String> variables;
    
    private String category;
    
    private boolean enabled = true;
}
