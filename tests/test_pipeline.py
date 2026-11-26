"""End-to-end pipeline test without a real model.

Run:  python3 -m tests.test_pipeline   (from the ib-marker directory)
"""

from __future__ import annotations

import io
import json
import random
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import grader, providers  # noqa: E402
from app.extract import count_words, extract_text, precheck  # noqa: E402
from app.main import _parse_custom_rubric  # noqa: E402
from app.rubrics import RUBRICS, get_rubric, resolve_rubric  # noqa: E402

MOCK_PROVIDER = providers.resolve("custom", model="mock", base_url="http://mock.invalid/v1")

ESSAY = """Rationing the Island: Food Policy and Civilian Morale in Malta, 1940 to 1943

Research question: To what extent did the British administration's food rationing policy sustain civilian morale in Malta between June 1940 and 1943?

Table of contents
1. Introduction
2. Phase one: bread rationing and the Victory Kitchens
3. Phase two: the crisis of 1942
4. Phase three: relaxation
5. Conclusion
Bibliography

1. Introduction
When Italy declared war on 10 June 1940 the island of Malta lost most of its imports within weeks (Holland, 2003). This essay proceeds chronologically through three phases of policy because morale responded to the supply situation rather than to policy announcements. Morale is used here in the sense defined by the Ministry of Information: the willingness of civilians to continue cooperating with the authorities (Mackenzie, 1997, p. 44).

2. Phase one
Bread rationing was introduced in May 1941 (Malta Government Gazette, 1941). The Victory Kitchens were unpopular, as the oral histories show (Vella, 1995), yet they prevented the collapse of distribution.

3. Phase two
Operation Pedestal's losses are well documented: of fourteen merchant ships, five reached Grand Harbour (Woodman, 2000). Police reports on looting in April 1942 qualify the unity described in later testimonies.

4. Phase three
From February 1943 the ration scales were increased (Malta Government Gazette, 1943).

5. Conclusion
Rationing was a necessary condition for civilian resilience; it was not a sufficient one.

Bibliography
Holland, J. (2003). Fortress Malta. London: Orion.
Mackenzie, S. (1997). Politics and Military Morale. Oxford: Clarendon.
Woodman, R. (2000). Malta Convoys. London: John Murray.
https://example.org/malta-gazette

Reflection and Progress Form: reflective statement
Finding the looting reports was uncomfortable because it meant my first question had assumed its own answer. I now check who produced a source before I ask what it says.
"""


def make_docx() -> bytes:
    import docx
    d = docx.Document()
    lines = ESSAY.strip().split("\n")
    d.add_heading(lines[0], level=0)
    for line in lines[1:]:
        if line[:2] in {"1.", "2.", "3.", "4.", "5."} and len(line) < 40:
            d.add_heading(line, level=1)
        elif line.strip():
            d.add_paragraph(line)
    t = d.add_table(rows=2, cols=3)
    t.rows[0].cells[0].text, t.rows[0].cells[1].text, t.rows[0].cells[2].text = "Date", "Bread (g)", "Sugar (g)"
    t.rows[1].cells[0].text, t.rows[1].cells[1].text, t.rows[1].cells[2].text = "March 1941", "300", "40"
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def make_pdf() -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    for line in ESSAY.strip().split("\n"):
        for chunk in [line[i:i + 95] for i in range(0, max(len(line), 1), 95)]:
            c.drawString(40, y, chunk)
            y -= 14
            if y < 60:
                c.showPage()
                y = 800
    c.save()
    return buf.getvalue()


