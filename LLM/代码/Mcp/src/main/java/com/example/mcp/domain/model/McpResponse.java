package com.example.mcp.domain.model;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * MCP响应领域模型
 * 表示一个MCP协议的响应对象
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class McpResponse {
    
    /**
     * 响应ID
     */
    private String id;
    
    /**
     * 响应结果
     */
    private Object result;
    
    /**
     * 错误信息
     */
    private McpError error;
    
    /**
     * JSON-RPC版本
     */
    private String jsonrpc;
    
    /**
     * 创建成功响应
     */
    public static McpResponse success(String id, Object result) {
        return McpResponse.builder()
                .id(id)
                .result(result)
                .jsonrpc("2.0")
                .build();
    }
    
    /**
     * 创建错误响应
     */
    public static McpResponse error(String id, McpError error) {
        return McpResponse.builder()
                .id(id)
                .error(error)
                .jsonrpc("2.0")
                .build();
    }
    
    /**
     * 判断是否为成功响应
     */
    public boolean isSuccess() {
        return error == null;
    }
}
