package com.example.mcp.infrastructure.persistence;

import com.example.mcp.domain.model.DatabaseQueryResult;
import com.example.mcp.domain.service.DatabaseService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.sql.*;
import java.util.*;

/**
 * 数据库服务实现
 * 提供PostgreSQL数据库操作的具体实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DatabaseServiceImpl implements DatabaseService {
    
    @Value("${spring.datasource.url}")
    private String jdbcUrl;
    
    @Value("${spring.datasource.username}")
    private String username;
    
    @Value("${spring.datasource.password}")
    private String password;
    
    private Connection connection;
    
    @PostConstruct
    public void init() {
        try {
            Class.forName("org.postgresql.Driver");
            connection = DriverManager.getConnection(jdbcUrl, username, password);
            log.info("Database connection established successfully");
        } catch (Exception e) {
            log.error("Failed to establish database connection", e);
        }
    }
    
    @Override
    public DatabaseQueryResult executeQuery(String sql, List<Object> parameters) {
        long startTime = System.currentTimeMillis();
        
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            // 设置参数
            if (parameters != null) {
                for (int i = 0; i < parameters.size(); i++) {
                    stmt.setObject(i + 1, parameters.get(i));
                }
            }
            
            // 执行查询
            boolean hasResultSet = stmt.execute();
            
            if (hasResultSet) {
                // SELECT查询
                try (ResultSet rs = stmt.getResultSet()) {
                    List<Map<String, Object>> data = new ArrayList<>();
                    ResultSetMetaData metaData = rs.getMetaData();
                    int columnCount = metaData.getColumnCount();
                    
                    while (rs.next()) {
                        Map<String, Object> row = new HashMap<>();
                        for (int i = 1; i <= columnCount; i++) {
                            String columnName = metaData.getColumnName(i);
                            Object value = rs.getObject(i);
                            row.put(columnName, value);
                        }
                        data.add(row);
                    }
                    
                    long executionTime = System.currentTimeMillis() - startTime;
                    return DatabaseQueryResult.success(data, data.size(), executionTime, sql, 
                            DatabaseQueryResult.QueryType.SELECT);
                }
            } else {
                // UPDATE/INSERT/DELETE查询
                int affectedRows = stmt.getUpdateCount();
                long executionTime = System.currentTimeMillis() - startTime;
                
                DatabaseQueryResult.QueryType queryType = determineQueryType(sql);
                return DatabaseQueryResult.success(Collections.emptyList(), affectedRows, executionTime, sql, queryType);
            }
            
        } catch (SQLException e) {
            log.error("Database query error: {}", e.getMessage(), e);
            return DatabaseQueryResult.error(e.getMessage(), sql);
        }
    }
    
    @Override
    public DatabaseQueryResult executeUpdate(String sql, List<Object> parameters) {
        long startTime = System.currentTimeMillis();
        
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            // 设置参数
            if (parameters != null) {
                for (int i = 0; i < parameters.size(); i++) {
                    stmt.setObject(i + 1, parameters.get(i));
                }
            }
            
            int affectedRows = stmt.executeUpdate();
            long executionTime = System.currentTimeMillis() - startTime;
            
            DatabaseQueryResult.QueryType queryType = determineQueryType(sql);
            return DatabaseQueryResult.success(Collections.emptyList(), affectedRows, executionTime, sql, queryType);
            
        } catch (SQLException e) {
            log.error("Database update error: {}", e.getMessage(), e);
            return DatabaseQueryResult.error(e.getMessage(), sql);
        }
    }
    
    @Override
    public List<String> getTableList() {
        String sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name";
        
        try (PreparedStatement stmt = connection.prepareStatement(sql);
             ResultSet rs = stmt.executeQuery()) {
            
            List<String> tables = new ArrayList<>();
            while (rs.next()) {
                tables.add(rs.getString("table_name"));
            }
            return tables;
            
        } catch (SQLException e) {
            log.error("Error getting table list: {}", e.getMessage(), e);
            return Collections.emptyList();
        }
    }
    
    @Override
    public List<Map<String, Object>> getTableStructure(String tableName) {
        String sql = "SELECT " +
                "column_name, " +
                "data_type, " +
                "is_nullable, " +
                "column_default, " +
                "character_maximum_length, " +
                "numeric_precision, " +
                "numeric_scale " +
                "FROM information_schema.columns " +
                "WHERE table_schema = 'public' AND table_name = ? " +
                "ORDER BY ordinal_position";
        
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setString(1, tableName);
            
            try (ResultSet rs = stmt.executeQuery()) {
                List<Map<String, Object>> structure = new ArrayList<>();
                while (rs.next()) {
                    Map<String, Object> column = new HashMap<>();
                    column.put("column_name", rs.getString("column_name"));
                    column.put("data_type", rs.getString("data_type"));
                    column.put("is_nullable", rs.getString("is_nullable"));
                    column.put("column_default", rs.getString("column_default"));
                    column.put("character_maximum_length", rs.getObject("character_maximum_length"));
                    column.put("numeric_precision", rs.getObject("numeric_precision"));
                    column.put("numeric_scale", rs.getObject("numeric_scale"));
                    structure.add(column);
                }
                return structure;
            }
            
        } catch (SQLException e) {
            log.error("Error getting table structure for {}: {}", tableName, e.getMessage(), e);
            return Collections.emptyList();
        }
    }
    
    @Override
    public DatabaseQueryResult getTableData(String tableName, int limit, int offset) {
        String sql = "SELECT * FROM " + tableName + " LIMIT ? OFFSET ?";
        List<Object> parameters = Arrays.asList(limit, offset);
        
        return executeQuery(sql, parameters);
    }
    
    @Override
    public boolean testConnection() {
        try {
            if (connection == null || connection.isClosed()) {
                connection = DriverManager.getConnection(jdbcUrl, username, password);
            }
            
            try (PreparedStatement stmt = connection.prepareStatement("SELECT 1")) {
                stmt.executeQuery();
                return true;
            }
        } catch (SQLException e) {
            log.error("Database connection test failed: {}", e.getMessage(), e);
            return false;
        }
    }
    
    @Override
    public Map<String, Object> getDatabaseInfo() {
        Map<String, Object> info = new HashMap<>();
        
        try {
            // 获取数据库版本
            try (PreparedStatement stmt = connection.prepareStatement("SELECT version()")) {
                try (ResultSet rs = stmt.executeQuery()) {
                    if (rs.next()) {
                        info.put("version", rs.getString(1));
                    }
                }
            }
            
            // 获取数据库名称
            info.put("database_name", connection.getCatalog());
            
            // 获取表数量
            try (PreparedStatement stmt = connection.prepareStatement(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")) {
                try (ResultSet rs = stmt.executeQuery()) {
                    if (rs.next()) {
                        info.put("table_count", rs.getInt(1));
                    }
                }
            }
            
            // 获取连接信息
            info.put("url", jdbcUrl);
            info.put("username", username);
            
        } catch (SQLException e) {
            log.error("Error getting database info: {}", e.getMessage(), e);
        }
        
        return info;
    }
    
    private DatabaseQueryResult.QueryType determineQueryType(String sql) {
        String upperSql = sql.trim().toUpperCase();
        
        if (upperSql.startsWith("SELECT")) {
            return DatabaseQueryResult.QueryType.SELECT;
        } else if (upperSql.startsWith("INSERT")) {
            return DatabaseQueryResult.QueryType.INSERT;
        } else if (upperSql.startsWith("UPDATE")) {
            return DatabaseQueryResult.QueryType.UPDATE;
        } else if (upperSql.startsWith("DELETE")) {
            return DatabaseQueryResult.QueryType.DELETE;
        } else if (upperSql.startsWith("CREATE") || upperSql.startsWith("ALTER") || 
                   upperSql.startsWith("DROP") || upperSql.startsWith("TRUNCATE")) {
            return DatabaseQueryResult.QueryType.DDL;
        } else {
            return DatabaseQueryResult.QueryType.OTHER;
        }
    }
}
