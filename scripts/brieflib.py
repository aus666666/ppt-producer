#!/usr/bin/env python3
"""Shared constants and helpers for ppt-producer brief tooling."""

from __future__ import annotations

import re
from typing import Any


SCENARIOS = {
    "business",
    "technology",
    "education",
    "work-report",
    "party-building",
    "creative",
}

PRODUCTION_MODES = {"auto", "standard-editable", "keynote-web", "dual-delivery"}
DELIVERABLES = {"html", "pptx", "pdf", "speaker-web"}
CONFIDENTIALITY = {"public", "internal", "confidential"}
MEDIA_POLICIES = {"none", "provided", "generate", "reserve"}
MEDIA_TYPES = {"image", "video", "screenshot", "diagram", "logo"}
MEDIA_RIGHTS = {"owned", "licensed", "public-domain", "unknown"}
MEDIA_STATUSES = {"available", "planned", "missing"}
STATUSES = {"draft", "ready"}
SOURCE_TYPES = {
    "official-document",
    "official-website",
    "law-regulation",
    "internal-document",
    "dataset",
    "report",
    "article",
    "book",
    "user-provided",
}
PARTY_AUTHORITY_SOURCE_TYPES = {"official-document", "official-website", "law-regulation"}
DECISION_TOPICS = {
    "production-mode",
    "visual-style",
    "theme",
    "media-policy",
    "deliverables",
    "brand",
}
DECISION_CONFIRMATIONS = {"user", "delegated", "assumed"}
GUIZANG_VISUAL_STYLES = {"guizang-a", "guizang-b"}

ROLES = {
    "cover",
    "statement",
    "breakdown",
    "transition",
    "context",
    "metrics",
    "trend",
    "comparison",
    "distribution",
    "relationship",
    "case",
    "image",
    "process",
    "risks",
    "observation",
    "ambient",
    "actions",
    "result",
    "team",
    "closing",
    "practice",
    "assessment",
}

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"(?:TODO|TBD|待补充|请输入文本|占位)", re.IGNORECASE)


