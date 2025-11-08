package com.example.mcp.interfaces.controller;

import com.example.mcp.application.service.McpApplicationService;
import com.example.mcp.domain.model.McpRequest;
import com.example.mcp.domain.model.McpResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * MCP协议控制器
 * 处理HTTP请求，提供MCP协议接口
 */
@Slf4j
@RestController
@RequestMapping("/mcp")
@RequiredArgsConstructor
public class McpController {
    
    private final McpApplicationService mcpApplicationService;
    
    /**
     * 处理MCP请求
     */
    @PostMapping("/request")
    public ResponseEntity<McpResponse> handleRequest(@RequestBody Map<String, Object> requestBody) {
        try {
            log.info("Received MCP request: {}", requestBody);
            
            // 将请求体转换为MCP请求对象
            McpRequest request = convertToMcpRequest(requestBody);
            
            // 处理请求
            McpResponse response = mcpApplicationService.processRequest(request);
            
            log.info("Sending MCP response: {}", response.isSuccess() ? "SUCCESS" : "ERROR");
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            log.error("Error handling MCP request", e);
            
            McpResponse errorResponse = McpResponse.error(
                extractIdFromRequestBody(requestBody),
                com.example.mcp.domain.model.McpError.internalError(e.getMessage())
            );
            
            return ResponseEntity.ok(errorResponse);
        }
    }
    
    /**
     * 获取支持的方法列表
     */
    @GetMapping("/methods")
    public ResponseEntity<Map<String, Object>> getSupportedMethods() {
        Map<String, Object> response = new HashMap<>();
        response.put("methods", mcpApplicationService.getSupportedMethods());
        return ResponseEntity.ok(response);
    }
    
    /**
     * 健康检查
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("service", "MCP PostgreSQL Server");
        response.put("version", "1.0.0");
        return ResponseEntity.ok(response);
    }
    
    /**
     * 将请求体转换为MCP请求对象
     */
    private McpRequest convertToMcpRequest(Map<String, Object> requestBody) {
        McpRequest.McpRequestBuilder builder = McpRequest.builder();
        
        if (requestBody.containsKey("id")) {
            builder.id(requestBody.get("id").toString());
        }
        
        if (requestBody.containsKey("method")) {
            builder.method(requestBody.get("method").toString());
        }
        
        if (requestBody.containsKey("params")) {
            builder.params((Map<String, Object>) requestBody.get("params"));
        }
        
        if (requestBody.containsKey("jsonrpc")) {
            builder.jsonrpc(requestBody.get("jsonrpc").toString());
        } else {
            builder.jsonrpc("2.0");
        }
        
        return builder.build();
    }
    
    /**
     * 从请求体中提取ID
     */
    private String extractIdFromRequestBody(Map<String, Object> requestBody) {
        if (requestBody.containsKey("id")) {
            return requestBody.get("id").toString();
        }
        return null;
    }
}
