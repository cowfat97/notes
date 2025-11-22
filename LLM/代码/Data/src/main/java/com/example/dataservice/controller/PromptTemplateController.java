package com.example.dataservice.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.dataservice.dto.PageQueryDTO;
import com.example.dataservice.dto.PromptTemplateQueryDTO;
import com.example.dataservice.entity.PromptTemplate;
import com.example.dataservice.service.PromptTemplateService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 提示词模板控制器
 */
@RestController
@RequestMapping("/api/prompt-template")
public class PromptTemplateController {

    private final PromptTemplateService service;

    @Autowired
    public PromptTemplateController(PromptTemplateService service) {
        this.service = service;
    }

    /**
     * 根据ID查询模板
     */
    @GetMapping("/{id}")
    public ResponseEntity<PromptTemplate> getById(@PathVariable Long id) {
        PromptTemplate template = service.getById(id);
        return template != null ? ResponseEntity.ok(template) : ResponseEntity.notFound().build();
    }

    /**
     * 分页查询模板列表
     */
    @GetMapping("/page")
    public ResponseEntity<Page<PromptTemplate>> getPage(PageQueryDTO pageQuery) {
        return ResponseEntity.ok(service.getPage(pageQuery.getCurrent(), pageQuery.getSize()));
    }

    /**
     * 通用查询接口
     */
    @GetMapping("/list")
    public ResponseEntity<List<PromptTemplate>> list(PromptTemplateQueryDTO query) {
        QueryWrapper<PromptTemplate> wrapper = service.buildQueryWrapper(
                query.getCategoryId(),
                query.getTemplateType(),
                query.getModelType(),
                query.getVisibility(),
                query.getCreatedBy(),
                query.getTeamId(),
                query.getKeyword()
        );
        return ResponseEntity.ok(service.list(wrapper));
    }
}

