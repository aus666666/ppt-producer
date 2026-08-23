# Canonical Brief 内容契约

## 目录

1. 作用
2. 顶层字段
3. 来源、事实与指标
4. 逐页契约
5. 状态与冻结规则
6. 引擎映射

## 1. 作用

Canonical brief 是内容唯一真相源。它不等于 Dashi `goal.json`，也不等于 Guizang HTML；它在引擎之前冻结目标、事实、叙事和交付要求，便于单轨或双轨生成。

使用 `scripts/new_brief.py` 初始化，使用 `scripts/validate_brief.py` 校验。不要把生成器内部 props、CSS 类名或模板布局写入 brief。

## 2. 顶层字段

```json
{
  "schemaVersion": 1,
  "status": "draft",
  "title": "项目名称",
  "scenario": "business",
  "objective": "希望受众理解或采取的行动",
  "audience": "目标受众",
  "owner": "内容负责人",
  "eventDate": null,
  "language": "zh-CN",
  "productionMode": "auto",
  "deliverables": ["html"],
  "pageCount": 10,
  "durationMinutes": null,
  "brand": {
    "name": "",
    "logo": null,
    "colors": [],
    "fonts": [],
    "tone": ""
  },
  "constraints": {
    "mustInclude": [],
    "mustAvoid": [],
    "confidentiality": "internal",
    "requiresCitations": false
  },
  "readiness": {"blockers": [], "assumptions": [], "decisions": []},
  "sources": [],
  "media": {"policy": "none", "items": []},
  "narrative": {"thesis": "", "sections": [], "slides": []}
}
```

枚举：

- `scenario`: `business`、`technology`、`education`、`work-report`、`party-building`、`creative`。
- `productionMode`: `auto`、`standard-editable`、`keynote-web`、`dual-delivery`。
- `deliverables`: `html`、`pptx`、`pdf`、`speaker-web`。
- `confidentiality`: `public`、`internal`、`confidential`。
- `media.policy`: `none`、`provided`、`generate`、`reserve`。
- `status`: `draft`、`ready`。

`status: ready` 表示事实、逐页结论、来源和交付要求已准备好进入生成器；不是指最终 deck 已完成。

`readiness.blockers` 使用非空字符串记录缺失数据、来源、素材、授权或用户决策；非空时不得进入 `ready`。`assumptions` 也使用非空字符串记录已经采用且要向用户披露的合理假设。`decisions` 使用结构化对象记录已确认选择：

```json
{
  "topic": "visual-style",
  "value": "guizang-a",
  "confirmedBy": "delegated",
  "basis": "用户明确要求全部由 Agent 决定"
}
```

`topic` 使用 `production-mode`、`visual-style`、`theme`、`media-policy`、`deliverables`、`brand`；`confirmedBy` 使用 `user`、`delegated`、`assumed`。`visual-style` 只使用 `guizang-a` 或 `guizang-b`，并且必须由 `user` 或 `delegated` 确认，不能用普通假设替代。

媒体记录使用：

```json
{
  "id": "m1",
  "type": "screenshot",
  "location": "/absolute/source/path.png",
  "rights": "owned",
  "status": "available",
  "notes": "保真展示，不能裁掉关键数据"
}
```

`type` 使用 `image`、`video`、`screenshot`、`diagram`、`logo`；`rights` 使用 `owned`、`licensed`、`public-domain`、`unknown`；`status` 使用 `available`、`planned`、`missing`。页面 `mediaRefs` 只引用这里登记的 ID。进入引擎后再按其媒体 staging 规则复制到最终项目，不把源路径直接写进交付物。

## 3. 来源、事实与指标

来源记录：

```json
{
  "id": "S1",
  "title": "正式来源标题",
  "type": "official-document",
  "location": "文件路径或 URL",
  "publisher": "发布机构",
  "publishedAt": "2026-01-01",
  "accessedAt": "2026-08-15",
  "notes": "口径或使用限制"
}
```

