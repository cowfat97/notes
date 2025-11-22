package com.example.dataservice.config;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.context.annotation.Configuration;

/**
 * MyBatis-Plus 配置类
 */
@Configuration
@MapperScan("com.example.dataservice.repository")
public class MyBatisPlusConfig {
}

