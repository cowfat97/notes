package com.example.mcp.domain.service;

import com.example.mcp.domain.model.PromptTemplate;

import java.util.List;
import java.util.Map;

/**
 * 提示词模板领域服务接口
 * 提供提示词模板管理的核心业务逻辑
 */
public interface PromptTemplateService {
    
    /**
     * 创建提示词模板
     * @param template 模板信息
     * @return 创建的模板
     */
    PromptTemplate createTemplate(PromptTemplate template);
    
    /**
     * 更新提示词模板
     * @param template 模板信息
     * @return 更新后的模板
     */
    PromptTemplate updateTemplate(PromptTemplate template);
    
    /**
     * 删除提示词模板
     * @param templateId 模板ID
     * @return 是否删除成功
     */
    boolean deleteTemplate(String templateId);
    
    /**
     * 根据ID获取模板
     * @param templateId 模板ID
     * @return 模板信息
     */
    PromptTemplate getTemplateById(String templateId);
    
    /**
     * 根据名称获取模板
     * @param name 模板名称
     * @return 模板信息
     */
    PromptTemplate getTemplateByName(String name);
    
    /**
     * 获取所有模板
     * @return 模板列表
     */
    List<PromptTemplate> getAllTemplates();
    
    /**
     * 根据分类获取模板
     * @param category 分类
     * @return 模板列表
     */
    List<PromptTemplate> getTemplatesByCategory(String category);
    
    /**
     * 搜索模板
     * @param keyword 关键词
     * @return 模板列表
     */
    List<PromptTemplate> searchTemplates(String keyword);
    
    /**
     * 渲染模板
     * @param templateId 模板ID
     * @param variables 变量值
     * @return 渲染后的内容
     */
    String renderTemplate(String templateId, Map<String, String> variables);
    
    /**
     * 渲染模板
     * @param template 模板对象
     * @param variables 变量值
     * @return 渲染后的内容
     */
    String renderTemplate(PromptTemplate template, Map<String, String> variables);
    
    /**
     * 启用模板
     * @param templateId 模板ID
     * @return 是否成功
     */
    boolean enableTemplate(String templateId);
    
    /**
     * 禁用模板
     * @param templateId 模板ID
     * @return 是否成功
     */
    boolean disableTemplate(String templateId);
}
