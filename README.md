# ppt-producer

面向商业方案、科技发布与技术方案、教学课件、工作总结与述职汇报、党建学习与主题活动、创意提案等场景的 Codex Skill。它先冻结一份 canonical brief，再按交付需求路由到标准可编辑演示、舞台级网页演讲或双轨交付。

## 能力

- 统一内容蓝图、事实、数据、来源、逐页结论与演讲备注
- 支持商业、科技、教学、工作汇报、党建和创意六类场景
- 按硬交付要求选择 `standard-editable`、`keynote-web` 或 `dual-delivery`
- 提供 brief 初始化、校验和四层质量门禁

## 安装

将本仓库克隆到 Codex Skills 目录：

```bash
git clone https://github.com/aus666666/ppt-producer.git ~/.codex/skills/ppt-producer
```

## 运行依赖

实际生成或修改 Deck 时，本 Skill 会按生产模式调用两个同级 Skill：

- `../dashi-ppt/SKILL.md`：可编辑 HTML、PPTX、PDF 等标准交付
- `../guizang-ppt-skill/SKILL.md`：讲者模式、观众屏和网页演讲

请把对应依赖安装为 `ppt-producer` 的同级目录；缺失依赖时，相关生产模式不会运行。

## 目录

- `SKILL.md`：主决策流程
- `references/`：内容契约、引擎路由、场景剧本和质量门禁
- `scripts/`：canonical brief 初始化与校验
- `agents/openai.yaml`：Skill 元数据

## 校验

```bash
python3 scripts/validate_brief.py path/to/brief.json
```
