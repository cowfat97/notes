package com.example.mcp.domain.repository;

import com.example.mcp.domain.model.PromptTemplate;

import java.util.List;
import java.util.Optional;

/**
 * 提示词模板领域仓库接口
 * 定义提示词模板的数据访问操作
 */
public interface PromptTemplateRepository {
    
    /**
     * 保存模板
     * @param template 模板
     * @return 保存的模板
     */
    PromptTemplate save(PromptTemplate template);
    
    /**
     * 根据ID查找模板
     * @param id 模板ID
     * @return 模板
     */
    Optional<PromptTemplate> findById(String id);
    
    /**
     * 根据名称查找模板
     * @param name 模板名称
     * @return 模板
     */
    Optional<PromptTemplate> findByName(String name);
    
    /**
     * 查找所有模板
     * @return 模板列表
     */
    List<PromptTemplate> findAll();
    
    /**
     * 根据分类查找模板
     * @param category 分类
     * @return 模板列表
     */
    List<PromptTemplate> findByCategory(String category);
    
    /**
     * 搜索模板
     * @param keyword 关键词
     * @return 模板列表
     */
    List<PromptTemplate> search(String keyword);
    
    /**
     * 删除模板
     * @param id 模板ID
     * @return 是否删除成功
     */
    boolean deleteById(String id);
    
    /**
     * 检查模板是否存在
     * @param id 模板ID
     * @return 是否存在
     */
    boolean existsById(String id);
    
    /**
     * 检查模板名称是否存在
     * @param name 模板名称
     * @return 是否存在
     */
    boolean existsByName(String name);
    
    /**
     * 统计模板数量
     * @return 模板数量
     */
    long count();
}
