package com.example.mcp.domain.service;

import com.example.mcp.domain.model.DatabaseQueryResult;

import java.util.List;
import java.util.Map;

/**
 * 数据库操作领域服务接口
 * 提供数据库查询和操作的核心业务逻辑
 */
public interface DatabaseService {
    
    /**
     * 执行SQL查询
     * @param sql SQL语句
     * @param parameters 参数
     * @return 查询结果
     */
    DatabaseQueryResult executeQuery(String sql, List<Object> parameters);
    
    /**
     * 执行SQL更新操作
     * @param sql SQL语句
     * @param parameters 参数
     * @return 执行结果
     */
    DatabaseQueryResult executeUpdate(String sql, List<Object> parameters);
    
    /**
     * 获取数据库表列表
     * @return 表列表
     */
    List<String> getTableList();
    
    /**
     * 获取表结构信息
     * @param tableName 表名
     * @return 表结构信息
     */
    List<Map<String, Object>> getTableStructure(String tableName);
    
    /**
     * 获取表数据
     * @param tableName 表名
     * @param limit 限制行数
     * @param offset 偏移量
     * @return 表数据
     */
    DatabaseQueryResult getTableData(String tableName, int limit, int offset);
    
    /**
     * 测试数据库连接
     * @return 连接是否成功
     */
    boolean testConnection();
    
    /**
     * 获取数据库信息
     * @return 数据库信息
     */
    Map<String, Object> getDatabaseInfo();
}
