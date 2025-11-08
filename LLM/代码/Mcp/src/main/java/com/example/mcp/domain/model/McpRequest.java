package com.example.mcp.domain.model;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * MCP请求领域模型
 * 表示一个MCP协议的请求对象
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class McpRequest {
    
    /**
     * 请求ID
     */
    private String id;
    
    /**
     * 请求方法
     */
    private String method;
    
    /**
     * 请求参数
     */
    private Map<String, Object> params;
    
    /**
     * JSON-RPC版本
     */
    private String jsonrpc;
    
    /**
     * 验证请求是否有效
     */
    public boolean isValid() {
        return id != null && method != null && jsonrpc != null;
    }
    
    /**
     * 获取参数值
     */
    public Object getParam(String key) {
        return params != null ? params.get(key) : null;
    }
    
    /**
     * 获取字符串参数
     */
    public String getStringParam(String key) {
        Object value = getParam(key);
        return value != null ? value.toString() : null;
    }
}
