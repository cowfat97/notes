# Data Service

基于 Spring Boot、Maven、PostgreSQL 和 Nacos 的数据中心服务。

## 技术栈

- **Java 8+**
- **Spring Boot 2.7.18**
- **Maven**
- **PostgreSQL**
- **Nacos** (服务注册与发现、配置中心)
- **Spring Data JPA**
- **Lombok**

## 项目结构

```
data-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/dataservice/
│   │   │       ├── DataServiceApplication.java    # 主应用类
│   │   │       ├── controller/                    # 控制器层
│   │   │       │   └── DataController.java
│   │   │       ├── service/                       # 服务层
│   │   │       │   └── DataService.java
│   │   │       ├── repository/                    # 数据访问层
│   │   │       │   └── DataRepository.java
│   │   │       ├── entity/                        # 实体类
│   │   │       │   └── DataEntity.java
│   │   │       ├── dto/                           # 数据传输对象
│   │   │       │   └── DataDTO.java
│   │   │       └── exception/                     # 异常处理
│   │   │           └── GlobalExceptionHandler.java
│   │   └── resources/
│   │       └── application.yml                    # 配置文件
│   └── test/                                      # 测试代码
├── pom.xml                                        # Maven 配置
└── README.md                                      # 项目说明
```

## 环境要求

- JDK 1.8 或更高版本
- Maven 3.6+
- PostgreSQL 12+
- Nacos Server 2.0+

## 配置说明

### 1. 数据库配置

在 `application.yml` 中配置 PostgreSQL 连接信息：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/datadb
    username: postgres
    password: postgres
```

### 2. Nacos 配置

在 `application.yml` 中配置 Nacos 服务地址：

```yaml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: localhost:8848
      config:
        server-addr: localhost:8848
```

## 快速开始

### 1. 创建数据库

```sql
CREATE DATABASE datadb;
```

### 2. 启动 Nacos

下载并启动 Nacos Server：

```bash
# 下载 Nacos
# 启动 Nacos (单机模式)
sh startup.sh -m standalone
```

### 3. 编译项目

```bash
mvn clean install
```

### 4. 运行项目

```bash
mvn spring-boot:run
```

或者：

```bash
java -jar target/data-service-1.0.0.jar
```

## API 接口

### 创建数据
```
POST /api/data
Content-Type: application/json

{
  "dataName": "测试数据",
  "dataType": "test",
  "dataContent": "这是测试内容",
  "status": "active"
}
```

### 查询所有数据
```
GET /api/data
```

### 根据ID查询
```
GET /api/data/{id}
```

### 根据类型查询
```
GET /api/data/type/{dataType}
```

### 搜索数据
```
GET /api/data/search?keyword=测试
```

### 更新数据
```
PUT /api/data/{id}
Content-Type: application/json

{
  "dataName": "更新后的数据",
  "dataType": "test",
  "dataContent": "更新后的内容",
  "status": "active"
}
```

### 删除数据
```
DELETE /api/data/{id}
```

### 健康检查
```
GET /api/data/health
```

## 功能特性

- ✅ RESTful API 接口
- ✅ PostgreSQL 数据库持久化
- ✅ Nacos 服务注册与发现
- ✅ Nacos 配置中心支持
- ✅ JPA 数据访问
- ✅ 全局异常处理
- ✅ 参数验证
- ✅ 自动创建数据表

## 开发说明

### 添加新功能

1. 在 `entity` 包中创建实体类
2. 在 `repository` 包中创建 Repository 接口
3. 在 `service` 包中创建 Service 类
4. 在 `controller` 包中创建 Controller 类
5. 在 `dto` 包中创建 DTO 类（如需要）

### 数据库迁移

项目使用 JPA 的 `ddl-auto: update` 模式，首次启动时会自动创建表结构。

如需使用 Flyway 或 Liquibase 进行数据库版本管理，可以添加相应依赖。

## 注意事项

1. 确保 PostgreSQL 和 Nacos 服务已启动
2. 根据实际环境修改 `application.yml` 中的配置
3. 生产环境建议关闭 `show-sql` 和调整日志级别
4. 生产环境建议使用连接池配置（如 HikariCP）

## 许可证

MIT License

