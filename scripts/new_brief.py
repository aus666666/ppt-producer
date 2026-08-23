#!/usr/bin/env python3
"""Create a scenario-aware canonical PPT brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from brieflib import DELIVERABLES, PRODUCTION_MODES, SCENARIOS, adjusted_outline, slide_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", required=True, choices=sorted(SCENARIOS))
    parser.add_argument("--title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--owner", default="")
    parser.add_argument("--event-date")
    parser.add_argument("--language", default="zh-CN")
    parser.add_argument("--mode", default="auto", choices=sorted(PRODUCTION_MODES))
    parser.add_argument(
        "--deliverable",
        dest="deliverables",
        action="append",
        choices=sorted(DELIVERABLES),
        help="Repeat for multiple deliverables; defaults to html.",
    )
    parser.add_argument("--page-count", type=int, default=10)
    parser.add_argument("--duration-minutes", type=float)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 4 <= args.page_count <= 60:
        raise SystemExit("--page-count must be between 4 and 60")
    if args.duration_minutes is not None and args.duration_minutes <= 0:
        raise SystemExit("--duration-minutes must be positive")

    slides = []
    for index, (role, title, objective) in enumerate(adjusted_outline(args.scenario, args.page_count)):
        slides.append(
            {
                "id": slide_id(index, role),
                "role": role,
                "title": title,
                "objective": objective,
                "keyMessage": "",
                "facts": [],
                "metrics": [],
                "items": [],
                "visualIntent": "",
                "mediaRefs": [],
                "speakerNotes": {"purpose": "", "talk": [], "transition": "", "minutes": None},
            }
        )

    brief = {
        "schemaVersion": 1,
        "status": "draft",
        "title": args.title.strip(),
        "scenario": args.scenario,
        "objective": args.objective.strip(),
        "audience": args.audience.strip(),
        "owner": args.owner.strip(),
        "eventDate": args.event_date,
        "language": args.language,
        "productionMode": args.mode,
        "deliverables": args.deliverables or ["html"],
        "pageCount": args.page_count,
        "durationMinutes": args.duration_minutes,
        "brand": {"name": "", "logo": None, "colors": [], "fonts": [], "tone": ""},
        "constraints": {
            "mustInclude": [],
            "mustAvoid": [],
            "confidentiality": "internal",
            "requiresCitations": args.scenario == "party-building",
        },
        "readiness": {"blockers": [], "assumptions": [], "decisions": []},
        "sources": [],
        "media": {"policy": "none", "items": []},
        "narrative": {"thesis": "", "sections": [], "slides": slides},
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