def mock_llm_factory(rubric):
    def mock(system: str, user: str) -> str:
        assert "CRITERIA AND LEVEL DESCRIPTORS" in user and "<<<BEGIN DOCUMENT>>>" in user
        rnd = random.Random(7)
        crits = []
        for c in rubric["criteria"]:
            if not c.get("assessable", True):
                crits.append({"code": c["code"], "mark": None, "band": "n/a", "justification": "Not assessable from a document.", "evidence": [], "strengths": [], "improvements": []})
                continue
            mark = rnd.randint(max(1, c["max"] // 2), c["max"])
            crits.append({"code": c["code"], "mark": mark, "band": "", "justification": f"Mock justification for {c['code']}.",
                          "evidence": ["\"Rationing was a necessary condition\""], "strengths": ["Clear question"], "improvements": ["Cut narrative"],
                          "next_band_requires": "More evaluation"})
        # Return with a markdown fence and a trailing comma to exercise the tolerant parser.
        body = {
            "document_summary": {"title": "Rationing the Island", "research_question": "To what extent...", "subject_and_task_detected": "History EE",
                                 "matches_selected_rubric": True, "summary": "The student investigates rationing and morale in Malta.", "structure_observations": ["Contents present"]},
            "criteria": crits,
            "overall_strengths": ["Focused question"],
            "priority_improvements": [{"priority": 1, "area": "Argument", "action": "Sustain analysis.", "criteria": ["C"]}],
            "integrity_flags": [],
            "confidence": "high",
            "confidence_reason": "Complete document.",
        }
        text = json.dumps(body, indent=1)
        text = text.replace('"confidence_reason": "Complete document."\n}', '"confidence_reason": "Complete document.",\n}')
        return "```json\n" + text + "\n```"
    return mock


def main() -> None:
    failures = 0

    def check(cond: bool, msg: str) -> None:
        nonlocal failures
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            failures += 1

    # 1. rubric library sanity
    ids = [r["id"] for r in RUBRICS]
    check(len(ids) == len(set(ids)), f"rubric ids unique ({len(ids)} rubrics)")
    for r in RUBRICS:
        res = resolve_rubric(r, "HL" if "HL" in r["levels"] else None)
        check(res["total_max"] == r["max_marks"] or r["id"] in {"ia-glopo", "ia-dt-2016"},
              f"{r['id']}: criteria sum {res['total_max']} vs declared max {r['max_marks']}")
        for c in r["criteria"]:
            top = max(int(str(b["marks"]).split("-")[-1]) for b in c["bands"])
            check(top == c["max"], f"{r['id']} {c['code']}: top band {top} == max {c['max']}")
    glopo_sl = resolve_rubric(get_rubric("ia-glopo"), "SL")
    glopo_hl = resolve_rubric(get_rubric("ia-glopo"), "HL")
    check(glopo_sl["total_max"] == 24 and glopo_hl["total_max"] == 30, "global politics SL 24 / HL 30")
    dt_sl = resolve_rubric(get_rubric("ia-dt-2016"), "SL")
    dt_hl = resolve_rubric(get_rubric("ia-dt-2016"), "HL")
    check(dt_sl["total_max"] == 36 and dt_hl["total_max"] == 54, "design technology 2016 SL 36 / HL 54")
    math_hl = resolve_rubric(get_rubric("ia-math-2019"), "HL")
    e_hl = [c for c in math_hl["criteria"] if c["code"] == "E"][0]
    check("sophistication and rigour" in e_hl["bands"][-1]["text"], "maths criterion E uses HL descriptors at HL")

    # 2. extraction
    docx_bytes = make_docx()
    doc = extract_text("essay.docx", docx_bytes)
    check(doc["kind"] == "docx" and "## 2. Phase one" in doc["text"], "docx extraction keeps headings in order")
    check("[TABLE]" in doc["text"] and "March 1941 | 300 | 40" in doc["text"], "docx tables extracted")
    pdf_bytes = make_pdf()
    pdoc = extract_text("essay.pdf", pdf_bytes)
    check(pdoc["kind"] == "pdf" and pdoc["pages"] >= 1 and "Rationing" in pdoc["text"], "pdf extraction works")
    check(count_words("Hello, world! It's 2026.") == 4, "word counter")

    # 3. pre-check
    ee = resolve_rubric(get_rubric("ee-2027"), None)
    checks = precheck(doc["text"], ee, doc["word_count"])
    labels = {c["label"]: c["status"] for c in checks}
    check(labels.get("Research question") == "ok", "precheck finds research question")
    check(labels.get("Bibliography or references") == "ok", "precheck finds bibliography")
    check(labels.get("Reflection form (criterion E)") == "ok", "precheck finds reflection form")
    check(labels.get("Contents page") == "ok", "precheck finds contents page")

    # 4. grader with mock model
    result = grader.run_analysis(ee, None, "History", "guidance text", doc, checks, "essay.docx", "First draft",
                                 MOCK_PROVIDER, "x", llm=mock_llm_factory(ee))
    check(result["total"]["max"] == 30 and 0 < result["total"]["mark"] <= 30, f"EE total computed: {result['total']['mark']}/30")
    check(result["total"]["indicative_grade"] in {"A", "B", "C", "D", "E"}, f"indicative grade {result['total']['indicative_grade']}")
    check(all(c["band"] != "?" for c in result["criteria"]), "band labels resolved for every criterion")
    check(result["document_summary"]["summary"].startswith("The student"), "document summary passed through")

    # non-assessable criteria excluded from the total
    film = resolve_rubric(get_rubric("ia-film-cfp"), "HL")
    fres = grader.run_analysis(film, "HL", None, None, doc, [], "report.docx", "", MOCK_PROVIDER, "x", llm=mock_llm_factory(film))
    check(fres["total"]["max"] == 16 and fres["criteria"][0]["mark"] is None, "film: criterion A excluded, total out of 16")

    # mark clamping and missing criterion handling
    def bad_llm(system, user):
        return json.dumps({"document_summary": {"summary": "x"}, "criteria": [{"code": "A", "mark": 99}, {"code": "B", "mark": -3}],
                           "overall_strengths": [], "priority_improvements": [], "integrity_flags": [], "confidence": "weird"})
    bres = grader.run_analysis(ee, None, None, None, doc, [], "x.docx", "", MOCK_PROVIDER, "x", llm=bad_llm)
    marks = {c["code"]: c["mark"] for c in bres["criteria"]}
    check(marks["A"] == 6 and marks["B"] == 0 and marks["C"] == 0, "marks clamped and missing criteria scored 0")
    check(any("did not return a mark" in f for f in bres["integrity_flags"]), "missing criteria flagged")
    check(bres["confidence"] == "medium", "invalid confidence normalised")

    # parser robustness
    check(grader.parse_json_response("Here you go:\n{\"a\": 1,}\nThanks")["a"] == 1, "parser strips prose and trailing comma")
    try:
        grader.parse_json_response("no json here")
        check(False, "parser rejects non-JSON")
    except grader.GraderError:
        check(True, "parser rejects non-JSON")

    # custom rubric
    custom = _parse_custom_rubric(json.dumps({"task": "Poster", "criteria": [{"code": "A", "name": "Content", "max": 5, "descriptor": "Accurate"}, {"name": "Design", "max": 3}]}))
    check(custom["max_marks"] == 8 and custom["criteria"][1]["code"] == "B", "custom rubric parsed with default codes")

    print(f"\n{'ALL PASSED' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
