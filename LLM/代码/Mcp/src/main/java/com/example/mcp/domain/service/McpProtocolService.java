package com.example.mcp.domain.service;

import com.example.mcp.domain.model.McpRequest;
import com.example.mcp.domain.model.McpResponse;

/**
 * MCP协议领域服务接口
 * 处理MCP协议的核心业务逻辑
 */
public interface McpProtocolService {
    
    /**
     * 处理MCP请求
     * @param request MCP请求
     * @return MCP响应
     */
    McpResponse processRequest(McpRequest request);
    
    /**
     * 验证请求格式
     * @param request MCP请求
     * @return 是否有效
     */
    boolean validateRequest(McpRequest request);
    
    /**
     * 获取支持的方法列表
     * @return 方法列表
     */
    java.util.List<String> getSupportedMethods();
}
