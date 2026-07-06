"""Audit dataset linkage vs hub ecosystem integration."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "datasets"


def load(rel: str) -> list:
    p = ROOT / rel
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get("records", d if isinstance(d, list) else [])


def main() -> None:
    tools = load("clinical/clinical_tools_catalog.json")
    tool_codes = {t["tool_code"] for t in tools}

    rels = load("master/entity_relations.json")
    tool_rels = [
        r for r in rels
        if r.get("source_entity_type") == "ClinicalTool" and r.get("source_code") in tool_codes
    ]
    target_types = Counter(r["target_entity_type"] for r in tool_rels)
    print("=== entity_relations (ClinicalTool source) ===")
    print(f"Total: {len(tool_rels)}")
    for tt, c in target_types.most_common():
        print(f"  -> {tt}: {c}")

    contents = load("content/nkos/contents.json")
    ct = Counter(c.get("content_type") for c in contents)
    print("\n=== contents.json ===")
    print(f"Total: {len(contents)}")
    for k, v in ct.most_common(20):
        print(f"  {k}: {v}")

    frags = load("content/nkos/content_fragments.json")
    frag_tools = Counter()
    for f in frags:
        tc = f.get("tool_code") or f.get("linked_tool_code")
        if tc:
            frag_tools[tc] += 1
    print(f"\n=== content_fragments: {len(frags)} total, {len(frag_tools)} tools ===")

    articles = load("content/editorial/articles.json")
    with_rt = sum(1 for a in articles if a.get("related_tools"))
    print(f"\n=== articles.json: {len(articles)} articles, {with_rt} with related_tools ===")

    quizzes = load("education/quizzes.json")
    flashcards = load("education/flashcards.json")
    paths = load("education/learning_paths.json")
    print("\n=== education ===")
    print(f"quizzes: {len(quizzes)}, linked_tool: {sum(1 for q in quizzes if q.get('linked_tool_code'))}")
    print(f"flashcards: {len(flashcards)}, linked_entity TOOL.*: {sum(1 for f in flashcards if (f.get('linked_entity_code') or '').startswith('TOOL.'))}")
    print(f"learning_paths: {len(paths)}, steps with tool_code: {sum(1 for p in paths for s in p.get('steps', []) if s.get('tool_code'))}")

    comps = load("education/competencies.json")
    protos = load("clinical/institutional_protocols.json")
    exams = load("education/simulated_exams.json")
    nanda = load("clinical/nursing_diagnoses.json")
    print(f"competencies linked: {sum(1 for c in comps if c.get('linked_tool_codes'))}/{len(comps)}")
    print(f"protocols linked: {sum(1 for p in protos if p.get('related_tool_codes'))}/{len(protos)}")
    print(f"exams linked: {sum(1 for e in exams if e.get('linked_quiz_codes'))}/{len(exams)}")
    print(f"nanda linked: {sum(1 for n in nanda if n.get('related_tool_codes'))}/{len(nanda)}")

    nic = load("clinical/nursing_interventions.json")
    noc = load("clinical/nursing_outcomes.json")
    print(f"NIC tool-linked: {sum(1 for i in nic if i.get('related_tool_codes'))}/{len(nic)}")
    print(f"NOC tool-linked: {sum(1 for o in noc if o.get('related_tool_codes'))}/{len(noc)}")

    mono = load("clinical/drug_monographs.json")
    refs = load("clinical/drug_references.json")
    gloss = load("master/nursing_dictionary.json")
    tips_raw = json.loads((ROOT / "content/editorial/daily_tips.json").read_text(encoding="utf-8"))
    tips = tips_raw.get("tips", []) if isinstance(tips_raw, dict) else tips_raw
    reass = load("operations/reassessment_rules.json")
    ev = load("clinical/evidence.json")
    print(f"\n=== clinical/content extras ===")
    print(f"drug_monographs: {len(mono)}")
    print(f"drug_references: {len(refs)}")
    print(f"dictionary tool-linked: {sum(1 for g in gloss if g.get('related_tool_codes') or g.get('tool_code'))}/{len(gloss)}")
    print(f"daily_tips tool-linked: {sum(1 for t in tips if t.get('tool_code'))}/{len(tips)}")
    print(f"reassessment_rules tool-linked: {sum(1 for r in reass if r.get('tool_code'))}/{len(reass)}")
    print(f"evidence tool-linked: {sum(1 for e in ev if e.get('tool_code') or e.get('related_tool_codes'))}/{len(ev)}")

    topics = load("community/forum_topics.json")
    jobs = load("community/job_listings.json")
    courses = load("community/course_listings.json")
    career = load("community/career_paths.json")
    labor = load("content/editorial/labor_calculators.json")
    print(f"\n=== community/labor ===")
    print(f"forum topics: {len(topics)}, posts: {len(load('community/forum_posts.json'))}")
    print(f"jobs: {len(jobs)}, courses: {len(courses)}, career_paths: {len(career)}")
    print(f"labor_calculators: {len(labor)}")

    # Ecosystem coverage from generated index
    idx_path = ROOT.parent / "website" / "assets" / "data" / "tool-concepts-index.json"
    if idx_path.exists():
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
        concepts = idx.get("concepts", [])
        bucket_counts: Counter[str] = Counter()
        tools_with_any = 0
        for c in concepts:
            eco = c.get("ecosystem") or []
            if eco:
                tools_with_any += 1
            for item in eco:
                bucket_counts[item.get("resource_type", "?")] += 1
        print(f"\n=== tool-concepts-index.json ({len(concepts)} concepts) ===")
        print(f"Tools with ≥1 ecosystem item: {tools_with_any}")
        for rt, n in bucket_counts.most_common():
            print(f"  {rt}: {n}")

    # entity_relations not used in build_extended_ecosystem_index
    integrated_targets = {
        "NursingDiagnosis", "ClinicalGuideline", "Quiz", "Flashcard",
        "SimulatedExam", "LearningPath", "Competency", "InstitutionalProtocol",
    }
    print("\n=== entity_relations target types NOT in extended index ===")
    for tt in sorted(target_types):
        flag = "partial" if tt in integrated_targets else "GAP"
        print(f"  [{flag}] {tt}: {target_types[tt]}")


if __name__ == "__main__":
    main()
