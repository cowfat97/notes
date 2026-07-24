# Docker

## What — 容器是什么

### 容器 vs 虚拟机

```text
虚拟机                              容器
──────                              ────
App                                 App
  ↓                                   ↓
Guest OS (完整操作系统，几 GB)         Docker Engine
  ↓                                   ↓
Hypervisor (虚拟硬件)                 Host OS (共享内核)
  ↓                                   ↓
Host OS                             Hardware
  ↓
Hardware
```

| | 虚拟机 | 容器 |
|------|--------|------|
| 启动速度 | 分钟级 | 秒级 |
| 资源开销 | 每个 VM 独立 OS，GB 级 | 共享内核，MB 级 |
| 隔离级别 | Hypervisor 硬件隔离 | Namespace + Cgroup 进程隔离 |
| 密度 | 一台机器十几个 VM | 一台机器上百个容器 |

本质区别：虚拟机虚拟硬件，容器虚拟操作系统。容器是 Host OS 上的一个普通进程，只是被 Namespace 隔离了视角、被 Cgroup 限制了资源。

### Docker 架构

```text
Client (docker CLI)
  ↓ REST API
Daemon (dockerd)  ← 后台进程，管理镜像/容器/网络/卷
  ↓ gRPC
containerd         ← 容器运行时管理器，管理镜像和容器生命周期
  ↓ shim
runc               ← OCI 标准实现，真正创建容器的底层工具
```

逐步解耦：早期 Docker 是单体，后来拆出 containerd→runc。K8s 可以直接用 containerd 而不经过 dockerd。

### 核心三要素

```text
镜像 (Image)  →  只读模板（类比：Class）
容器 (Container) → 镜像的运行实例（类比：Object）
仓库 (Registry)  → 镜像存储和分发（类比：Maven 仓库）

docker pull → docker run → docker push
```

OCI（Open Container Initiative）定义了镜像格式和运行时规范，保证了 Docker/Podman/K8s 的容器互操作。

---

## How — 怎么用

### 镜像

#### 分层存储（UnionFS / Overlay2）

```text
镜像由多层只读文件系统叠加：

Container (可写层)      ← 写时复制 (CoW)
───────────────
Layer 4: CMD             ← 只读
Layer 3: COPY app.jar    ← 只读
Layer 2: RUN apt-get     ← 只读
Layer 1: FROM ubuntu     ← 只读
```

每一条 Dockerfile 指令生成一个层。层是只读的，容器启动时在顶部叠加一个可写层。修改文件时触发**写时复制（Copy-on-Write）**——从下层把文件复制到可写层再修改，原层不变。

**为什么分层**：镜像复用。同一个基础镜像的层在所有容器间共享，节省磁盘和拉取时间。

#### Dockerfile 关键指令

| 指令 | 用途 | 坑 |
|------|------|-----|
| `FROM` | 指定基础镜像 | 优先选 `alpine`/`slim`，减少体积和攻击面 |
| `COPY` vs `ADD` | 复制文件 | `ADD` 能自动解压 tar 和远程下载 → 行为不透明，用 `COPY` 更可控 |
| `RUN` | 构建时执行命令 | shell form（`RUN apt-get`）vs exec form（`RUN ["apt-get"]`），exec form 不启动 shell |
| `CMD` vs `ENTRYPOINT` | 容器启动命令 | `CMD` 可被 `docker run` 覆盖，`ENTRYPOINT` 不可覆盖。组合：`ENTRYPOINT ["java"]` + `CMD ["-jar", "app.jar"]` |
| `ENV` | 环境变量 | 构建时和运行时都生效；`ARG` 只在构建时 |
| `WORKDIR` | 工作目录 | 用绝对路径，不用 `cd` |
| `EXPOSE` | 声明端口 | 只是文档，不实际映射。映射用 `-p` |

**shell form vs exec form**：

```dockerfile
# shell form — 启动 sh -c "java -jar app.jar"，PID 1 是 sh，java 是子进程
CMD java -jar app.jar

# exec form — 直接启动 java，PID 1 是 java，能收到 SIGTERM
CMD ["java", "-jar", "app.jar"]
```

exec form 的容器能正确响应 `docker stop`（收到 SIGTERM 后优雅退出），shell form 的容器等到超时被 SIGKILL 强杀。

#### 多阶段构建（Multi-stage Build）

