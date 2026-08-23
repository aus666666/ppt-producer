---
name: ppt-producer
description: 面向商业方案、科技发布与技术方案、教学课件、工作总结与述职汇报、党建学习与主题活动、创意提案等高频场景，规划、生成、修改和验收专业 PPT/演示文稿。统一内容蓝图后，按交付需求路由到 Dashi 的可编辑 HTML/PPTX/PDF 生产链、Guizang 的电子杂志/瑞士风网页演讲链，或双轨交付；适用于“做PPT/幻灯片/汇报材料/课件/路演/发布会/演讲稿/可编辑PPTX/网页版Slides”等请求。
---

# PPT Producer

把内容正确性、场景叙事、视觉系统和交付格式视为同一条生产链。先冻结一份 canonical brief，再选择一个生产模式；不要先选模板再硬塞内容。

## 资源加载顺序

1. 始终读取 [content-contract.md](references/content-contract.md) 和 [engine-routing.md](references/engine-routing.md)。
2. 只读取用户场景对应的 [scenario-playbooks.md](references/scenario-playbooks.md) 小节。
3. 生成完成后读取 [quality-gates.md](references/quality-gates.md)。
4. 只有进入实际 Deck 生成/修改阶段时，选定 `standard-editable` 后完整读取并遵循相邻 Skill `../dashi-ppt/SKILL.md`。
5. 只有进入实际 Deck 生成/修改阶段时，选定 `keynote-web` 后完整读取并遵循相邻 Skill `../guizang-ppt-skill/SKILL.md`。
6. 进入实际双轨生成时再按上面顺序读取两者；共享 brief，但分别遵循各自模板和校验规则。

如果依赖 Skill 不存在，停止对应生产模式并报告缺失项；不要临时复刻其生成器或模板。

## 不可妥协的原则

- 只维护一份事实源：标题、结论、数据、单位、日期、专名和行动项先写入 canonical brief。
- 先定交付再定风格：可编辑 PPTX、浏览器演讲、讲者模式、PDF、离线 HTML 等要求优先于审美偏好。
- 不混用运行时：同一产物不得混合 Dashi 组件与 Guizang CSS/HTML 类名。双轨交付是两份独立产物，不是一份混合模板。
- 不编造事实：缺少数据、政策原文、引用、组织信息或品牌素材时，标记缺口或询问；不得用模板默认文案补事实。
- 每页只讲一个主结论：页面标题表达结论或任务，不使用空泛的“背景介绍”“核心内容”占位标题交付。
- 设计服从场景：教学优先可读与练习，工作汇报优先结论与决策，商业优先说服，科技优先证据与架构，党建优先准确与庄重，创意优先概念与记忆点。
- 生成即验收：脚本校验、浏览器视觉检查、内容核对、文件可打开与格式正确缺一不可。

## 工作流

### 1. 建立任务边界

提取或合理假设以下信息：`scenario`、目标、受众、使用场合、语言、页数或时长、交付格式、来源材料、品牌要求、媒体意图、必须包含和必须避免的内容。

只在缺口会改变生产模式、事实正确性或素材处理时提问；一次询问 1–3 个关键问题。用户明确“都你来定/直接做”时，自主选择并在交付中说明假设。

用户只说“做 PPT”而未指定文件格式时，默认 HTML；若同时强调正式文件、归档、交付客户或后续编辑且没有授权代选，先确认 HTML/PPTX/PDF。用户要求直接做时可默认 HTML，但必须在交付中明确说明。

### 2. 创建 canonical brief

使用脚本创建骨架：

```bash
python3 <skill-root>/scripts/new_brief.py \
  --scenario business \
  --title "项目名称" \
  --objective "希望受众理解或采取的行动" \
  --audience "目标受众" \
  --page-count 10 \
  --out output/project-name/brief.json
```

按 [content-contract.md](references/content-contract.md) 补全来源、事实、指标、逐页结论、视觉意图和演讲备注。正式生成前把 `status` 改为 `ready`，再运行：

```bash
python3 <skill-root>/scripts/validate_brief.py output/project-name/brief.json
```

有错误时修正后再生成；警告必须逐项判断并在验收记录中闭环。

用户只要求大纲、逐页计划或 brief 时，在本步骤校验并交付 brief，不加载引擎模板、不选择具体视觉主题、不渲染 Deck。把仍缺少的数据、来源、品牌素材或决策写入 `readiness.blockers`，不要自定义其他阻塞字段。

