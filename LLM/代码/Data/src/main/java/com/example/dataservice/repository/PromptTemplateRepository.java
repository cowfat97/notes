package com.example.dataservice.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.dataservice.entity.PromptTemplate;
import org.apache.ibatis.annotations.Mapper;

/**
 * 提示词模板 Mapper 接口
 */
@Mapper
public interface PromptTemplateRepository extends BaseMapper<PromptTemplate> {
}

