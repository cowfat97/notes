# MCP PostgreSQL Server

基于Java 8和SpringBoot框架的MCP (Model Context Protocol) 服务器，提供PostgreSQL数据库操作和提示词模板管理功能。

## 项目特性

- 🏗️ **DDD架构设计**：采用领域驱动设计，清晰的层次结构
- 🗄️ **PostgreSQL支持**：完整的数据库操作功能
- 📝 **提示词模板管理**：可重用的提示词模板系统
- 🔌 **MCP协议兼容**：完全兼容MCP协议规范
- 🚀 **SpringBoot框架**：基于SpringBoot 2.7.18
- 📦 **Maven构建**：使用Maven进行项目构建和依赖管理

## 技术栈

- **Java**: JDK 8
- **框架**: SpringBoot 2.7.18
- **数据库**: PostgreSQL
- **ORM**: JPA/Hibernate
- **构建工具**: Maven
- **JSON处理**: Jackson
- **日志**: SLF4J + Logback

## 项目结构

```
src/main/java/com/example/mcp/
├── domain/                    # 领域层
│   ├── model/                # 领域模型
│   ├── repository/           # 领域仓库接口
│   └── service/              # 领域服务接口
├── application/              # 应用层
│   └── service/              # 应用服务
├── infrastructure/           # 基础设施层
│   ├── persistence/          # 数据持久化
│   ├── external/             # 外部服务
│   └── config/               # 配置类
├── interfaces/               # 接口层
│   ├── controller/           # 控制器
│   └── dto/                  # 数据传输对象
└── McpPgServerApplication.java  # 启动类
```

## 快速开始

### 环境要求

- JDK 8+
- Maven 3.6+
- PostgreSQL 12+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd mcp-pg-server
   ```

2. **配置数据库**
   ```bash
   # 创建数据库
   createdb mcp_db
   
   # 或者使用Docker
   docker run --name postgres-mcp -e POSTGRES_DB=mcp_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:13
   ```

3. **配置环境变量**
   ```bash
   export DB_USERNAME=postgres
   export DB_PASSWORD=password
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=mcp_db
   ```

4. **构建项目**
   ```bash
   mvn clean compile
   ```

5. **运行应用**
   ```bash
   mvn spring-boot:run
   ```

   或者使用不同的环境配置：
   ```bash
   # 开发环境
   mvn spring-boot:run -Dspring-boot.run.profiles=dev
   
   # 生产环境
   mvn spring-boot:run -Dspring-boot.run.profiles=prod
   ```

## API文档

### MCP协议接口

#### 1. 初始化服务器
```http
POST /mcp/request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "initialize",
  "params": {}
}
```

#### 2. 获取工具列表
```http
POST /mcp/request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/list",
  "params": {}
}
```

#### 3. 执行数据库查询
```http
POST /mcp/request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "database_query",
    "arguments": {
      "sql": "SELECT * FROM users LIMIT 10",
      "parameters": []
    }
  }
}
```

#### 4. 获取数据库表列表
```http
POST /mcp/request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "4",
  "method": "database/tables",
  "params": {}
}
```

#### 5. 渲染提示词模板
```http
POST /mcp/request
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "5",
  "method": "prompt_templates/render",
  "params": {
    "template_id": "sample-1",
    "variables": {
      "table_name": "users",
      "condition": "age > 18",
      "columns": "name, email, age"
    }
  }
}
```

### REST API接口

#### 提示词模板管理

1. **创建模板**
   ```http
   POST /api/prompt-templates
   Content-Type: application/json
   
   {
     "name": "用户查询助手",
     "description": "帮助用户查询用户信息",
     "content": "请查询{{table_name}}表中{{condition}}的用户信息",
     "category": "query",
     "createdBy": "admin"
   }
   ```

2. **获取所有模板**
   ```http
   GET /api/prompt-templates
   ```

3. **获取模板详情**
   ```http
   GET /api/prompt-templates/{id}
   ```

4. **更新模板**
   ```http
   PUT /api/prompt-templates/{id}
   Content-Type: application/json
   
   {
     "name": "更新后的模板名称",
     "content": "更新后的模板内容"
   }
   ```

5. **删除模板**
   ```http
   DELETE /api/prompt-templates/{id}
   ```

6. **搜索模板**
   ```http
   GET /api/prompt-templates/search?keyword=查询
   ```

7. **渲染模板**
   ```http
   POST /api/prompt-templates/{id}/render
   Content-Type: application/json
   
   {
     "table_name": "users",
     "condition": "status = 'active'"
   }
   ```

## 配置说明

### 数据库配置

在 `application.yml` 中配置数据库连接：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mcp_db
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:password}
    driver-class-name: org.postgresql.Driver
```

### 环境配置

- **开发环境** (`application-dev.yml`): 启用SQL日志，使用create-drop模式
- **生产环境** (`application-prod.yml`): 关闭SQL日志，使用validate模式

## 支持的工具

1. **database_query**: 执行SQL查询
2. **database_tables**: 获取数据库表列表
3. **table_structure**: 获取表结构信息
4. **prompt_template_render**: 渲染提示词模板

## 示例用法

### 使用MCP客户端连接

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 连接到MCP服务器
    server_params = StdioServerParameters(
        command="java",
        args=["-jar", "target/mcp-pg-server-1.0.0.jar"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()
            
            # 执行数据库查询
            result = await session.call_tool(
                "database_query",
                {"sql": "SELECT version()", "parameters": []}
            )
            print(result)
            
            # 渲染提示词模板
            rendered = await session.call_tool(
                "prompt_template_render",
                {
                    "template_id": "sample-1",
                    "variables": {
                        "table_name": "users",
                        "condition": "age > 18",
                        "columns": "name, email"
                    }
                }
            )
            print(rendered)

if __name__ == "__main__":
    asyncio.run(main())
```

## 开发指南

### 添加新的MCP方法

1. 在 `McpApplicationService` 中添加新的处理方法
2. 在 `getSupportedMethods()` 中注册新方法
3. 在 `handleToolsCall()` 中添加工具调用处理

### 添加新的领域模型

1. 在 `domain/model` 中创建领域模型
2. 在 `domain/repository` 中定义仓库接口
3. 在 `infrastructure/persistence` 中实现仓库
4. 在 `application/service` 中实现应用服务

## 测试

```bash
# 运行单元测试
mvn test

# 运行集成测试
mvn verify
```

## 部署

### Docker部署

```dockerfile
FROM openjdk:8-jre-alpine
COPY target/mcp-pg-server-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

```bash
# 构建Docker镜像
docker build -t mcp-pg-server .

# 运行容器
docker run -p 8080:8080 \
  -e DB_HOST=postgres \
  -e DB_USERNAME=postgres \
  -e DB_PASSWORD=password \
  mcp-pg-server
```

### 生产环境部署

```bash
# 构建JAR包
mvn clean package

# 运行应用
java -jar target/mcp-pg-server-1.0.0.jar --spring.profiles.active=prod
```

## 监控和日志

- 健康检查: `GET /mcp/health`
- 应用指标: `GET /actuator/metrics`
- 日志文件: `logs/mcp-server.log`

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**注意**: 请确保在生产环境中使用强密码和适当的网络安全配置。
