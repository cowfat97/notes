package com.example.dataservice.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.dataservice.entity.PromptTemplate;
import com.example.dataservice.repository.PromptTemplateRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 提示词模板服务类
 */
@Service
public class PromptTemplateService {

    private final PromptTemplateRepository repository;

    @Autowired
    public PromptTemplateService(PromptTemplateRepository repository) {
        this.repository = repository;
    }

    /**
     * 根据ID查询模板
     */
    public PromptTemplate getById(Long id) {
        return repository.selectById(id);
    }

    /**
     * 分页查询模板列表
     */
    public Page<PromptTemplate> getPage(Integer current, Integer size) {
        Page<PromptTemplate> page = new Page<>(current, size);
        return repository.selectPage(page, buildActiveWrapper());
    }

    /**
     * 根据条件查询模板列表
     */
    public List<PromptTemplate> list(QueryWrapper<PromptTemplate> wrapper) {
        return repository.selectList(wrapper);
    }

    /**
     * 根据查询条件构建查询包装器
     */
    public QueryWrapper<PromptTemplate> buildQueryWrapper(Long categoryId, String templateType, 
                                                           String modelType, String visibility,
                                                           Long createdBy, Long teamId, String keyword) {
        QueryWrapper<PromptTemplate> wrapper = buildActiveWrapper();
        
        if (categoryId != null) {
            wrapper.eq("category_id", categoryId);
        }
        if (templateType != null) {
            wrapper.eq("template_type", templateType);
        }
        if (modelType != null) {
            wrapper.eq("model_type", modelType);
        }
        if (visibility != null) {
            wrapper.eq("visibility", visibility);
        }
        if (createdBy != null) {
            wrapper.eq("created_by", createdBy);
        }
        if (teamId != null) {
            wrapper.eq("team_id", teamId);
        }
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.and(w -> w.like("name", keyword).or().like("title", keyword));
        }
        
        return wrapper;
    }

    /**
     * 构建活动模板的查询条件
     */
    private QueryWrapper<PromptTemplate> buildActiveWrapper() {
        QueryWrapper<PromptTemplate> wrapper = new QueryWrapper<>();
        wrapper.eq("status", "active");
        wrapper.eq("is_latest", true);
        wrapper.orderByDesc("created_at");
        return wrapper;
    }
}