OUTLINES: dict[str, list[tuple[str, str, str]]] = {
    "business": [
        ("cover", "商业提案", "用一句价值主张建立预期"),
        ("context", "问题与机会", "界定客户问题及其代价"),
        ("trend", "为什么是现在", "证明窗口期已经形成"),
        ("statement", "解决方案", "说明方案如何改变关键流程"),
        ("metrics", "客户价值", "量化收益与体验改善"),
        ("process", "商业模式", "解释付费、成本与规模化逻辑"),
        ("case", "验证证据", "展示试点、客户或增长证据"),
        ("comparison", "竞争与差异", "建立公平可核验的比较"),
        ("actions", "落地路径", "明确里程碑、资源和风险"),
        ("closing", "决策请求", "让受众知道下一步需要做什么"),
    ],
    "technology": [
        ("cover", "技术方案", "定义系统与核心能力"),
        ("context", "问题边界", "明确输入、输出、约束和非目标"),
        ("metrics", "现状与瓶颈", "用基线证明改变的必要性"),
        ("relationship", "总体架构", "展示组件、层次和边界"),
        ("process", "关键流程", "解释请求、数据或任务如何流动"),
        ("statement", "核心创新", "说明相对常规方案的关键变化"),
        ("comparison", "Benchmark", "呈现条件完整的验证结果"),
        ("case", "Demo 与案例", "说明成功路径与失败边界"),
        ("risks", "可靠性与成本", "覆盖安全、成本和运行风险"),
        ("closing", "路线图", "明确试点、扩展和验收"),
    ],
    "education": [
        ("cover", "课程主题", "建立学习目标和课程范围"),
        ("assessment", "先备知识", "诊断学习者起点"),
        ("statement", "核心概念", "一次讲清一个可迁移模型"),
        ("process", "示范步骤", "逐步展示正确方法"),
        ("comparison", "正例与反例", "澄清边界和常见误区"),
        ("practice", "引导练习", "让学习者按步骤尝试"),
        ("assessment", "理解检查", "用问题或短答获得反馈"),
        ("case", "迁移案例", "把方法应用到新场景"),
        ("result", "课程总结", "凝练可复述的关键要点"),
        ("closing", "作业与延伸", "给出标准、资源和下一步"),
    ],
    "work-report": [
        ("cover", "工作汇报", "明确周期、团队和主题"),
        ("statement", "执行摘要", "结论先行呈现整体状态"),
        ("context", "目标与口径", "对齐计划、实际和比较基准"),
        ("result", "关键成果", "展示结果而非活动清单"),
        ("trend", "KPI 与趋势", "用统一口径解释表现"),
        ("case", "亮点案例", "提炼可复制的经验"),
        ("risks", "偏差与根因", "区分症状、原因和外部因素"),
        ("risks", "风险与依赖", "说明概率、影响和责任边界"),
        ("actions", "下一阶段计划", "明确里程碑、资源和验收"),
        ("closing", "需要决策", "提出清晰的批准、支持或取舍"),
    ],
    "party-building": [
        ("cover", "党建主题", "准确呈现主题、组织和日期"),
        ("context", "学习目的与依据", "列出正式文件或权威来源"),
        ("trend", "背景脉络", "澄清时间、事件和概念边界"),
        ("breakdown", "核心要义", "按权威结构组织重点"),
        ("relationship", "职责映射", "连接要求与本单位职责"),
        ("case", "实践案例", "呈现有来源的条件与结果"),
        ("risks", "问题与差距", "基于真实材料识别改进空间"),
        ("actions", "行动计划", "落实责任、时间、成果物和验收"),
        ("risks", "纪律与风险", "准确呈现边界和要求"),
        ("closing", "学习要点与安排", "收束共识并明确下一步"),
    ],
    "creative": [
        ("cover", "创意概念", "用概念名和一句主张定调"),
        ("context", "受众洞察", "揭示真实张力而非人口标签"),
        ("observation", "创意机会", "说明现有表达的缺口"),
        ("statement", "Big Idea", "提出可复述的核心创意"),
        ("image", "视觉世界", "建立色、形、字体和材质语言"),
        ("case", "关键场景", "展示高记忆触点"),
        ("process", "用户旅程", "说明进入、参与、分享和转化"),
        ("relationship", "渠道与内容系统", "展示可扩展的表达体系"),
        ("risks", "可行性", "覆盖时间、预算、技术和风险"),
        ("closing", "下一步", "明确原型、测试和决策点"),
    ],
}


def adjusted_outline(scenario: str, page_count: int) -> list[tuple[str, str, str]]:
    """Return an outline with cover and closing preserved at any supported length."""
    base = OUTLINES[scenario]
    if page_count == len(base):
        return base.copy()
    if page_count < len(base):
        return [base[0], *base[1 : page_count - 1], base[-1]]

    result = base[:-1].copy()
    extra_count = page_count - len(base)
    for index in range(extra_count):
        result.append(
            (
                "breakdown",
                f"拓展分析 {index + 1}",
                "补充支撑总命题的证据、案例或实施细节",
            )
        )
    result.append(base[-1])
    return result


def slide_id(index: int, role: str) -> str:
    """Create a stable, readable initial ID without using page numbers alone."""
    return "cover" if index == 0 else ("closing" if role == "closing" else f"{role}-{index + 1:02d}")


def recommended_mode(brief: dict[str, Any]) -> str:
    """Recommend a production mode from hard delivery requirements first."""
    explicit = brief.get("productionMode")
    if explicit in PRODUCTION_MODES - {"auto"}:
        return explicit

    deliverables = set(brief.get("deliverables") or [])
    needs_editable = bool(deliverables & {"pptx", "pdf"})
    needs_speaker = "speaker-web" in deliverables
    if needs_editable and needs_speaker:
        return "dual-delivery"
    if needs_speaker:
        return "keynote-web"
    if brief.get("scenario") == "creative" and deliverables <= {"html", "speaker-web"}:
        return "keynote-web"
    return "standard-editable"
