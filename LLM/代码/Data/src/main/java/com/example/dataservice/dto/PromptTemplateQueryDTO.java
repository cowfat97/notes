package com.example.dataservice.dto;

import lombok.Data;

/**
 * 提示词模板查询参数对象
 */
@Data
public class PromptTemplateQueryDTO {

    private Long categoryId;

    private String templateType;

    private String modelType;

    private String visibility;

    private Long createdBy;

    private Long teamId;

    private String keyword;
}

