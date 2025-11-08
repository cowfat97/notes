package com.example.mcp;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.junit4.SpringRunner;

/**
 * MCP服务器应用测试类
 */
@RunWith(SpringRunner.class)
@SpringBootTest
@ActiveProfiles("test")
public class McpPgServerApplicationTests {

    @Test
    public void contextLoads() {
        // 测试Spring上下文是否能正常加载
    }
}
