# Nacos

## What — 是什么

阿里巴巴开源的服务发现、配置管理平台。Nacos = Naming（服务发现）+ Configuration（配置管理）+ Service（服务）。

```text
Nacos Server
  ├─ 服务注册与发现（替代 Eureka）
  ├─ 配置中心（替代 Spring Cloud Config / Apollo）
  └─ 健康检查（临时实例 heartbeat，持久实例主动探测）
```

| 概念 | 说明 |
|------|------|
| Namespace | 命名空间，环境隔离（dev/test/prod） |
| Group | 服务分组（同一环境内的更细粒度隔离） |
| Service | 服务，包含多个实例 |
| Instance | 服务实例（IP:Port） |
| 临时实例 | 靠心跳维持，心跳断了自动剔除（类似 Eureka） |
| 持久实例 | 不靠心跳，主动健康检查（类似 DNS） |

---

## How — 怎么用

### 服务注册与发现

```java
// Spring Cloud Alibaba
@SpringBootApplication
@EnableDiscoveryClient
public class OrderService {
    public static void main(String[] args) {
        SpringApplication.run(OrderService.class, args);
    }
}
```

```yaml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
        namespace: dev
        group: order-group
```

启动后自动注册到 Nacos，Nacos 控制台能看到 `order-service` 及其 IP:Port。

**调用链路**：

```text
Gateway → Nacos Server "我要找 order-service"
       ← Nacos 返回 Instance 列表 [192.168.3.1:8080, 192.168.3.2:8080]
       → Gateway 负载均衡选一个 → 转发请求
```

配合 Spring Cloud LoadBalancer / Ribbon 自动客户端负载均衡，不需要在代码里写 IP。

### 配置管理

```yaml
# Nacos 控制台或 bootstrap.yml
spring:
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        namespace: dev
        file-extension: yaml
        group: DEFAULT_GROUP
```

配置存在 Nacos 服务端，应用启动时拉取。运行中改配置 → Nacos 推通知 → 应用热更新（`@RefreshScope`）。

**为什么比本地文件好**：所有实例同一份配置、改一个地方全局生效、有版本历史和回滚、安全管理（敏感配置加密）。

### AP vs CP

```text
AP 模式（默认）：
  Nacos 集群，数据异步同步
  网络分区时保证可用性，可能读到旧数据
  适合服务发现（短暂不一致影响不大）

CP 模式：
  基于 Raft 协议，数据强一致
  网络分区时牺牲可用性保证一致性
  适合配置管理（读错数据库密码就炸了）
```

Nacos 的服务发现和配置管理可以用不同一致性级别——服务发现 AP，配置管理 CP。

---

## Why — 微服务体系里 Nacos 的位置

### 替代品对比

| | Nacos | Eureka | Consul | ZooKeeper |
|------|-------|--------|--------|----------|
| CAP | AP / CP 可切换 | AP | CP | CP |
| 配置中心 | 内置 | 无（需 Spring Cloud Config） | 内置 | 无 |
| 健康检查 | TCP/HTTP/MySQL | HTTP heartbeat | TCP/HTTP | TCP |
| 一致性协议 | 自研 Distro / Raft | 无（Peer to Peer） | Raft | ZAB |
| 国内生态 | 最强（Spring Cloud Alibaba） | Netflix 不再维护 | HashiCorp | 老牌但重 |
| 控制台 | 有 | 有 | 有 | 无 |

**为什么国内 Nacos 主流**：Spring Cloud Alibaba 深度集成、配置中心不需要额外部署、阿里背书 + 开源活跃。

### 在 LLM 系统中的应用

```text
QwenPaw 这类 Agent 平台的微服务拆分：
  Agent Gateway → Nacos 发现后端 Agent Service
  LLM Router → Nacos 发现多个模型服务实例
  配置中心 → 模型参数、API Key、prompt 模板热更新
```

微服务化的 Agent 系统里 Nacos 是基础设施——服务找得到、配置改得了。

---

## 面试追问

### Nacos 和 Eureka 的区别？

Eureka 只有服务发现（AP），配置中心要另装 Spring Cloud Config。Nacos 服务发现 + 配置中心一体，AP / CP 可切。Eureka 2.0 已停更，Nacos 还在活跃开发。

### 健康检查机制？

临时实例：客户端每 5s 发心跳，15s 没收到就剔除。持久实例：Nacos Server 主动探测（TCP/HTTP/MySQL）。AP 模式下剔除不保证一致性。

### 配置热更新怎么做？

`@RefreshScope` + Nacos Config。Nacos 检测到配置变更 → 发通知 → Spring Cloud 重新绑定配置 → `@Value` 字段刷新。注意：Bean 重建期间旧实例可能还读旧值。

### CP 模式的数据一致性怎么保证？

Raft 协议。写请求到 Leader → Leader 发送日志到 Follower → 过半确认 → Leader 提交 → 返回。节点必须是奇数，至少 N/2+1 存活才选举。