处理现有 Deck 时，先识别其来源和运行时，再从现有页面、备注和用户材料反向建立 brief。保留未修改页的稳定 ID、事实和素材；只重写用户要求的页面及受其影响的跨页叙事。Dashi 产物继续用 Dashi 修改，Guizang 产物继续用 Guizang 修改；除非用户明确要求迁移，不要在修订中偷偷更换引擎。

### 3. 选择生产模式

按 [engine-routing.md](references/engine-routing.md) 决策：

- `standard-editable`：需要浏览器编辑、PPTX/PDF、密集数据、培训课件、日常汇报或模板多方案。
- `keynote-web`：需要现场演讲、观众屏、讲者备注、排练计时、电子杂志风或瑞士风单文件网页。
- `dual-delivery`：既要可编辑/归档文件，又要舞台级网页演讲；两个产物共享事实和叙事顺序。

不要用审美偏好覆盖硬交付要求。用户要求 PPTX 且又要求完整演讲者模式时，默认 `dual-delivery`。

### 4. 设计叙事与逐页计划

读取相应场景 Playbook，先写“页码 → 页面任务 → 主结论 → 证据 → 视觉角色 → 演讲者补充”。优先采用 8–12 页基础结构；按实际内容扩展或压缩，不用固定页数强行凑页。

对每页执行：

1. 写一句可验证的 `keyMessage`。
2. 绑定支持它的 `facts`、`metrics` 或用户素材。
3. 选择合适的页面 `role`，不要把概念页伪装成数据页。
4. 决定观众看什么、讲者补充什么。
5. 删除不服务本页结论的内容。

### 5. 执行选定引擎

#### Dashi / `standard-editable`

完整遵循 `../dashi-ppt/SKILL.md`：展示其风格网格并确认主题（除非用户已授权代选），把 canonical brief 映射为 Dashi schema v2，使用 3 个模板候选 + 1 个 bespoke 方案，运行 props、goal、copy、渲染和四方案质量校验。需要 PPTX/PDF 时使用 Dashi 的导出链。

#### Guizang / `keynote-web`

完整遵循 `../guizang-ppt-skill/SKILL.md`：选择电子杂志或瑞士风，使用对应模板与登记布局，生成稳定 `data-slide-id` 和 `SPEAKER_NOTES`，运行演讲者模式及瑞士布局校验，并实测观众屏、翻页、计时和恢复能力。

#### 双轨 / `dual-delivery`

先冻结 brief 的 slide ID、顺序、关键结论和证据，再分别生成：

1. Dashi 可编辑/归档版。
2. Guizang 舞台演讲版。

允许两版因媒介不同而改变信息密度和构图；不允许更改事实、数字、单位、结论方向和行动项。使用 [quality-gates.md](references/quality-gates.md) 的 cross-delivery gate 对齐。

### 6. 处理素材

- 将用户素材按语义和页码登记到 brief，不直接把临时路径写入最终产物。
- 证据截图、UI、代码和 dashboard 以保真为先；照片和插图以主体安全区为先。
- 只有用户明确要求生成原创视觉时才调用 image generation；多张独立图片按当前环境能力并行生成。
- 同一素材不要跨多个逻辑页重复充当不同证据。
- 无合法来源或使用权限的标志、人物照片、地图、政策原文和商业数据不得擅自补入。

### 7. 验收与交付

按 [quality-gates.md](references/quality-gates.md) 完成四层验收：内容、叙事、视觉/运行时、交付。状态只使用：

- `通过`：所有必需门禁通过。
- `待修正`：可在当前授权范围内修复；修复后只复验受影响页和跨页一致性。
- `阻塞`：缺少事实、权限、素材或必要依赖，无法安全完成。

最终仅交付用户要求的产物和必要使用说明；不要把内部比较稿、模板预览、临时 brief 或校验截图当成最终文件。

## 维护本 Skill

修改场景或契约后运行：

```bash
python3 <skill-root>/scripts/validate_brief.py <representative-brief.json>
python3 <skill-creator-root>/scripts/quick_validate.py <skill-root>
```

保持 `SKILL.md` 为决策主线；将新增场景细则、引擎约束和 QA 规则放入直接引用的 `references/` 文件，不复制两套依赖 Skill 的大段原文或模板资产。
