package com.example.mcp.domain.model;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

/**
 * 数据库查询结果领域模型
 * 表示数据库查询的执行结果
 */
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class DatabaseQueryResult {
    
    /**
     * 查询是否成功
     */
    private boolean success;
    
    /**
     * 查询结果数据
     */
    private List<Map<String, Object>> data;
    
    /**
     * 查询影响的行数
     */
    private int affectedRows;
    
    /**
     * 查询执行时间（毫秒）
     */
    private long executionTime;
    
    /**
     * 错误信息
     */
    private String errorMessage;
    
    /**
     * 查询类型
     */
    private QueryType queryType;
    
    /**
     * 查询SQL
     */
    private String sql;
    
    /**
     * 查询类型枚举
     */
    public enum QueryType {
        SELECT,
        INSERT,
        UPDATE,
        DELETE,
        DDL,
        OTHER
    }
    
    /**
     * 创建成功结果
     */
    public static DatabaseQueryResult success(List<Map<String, Object>> data, 
                                            int affectedRows, 
                                            long executionTime, 
                                            String sql, 
                                            QueryType queryType) {
        return DatabaseQueryResult.builder()
                .success(true)
                .data(data)
                .affectedRows(affectedRows)
                .executionTime(executionTime)
                .sql(sql)
                .queryType(queryType)
                .build();
    }
    
    /**
     * 创建错误结果
     */
    public static DatabaseQueryResult error(String errorMessage, String sql) {
        return DatabaseQueryResult.builder()
                .success(false)
                .errorMessage(errorMessage)
                .sql(sql)
                .build();
    }
    
    /**
     * 获取结果行数
     */
    public int getRowCount() {
        return data != null ? data.size() : 0;
    }
    
    /**
     * 判断是否有数据
     */
    public boolean hasData() {
        return data != null && !data.isEmpty();
    }
    
    /**
     * 获取第一行数据
     */
    public Map<String, Object> getFirstRow() {
        return hasData() ? data.get(0) : null;
    }
    
    /**
     * 获取指定列的值
     */
    public Object getColumnValue(int rowIndex, String columnName) {
        if (!hasData() || rowIndex >= data.size()) {
            return null;
        }
        return data.get(rowIndex).get(columnName);
    }
}