`type` 使用：`official-document`、`official-website`、`law-regulation`、`internal-document`、`dataset`、`report`、`article`、`book`、`user-provided`。党建正式稿至少登记一个前三类权威来源，并补齐 `publisher` 与 ISO 日期 `publishedAt`。

事实记录放在对应 slide：

```json
{"claim": "需要在页面中成立的事实", "sourceIds": ["S1"], "confidence": "verified"}
```

指标记录：

```json
{
  "label": "转化率",
  "value": 18.6,
  "displayValue": "18.6%",
  "unit": "%",
  "period": "2026 Q2",
  "baseline": "2025 Q2",
  "sourceId": "S2"
}
```

规则：

- 显示值、单位、周期和比较基准必须一致。
- 预测和目标不得标记为历史实际。
- 引用原文时保留来源与边界，不用二手摘要冒充原文。
- `sourceIds` 和 `sourceId` 必须指向顶层 `sources` 已登记 ID。

## 4. 逐页契约

```json
{
  "id": "market-opportunity",
  "role": "context",
  "title": "机会正在从试验走向规模化",
  "objective": "解释为什么现在需要投入",
  "keyMessage": "窗口期由需求、技术成熟度和成本共同形成",
  "facts": [],
  "metrics": [],
  "items": [],
  "visualIntent": "三条证据形成因果链，不使用装饰性图表",
  "mediaRefs": [],
  "speakerNotes": {
    "purpose": "为下一页方案建立必要性",
    "talk": [],
    "transition": "既然窗口已打开，下一步看方案如何抓住它",
    "minutes": 0.8
  }
}
```

`role` 使用：`cover`、`statement`、`breakdown`、`transition`、`context`、`metrics`、`trend`、`comparison`、`distribution`、`relationship`、`case`、`image`、`process`、`risks`、`observation`、`ambient`、`actions`、`result`、`team`、`closing`、`practice`、`assessment`。

页面 ID 使用稳定英文 slug，不使用页码；双轨交付时保持一致。`visualIntent` 说明视觉任务，不写具体引擎类名。

## 5. 状态与冻结规则

从 `draft` 切换到 `ready` 前：

1. 补齐 title、objective、audience 和逐页 `objective`、`keyMessage`。
2. 清除“待补充/TODO/请输入文本”等占位文案；无法补齐项写入 `readiness.blockers` 并保持 `draft`。
3. 校验页面数量、唯一 ID、事实来源、指标口径和素材路径。
4. 确认交付模式与 deliverables 一致。
5. 党建场景设置 `requiresCitations: true`，补齐 `owner`、`eventDate`，登记带发布机构与发布日期的权威来源，并让页面 facts/metrics 绑定来源。
6. 演讲模式补充 `speakerNotes`；默认写提词卡，不写逐字稿。用户给出总时长时，每页填写 `minutes`，合计不超过总时长的 90%。

进入引擎后冻结：`slide.id`、标题语义、`keyMessage`、事实、指标和行动项。模板容量不足时优先拆页或缩短表达，不得删除 required facts 或改变数字。

## 6. 引擎映射

### Dashi

- 将 brief 映射为 schema v2 `goal.json`。
- 将 `keyMessage`、facts、metrics 和 items 组织为唯一 `slide.content.presentation`。
- 用 brief role、内容容量和媒体意图查询布局；不要把 role 当成最终 layout。
- 保持 3 个 template + 1 个 bespoke 的事实一致。

### Guizang

- 将 slides 映射为稳定 `data-slide-id` 和已登记布局。
- 将屏幕必要信息写入 slide，将背景、例子、转场写入 `SPEAKER_NOTES`。
- 依据 `visualIntent` 选择电子杂志或瑞士布局；不要把 Dashi layout/props 带入 HTML。

### 双轨

- 两版共享 ID、顺序、主结论和证据。
- 每版可针对媒介重新分配屏幕文字与备注，但不得创作第二套事实。