```dockerfile
# 阶段 1：编译
FROM maven:3.8-openjdk-11 AS build
COPY src /app/src
COPY pom.xml /app
RUN mvn -f /app/pom.xml clean package

# 阶段 2：运行（最终镜像只有运行时依赖）
FROM openjdk:11-jre-slim
COPY --from=build /app/target/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

**为什么**：编译工具链（Maven/GCC）不进最终镜像。镜像只包含运行时所需的 JRE + jar，体积从 GB 缩到 MB。

#### 镜像优化策略

| 手段 | 效果 | 原理 |
|------|------|------|
| 选对基础镜像 | alpine < slim < full | 攻击面小、体积小 |
| 合并 RUN 命令 | 减少层数 | `RUN apt-get update && apt-get install && rm -rf /var/lib/apt/lists/*` |
| .dockerignore | 减小 context | node_modules/、.git/ 不传进 daemon |
| 多阶段构建 | 编译工具不进镜像 | 只有产物进入最终镜像 |
| 合理排序层 | 利用缓存 | 不变的上层（依赖安装）放前面；频繁变的下层（COPY 代码）放后面 |
| dive 分析 | 找浪费空间 | `dive <image>` 逐层看新增文件 |

---

### 容器

#### 生命周期

```text
create  →  start  →  run（create + start）
  ↓         ↓
  分配资源   进程跑起来
              ↓
           pause / unpause（冻结/恢复，内核 cgroup freezer）
              ↓
           stop（SIGTERM → 10s 超时 → SIGKILL）
              ↓
           rm（-f 强制、-v 清 volume）
```

`docker stop` 发 SIGTERM → 应用程序可以优雅关闭（关闭连接、flush 数据）→ 超时后 SIGKILL 强杀。exec form 的 ENTRYPOINT 正确响应，shell form 的收不到。

#### 资源限制

```bash
docker run --cpus="1.5" \         # 最多用 1.5 个核
           --memory="512m" \       # 硬限制 512MB
           --memory-swap="1g" \    # 物理+swap 总共 1G
           --pids-limit=100 \      # 进程数上限
           nginx
```

Linux cgroup v2 实现。CPU 是相对权重（`--cpu-shares`）或绝对限制（`--cpus`），内存是硬限制（超了 OOM Kill）。

#### 调试

```bash
docker exec -it <容器> /bin/sh      # 进容器看
docker logs --tail 100 -f <容器>     # 看日志
docker inspect <容器>                # 全部元数据（IP、挂载、环境变量）
docker stats                         # 实时资源
docker top <容器>                     # 容器内进程
```

容器起不来的时候：`docker logs` 看启动日志 → 大概率是配置错了或端口冲突。如果刚启动就退出了，加 `--rm` 重跑看输出。

---

### 网络

#### 四种模式

| 模式 | 原理 | 何时用 |
|------|------|--------|
| **bridge**（默认） | docker0 虚拟网桥，NAT 到宿主机网卡，`-p` 映射端口 | 单机容器通信，最常用 |
| **host** | 容器直接使用宿主机网络栈，没有隔离 | 高性能（跳过 NAT）、端口冲突敏感 |
| **none** | 无网络，只有 lo 接口 | 安全要求极高 |
| **container** | 共享另一个容器的网络栈 | 两个容器必须共享 127.0.0.1 通信 |

#### bridge 端口映射原理

```text
宿主机 :8080 → iptables DNAT → docker0 网桥 → 容器 172.17.0.2:80
```

`-p 8080:80` 实际是加了 iptables 规则，把 `eth0:8080` 的流量转到 `172.17.0.2:80`。

#### 自定义网络 vs 默认 bridge

```bash
docker network create my-net
docker run --network my-net --name redis redis
docker run --network my-net --name app my-app
```

自定义网络内置 DNS 解析：`app` 容器内 `ping redis` 能直接解析到 Redis 容器的 IP。默认 bridge 没这个功能——只能用 IP。

#### 跨主机（了解）

```text
overlay   — Swarm 内置，多台机器一个虚拟网
macvlan   — 容器直接拿物理网络 IP，像真主机
Calico    — K8s 常用，BGP 路由
```

面试不会问太深，知道"跨主机不走 bridge"就行。

---

### 存储

#### 三种挂载

| | volume | bind mount | tmpfs |
|------|--------|-----------|-------|
| 存在位置 | `/var/lib/docker/volumes/` | 宿主机任意路径 | 内存 |
| 谁管理 | Docker | 用户 | Docker |
| 持久化 | 是 | 是 | 否（重启就丢） |
| 什么时候用 | 生产数据 | 开发（代码热更新、配置文件） | 临时敏感数据 |

#### volume 原理

```bash
docker volume create my-data
docker run -v my-data:/var/lib/mysql mysql

# volume 实际存在
/var/lib/docker/volumes/my-data/_data/
```

volume 和容器生命周期解耦——容器删了数据在。bind mount 路径写死在宿主机路径，容器删了没关系但迁移难。

---

## Why — 为什么这样设计

### Docker Compose

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports: ["8080:8080"]
    depends_on:
      - redis
      - postgres
    environment:
      - SPRING_DATASOURCE_URL=jdbc:postgresql://pg:5432/mydb

  redis:
    image: redis:7-alpine

  pg:
    image: postgres:15-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=secret

volumes:
  pgdata:
```

`docker compose up -d` → 三个容器、一个网络、一个卷全部创建。

**关键原理**：
- `depends_on` 只保证启动顺序，不保证服务就绪（MySQL 启动了但还在初始化，应用就连不上）。生产用 `wait-for-it.sh` 或 healthcheck
- 所有服务默认在一个自定义网络里，容器名即 DNS 名（`redis` 直接解析）
- Compose v2（`docker compose`）用 Go 重写，v1（`docker-compose`）是 Python。合并不再维护

### Docker vs K8s

| | Docker / Compose | K8s |
|------|------|-----|
| 编排范围 | 单机 | 集群（多节点） |
| 服务发现 | DNS 自动（Compose 网络内） | CoreDNS + Service |
| 自愈 | 手动（restart: always） | 自动（控制器循环） |
| 伸缩 | 手动改 scale 数 | 自动（HPA） |
| 配置管理 | env / env_file | ConfigMap / Secret |
| 升级策略 | 手动 restart | Rolling Update / Blue-Green |
| 适合场景 | 开发环境、小规模部署 | 生产集群、微服务 |

**边界判断**：单机能跑 → Compose；多台机器、高可用、自动伸缩 → K8s。大部分公司里的 LLM 应用（RAG/Agent）生产也用 K8s，但本地开发 Compose 够用。

### 在 RAG/Agent 系统中的定位

```text
开发环境（你的实际用法）：
  docker compose up -d → PostgreSQL + Redis + Milvus + Kafka
  Python 应用裸跑在宿主机，只有数据层容器化

生产环境：
  应用也容器化 → CI/CD 构建镜像 → K8s 部署
  数据层 → 有状态服务（PostgreSQL/Milvus）需要 StatefulSet + PV
```

---

## 面试追问

### 镜像优化怎么做？

减小体积：选 alpine/slim、多阶段构建、合并 RUN、清理缓存。加快构建：合理排序层（不常变的放前面）、利用缓存。减攻击面：最小基础镜像、不用 root、固定软件版本。

### COPY vs ADD？

`COPY` 只做文件复制，行为明确。`ADD` 额外支持 tar 自动解压和 URL 下载——行为隐式、不可预期。面试原则：默认用 `COPY`，需要解压时用 `ADD`。

### CMD vs ENTRYPOINT？

`CMD` 给默认参数，可被 `docker run <image> <cmd>` 覆盖。`ENTRYPOINT` 固定启动程序，不可覆盖。组合用：`ENTRYPOINT ["java"]` + `CMD ["-jar", "app.jar"]`——固定启动器，参数可换。

### 如何调试起不来的容器？

```bash
docker logs <容器>              # 看错误日志
docker run --rm -it <镜像> sh    # 覆盖 ENTRYPOINT，进 shell 排查
docker inspect <容器> | jq .[0].State  # 看退出码
```

### 容器安全风险？

- root 运行：默认容器内 root ≈ 宿主机 root（除非用 userns remap）
- 特权模式：`--privileged` 给所有设备、capability
- 镜像漏洞扫描：`docker scan` / Trivy / Clair
- 敏感信息：`ENV` 的值在 `docker inspect` 里明文可见，密钥用 Docker secret 或 K8s Secret

### bridge 和 host 网络？

bridge：隔离好，NAT 一次，大多数场景。host：零网络开销，但端口直接暴露在宿主机上——高性能和端口冲突敏感时用。

### volume 和 bind mount？

volume：Docker 管理，权限简单，生产用。bind mount：宿主机指定路径，开发用（代码挂进去热更新，`./src:/app/src`）。
