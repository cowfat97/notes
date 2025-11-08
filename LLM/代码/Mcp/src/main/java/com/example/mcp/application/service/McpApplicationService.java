package com.example.mcp.application.service;

import com.example.mcp.domain.model.*;
import com.example.mcp.domain.service.DatabaseService;
import com.example.mcp.domain.service.McpProtocolService;
import com.example.mcp.domain.service.PromptTemplateService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * MCP应用服务
 * 协调领域服务，处理MCP协议的业务流程
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class McpApplicationService implements McpProtocolService {
    
    private final DatabaseService databaseService;
    private final PromptTemplateService promptTemplateService;
    
    @Override
    public McpResponse processRequest(McpRequest request) {
        log.info("Processing MCP request: {}", request.getMethod());
        
        if (!validateRequest(request)) {
            return McpResponse.error(request.getId(), McpError.invalidRequest("Invalid request format"));
        }
        
        try {
            switch (request.getMethod()) {
                case "initialize":
                    return handleInitialize(request);
                case "tools/list":
                    return handleToolsList(request);
                case "tools/call":
                    return handleToolsCall(request);
                case "prompt_templates/list":
                    return handlePromptTemplatesList(request);
                case "prompt_templates/get":
                    return handlePromptTemplateGet(request);
                case "prompt_templates/render":
                    return handlePromptTemplateRender(request);
                case "database/query":
                    return handleDatabaseQuery(request);
                case "database/tables":
                    return handleDatabaseTables(request);
                case "database/table_structure":
                    return handleTableStructure(request);
                case "database/test_connection":
                    return handleTestConnection(request);
                default:
                    return McpResponse.error(request.getId(), McpError.methodNotFound(request.getMethod()));
            }
        } catch (Exception e) {
            log.error("Error processing MCP request: {}", e.getMessage(), e);
            return McpResponse.error(request.getId(), McpError.internalError(e.getMessage()));
        }
    }
    
    @Override
    public boolean validateRequest(McpRequest request) {
        return request != null && request.isValid();
    }
    
    @Override
    public List<String> getSupportedMethods() {
        return Arrays.asList(
            "initialize",
            "tools/list",
            "tools/call",
            "prompt_templates/list",
            "prompt_templates/get",
            "prompt_templates/render",
            "database/query",
            "database/tables",
            "database/table_structure",
            "database/test_connection"
        );
    }
    
    private McpResponse handleInitialize(McpRequest request) {
        Map<String, Object> result = new HashMap<>();
        result.put("protocolVersion", "2024-11-05");
        result.put("capabilities", getCapabilities());
        result.put("serverInfo", getServerInfo());
        
        return McpResponse.success(request.getId(), result);
    }
    
    private McpResponse handleToolsList(McpRequest request) {
        List<Map<String, Object>> tools = Arrays.asList(
            createTool("database_query", "Execute SQL query on PostgreSQL database", 
                Arrays.asList(
                    createParameter("sql", "string", "SQL query to execute", true),
                    createParameter("parameters", "array", "Query parameters", false)
                )),
            createTool("database_tables", "Get list of database tables", 
                Collections.emptyList()),
            createTool("table_structure", "Get table structure information", 
                Arrays.asList(
                    createParameter("table_name", "string", "Name of the table", true)
                )),
            createTool("prompt_template_render", "Render prompt template with variables", 
                Arrays.asList(
                    createParameter("template_id", "string", "Template ID", true),
                    createParameter("variables", "object", "Template variables", true)
                ))
        );
        
        Map<String, Object> result = new HashMap<>();
        result.put("tools", tools);
        return McpResponse.success(request.getId(), result);
    }
    
    private McpResponse handleToolsCall(McpRequest request) {
        String toolName = request.getStringParam("name");
        Map<String, Object> arguments = (Map<String, Object>) request.getParam("arguments");
        
        switch (toolName) {
            case "database_query":
                return handleDatabaseQueryTool(request, arguments);
            case "database_tables":
                return handleDatabaseTablesTool(request);
            case "table_structure":
                return handleTableStructureTool(request, arguments);
            case "prompt_template_render":
                return handlePromptTemplateRenderTool(request, arguments);
            default:
                return McpResponse.error(request.getId(), McpError.methodNotFound(toolName));
        }
    }
    
    private McpResponse handlePromptTemplatesList(McpRequest request) {
        List<PromptTemplate> templates = promptTemplateService.getAllTemplates();
        List<Map<String, Object>> result = new ArrayList<>();
        
        for (PromptTemplate template : templates) {
            Map<String, Object> templateInfo = new HashMap<>();
            templateInfo.put("id", template.getId());
            templateInfo.put("name", template.getName());
            templateInfo.put("description", template.getDescription());
            templateInfo.put("category", template.getCategory());
            templateInfo.put("enabled", template.isEnabled());
            templateInfo.put("createdAt", template.getCreatedAt());
            result.add(templateInfo);
        }
        
        Map<String, Object> response = new HashMap<>();
        response.put("templates", result);
        return McpResponse.success(request.getId(), response);
    }
    
    private McpResponse handlePromptTemplateGet(McpRequest request) {
        String templateId = request.getStringParam("template_id");
        if (templateId == null) {
            return McpResponse.error(request.getId(), McpError.invalidParams("template_id is required"));
        }
        
        PromptTemplate template = promptTemplateService.getTemplateById(templateId);
        if (template == null) {
            return McpResponse.error(request.getId(), McpError.invalidParams("Template not found"));
        }
        
        return McpResponse.success(request.getId(), template);
    }
    
    private McpResponse handlePromptTemplateRender(McpRequest request) {
        String templateId = request.getStringParam("template_id");
        Map<String, String> variables = (Map<String, String>) request.getParam("variables");
        
        if (templateId == null) {
            return McpResponse.error(request.getId(), McpError.invalidParams("template_id is required"));
        }
        
        String rendered = promptTemplateService.renderTemplate(templateId, variables);
        Map<String, Object> response = new HashMap<>();
        response.put("rendered", rendered);
        return McpResponse.success(request.getId(), response);
    }
    
    private McpResponse handleDatabaseQuery(McpRequest request) {
        String sql = request.getStringParam("sql");
        List<Object> parameters = (List<Object>) request.getParam("parameters");
        
        if (sql == null) {
            return McpResponse.error(request.getId(), McpError.invalidParams("sql is required"));
        }
        
        DatabaseQueryResult result = databaseService.executeQuery(sql, parameters);
        return McpResponse.success(request.getId(), result);
    }
    
    private McpResponse handleDatabaseTables(McpRequest request) {
        List<String> tables = databaseService.getTableList();
        return McpResponse.success(request.getId(), createMap("tables", tables));
    }
    
    private McpResponse handleTableStructure(McpRequest request) {
        String tableName = request.getStringParam("table_name");
        if (tableName == null) {
            return McpResponse.error(request.getId(), McpError.invalidParams("table_name is required"));
        }
        
        List<Map<String, Object>> structure = databaseService.getTableStructure(tableName);
        return McpResponse.success(request.getId(), createMap("structure", structure));
    }
    
    private McpResponse handleTestConnection(McpRequest request) {
        boolean connected = databaseService.testConnection();
        return McpResponse.success(request.getId(), createMap("connected", connected));
    }
    
    // Tool handlers
    private McpResponse handleDatabaseQueryTool(McpRequest request, Map<String, Object> arguments) {
        String sql = (String) arguments.get("sql");
        List<Object> parameters = (List<Object>) arguments.get("parameters");
        
        DatabaseQueryResult result = databaseService.executeQuery(sql, parameters);
        return McpResponse.success(request.getId(), createMap("result", result));
    }
    
    private McpResponse handleDatabaseTablesTool(McpRequest request) {
        List<String> tables = databaseService.getTableList();
        return McpResponse.success(request.getId(), createMap("tables", tables));
    }
    
    private McpResponse handleTableStructureTool(McpRequest request, Map<String, Object> arguments) {
        String tableName = (String) arguments.get("table_name");
        List<Map<String, Object>> structure = databaseService.getTableStructure(tableName);
        return McpResponse.success(request.getId(), createMap("structure", structure));
    }
    
    private McpResponse handlePromptTemplateRenderTool(McpRequest request, Map<String, Object> arguments) {
        String templateId = (String) arguments.get("template_id");
        Map<String, String> variables = (Map<String, String>) arguments.get("variables");
        
        String rendered = promptTemplateService.renderTemplate(templateId, variables);
        return McpResponse.success(request.getId(), createMap("rendered", rendered));
    }
    
    // Helper methods
    private Map<String, Object> createMap(Object... keyValues) {
        Map<String, Object> map = new HashMap<>();
        for (int i = 0; i < keyValues.length; i += 2) {
            map.put((String) keyValues[i], keyValues[i + 1]);
        }
        return map;
    }
    
    private Map<String, Object> getCapabilities() {
        Map<String, Object> capabilities = new HashMap<>();
        capabilities.put("tools", createMap("listChanged", true));
        capabilities.put("promptTemplates", createMap("listChanged", true));
        return capabilities;
    }
    
    private Map<String, Object> getServerInfo() {
        Map<String, Object> serverInfo = new HashMap<>();
        serverInfo.put("name", "MCP PostgreSQL Server");
        serverInfo.put("version", "1.0.0");
        return serverInfo;
    }
    
    private Map<String, Object> createTool(String name, String description, List<Map<String, Object>> parameters) {
        Map<String, Object> tool = new HashMap<>();
        tool.put("name", name);
        tool.put("description", description);
        tool.put("inputSchema", createMap(
            "type", "object",
            "properties", createPropertiesMap(parameters),
            "required", getRequiredParameters(parameters)
        ));
        return tool;
    }
    
    private Map<String, Object> createParameter(String name, String type, String description, boolean required) {
        Map<String, Object> param = new HashMap<>();
        param.put("name", name);
        param.put("type", type);
        param.put("description", description);
        param.put("required", required);
        return param;
    }
    
    private Map<String, Object> createPropertiesMap(List<Map<String, Object>> parameters) {
        Map<String, Object> properties = new HashMap<>();
        for (Map<String, Object> param : parameters) {
            String name = (String) param.get("name");
            String type = (String) param.get("type");
            String description = (String) param.get("description");
            
            Map<String, Object> property = new HashMap<>();
            property.put("type", type);
            property.put("description", description);
            properties.put(name, property);
        }
        return properties;
    }
    
    private List<String> getRequiredParameters(List<Map<String, Object>> parameters) {
        List<String> required = new ArrayList<>();
        for (Map<String, Object> param : parameters) {
            if ((Boolean) param.get("required")) {
                required.add((String) param.get("name"));
            }
        }
        return required;
    }
}
