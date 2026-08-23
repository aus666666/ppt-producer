#!/usr/bin/env python3
"""Validate a ppt-producer canonical brief with standard-library checks."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from brieflib import (
    CONFIDENTIALITY,
    DECISION_CONFIRMATIONS,
    DECISION_TOPICS,
    DELIVERABLES,
    MEDIA_RIGHTS,
    MEDIA_POLICIES,
    MEDIA_STATUSES,
    MEDIA_TYPES,
    PLACEHOLDER_RE,
    PARTY_AUTHORITY_SOURCE_TYPES,
    PRODUCTION_MODES,
    ROLES,
    SCENARIOS,
    SLUG_RE,
    SOURCE_TYPES,
    STATUSES,
    GUIZANG_VISUAL_STYLES,
    recommended_mode,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_iso_date(value: Any) -> bool:
    if not nonempty(value):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def validate(data: Any) -> tuple[list[str], list[str], str]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["brief root must be an object"], warnings, "unknown"

    if data.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")

    status = data.get("status")
    if status not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")
    ready = status == "ready"

    for field in ("title", "objective", "audience", "language"):
        if not nonempty(data.get(field)):
            errors.append(f"{field} must be a non-empty string")

    scenario = data.get("scenario")
    if scenario not in SCENARIOS:
        errors.append(f"scenario must be one of {sorted(SCENARIOS)}")

    mode = data.get("productionMode")
    if mode not in PRODUCTION_MODES:
        errors.append(f"productionMode must be one of {sorted(PRODUCTION_MODES)}")

    deliverables = data.get("deliverables")
    if not isinstance(deliverables, list) or not deliverables:
        errors.append("deliverables must be a non-empty array")
        deliverable_set: set[str] = set()
    else:
        deliverable_set = set(deliverables)
        invalid = deliverable_set - DELIVERABLES
        if invalid:
            errors.append(f"unsupported deliverables: {sorted(invalid)}")
        if len(deliverable_set) != len(deliverables):
            warnings.append("deliverables contains duplicates")

    if mode == "keynote-web" and deliverable_set & {"pptx", "pdf"}:
        errors.append("keynote-web cannot satisfy pptx/pdf alone; use dual-delivery")
    if mode == "standard-editable" and "speaker-web" in deliverable_set:
        errors.append("standard-editable cannot satisfy speaker-web; use keynote-web or dual-delivery")
    if mode == "dual-delivery" and ready:
        if "speaker-web" not in deliverable_set:
            errors.append("dual-delivery requires speaker-web in deliverables")
        if not deliverable_set & {"pptx", "pdf"}:
            errors.append("dual-delivery requires pptx or pdf in deliverables")

    page_count = data.get("pageCount")
    if not isinstance(page_count, int) or isinstance(page_count, bool) or not 4 <= page_count <= 60:
        errors.append("pageCount must be an integer between 4 and 60")

    duration = data.get("durationMinutes")
    if duration is not None and (
        not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0
    ):
        errors.append("durationMinutes must be null or a positive number")

    event_date = data.get("eventDate")
    if event_date is not None and not valid_iso_date(event_date):
        errors.append("eventDate must be null or an ISO date in YYYY-MM-DD format")

    constraints = data.get("constraints")
    if not isinstance(constraints, dict):
        errors.append("constraints must be an object")
        constraints = {}
    if constraints.get("confidentiality") not in CONFIDENTIALITY:
        errors.append(f"constraints.confidentiality must be one of {sorted(CONFIDENTIALITY)}")

    media = data.get("media")
    if not isinstance(media, dict):
        errors.append("media must be an object")
        media = {}
    if media.get("policy") not in MEDIA_POLICIES:
        errors.append(f"media.policy must be one of {sorted(MEDIA_POLICIES)}")
    if not isinstance(media.get("items", []), list):
        errors.append("media.items must be an array")
        media_items = []
    else:
        media_items = media.get("items", [])
    media_ids: set[str] = set()
    for index, item in enumerate(media_items):
        path = f"media.items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{path} must be an object")
            continue
        media_id = item.get("id")
        if not nonempty(media_id) or not SLUG_RE.fullmatch(media_id):
            errors.append(f"{path}.id must be a lowercase kebab-case slug")
        elif media_id in media_ids:
            errors.append(f"duplicate media id: {media_id}")
        else:
            media_ids.add(media_id)
        if item.get("type") not in MEDIA_TYPES:
            errors.append(f"{path}.type must be one of {sorted(MEDIA_TYPES)}")
        if item.get("rights") not in MEDIA_RIGHTS:
            errors.append(f"{path}.rights must be one of {sorted(MEDIA_RIGHTS)}")
        if item.get("status") not in MEDIA_STATUSES:
            errors.append(f"{path}.status must be one of {sorted(MEDIA_STATUSES)}")
        if ready and media.get("policy") == "provided":
            if not nonempty(item.get("location")) or item.get("status") != "available":
                errors.append(f"{path} must be available with a location for provided media")

    readiness = data.get("readiness")
    if not isinstance(readiness, dict):
        errors.append("readiness must be an object")
        readiness = {}
    for field in ("blockers", "assumptions", "decisions"):
        if not isinstance(readiness.get(field), list):
            errors.append(f"readiness.{field} must be an array")
    for field in ("blockers", "assumptions"):
        values = readiness.get(field) if isinstance(readiness.get(field), list) else []
        for index, value in enumerate(values):
            if not nonempty(value):
                errors.append(f"readiness.{field}[{index}] must be a non-empty string")
    blockers = readiness.get("blockers") if isinstance(readiness.get("blockers"), list) else []
    if ready and blockers:
        errors.append("status cannot be ready while readiness.blockers is non-empty")
    elif status == "draft" and blockers:
        warnings.append(f"draft has {len(blockers)} unresolved readiness blockers")
    decisions = readiness.get("decisions") if isinstance(readiness.get("decisions"), list) else []
    visual_style_decisions: list[dict[str, Any]] = []
    for index, decision in enumerate(decisions):
        path = f"readiness.decisions[{index}]"
        if not isinstance(decision, dict):
            errors.append(f"{path} must be an object")
            continue
        if decision.get("topic") not in DECISION_TOPICS:
            errors.append(f"{path}.topic must be one of {sorted(DECISION_TOPICS)}")
        if not nonempty(decision.get("value")):
            errors.append(f"{path}.value must be non-empty")
        if decision.get("confirmedBy") not in DECISION_CONFIRMATIONS:
            errors.append(f"{path}.confirmedBy must be one of {sorted(DECISION_CONFIRMATIONS)}")
        if not nonempty(decision.get("basis")):
            errors.append(f"{path}.basis must be non-empty")
        if decision.get("topic") == "visual-style":
            visual_style_decisions.append(decision)
            if decision.get("value") not in GUIZANG_VISUAL_STYLES:
                errors.append(f"{path}.value must be one of {sorted(GUIZANG_VISUAL_STYLES)}")
            if decision.get("confirmedBy") not in {"user", "delegated"}:
                errors.append(f"{path}.confirmedBy must be user or delegated for visual-style")

    sources = data.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        sources = []
    source_ids: set[str] = set()
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{path} must be an object")
            continue
        source_id = source.get("id")
        if not nonempty(source_id):
            errors.append(f"{path}.id must be non-empty")
        elif source_id in source_ids:
            errors.append(f"duplicate source id: {source_id}")
        else:
            source_ids.add(source_id)
        if source.get("type") not in SOURCE_TYPES:
            errors.append(f"{path}.type must be one of {sorted(SOURCE_TYPES)}")
        if ready and (not nonempty(source.get("title")) or not nonempty(source.get("location"))):
            errors.append(f"{path} requires title and location when status is ready")
        published_at = source.get("publishedAt")
        if published_at is not None and not valid_iso_date(published_at):
            errors.append(f"{path}.publishedAt must be null or an ISO date in YYYY-MM-DD format")

    narrative = data.get("narrative")
    if not isinstance(narrative, dict):
        errors.append("narrative must be an object")
        narrative = {}
    slides = narrative.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("narrative.slides must be a non-empty array")
        slides = []
    if isinstance(page_count, int) and len(slides) != page_count:
        errors.append(f"pageCount is {page_count}, but narrative.slides has {len(slides)} entries")

    slide_ids: set[str] = set()
    total_facts = 0
    total_metrics = 0
    party_evidence_refs: set[str] = set()
    speaker_minutes: list[float] = []
    effective_mode = recommended_mode(data)
    for index, slide in enumerate(slides):
        path = f"narrative.slides[{index}]"
        if not isinstance(slide, dict):
            errors.append(f"{path} must be an object")
            continue
        sid = slide.get("id")
        if not nonempty(sid) or not SLUG_RE.fullmatch(sid):
            errors.append(f"{path}.id must be a lowercase kebab-case slug")
        elif sid in slide_ids:
            errors.append(f"duplicate slide id: {sid}")
        else:
            slide_ids.add(sid)
        if slide.get("role") not in ROLES:
            errors.append(f"{path}.role must be one of the supported roles")
        if not nonempty(slide.get("title")):
            errors.append(f"{path}.title must be non-empty")

        for field in ("objective", "keyMessage"):
            value = slide.get(field)
            if ready and not nonempty(value):
                errors.append(f"{path}.{field} must be non-empty when status is ready")
            elif isinstance(value, str) and PLACEHOLDER_RE.search(value):
                errors.append(f"{path}.{field} contains a placeholder")

        facts = slide.get("facts", [])
        if not isinstance(facts, list):
            errors.append(f"{path}.facts must be an array")
            facts = []
        total_facts += len(facts)
        for fact_index, fact in enumerate(facts):
            fact_path = f"{path}.facts[{fact_index}]"
            if not isinstance(fact, dict) or not nonempty(fact.get("claim")):
                errors.append(f"{fact_path} must be an object with a non-empty claim")
                continue
            refs = fact.get("sourceIds", [])
            if not isinstance(refs, list):
                errors.append(f"{fact_path}.sourceIds must be an array")
            else:
                missing = set(refs) - source_ids
                if missing:
                    errors.append(f"{fact_path} references missing sources: {sorted(missing)}")
                if ready and constraints.get("requiresCitations") is True and not refs:
                    errors.append(f"{fact_path}.sourceIds is required when citations are required")
                if scenario == "party-building":
                    party_evidence_refs.update(refs)

        metrics = slide.get("metrics", [])
        if not isinstance(metrics, list):
            errors.append(f"{path}.metrics must be an array")
            metrics = []
        total_metrics += len(metrics)
        for metric_index, metric in enumerate(metrics):
            metric_path = f"{path}.metrics[{metric_index}]"
            if not isinstance(metric, dict) or not nonempty(metric.get("label")):
                errors.append(f"{metric_path} must be an object with a non-empty label")
                continue
            if "value" not in metric and not nonempty(metric.get("displayValue")):
                errors.append(f"{metric_path} needs value or displayValue")
            source_id = metric.get("sourceId")
            if source_id and source_id not in source_ids:
                errors.append(f"{metric_path}.sourceId does not exist: {source_id}")
            if ready and constraints.get("requiresCitations") is True and not source_id:
                errors.append(f"{metric_path}.sourceId is required when citations are required")
            if scenario == "party-building" and source_id:
                party_evidence_refs.add(source_id)

        for array_field in ("items", "mediaRefs"):
            if not isinstance(slide.get(array_field, []), list):
                errors.append(f"{path}.{array_field} must be an array")
        media_refs = slide.get("mediaRefs", [])
        if isinstance(media_refs, list):
            missing_media = set(media_refs) - media_ids
            if missing_media:
                errors.append(f"{path}.mediaRefs references missing media: {sorted(missing_media)}")
            if media.get("policy") == "none" and media_refs:
                errors.append(f"{path}.mediaRefs must be empty when media.policy is none")

        speaker_notes = slide.get("speakerNotes")
        if not isinstance(speaker_notes, dict):
            errors.append(f"{path}.speakerNotes must be an object")
        elif ready and effective_mode in {"keynote-web", "dual-delivery"}:
            if not nonempty(speaker_notes.get("purpose")):
                errors.append(f"{path}.speakerNotes.purpose is required for speaker delivery")
            if not isinstance(speaker_notes.get("talk"), list) or not speaker_notes.get("talk"):
                errors.append(f"{path}.speakerNotes.talk is required for speaker delivery")
            if not nonempty(speaker_notes.get("transition")):
                errors.append(f"{path}.speakerNotes.transition is required for speaker delivery")
        if isinstance(speaker_notes, dict):
            minutes = speaker_notes.get("minutes")
            if minutes is not None:
                if not isinstance(minutes, (int, float)) or isinstance(minutes, bool) or minutes <= 0:
                    errors.append(f"{path}.speakerNotes.minutes must be null or a positive number")
                else:
                    speaker_minutes.append(float(minutes))
            elif ready and effective_mode in {"keynote-web", "dual-delivery"} and duration is not None:
                errors.append(f"{path}.speakerNotes.minutes is required when durationMinutes is set")

    if scenario == "party-building":
        if constraints.get("requiresCitations") is not True:
            errors.append("party-building requires constraints.requiresCitations=true")
        if ready and not nonempty(data.get("owner")):
            errors.append("party-building requires owner when status is ready")
        if ready and not nonempty(event_date):
            errors.append("party-building requires eventDate when status is ready")
        if ready:
            authoritative = [
                source
                for source in sources
                if isinstance(source, dict)
                and source.get("type") in PARTY_AUTHORITY_SOURCE_TYPES
                and nonempty(source.get("publisher"))
                and nonempty(source.get("publishedAt"))
            ]
            if not authoritative:
                errors.append(
                    "party-building requires an official source with publisher and publishedAt when status is ready"
                )
            authoritative_ids = {
                source.get("id") for source in authoritative if nonempty(source.get("id"))
            }
            if authoritative_ids and not (party_evidence_refs & authoritative_ids):
                errors.append("party-building must bind at least one fact or metric to an official source")
            evidence_optional_roles = {"cover", "actions", "closing", "transition", "ambient"}
            for index, slide in enumerate(slides):
                if not isinstance(slide, dict) or slide.get("role") in evidence_optional_roles:
                    continue
                if not slide.get("facts") and not slide.get("metrics"):
                    errors.append(
                        f"narrative.slides[{index}] requires a fact or metric for a factual party-building page"
                    )

    if ready and scenario in {"work-report", "party-building"} and total_facts + total_metrics == 0:
        errors.append(f"{scenario} requires at least one fact or metric when status is ready")
    elif ready and scenario in {"business", "technology"} and total_facts + total_metrics == 0:
        warnings.append(f"{scenario} brief is ready but contains no structured facts or metrics")

    if (
        ready
        and effective_mode in {"keynote-web", "dual-delivery"}
        and isinstance(duration, (int, float))
        and not isinstance(duration, bool)
        and len(speaker_minutes) == len(slides)
        and sum(speaker_minutes) > float(duration) * 0.9 + 1e-9
    ):
        errors.append(
            f"speakerNotes.minutes totals {sum(speaker_minutes):.2f}, exceeding 90% of durationMinutes"
        )

    if ready and effective_mode in {"keynote-web", "dual-delivery"}:
        if len(visual_style_decisions) != 1:
            errors.append("speaker delivery requires exactly one confirmed visual-style decision")

    if ready and constraints.get("requiresCitations") and not sources and scenario != "party-building":
        errors.append("requiresCitations=true requires at least one source when status is ready")

    if status == "draft":
        empty_messages = sum(
            1 for slide in slides if isinstance(slide, dict) and not nonempty(slide.get("keyMessage"))
        )
        if empty_messages:
            warnings.append(f"draft has {empty_messages} slides without keyMessage")
        if scenario == "party-building" and not sources:
            warnings.append("add authoritative sources before marking the party-building brief ready")

    return errors, warnings, recommended_mode(data)


def main() -> int:
    args = parse_args()
    try:
        data = json.loads(args.brief.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.brief}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2

    errors, warnings, mode = validate(data)
    result = {"valid": not errors, "recommendedMode": mode, "errors": errors, "warnings": warnings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"recommended mode: {mode}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("VALID" if not errors else "INVALID")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
