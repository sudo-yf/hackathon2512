# 贡献指南

## 开发环境

```bash
uv sync
cp .env.example .env
```

## 本地检查

```bash
make lint
make test
make check
```

## 提交要求

- 变更说明清晰：问题、方案、验证
- 行为变化必须同步更新文档
- 不提交无关重构或格式化噪音

## PR 检查清单

- [ ] lint 通过
- [ ] test 通过
- [ ] README/docs 已同步
- [ ] 配置变更已标注兼容性影响

