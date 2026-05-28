export interface Diary {
  date: string;
  title: string;
  body: string;
}

const diaries: Diary[] = [
  {
    date: "2026-05-26 · 包头 · 雨",
    title: "读书 + 日记",
    body: `<p>继续看《统计学习方法》，决策树章节的公式推导比想象中复杂。CART 树的剪枝策略和 ID3/C4.5 的信息增益思路完全不同，需要重新理解。</p><p>晚上写了日记，整理了最近一周的时间安排。</p>`,
  },
  {
    date: "2026-05-25 · 包头 · 晴",
    title: "中间件笔记推进",
    body: `<p>Redis 集群模式整理完成。主从模式适合读写分离，哨兵模式解决高可用，Cluster 解决数据分片。三种方案不是互斥的，实际生产环境经常组合使用。</p><p>Nginx 反向代理和负载均衡的配置也写完了。</p>`,
  },
  {
    date: "2026-05-24 · 北京 · 多云",
    title: "开始准备面试",
    body: `<p>简历初稿完成，重点突出了 Spring Cloud 微服务项目经验和最近在学的 LLM 技术栈。投了几家深圳的岗位。</p><p>开始整理常见面试题，按 Java 基础、中间件、项目经验三个维度分类。</p>`,
  },
  {
    date: "2026-05-23 · 北京 · 晴",
    title: "RAG 项目收尾",
    body: `<p>MCP Server 基本跑通，笔记检索准确率比预期好。向量化模型用的 text-embedding-3-small，在中文笔记上的召回效果不错。</p><p>后续计划：加上重排序模块，提升 top-3 的精确率。</p>`,
  },
  {
    date: "2026-05-22 · 北京 · 阴",
    title: "LeetCode 刷题",
    body: `<p>动态规划找到感觉了。从爬楼梯到背包问题，状态转移方程越来越顺手。核心就两步：定义 dp[i] 的含义，找到递推关系。</p><p>今天刷了 5 道 DP 题，正确率 80%。</p>`,
  },
];

export default diaries;
