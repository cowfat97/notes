-- 创建提示词模板表
CREATE TABLE IF NOT EXISTS prompt_templates (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    content TEXT NOT NULL,
    variables TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    created_by VARCHAR(255),
    enabled BOOLEAN NOT NULL DEFAULT true
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_prompt_templates_name ON prompt_templates(name);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_enabled ON prompt_templates(enabled);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_created_at ON prompt_templates(created_at);

-- 插入示例数据
INSERT INTO prompt_templates (id, name, description, content, category, created_at, updated_at, created_by, enabled) VALUES
('sample-1', 'SQL查询助手', '帮助用户生成SQL查询语句的模板', '请帮我生成一个SQL查询语句，用于查询{{table_name}}表中{{condition}}的记录，需要返回{{columns}}字段。', 'sql', NOW(), NOW(), 'system', true),
('sample-2', '数据分析助手', '帮助用户进行数据分析的模板', '请分析以下数据：{{data_description}}，重点关注{{analysis_focus}}，并提供{{output_format}}格式的分析结果。', 'analysis', NOW(), NOW(), 'system', true),
('sample-3', '代码生成助手', '帮助用户生成代码的模板', '请帮我生成{{language}}代码，实现{{functionality}}功能，要求{{requirements}}。', 'code', NOW(), NOW(), 'system', true)
ON CONFLICT (id) DO NOTHING;
