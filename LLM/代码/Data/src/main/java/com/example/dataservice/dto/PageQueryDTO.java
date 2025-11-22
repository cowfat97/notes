package com.example.dataservice.dto;

import lombok.Data;

/**
 * 分页查询参数对象
 */
@Data
public class PageQueryDTO {

    private Integer current = 1;

    private Integer size = 10;
}

