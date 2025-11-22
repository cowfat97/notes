package com.example.dataservice.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * LLM 提示词模板实体类
 */
@TableName("llm_prompt_template")
@Data
public class PromptTemplate {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String name;

    private String title;

    private String description;

    private String content;

    private Long categoryId;

    private String subcategory;

    private String[] tags;

    private String templateType;

    private String modelType;

    private String variables;

    private String exampleData;

    private BigDecimal temperature;

    private Integer maxTokens;

    private Long usageCount;

    private BigDecimal avgRating;

    private BigDecimal successRate;

    private String visibility;

    private Long createdBy;

    private Long teamId;

    private Integer version;

    private Long parentVersionId;

    private Boolean isLatest;

    private String status;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private LocalDateTime lastUsedAt;
}

