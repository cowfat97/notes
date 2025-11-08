package com.example.mcp.domain.model;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

/**
 * MCP错误领域模型
 * 表示MCP协议中的错误信息
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class McpError {
    
    /**
     * 错误代码
     */
    private int code;
    
    /**
     * 错误消息
     */
    private String message;
    
    /**
     * 错误数据
     */
    private Object data;
    
    /**
     * 预定义错误代码
     */
    public static class ErrorCode {
        public static final int PARSE_ERROR = -32700;
        public static final int INVALID_REQUEST = -32600;
        public static final int METHOD_NOT_FOUND = -32601;
        public static final int INVALID_PARAMS = -32602;
        public static final int INTERNAL_ERROR = -32603;
        public static final int DATABASE_ERROR = -32000;
        public static final int VALIDATION_ERROR = -32001;
    }
    
    /**
     * 创建解析错误
     */
    public static McpError parseError(String message) {
        return McpError.builder()
                .code(ErrorCode.PARSE_ERROR)
                .message(message)
                .build();
    }
    
    /**
     * 创建无效请求错误
     */
    public static McpError invalidRequest(String message) {
        return McpError.builder()
                .code(ErrorCode.INVALID_REQUEST)
                .message(message)
                .build();
    }
    
    /**
     * 创建方法未找到错误
     */
    public static McpError methodNotFound(String method) {
        return McpError.builder()
                .code(ErrorCode.METHOD_NOT_FOUND)
                .message("Method not found: " + method)
                .build();
    }
    
    /**
     * 创建无效参数错误
     */
    public static McpError invalidParams(String message) {
        return McpError.builder()
                .code(ErrorCode.INVALID_PARAMS)
                .message(message)
                .build();
    }
    
    /**
     * 创建内部错误
     */
    public static McpError internalError(String message) {
        return McpError.builder()
                .code(ErrorCode.INTERNAL_ERROR)
                .message(message)
                .build();
    }
    
    /**
     * 创建数据库错误
     */
    public static McpError databaseError(String message) {
        return McpError.builder()
                .code(ErrorCode.DATABASE_ERROR)
                .message("Database error: " + message)
                .build();
    }
    
    /**
     * 创建验证错误
     */
    public static McpError validationError(String message) {
        return McpError.builder()
                .code(ErrorCode.VALIDATION_ERROR)
                .message("Validation error: " + message)
                .build();
    }
}
