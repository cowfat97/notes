package com.example.mcp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * MCP PostgreSQL Server 启动类
 * 基于SpringBoot的MCP服务器应用
 */
@SpringBootApplication
@EnableJpaRepositories(basePackages = "com.example.mcp.infrastructure.persistence")
public class McpPgServerApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(McpPgServerApplication.class, args);
    }
}
