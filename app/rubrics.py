"""
IB assessment rubric database for the IB Marker web app.

Each rubric describes one assessed task (Extended Essay, an Internal Assessment,
or a TOK task) with its criteria and level descriptors. Descriptors are close
paraphrases of the published IB guides unless the rubric's `fidelity` field says
"summarised" (used where the guide is new or where the exact wording could not be
verified from public sources). Teachers should always confirm against the official
guide for their examination session.
"""

from __future__ import annotations

from typing import Any


def C(code: str, name: str, max_marks: int, focus: str, bands: list[tuple[str, str]],
      strands: str | None = None, assessable: bool = True, levels: list[str] | None = None,
      bands_by_level: dict[str, list[tuple[str, str]]] | None = None) -> dict[str, Any]:
    crit: dict[str, Any] = {
        "code": code,
        "name": name,
        "max": max_marks,
        "focus": focus,
        "bands": [{"marks": m, "text": t} for m, t in bands],
        "assessable": assessable,
    }
    if strands:
        crit["strands"] = strands
    if levels:
        crit["levels"] = levels
    if bands_by_level:
        crit["bands_by_level"] = {lvl: [{"marks": m, "text": t} for m, t in bl] for lvl, bl in bands_by_level.items()}
    return crit


def R(**kwargs: Any) -> dict[str, Any]:
    base = {
        "levels": ["SL", "HL"],
        "fidelity": "paraphrased",
        "word_limit": None,
        "limit_note": "",
        "evidence_note": "",
        "variants": None,
        "grade_bands": None,
        "weighting": "",
        "notes": "",
    }
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# Shared descriptor sets
# ---------------------------------------------------------------------------

SCI_2025_CRITERIA = [
    C("RD", "Research design", 6,
      "A focused research question in a specific context; methodological considerations for collecting relevant and sufficient data; a reproducible method; safety, ethical and environmental considerations.",
      [("1-2", "The research question is stated without context. Methodological considerations associated with collecting data relevant to the research question are stated. The description of the methodology lacks the detail needed to reproduce the investigation."),
       ("3-4", "The research question is outlined within a broad context. Methodological considerations associated with collecting relevant and sufficient data are described. The description of the methodology allows the investigation to be reproduced with few ambiguities or omissions."),
       ("5-6", "The research question is described within a specific and appropriate context. Methodological considerations associated with collecting relevant and sufficient data to answer the research question are explained. The description of the methodology allows the investigation to be reproduced.")]),
    C("DA", "Data analysis", 6,
      "Clear and precise recording and processing of data relevant to the research question, with appropriate treatment of measurement uncertainty and effective presentation.",
      [("1-2", "The recording and processing of the data is communicated but is neither clear nor precise. The recording and processing of data relevant to the research question is limited, with little or no consideration of uncertainty. The processing contains major omissions, inaccuracies or inconsistencies."),
       ("3-4", "The recording and processing of the data is communicated clearly but not always precisely. The recording and processing of data is relevant to the research question but there are some omissions or inaccuracies, and consideration of the impact of measurement uncertainty is incomplete."),
       ("5-6", "The communication of the recording and processing of the data is both clear and precise. The recording and processing of data is relevant to the research question and includes appropriate consideration of the impact of measurement uncertainty. The processing is carried out correctly and completely.")]),
    C("CO", "Conclusion", 6,
      "A justified conclusion that answers the research question, is consistent with the analysis, and is compared with the accepted scientific context (theory or published values).",
      [("1-2", "A conclusion is stated that is relevant to the research question but is not supported by the analysis presented. The conclusion makes only a superficial comparison to the accepted scientific context."),
       ("3-4", "A conclusion is described that is relevant to the research question but is not fully consistent with the analysis presented. The conclusion makes some relevant comparison to the accepted scientific context."),
       ("5-6", "A conclusion is justified that is relevant to the research question and fully consistent with the analysis presented. The conclusion is justified through relevant comparison to the accepted scientific context.")]),
    C("EV", "Evaluation", 6,
      "Specific methodological weaknesses and limitations, their relative impact on the conclusion, and realistic improvements that address them.",
      [("1-2", "The report states generic methodological weaknesses or limitations. Realistic improvements to the investigation are stated but are not clearly relevant to the weaknesses."),
       ("3-4", "The report describes specific methodological weaknesses or limitations. Realistic improvements to the investigation that are relevant to the identified weaknesses or limitations are described."),
       ("5-6", "The report explains the relative impact of specific methodological weaknesses or limitations. Realistic improvements to the investigation that are relevant to the identified weaknesses or limitations are explained.")]),
]

LANG_A_IO_CRITERIA = [
    C("A", "Knowledge, understanding and interpretation", 10,
      "Knowledge and understanding of the extracts and of the works/texts they come from, with an interpretation of how they present the chosen global issue, supported by well-chosen references.",
      [("1-2", "Little knowledge and understanding of the extracts, texts and works in relation to the global issue. Supporting evidence is limited or inappropriate."),
       ("3-4", "Limited knowledge and understanding; an interpretation of the global issue is attempted. Supporting evidence is sometimes appropriate."),
       ("5-6", "Satisfactory knowledge and understanding, offering an interpretation in the context of the global issue. Supporting evidence is mainly appropriate and supports the development of ideas."),
       ("7-8", "Good knowledge and understanding, offering a consistent interpretation in the context of the global issue. Supporting evidence is appropriate and supports the development of ideas."),
       ("9-10", "Excellent knowledge and understanding, offering a compelling interpretation in the context of the global issue. Supporting evidence is well chosen and supports the development of ideas.")]),
    C("B", "Analysis and evaluation", 10,
      "How the authors' choices of language, structure, technique and style construct meaning and establish a perspective on the global issue; the quality of evaluative commentary.",
      [("1-2", "The oral is descriptive or contains little relevant analysis of language, structure and style."),
       ("3-4", "Some appropriate analysis of language, structure and style, but the oral relies on description."),
       ("5-6", "Generally appropriate analysis of how language, structure and style construct meaning in relation to the global issue; some evaluation."),
       ("7-8", "Appropriate and at times insightful analysis and evaluation of how the authors' choices present the global issue; good understanding of language, structure and style."),
       ("9-10", "Insightful and convincing analysis and evaluation of the authors' choices in relation to the global issue; excellent and nuanced understanding of language, structure and style.")]),
    C("C", "Focus and organization", 10,
      "A clear, sustained focus on the global issue, balanced treatment of both works and extracts, and a coherent, well-organised development of ideas.",
      [("1-2", "The oral rarely focuses on the task; little organisation or balance between the works."),
       ("3-4", "The oral is only sometimes focused on the task; some organisation, but treatment of the works is unbalanced."),
       ("5-6", "The oral mostly maintains focus on the task; ideas are adequately organised and the treatment of the works is generally balanced."),
       ("7-8", "The oral maintains a mostly clear and sustained focus; ideas are well organised and the treatment of the works is balanced."),
       ("9-10", "The oral maintains a clear and sustained focus on the task; ideas are well organised, cohesive and balanced across both works and extracts.")]),
    C("D", "Language", 10,
      "Clarity, accuracy and variety of language; appropriateness of register and style for an academic oral.",
      [("1-2", "Language is rarely clear and accurate; frequent errors; register and style are inappropriate."),
       ("3-4", "Language is sometimes clear and accurate; errors sometimes hinder communication; register is inconsistent."),
       ("5-6", "Language is clear and generally accurate; errors do not hinder communication; register and style are generally appropriate."),
       ("7-8", "Language is clear, accurate and varied, with only occasional errors; register and style are appropriate."),
       ("9-10", "Language is very clear, effective, carefully chosen and precise, with a high degree of accuracy; register and style are consistently appropriate.")]),
]

LANG_B_IO_CRITERIA = [
    C("A", "Language", 12,
      "Range and accuracy of vocabulary and grammar; clarity of pronunciation and intonation; fluency throughout the oral.",
      [("1-3", "Command of the language is limited: vocabulary is basic and sometimes inaccurate, grammatical errors frequently interfere with communication, pronunciation and intonation often impede understanding."),
       ("4-6", "Command of the language is partially effective: vocabulary is generally appropriate, basic structures are mostly accurate but more complex ones are not, pronunciation and intonation sometimes interfere with communication."),
       ("7-9", "Command of the language is mostly effective: vocabulary is appropriate and varied, a range of structures is used mostly accurately, pronunciation and intonation are generally clear."),
       ("10-12", "Command of the language is effective: vocabulary is wide and used accurately, complex structures are used accurately, pronunciation and intonation are clear and aid communication.")]),
    C("B1", "Message: visual stimulus (SL) or literary extract (HL)", 6,
      "At SL, how relevant and developed the presentation is in relation to the visual stimulus and the target culture; at HL, how well the extract is interpreted and placed within the work.",
      [("1-2", "The presentation is superficial or only marginally related to the stimulus or extract; ideas are undeveloped."),
       ("3-4", "The presentation is relevant to the stimulus or extract but ideas are only partly developed; links to the target culture (SL) or to the wider work (HL) are limited."),
       ("5-6", "The presentation is consistently relevant and well developed, using specific features of the stimulus or extract, with clear links to the target culture (SL) or to the wider work (HL).")]),
    C("B2", "Message: conversation", 6,
      "Relevance, breadth and depth of the ideas expressed in the follow-up discussion and the general conversation.",
      [("1-2", "Responses are mostly brief or irrelevant; ideas are rarely developed."),
       ("3-4", "Responses are relevant and sometimes developed, with some breadth and depth."),
       ("5-6", "Responses are consistently relevant, developed in depth and show breadth across the topics discussed.")]),
    C("C", "Interactive skills: communication", 6,
      "Comprehension of the teacher's questions, ability to sustain participation, and independent contributions to the conversation.",
      [("1-2", "Comprehension and interaction are limited; participation depends heavily on prompting."),
       ("3-4", "Comprehension is mostly good and participation is mostly sustained, with occasional independent contributions."),
       ("5-6", "Comprehension is consistently good, participation is sustained and the student makes independent contributions that move the conversation forward.")]),
]

MATH_2019_E_SL = [
    ("1", "Some relevant mathematics is used."),
    ("2", "Some relevant mathematics is used. Limited understanding is demonstrated."),
    ("3", "Relevant mathematics commensurate with the level of the course is used. Limited understanding is demonstrated."),
    ("4", "Relevant mathematics commensurate with the level of the course is used. The mathematics explored is partially correct. Some knowledge and understanding are demonstrated."),
    ("5", "Relevant mathematics commensurate with the level of the course is used. The mathematics explored is mostly correct. Good knowledge and understanding are demonstrated."),
    ("6", "Relevant mathematics commensurate with the level of the course is used. The mathematics explored is correct. Thorough knowledge and understanding are demonstrated."),
]
MATH_2019_E_HL = [
    ("1", "Some relevant mathematics is used. Limited understanding is demonstrated."),
    ("2", "Some relevant mathematics is used. The mathematics explored is partially correct. Some knowledge and understanding are demonstrated."),
    ("3", "Relevant mathematics commensurate with the level of the course is used. The mathematics explored is correct. Some knowledge and understanding are demonstrated."),
    ("4", "Relevant mathematics commensurate with the level of the course is used. The mathematics explored is correct. Good knowledge and understanding are demonstrated."),
    ("5", "Relevant mathematics commensurate with the level of the course is used. The mathematics explored is correct and demonstrates sophistication or rigour. Thorough knowledge and understanding are demonstrated."),
    ("6", "Relevant mathematics commensurate with the level of the course is used. The mathematics explored is precise and demonstrates sophistication and rigour. Thorough knowledge and understanding are demonstrated."),
]

# ---------------------------------------------------------------------------
# Rubrics
# ---------------------------------------------------------------------------

RUBRICS: list[dict[str, Any]] = []

# ----- Extended Essay ------------------------------------------------------

EE_SUBJECTS = [
    "Language A: literature", "Language A: language and literature", "Literature and performance",
    "Language B", "Language ab initio", "Classical languages",
    "Business management", "Digital society", "Economics", "Geography", "Global politics", "History",
    "Philosophy", "Psychology", "Social and cultural anthropology", "World religions",
    "Environmental systems and societies",
    "Biology", "Chemistry", "Physics", "Computer science", "Design technology", "Sports, exercise and health science",
    "Mathematics",
    "Dance", "Film", "Music", "Theatre", "Visual arts",
    "Interdisciplinary (two subjects) / World studies",
]

RUBRICS.append(R(
    id="ee-2027",
    component="Extended Essay",
    group="DP core",
    subject="Extended essay",
    task="Extended essay (subject-focused or interdisciplinary pathway)",
    version="New guide: first assessment May 2027 onwards",
    levels=["SL/HL"],
    max_marks=30,
    word_limit=4000,
    limit_note="4,000 words for the essay (title page, contents, charts, tables, equations, citations and bibliography excluded). The reflective statement on the Reflection and Progress Form (RPF) is at most 500 words and is the only evidence for criterion E.",
    evidence_note="Upload the full essay. Paste or append the RPF reflective statement if available; without it, criterion E cannot be awarded.",
    variants={"label": "EE subject", "options": EE_SUBJECTS},
    fidelity="summarised",
    weighting="Graded A to E; combined with TOK for up to 3 diploma points. An E is a failing condition.",
    grade_bands=[{"grade": "A", "min": 24}, {"grade": "B", "min": 19}, {"grade": "C", "min": 12}, {"grade": "D", "min": 6}, {"grade": "E", "min": 0}],
    grade_note="Provisional estimate only: official boundaries for the 30-mark model will be published after the first sessions.",
    criteria=[
        C("A", "Framework for the essay", 6, "Does the research question, the research methods and the structure of the essay give it an effective framework?", [
            ("1-2", "The research question is stated but is unclear, too broad or not answerable within the scope of the essay. Research methods are described in a limited way or are not appropriate to the subject(s). The structure is unclear and formal elements are incomplete."),
            ("3-4", "The research question is clearly stated but only partially focused. Research methods are appropriate but incompletely justified. The structure mostly supports the development of the essay and most formal elements are present."),
            ("5-6", "The research question is clearly stated, focused and answerable within 4,000 words. Research methods are appropriate to the chosen subject(s) and well justified. The structure, including the required formal elements, gives the essay an effective framework."),
        ], strands="Research question; research methods; structure"),
        C("B", "Knowledge and understanding", 6, "Are comprehensive, relevant research materials used to establish knowledge of the subject matter, with terminology and concepts used accurately and effectively?", [
            ("1-2", "Knowledge of the subject matter is limited and research materials have limited relevance. Subject-specific terminology is used with limited accuracy and relevant concepts are not explained."),
            ("3-4", "Knowledge of the subject matter is good and research materials are relevant. Terminology is mostly accurate; relevant concepts are explained but not always used effectively."),
            ("5-6", "Comprehensive and relevant research materials establish secure knowledge of the subject matter. Terminology is used accurately and consistently; relevant concepts are explained and used effectively."),
        ], strands="Knowledge; understanding of terminology; understanding of concepts"),
        C("C", "Analysis and line of argument", 6, "Is the research analysed so that the findings are relevant to the research question, and is there a coherent line of argument?", [
            ("1-2", "The essay is mostly descriptive; findings have limited relevance to the research question and the line of argument is unclear or absent."),
            ("3-4", "There is some analysis producing findings relevant to the research question; a line of argument is present but is not sustained throughout."),
            ("5-6", "Analysis of the research produces findings that are clearly relevant to the research question, and a coherent line of argument is sustained throughout the essay."),
        ], strands="Analysis; line of argument"),
        C("D", "Discussion and evaluation", 8, "Is there a balanced, evidence-based discussion of the significance of the findings, and an evaluation of the essay's effectiveness including its strengths and limitations?", [
            ("1-2", "Discussion of the findings is limited or unsupported by evidence. There is little or no evaluation of the essay's strengths and limitations."),
            ("3-4", "There is some discussion of the significance of the findings, supported by some evidence. Evaluation of strengths and limitations is superficial or generic."),
            ("5-6", "There is a mostly balanced discussion of the significance of the findings, supported by evidence. Evaluation identifies specific strengths and limitations of the essay."),
            ("7-8", "There is a balanced, evidence-based discussion of the significance of the findings. There is a convincing evaluation of how effective the essay has been, identifying specific strengths and limitations and their implications for the conclusion."),
        ], strands="Discussion; evaluation"),
        C("E", "Reflection", 4, "Does the reflective statement (RPF) evaluate, with specific examples, how the extended essay experience affected the student as a learner: growth and transfer of learning?", [
            ("1-2", "The reflective statement is a largely descriptive account of what was done. Growth or transferable learning is asserted with little support."),
            ("3-4", "The reflective statement is evaluative, using specific examples to show how the experience affected the student as a learner, with clear evidence of growth and of learning that can be transferred."),
        ], strands="Evaluative; growth"),
    ],
))

RUBRICS.append(R(
    id="ee-2018",
    component="Extended Essay",
    group="DP core",
    subject="Extended essay",
    task="Extended essay (single subject or World Studies)",
    version="Guide in force for sessions up to and including November 2026",
    levels=["SL/HL"],
    max_marks=34,
    word_limit=4000,
    limit_note="4,000 words for the essay; examiners do not read beyond the limit. The Reflections on Planning and Progress Form (RPPF) holds three reflections totalling at most 500 words and is the only evidence for criterion E.",
    evidence_note="Upload the full essay. Paste or append the RPPF reflections if available; without them, criterion E cannot be awarded.",
    variants={"label": "EE subject", "options": EE_SUBJECTS},
    weighting="Graded A to E; combined with TOK for up to 3 diploma points. An E is a failing condition.",
    grade_bands=[{"grade": "A", "min": 27}, {"grade": "B", "min": 21}, {"grade": "C", "min": 14}, {"grade": "D", "min": 7}, {"grade": "E", "min": 0}],
    grade_note="Indicative boundaries from recent sessions; the IB sets boundaries for each session.",
    criteria=[
        C("A", "Focus and method", 6, "Topic, research question and methodology.", [
            ("1-2", "The topic is communicated unclearly and incompletely. The research question is stated but not clearly expressed or is too broad. The methodology is limited: sources and/or methods are limited, with limited evidence of planning."),
            ("3-4", "The topic is communicated. The research question is clearly stated but only partially focused. The methodology is mostly complete: sources and/or methods are generally relevant and appropriate, with some evidence of planning."),
            ("5-6", "The topic is communicated accurately and effectively. The research question is clearly stated and focused. The methodology is complete: sources and/or methods are appropriate and effective, with evidence of effective planning."),
        ], strands="Topic; research question; methodology"),
        C("B", "Knowledge and understanding", 6, "Context, and subject-specific terminology and concepts.", [
            ("1-2", "Knowledge and understanding is limited. The selection of source material has limited relevance and is only partially appropriate. Subject-specific terminology and/or concepts are used with limited accuracy."),
            ("3-4", "Knowledge and understanding is good. The selection of source material is relevant and placed in context with partial understanding. Subject-specific terminology and/or concepts are used appropriately, with some inaccuracies."),
            ("5-6", "Knowledge and understanding is excellent. Source material is clearly relevant and the research is placed accurately in its academic context. Subject-specific terminology and/or concepts are used accurately and consistently."),
        ], strands="Context; subject-specific terminology and concepts"),
        C("C", "Critical thinking", 12, "Research, analysis, discussion and evaluation.", [
            ("1-3", "The research is limited. Analysis is limited and mostly descriptive. Discussion is limited; the conclusion is not consistent with the evidence presented and evaluation of sources is superficial or absent."),
            ("4-6", "The research is adequate. Analysis is present but not sustained and partially descriptive. There is some discussion and evaluation; a conclusion is drawn but may not be fully consistent with the evidence."),
            ("7-9", "The research is appropriate and applied consistently. Analysis is good with minor inconsistencies. A reasoned argument is developed; conclusions are consistent with the evidence and sources are evaluated."),
            ("10-12", "The research is appropriate, well selected and effectively applied. Analysis is excellent and consistently relevant. The argument is effectively reasoned, conclusions are well reasoned and consistent, and there is critical evaluation of the sources and of the argument."),
        ], strands="Research; analysis; discussion and evaluation"),
        C("D", "Presentation", 4, "Structure and layout of the essay.", [
            ("1-2", "Presentation is limited: the structure or layout only partly follows academic conventions; some required elements (title page, contents page, page numbers, headings, consistent referencing, bibliography) are missing or inconsistent, or the layout obstructs reading."),
            ("3-4", "Presentation is good: structure and layout follow academic conventions, all required elements are present and consistently applied, and the essay respects the word limit."),
        ], strands="Structure; layout"),
        C("E", "Engagement", 6, "Process and research focus, assessed only from the student's reflections on the RPPF.", [
            ("1-2", "Engagement is limited. Reflections are mostly descriptive and focused on procedure; there is little evidence of personal engagement with the research focus or of decision-making."),
            ("3-4", "Engagement is good. Reflections show some evaluation of decision-making and of the research process, and some evidence of intellectual initiative."),
            ("5-6", "Engagement is excellent. Reflections are evaluative, consider challenges and how the student responded to them, and show intellectual initiative, creativity and an authentic personal voice."),
        ], strands="Process; research focus"),
    ],
))

EE_SUBJECT_GUIDANCE: dict[str, str] = {
    "Language A: literature": "The essay must be a literary analysis: the text(s) are the object of study, not documentary evidence for a social issue. Expect close reading, discussion of authorial choices and engagement (not summary) with secondary criticism. Applying a generic theory to a text without close analysis is self-limiting.",
    "Language A: language and literature": "The essay analyses how language, culture and context shape meaning in literary or non-literary texts. Reward analysis of textual features and audience/purpose/context; penalise content summary or sociology without textual analysis.",
    "Literature and performance": "Subject-focused only. The essay should connect literary analysis with the dramatic or performative potential of texts.",
    "Language B": "Written in the target language; all texts must originally be in that language. Reward command of the language alongside cultural or literary analysis; the essay cannot be in a language the student takes as Language A.",
    "Language ab initio": "Not normally an available EE subject at this level; check the current guide.",
    "Classical languages": "Essays focus on a controversial aspect of the Greek or Roman world using primary sources in the original language and secondary scholarship; the topic must not overlap with the student's research dossier.",
    "Business management": "Expect a forward- or backward-looking business question about a real organisation, analysed with business tools and theories, mostly from secondary sources, with a recommendation or conclusion that follows from the evidence.",
    "Digital society": "Expect analysis of impacts and implications of a specific digital system for people and communities, using course concepts, with evaluation of perspectives and sources.",
    "Economics": "Expect economic theory and diagrams applied to a specific question, with analysis and evaluation of data; the former time restriction on topics no longer applies in the 2027 guide. Purely descriptive or historical essays score poorly.",
    "Geography": "Expect a spatial or environmental question with primary or secondary geographical data, maps and appropriate techniques, analysed in relation to geographic theory.",
    "Global politics": "Expect analysis of a political issue using key concepts (power, sovereignty, legitimacy, interdependence, etc.), multiple perspectives and evaluation of sources; the former time restriction no longer applies in the 2027 guide.",
    "History": "Expect a focused historical question answered through analysis of a range of sources, awareness and evaluation of historians' perspectives, and a reasoned conclusion. Narrative essays score poorly. The ten-year rule is removed in the 2027 guide.",
    "Philosophy": "Expect a philosophical question analysed through arguments and counter-arguments, with accurate use of philosophers' positions and the student's own justified conclusion.",
    "Psychology": "Secondary sources only: the student must not conduct experiments, surveys or interviews. Reward critical evaluation of empirical studies and theories in relation to the question.",
    "Social and cultural anthropology": "Expect anthropological concepts and theory applied to ethnographic material; fieldwork is not required. Reward comparative and critical analysis rather than description.",
    "World religions": "Expect an investigation of religious belief or practice with academic sources and critical analysis; devotional or purely descriptive essays score poorly.",
    "Environmental systems and societies": "Subject-focused only. The essay must address the interaction of environment and society; methods may include fieldwork, experiments or secondary data, described in enough detail to be repeated.",
    "Biology": "The topic must be approached through biology (an essay registered as biology is judged on its biological content). Experimental essays need a reproducible method and must follow the IB experimentation guidelines; essays using secondary data need the student's own analysis.",
    "Chemistry": "The topic must be chemical in nature. Experimental work needs a reproducible method, safety and ethical compliance, and the student's own data analysis; theoretical essays need genuine chemical reasoning beyond the syllabus.",
    "Physics": "The topic should use physics beyond the course to answer a non-trivial question. Avoid topics requiring theory beyond the student's grasp. Experimental essays need a reproducible method and uncertainty analysis.",
    "Computer science": "The essay must go beyond programming alone and analyse a computer science question with technical depth and evaluation; a software product on its own is not an essay.",
    "Design technology": "Expect a design question analysed through design theory, product analysis and evidence, not a design project write-up.",
    "Sports, exercise and health science": "The essay must have a clear SEHS emphasis on human performance or exercise and health. Human-subject work needs written consent, a readiness questionnaire and must avoid pain, undue stress or body fluids.",
    "Mathematics": "The essay must contain genuine mathematics beyond the taught course with correct notation and proof or modelling; a historical or descriptive essay about mathematics does not satisfy the criteria.",
    "Dance": "Expect analysis of dance works or traditions using dance vocabulary, placed in cultural and historical context.",
    "Film": "Expect film analysis using the language of film, placed in context; films used in the student's other Film assessments cannot be reused.",
    "Music": "Expect musical analysis (scores, recordings) with appropriate terminology and context, not biography.",
    "Theatre": "Expect analysis of theatre practice, texts or traditions using theatre vocabulary and context.",
    "Visual arts": "Images are compulsory and must appear in the body of the essay; expect visual analysis with appropriate terminology placed in cultural context.",
    "Interdisciplinary (two subjects) / World studies": "Under the 2027 guide the essay integrates two DP subjects within one of five frameworks (power, equality, justice; culture, identity, expression; movement, time, space; evidence, measurement, innovation; sustainability, development, change). Reward genuine integration of the two subjects' concepts or methods rather than two parallel essays. Under the 2018 guide (World Studies), the issue must be of contemporary global significance and examined through two subjects.",
}

# ----- Theory of Knowledge ---------------------------------------------------

RUBRICS.append(R(
    id="tok-essay",
    component="Theory of Knowledge",
    group="DP core",
    subject="Theory of knowledge",
    task="TOK essay on a prescribed title",
    version="Guide in force (first assessment 2022)",
    levels=["SL/HL"],
    max_marks=10,
    word_limit=1600,
    limit_note="1,600 words; examiners stop reading at the limit. The essay must respond to one of the six prescribed titles for the session, otherwise it scores 0.",
    evidence_note="Upload the essay. Add the prescribed title in the teacher notes if it is not on the document.",
    weighting="Two thirds of the TOK grade (combined with the exhibition and converted to A to E).",
    notes="Marked holistically by global impression against a single driving question; there are no sub-criteria to add up.",
    criteria=[
        C("ESSAY", "Global impression: Does the student provide a clear, coherent and critical exploration of the essay title?", 10,
          "The essay is matched as a whole to the level whose descriptor best fits it.", [
              ("1-2", "Rudimentary: the discussion is weakly connected to the title. Any relevant points are descriptive or consist only of unsupported assertions. (Ineffective, descriptive, incoherent, formless.)"),
              ("3-4", "Basic: the discussion is connected to the title and makes superficial or limited links to areas of knowledge. The discussion is largely descriptive. Limited arguments are offered but they are unclear and are not supported by effective examples. (Underdeveloped, basic, superficial, limited.)"),
              ("5-6", "Satisfactory: the discussion is focused on the title and is developed with some links to areas of knowledge. Arguments are offered and are supported by examples, although there are inconsistencies and gaps. There is some awareness of different points of view. (Acceptable, mainstream, adequate, competent.)"),
              ("7-8", "Good: the discussion is focused on the title and is linked effectively to areas of knowledge. Arguments are clear, coherent and supported by examples. There is awareness and some evaluation of different points of view. (Pertinent, relevant, analytical, organised.)"),
              ("9-10", "Excellent: the discussion has a sustained focus on the title and is linked effectively to areas of knowledge. Arguments are clear, coherent and effectively supported by specific examples. The implications of arguments are considered. There is clear awareness and evaluation of different points of view. (Insightful, convincing, accomplished, lucid.)"),
          ]),
    ],
))

RUBRICS.append(R(
    id="tok-exhibition",
    component="Theory of Knowledge",
    group="DP core",
    subject="Theory of knowledge",
    task="TOK exhibition (three objects and commentary)",
    version="Guide in force (first assessment 2022)",
    levels=["SL/HL"],
    max_marks=10,
    word_limit=950,
    limit_note="950 words across the three commentaries combined, linked to one of the 35 IA prompts; the prompt wording must not be altered.",
    evidence_note="Upload the exhibition document (prompt, three objects with images or descriptions, and commentaries).",
    weighting="One third of the TOK grade. Internally assessed, externally moderated.",
    notes="Marked holistically by global impression against a single driving question.",
    criteria=[
        C("EXH", "Global impression: Does the exhibition successfully show how TOK manifests in the world around us?", 10,
          "The exhibition is matched as a whole to the level whose descriptor best fits it.", [
              ("1-2", "Rudimentary: the exhibition presents three objects but the real-world contexts are not stated, or the objects are generic images of types of object. Links to the prompt are minimal, tenuous or illogical. There is very limited justification for including the objects; the commentary is highly descriptive or consists of unsupported assertions. (Ineffective, descriptive, incoherent.)"),
              ("3-4", "Basic: the exhibition identifies three objects, although their real-world contexts are only implied. Basic links between the objects and the prompt are made, but are unconvincing or unfocused. Justification of the objects' contribution is superficial; reasons are not supported by evidence and there may be repetition across the objects. (Simplistic, limited, underdeveloped.)"),
              ("5-6", "Satisfactory: the exhibition identifies three objects, although the real-world contexts may be vaguely or imprecisely stated. There is some explanation of the links between the objects and the prompt. There is some justification for including each object; some points are supported by evidence and references to the prompt. (Adequate, competent, acceptable.)"),
              ("7-8", "Good: the exhibition identifies three objects and their real-world contexts. Links between each object and the prompt are explained, although the explanation may lack precision in parts. There is a justification of the contribution each object makes; many points are supported by evidence and references to the prompt. (Focused, relevant, coherent.)"),
              ("9-10", "Excellent: the exhibition clearly identifies three objects and their specific real-world contexts. Links between each of the three objects and the selected prompt are clearly made and well explained. There is a strong justification of the particular contribution each object makes; all or nearly all points are well supported by appropriate evidence and explicit references to the prompt. (Convincing, lucid, precise.)"),
          ]),
    ],
))

# ----- Group 1 ---------------------------------------------------------------

RUBRICS.append(R(
    id="ia-langa-lit-io",
    component="Internal Assessment",
    group="Group 1: Studies in language and literature",
    subject="Language A: literature",
    task="Individual oral (two literary works, one in translation, on a global issue)",
    version="Guide in force (first assessment 2021; minor changes 2026)",
    max_marks=40,
    word_limit=None,
    limit_note="10-minute oral plus 5 minutes of questions; the student speaks from an outline of at most 10 bullet points.",
    evidence_note="Upload a transcript of the oral (ideally including the teacher's questions and answers). An outline alone gives very limited evidence for criteria B and D.",
    weighting="30% at SL, 20% at HL.",
    criteria=LANG_A_IO_CRITERIA,
))

RUBRICS.append(R(
    id="ia-langa-ll-io",
    component="Internal Assessment",
    group="Group 1: Studies in language and literature",
    subject="Language A: language and literature",
    task="Individual oral (one literary work and one non-literary body of work, on a global issue)",
    version="Guide in force (first assessment 2021; minor changes 2026)",
    max_marks=40,
    limit_note="10-minute oral plus 5 minutes of questions; outline of at most 10 bullet points.",
    evidence_note="Upload a transcript of the oral. An outline alone gives very limited evidence for criteria B and D.",
    weighting="30% at SL, 20% at HL.",
    criteria=LANG_A_IO_CRITERIA,
))

RUBRICS.append(R(
    id="ia-litperf",
    component="Internal Assessment",
    group="Group 1: Studies in language and literature (also Group 6)",
    subject="Literature and performance",
    task="Transformative performance and individual oral",
    version="Guide in force (first assessment 2024; minor changes 2026)",
    levels=["SL"],
    max_marks=32,
    limit_note="15-minute individual oral explaining the transformation of a non-dramatic extract into performance.",
    evidence_note="Upload a transcript of the individual oral. Criterion A is assessed from the performance itself and cannot be marked from a document.",
    weighting="40% (SL only).",
    fidelity="summarised",
    criteria=[
        C("A", "Individual contributions to the performance", 8, "Command of performance elements and contribution to the effectiveness of the piece (assessed from the performance).", [
            ("1-2", "Limited command of performance elements; limited contribution to the effectiveness of the piece."),
            ("3-4", "Underdeveloped command of performance elements; underdeveloped contribution."),
            ("5-6", "Good command of performance elements; good contribution."),
            ("7-8", "Very good command of performance elements; very good, purposeful and controlled contribution."),
        ], assessable=False),
        C("B", "Knowledge and understanding of the extract", 4, "How well the student demonstrates knowledge and understanding of the chosen extract.", [
            ("1", "Little knowledge and understanding of the extract."), ("2", "Some knowledge and understanding."), ("3", "Good knowledge and understanding."), ("4", "Very good, detailed knowledge and understanding of the extract.")]),
        C("C", "Interpretation and transformation of the extract", 8, "Interpretation of the dramatic potential of textual features and authorial choices, and explanation of how that interpretation informed staging choices.", [
            ("1-2", "Textual features are identified with little interpretation; staging choices are listed without explanation."),
            ("3-4", "Some interpretation of textual features; staging choices are described with partial links to the interpretation."),
            ("5-6", "Textual features are interpreted and staging choices are explained with clear links to the interpretation."),
            ("7-8", "Insightful interpretation of the dramatic potential of textual features; staging choices are thoroughly justified in relation to that interpretation."),
        ]),
        C("D", "Evaluation of the final production", 4, "Evaluation of the final piece and the extent to which it met the group's intentions.", [
            ("1", "The piece is described rather than evaluated."), ("2", "Some evaluation with limited reference to intentions."), ("3", "Clear evaluation against the group's intentions."), ("4", "Convincing, balanced evaluation of the piece against the group's intentions with specific examples.")]),
        C("E", "Focus and organization", 4, "A structured, well-balanced and focused oral.", [
            ("1", "Little organisation is apparent in the presentation of ideas."), ("2", "Some organisation is apparent."), ("3", "Ideas are organised in a generally coherent manner."), ("4", "Ideas are effectively organised and coherent.")]),
        C("F", "Language", 4, "Clarity, accuracy and appropriateness of language and register.", [
            ("1", "Language is rarely clear or appropriate; frequent errors."), ("2", "Language is sometimes clear; errors sometimes hinder communication."), ("3", "Language is clear and generally accurate with appropriate register."), ("4", "Language is very clear, precise, accurate and consistently appropriate in register.")]),
    ],
))

# ----- Group 2 ---------------------------------------------------------------

RUBRICS.append(R(
    id="ia-langb-io",
    component="Internal Assessment",
    group="Group 2: Language acquisition",
    subject="Language B",
    task="Individual oral (SL: visual stimulus; HL: literary extract)",
    version="Guide in force (first assessment 2020; descriptors for B2 and C reworded for 2029)",
    max_marks=30,
    limit_note="12 to 15 minutes: presentation 3 to 4 minutes, follow-up discussion 4 to 5 minutes, general conversation 5 to 6 minutes.",
    evidence_note="Upload a transcript in the target language. Pronunciation and intonation (part of criterion A) cannot be judged from text; mark criterion A on vocabulary and grammar only and say so.",
    weighting="25% at SL and HL.",
    criteria=LANG_B_IO_CRITERIA,
))

RUBRICS.append(R(
    id="ia-abinitio-io",
    component="Internal Assessment",
    group="Group 2: Language acquisition",
    subject="Language ab initio",
    task="Individual oral (visual stimulus)",
    version="Guide in force (first assessment 2020)",
    levels=["SL"],
    max_marks=30,
    limit_note="About 7 to 10 minutes: presentation 1 to 2 minutes, follow-up 2 to 3 minutes, general conversation 3 to 4 minutes. The presentation must make clear links to the target culture.",
    evidence_note="Upload a transcript in the target language. Pronunciation cannot be judged from text.",
    weighting="25% (SL only).",
    criteria=LANG_B_IO_CRITERIA,
))

RUBRICS.append(R(
    id="ia-classical",
    component="Internal Assessment",
    group="Group 2: Language acquisition",
    subject="Classical languages (Latin, Classical Greek)",
    task="Research dossier (seven to nine annotated primary sources plus an introductory inspiration source)",
    version="Guide in force (first assessment 2024)",
    max_marks=24,
    limit_note="Annotations only count towards the length; the current guide totals 28 marks.",
    evidence_note="The 2024 guide marks the dossier out of 28, but its exact criterion split could not be verified from public sources. The three strands below follow the previous guide (24 marks). Edit them with the custom rubric option if you have the current guide.",
    weighting="30% at SL, 20% at HL.",
    fidelity="summarised",
    criteria=[
        C("A", "Sources", 8, "Relevance of the primary sources to the research question and their contribution to broad coverage of the topic.", [
            ("1-2", "Few of the selected sources are relevant; the sources provide limited coverage of the topic."),
            ("3-4", "Some of the selected sources are relevant; the sources provide a narrow coverage of the topic."),
            ("5-6", "Most of the selected sources are relevant; the sources contribute to a general coverage of the topic."),
            ("7-8", "Nearly all selected sources have clear relevance; the sources contribute to a broad coverage of the topic."),
        ]),
        C("B", "Annotations", 8, "The extent to which annotations relate to the research question and the depth of analysis of each source.", [
            ("1-2", "The annotations relate to the research question in a limited way; the analysis shows limited understanding of the sources."),
            ("3-4", "The majority of annotations are not directly related to the research question; the analysis shows some understanding of the sources."),
            ("5-6", "The majority of annotations are directly related to the research question; the analysis shows general understanding of each source."),
            ("7-8", "Nearly all annotations are directly related to the research question; the analysis shows deep understanding of each source."),
        ]),
        C("C", "Argument", 8, "How well the argument is supported by the sources and annotations, and how logically it progresses.", [
            ("1-2", "There is little focus or coherence to the argument; it lacks a logical progression."),
            ("3-4", "There is some focus and coherence; the argument progresses with some logic but with gaps."),
            ("5-6", "The argument is focused and coherent and is mostly supported by the sources and annotations in a logical progression."),
            ("7-8", "The argument is consistently focused, well supported by the sources and annotations, and organised in a clear and logical progression throughout the dossier."),
        ]),
    ],
))

# ----- Group 3 ---------------------------------------------------------------

RUBRICS.append(R(
    id="ia-bm",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Business management",
    task="Business research project",
    version="Guide in force (first assessment 2024)",
    max_marks=25,
    word_limit=1800,
    limit_note="1,800 words; three to five supporting documents published within three years of submission must be attached; exactly one key concept (change, creativity, ethics or sustainability).",
    evidence_note="Upload the project; include the supporting documents if possible so criterion B can be judged.",
    weighting="30% at SL, 20% at HL. Same task and criteria at both levels.",
    criteria=[
        C("A", "Integration of a key concept", 5, "How well the chosen key concept (change, creativity, ethics or sustainability) shapes the research question, analysis and conclusion.", [
            ("1", "A key concept is named but is not used; or a concept outside the four prescribed concepts is used (score 0 in that case)."),
            ("2", "The key concept is described with limited connection to the research question."),
            ("3", "The key concept is described and used with some integration into the analysis."),
            ("4", "The key concept is integrated throughout most of the project and informs the analysis."),
            ("5", "The key concept is fully integrated and used as a lens through which the whole project, from question to conclusion, is analysed."),
        ]),
        C("B", "Supporting documents", 4, "Relevance, depth, currency and variety of perspective of the three to five supporting documents.", [
            ("1", "Fewer than three or more than five documents, or documents of limited relevance and depth."),
            ("2", "Three to five documents that are somewhat relevant and detailed."),
            ("3", "Three to five relevant documents with sufficient depth, mostly contemporary."),
            ("4", "Three to five directly relevant, sufficiently detailed, contemporary documents that provide a range of ideas and perspectives."),
        ]),
        C("C", "Selection and application of tools and theories", 4, "Selection and accurate, effective application of business management tools and theories relevant to the research question.", [
            ("1", "Tools and theories are stated with limited application."),
            ("2", "Some appropriate tools and theories are applied, with limited accuracy."),
            ("3", "Appropriate tools and theories are applied mostly accurately."),
            ("4", "Appropriate tools and theories are selected and applied accurately and effectively to the research question."),
        ]),
        C("D", "Analysis and evaluation", 5, "Effective selection and use of data from the supporting documents in analysis and evaluation of the research question.", [
            ("1", "The project is descriptive; data from the documents is barely used."),
            ("2", "Some data from the documents is used; analysis is limited and evaluation absent."),
            ("3", "Data is used with some analysis and limited evaluation."),
            ("4", "Data from the documents is used effectively; analysis and evaluation are mostly well developed."),
            ("5", "Data from the documents is used effectively in well-developed, integrated analysis and evaluation that addresses the research question."),
        ]),
        C("E", "Conclusions", 3, "Consistency of the conclusion with the evidence, and whether it explicitly answers the research question.", [
            ("1", "A conclusion is stated but is not consistent with the evidence or does not answer the research question."),
            ("2", "The conclusion answers the research question and is mostly consistent with the evidence."),
            ("3", "The conclusion is consistent with the evidence presented and explicitly answers the research question."),
        ]),
        C("F", "Structure", 2, "Logical organisation of the project.", [
            ("1", "Some structure is evident but the argument is hard to follow."),
            ("2", "The project is organised using an appropriate, logical structure that builds to the conclusion."),
        ]),
        C("G", "Presentation", 2, "Title page (research question, key concept, word count), contents, headings, page numbers, consistent referencing and bibliography.", [
            ("1", "Some of the required presentation elements are present."),
            ("2", "All required presentation elements are present and correctly applied."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-ds",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Digital society",
    task="Inquiry project (inquiry process document plus multimedia presentation)",
    version="Guide in force (first assessment 2024)",
    max_marks=24,
    word_limit=1500,
    limit_note="Inquiry process document at most 1,500 words (focus about 300, claims and perspectives about 1,200); presentation at most 10 minutes.",
    evidence_note="Upload the inquiry process document, and a script or transcript of the presentation if available. Criteria C to E are assessed from the presentation only.",
    weighting="30% at SL, 20% at HL.",
    fidelity="summarised",
    criteria=[
        C("A", "Inquiry focus", 3, "Connection between the inquiry question, a specific real-world example (an existing digital system) and course concepts, content and contexts.", [
            ("1", "The focus is limited or incomplete."),
            ("2", "The focus is adequate: the inquiry question, real-world example and course connections are stated with some explanation."),
            ("3", "The focus is well developed: a compelling, open inquiry question is clearly connected to a specific existing digital system and to course concepts, content and contexts."),
        ]),
        C("B", "Claims and perspectives", 6, "Identification and analysis of exactly three sources: their claims, perspectives, origin and purpose, and justification of their usefulness.", [
            ("1-2", "Fewer or more than three sources, or sources treated superficially; claims are stated but perspectives, origin and purpose are unclear."),
            ("3-4", "Three sources with claims and perspectives described; some discussion of origin and purpose; some justification of usefulness."),
            ("5-6", "Three relevant sources; claims and perspectives are analysed, origin and purpose discussed, and the usefulness of each source for the inquiry is explicitly justified."),
        ]),
        C("C", "Analysis and evaluation", 6, "The student's own sustained, well-supported analysis and evaluation of the impacts and implications of the digital system for people and communities (presentation).", [
            ("1-2", "Analysis and evaluation are limited and largely unsupported."),
            ("3-4", "Some analysis and evaluation of impacts and implications, partly supported by evidence."),
            ("5-6", "Sustained, well-supported analysis and evaluation of impacts and implications for people and communities, drawing on multiple perspectives."),
        ]),
        C("D", "Conclusion", 6, "Further insight reflecting new understanding of the inquiry focus, with discussion of emerging trends and future developments (presentation).", [
            ("1-2", "The conclusion offers limited further insight; trends and developments are mentioned only."),
            ("3-4", "The conclusion offers some further insight and some discussion of emerging trends and future developments."),
            ("5-6", "The conclusion provides effective, well-supported further insight into the inquiry focus with a thorough, substantiated discussion of emerging trends and future developments."),
        ]),
        C("E", "Communication", 3, "Organisation of ideas and evidence and coherent use of media in the presentation.", [
            ("1", "Communication is limited; ideas and media are poorly organised."),
            ("2", "Communication is adequate; ideas are organised and media are used appropriately."),
            ("3", "Communication is effective; ideas and evidence are well organised and media are used coherently to support understanding."),
        ]),
    ],
))

ECON_COMMENTARY_CRITERIA = [
    C("A", "Diagrams", 3, "Relevant, accurate and correctly labelled diagrams with full explanation linked to the article.", [
        ("1", "Relevant diagrams are included but are not explained, or are not fully labelled."),
        ("2", "Relevant, accurate and correctly labelled diagrams are included, with limited explanation."),
        ("3", "Relevant, accurate and correctly labelled diagrams are included, with a full explanation."),
    ]),
    C("B", "Terminology", 2, "Economic terminology relevant to the article used appropriately throughout.", [
        ("1", "Terminology relevant to the article is used, but not always appropriately."),
        ("2", "Terminology relevant to the article is used appropriately throughout the commentary."),
    ]),
    C("C", "Application and analysis", 3, "Relevant economic theory applied to the article's specific situation with an effective chain of reasoning.", [
        ("1", "Relevant economic theory is applied to the article, but the analysis is limited."),
        ("2", "Relevant economic theory is applied to the article, with some effective analysis."),
        ("3", "Relevant economic theory is applied to the article throughout the commentary, with effective analysis."),
    ]),
    C("D", "Key concept", 3, "The chosen key concept is identified and used as a lens for the analysis.", [
        ("1", "A key concept is identified, but the link to the article is limited."),
        ("2", "A key concept is identified and linked to the article with some explanation."),
        ("3", "A key concept is identified and effectively linked to the article throughout the commentary."),
    ]),
    C("E", "Evaluation", 3, "Judgements supported by balanced, reasoned arguments.", [
        ("1", "Judgements are made but are not supported by reasoned arguments."),
        ("2", "Judgements are made and supported by some reasoned arguments."),
        ("3", "Judgements are made and supported by effective and balanced reasoning."),
    ]),
]

RUBRICS.append(R(
    id="ia-econ-commentary",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Economics",
    task="Single commentary from the portfolio (criteria A to E)",
    version="Guide in force (first assessment 2022)",
    max_marks=14,
    word_limit=800,
    limit_note="800 words per commentary; the article must be published within one year of writing and come from published news media. Diagrams, labels, tables, equations and references are not counted.",
    evidence_note="Upload one commentary (and the article if possible). Portfolio-level criterion F (3 marks) is not applied to a single commentary.",
    weighting="The three-commentary portfolio is 30% at SL and 20% at HL.",
    criteria=ECON_COMMENTARY_CRITERIA,
))

RUBRICS.append(R(
    id="ia-econ-portfolio",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Economics",
    task="Full portfolio of three commentaries (criteria A to E for each, plus F)",
    version="Guide in force (first assessment 2022)",
    max_marks=45,
    word_limit=2400,
    limit_note="800 words per commentary. Each commentary must use a different article from a different source, a different syllabus unit (microeconomics, macroeconomics, the global economy) and a different key concept.",
    evidence_note="Upload the whole portfolio in one file. For each commentary the examiner reports the A to E breakdown (3+2+3+3+3) inside the justification.",
    weighting="30% at SL, 20% at HL.",
    criteria=[
        C("C1", "Commentary 1: criteria A to E (Diagrams 3, Terminology 2, Application and analysis 3, Key concept 3, Evaluation 3)", 14,
          "Mark the first commentary against the five commentary criteria and report each sub-mark.", [
              ("1-5", "Weak: diagrams unexplained or missing, limited application of theory, key concept barely linked, judgements unsupported."),
              ("6-9", "Adequate: relevant diagrams with limited explanation, some effective analysis, key concept linked with some explanation, some reasoned evaluation."),
              ("10-14", "Strong: accurate, fully explained diagrams, theory applied throughout, key concept used as a lens, effective balanced evaluation.")]),
        C("C2", "Commentary 2: criteria A to E", 14, "As for commentary 1.", [
            ("1-5", "Weak, as above."), ("6-9", "Adequate, as above."), ("10-14", "Strong, as above.")]),
        C("C3", "Commentary 3: criteria A to E", 14, "As for commentary 1.", [
            ("1-5", "Weak, as above."), ("6-9", "Adequate, as above."), ("10-14", "Strong, as above.")]),
        C("F", "Rubric requirements (whole portfolio)", 3, "One mark for each requirement met: three different syllabus units; three different news sources; each article published within one year of the commentary being written.", [
            ("1", "One requirement met."), ("2", "Two requirements met."), ("3", "All three requirements met.")]),
    ],
))

RUBRICS.append(R(
    id="ia-geo",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Geography",
    task="Fieldwork report",
    version="Guide in force (first assessment 2019)",
    max_marks=25,
    word_limit=2500,
    limit_note="2,500 words, including text in tables, figure annotations and captions. Primary data collected by the student is required.",
    evidence_note="Upload the full report with maps, graphs and data tables.",
    weighting="25% at SL, 20% at HL. Same criteria at both levels.",
    criteria=[
        C("A", "Fieldwork question and geographic context", 3, "A focused fieldwork question with a justified, located geographic context linked to the syllabus.", [
            ("1", "The fieldwork question is stated but vague; the geographic context is limited."),
            ("2", "The fieldwork question is stated and the geographic context is described with a location map."),
            ("3", "The fieldwork question is focused and appropriate; the geographic context is well explained, located with an annotated map and linked to relevant geographic theory and the syllabus."),
        ]),
        C("B", "Method(s) of investigation", 3, "Description and justification of primary data collection methods, including sampling.", [
            ("1", "Methods are described only."),
            ("2", "Methods are described with some justification."),
            ("3", "Methods are clearly described and justified in relation to the fieldwork question, including sampling and the quantity of data collected."),
        ]),
        C("C", "Quality and treatment of information collected", 6, "Relevance and sufficiency of the information, and appropriateness of the techniques used to treat and display it.", [
            ("1-2", "The information collected is of limited relevance or quantity; techniques used to treat and display it are inappropriate or ineffective."),
            ("3-4", "The information is relevant and sufficient for some analysis; appropriate techniques are used, though not always effectively."),
            ("5-6", "The information is directly relevant to the question and sufficient in quantity and quality for in-depth analysis; the most appropriate techniques are used effectively for both treatment and display."),
        ]),
        C("D", "Written analysis", 8, "Interpretation of the information in relation to the question and geographic theory: trends, spatial patterns, relationships, statistics and anomalies.", [
            ("1-2", "The analysis is descriptive with minimal interpretation; little reference to the question."),
            ("3-4", "There is some analysis; some patterns or relationships are identified; links to the question and context are limited."),
            ("5-6", "The information is analysed; trends, relationships and anomalies are identified and linked to the question and to geographic context."),
            ("7-8", "There is an in-depth analysis in which trends, relationships and anomalies are explained and integrated with geographic theory and the fieldwork question."),
        ]),
        C("E", "Conclusion", 2, "A conclusion to the fieldwork question consistent with the analysis.", [
            ("1", "Some attempt to draw a conclusion, which may not be completely consistent with the analysis."),
            ("2", "A clear conclusion to the fieldwork question, consistent with the analysis."),
        ]),
        C("F", "Evaluation", 3, "Evaluation of methods, sampling, data reliability and validity, with realistic improvements.", [
            ("1", "Evaluation is limited; weaknesses are listed."),
            ("2", "Methods are evaluated with some improvements suggested."),
            ("3", "Methods and data reliability are evaluated with explanation of their effect on the findings, and realistic, specific improvements or extensions are proposed."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-glopo",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Global politics",
    task="Engagement project report",
    version="New guide: first assessment 2026 onwards",
    max_marks=24,
    word_limit=2000,
    limit_note="2,000-word report. HL students add a separate recommendation of at most 400 words (criterion F). SL total 24, HL total 30. Unethical work scores zero.",
    evidence_note="Upload the report (and the HL recommendation).",
    weighting="30% at SL, 20% at HL.",
    fidelity="summarised",
    criteria=[
        C("A", "Explanation and justification", 4, "Clear explanation of the political issue, the importance and suitability of the project, and justification of the engagement activities.", [
            ("1-2", "A political issue is identified but not clearly explained; limited explanation of the importance and suitability of the project; engagement activities are described but their relevance is not justified."),
            ("3-4", "The political issue is identified and clearly explained; there is a clear explanation of the importance and suitability of the project; the engagement activities are justified."),
        ]),
        C("B", "Process", 3, "Evidence of a planned and integrated research and engagement process.", [
            ("1", "The report evidences a limited research and engagement process."),
            ("2", "The report evidences an adequate research and engagement process."),
            ("3", "The report evidences a well-planned and integrated research and engagement process."),
        ]),
        C("C", "Analysis and synthesis", 8, "Analysis of the political issue using course concepts and content, and synthesis of the perspectives of stakeholders and sources with the engagement.", [
            ("1-2", "Limited analysis of the issue; stakeholder perspectives are stated; little connection to course concepts or content."),
            ("3-4", "Some analysis of the issue; some perspectives are described; some links to course concepts and content."),
            ("5-6", "Analysis uses relevant course concepts and content; multiple stakeholder perspectives are explained and partly synthesised with the research and engagement."),
            ("7-8", "Effective analysis of the political issue that integrates course concepts, content, research and engagement; the perspectives of stakeholders and sources are synthesised into a coherent, well-supported account."),
        ]),
        C("D", "Evaluation and reflection", 6, "Critical evaluation of the research and engagement activities, identification of personal positions and biases, and reflection on the project as a learning experience.", [
            ("1-2", "The research and engagement activities are not evaluated; personal positions and biases are not identified; there is limited reflection on the project as a learning experience."),
            ("3-4", "The research and engagement activities are partially evaluated; some personal positions and biases are identified; there is adequate reflection."),
            ("5-6", "The research and engagement activities are critically evaluated; personal positions and biases are identified and considered; there is critical reflection on the project as a learning experience."),
        ]),
        C("E", "Communication", 3, "Clarity, structure, referencing and compliance with the word limit.", [
            ("1", "Communication is limited: the report is unclear, poorly structured or inadequately referenced."),
            ("2", "Communication is adequate: the report is mostly clear and structured, with referencing."),
            ("3", "Communication is effective: the report is clear, well structured, correctly referenced and within the word limit."),
        ]),
        C("F", "Recommendation (HL only)", 6, "A justified, feasible recommendation derived from the analysis, considering stakeholders and consequences.", [
            ("1-2", "A recommendation is stated with limited connection to the analysis."),
            ("3-4", "A recommendation is described and linked to the issue and some stakeholders, with some discussion of feasibility."),
            ("5-6", "A justified, feasible recommendation clearly derived from the analysis, considering stakeholders, consequences and limitations."),
        ], levels=["HL"]),
    ],
))

RUBRICS.append(R(
    id="ia-hist-2017",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="History",
    task="Historical investigation (three sections)",
    version="Guide in force for sessions up to and including November 2027",
    max_marks=25,
    word_limit=2200,
    limit_note="2,200 words across the three sections (bibliography excluded). Topics within the last ten years are not permitted under this guide.",
    evidence_note="Upload the full investigation with all three sections and the bibliography.",
    weighting="25% at SL, 20% at HL.",
    criteria=[
        C("A", "Identification and evaluation of sources", 6, "A clearly stated research question; two appropriate sources identified, their relevance explained, and their value and limitations analysed with reference to origin, purpose and content.", [
            ("1-2", "The question is stated. The two sources are identified but their relevance is only partly explained; the sources are described rather than evaluated, or evaluation is limited."),
            ("3-4", "An appropriate question is stated. The two sources are identified and their relevance explained; there is some analysis and evaluation of value and limitations, but with limited reference to origin, purpose and content."),
            ("5-6", "An appropriate question is clearly stated. Two appropriate sources are identified and their relevance explained. There is a detailed analysis and evaluation of the two sources with explicit discussion of their value and limitations with reference to origin, purpose and content."),
        ]),
        C("B", "Investigation", 15, "A clear, coherent, effectively organised investigation containing critical analysis focused on the question, using evidence from a range of sources, evaluating different perspectives and reaching a reasoned conclusion.", [
            ("1-3", "The investigation lacks clarity and is poorly organised; little critical analysis; limited evidence; no clear conclusion."),
            ("4-6", "Some organisation; limited critical analysis, mostly narrative; some evidence from sources; a conclusion stated but not consistent with the evidence."),
            ("7-9", "Generally clear and organised; some critical analysis; evidence from a range of sources; some awareness of different perspectives; a conclusion that may not be fully consistent with the evidence."),
            ("10-12", "Generally clear and well organised, with some repetition or lack of clarity in places; critical analysis that may lack development; evidence from a range of sources supports the argument; awareness and some evaluation of different perspectives; a reasoned conclusion."),
            ("13-15", "Clear, coherent and effectively organised; well-developed critical analysis focused clearly on the stated question; evidence from a range of sources used effectively; evaluation of different perspectives; a reasoned conclusion consistent with the evidence and arguments."),
        ]),
        C("C", "Reflection", 4, "What the investigation highlighted about the methods used by, and the challenges facing, the historian, with an explicit connection to the investigation.", [
            ("1-2", "Some discussion of what the investigation highlighted about historians' methods; little awareness of challenges or limitations; the connection to the rest of the investigation is implied but not explicit."),
            ("3-4", "The reflection is clearly focused on what the investigation highlighted about historians' methods, demonstrates clear awareness of challenges facing the historian and/or limitations of the methods, and makes a clear, explicit connection to the rest of the investigation."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-hist-2028",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="History",
    task="Historical investigation (inquiry question, sources and perspectives, synthesis and evaluation)",
    version="New guide: first assessment May 2028 onwards",
    max_marks=24,
    word_limit=2200,
    limit_note="2,200 words; a maximum of seven sources; no ten-year rule (contemporary topics allowed if treated historically).",
    evidence_note="Upload the full investigation.",
    weighting="30% at SL, 20% at HL.",
    fidelity="summarised",
    criteria=[
        C("Q", "Historical inquiry question", 6, "Formulation of an appropriate, focused inquiry question, explanation of how it developed, and its connection to a relevant historical concept (causation, consequence, continuity and change, significance, perspectives).", [
            ("1-2", "A question is stated but is unfocused or unsuitable for historical inquiry; little explanation of how it developed or of its connection to a historical concept."),
            ("3-4", "An appropriate, focused question; some explanation of its development and of its connection to a historical concept."),
            ("5-6", "A clearly focused, appropriate question; a clear explanation of how it developed and why it suits historical inquiry, explicitly linked to a relevant historical concept."),
        ]),
        C("S", "Sources and perspectives", 6, "Justified selection of sources (maximum seven) and explanation of how the diverse perspectives they contain inform the inquiry.", [
            ("1-2", "Sources are listed with limited explanation of why they were chosen; perspectives are identified but not explained."),
            ("3-4", "Sources are selected with some justification; different perspectives are described and partly linked to the question."),
            ("5-6", "The selection of each source is justified; diverse perspectives are explained and their relevance to the inquiry is clear."),
        ]),
        C("E", "Synthesis and evaluation", 12, "Synthesis of evidence from the sources into an argument, evaluation of sources and perspectives, and a supported judgement answering the inquiry question.", [
            ("1-3", "Largely descriptive or narrative; little synthesis; sources used without evaluation; no clear judgement."),
            ("4-6", "Some synthesis of evidence; limited evaluation of sources and perspectives; a judgement that is only partly supported."),
            ("7-9", "Evidence from the sources is synthesised into an argument; sources and perspectives are evaluated; a supported judgement with minor inconsistencies."),
            ("10-12", "Sustained synthesis of evidence from the sources; critical evaluation of sources and perspectives with reference to origin, purpose, content and context; a well-supported, qualified judgement that answers the inquiry question."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-phil",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Philosophy",
    task="Philosophical analysis of a non-philosophical stimulus",
    version="Guide in force (first assessment 2016)",
    max_marks=25,
    word_limit=2000,
    limit_note="2,000 words excluding bibliography and the copy or description of the stimulus (description at most 200 words).",
    evidence_note="Upload the analysis with the stimulus or its description attached.",
    weighting="25% at SL, 20% at HL.",
    criteria=[
        C("A", "Identification of issue and justification", 3, "Explicit identification of the philosophical issue raised by the stimulus and justification of the connection between stimulus and issue.", [
            ("1", "The philosophical issue is implied but not explicitly identified; no justification of the connection between stimulus and issue."),
            ("2", "The philosophical issue is clearly identified; some justification of the connection."),
            ("3", "The philosophical issue is clearly and explicitly identified; there is a clear justification of the connection between the stimulus and the issue."),
        ]),
        C("B", "Clarity", 4, "Clarity, coherence and organisation of the response.", [
            ("1", "The response is unclear and incoherent in places."), ("2", "The response is partly clear but lacks coherence or organisation."), ("3", "The response is generally clear, coherent and organised."), ("4", "The response is clear, coherent and well organised throughout.")]),
        C("C", "Knowledge and understanding", 4, "Accuracy and relevance of philosophical knowledge (positions, arguments, concepts) deployed.", [
            ("1", "Little relevant philosophical knowledge or understanding."), ("2", "Some relevant knowledge and understanding, with inaccuracies or gaps."), ("3", "Good, mostly accurate knowledge and understanding of the relevant philosophical issue."), ("4", "Excellent, accurate and detailed knowledge and understanding of the relevant philosophical issue, ideas and arguments.")]),
        C("D", "Analysis", 8, "Development of philosophical analysis supported by relevant, effective examples.", [
            ("1-2", "The response is mostly descriptive; little analysis; examples ineffective or irrelevant."),
            ("3-4", "Limited analysis; more descriptive than analytical; some examples included."),
            ("5-6", "Analysis is present but lacks development; relevant examples support the argument."),
            ("7-8", "Clear, well-developed analysis of the issue; relevant and effective examples are used to support and advance the argument."),
        ]),
        C("E", "Evaluation", 6, "Evaluation of arguments and counter-arguments, leading to a justified personal position.", [
            ("1-2", "Little or no evaluation; counter-arguments are absent; the student's position is asserted rather than argued."),
            ("3-4", "Some evaluation; counter-arguments are identified but not developed; the student's position is partly justified."),
            ("5-6", "Clear, well-developed evaluation of arguments and counter-arguments; the student's own position is explained and convincingly justified."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-psych-2017",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Psychology",
    task="Experimental study report",
    version="Guide in force for sessions up to and including November 2026",
    max_marks=22,
    word_limit=2200,
    limit_note="1,800 to 2,200 words. The study must be a simple experiment with ethical approval; appendices hold consent forms, materials and raw data.",
    evidence_note="Upload the full report with appendices.",
    weighting="25% at SL, 20% at HL.",
    criteria=[
        C("A", "Introduction", 6, "Aim, relevance of the chosen theory or model, operationalised independent and dependent variables, and hypotheses.", [
            ("1-2", "The aim is stated but not focused; the background theory or model is described but its relevance is not explained; variables are not operationalised."),
            ("3-4", "The aim is stated and the relevance of the theory or model is partly explained; the independent and dependent variables are operationalised but with omissions."),
            ("5-6", "The aim is clearly stated; the relevant theory or model is explained and explicitly linked to the investigation; the independent and dependent variables are clearly operationalised and the hypotheses are appropriate."),
        ]),
        C("B", "Exploration", 4, "Research design, sampling technique, participant characteristics, controlled variables, materials and procedure, and ethical considerations.", [
            ("1-2", "Design, sampling, controls, materials and procedure are described with omissions; ethical considerations are only partly addressed."),
            ("3-4", "The research design is explained and justified; the sampling technique, participant characteristics, controlled variables, materials and procedure are described; ethical considerations are addressed."),
        ]),
        C("C", "Analysis", 6, "Appropriate, justified descriptive and inferential statistics, a relevant graph, and interpretation of the results in relation to the hypothesis.", [
            ("1-2", "Descriptive statistics are applied with errors or without justification; the graph is inappropriate; inferential statistics are missing or incorrect."),
            ("3-4", "Appropriate descriptive and inferential statistics are applied with minor errors or limited justification; the graph is appropriate; interpretation is partly accurate."),
            ("5-6", "Descriptive and inferential statistics are appropriately and accurately applied and explicitly justified; the graph addresses the hypothesis; statistical findings are interpreted accurately and linked to the hypothesis."),
        ]),
        C("D", "Evaluation", 6, "Discussion of findings in relation to the background theory, strengths and limitations of design, sample and procedure, and relevant modifications.", [
            ("1-2", "Findings are discussed with limited reference to the theory or model; strengths and limitations are listed; modifications are not relevant."),
            ("3-4", "Findings are discussed with reference to the theory or model; strengths and limitations of the design, sample and procedure are described with some relevance; modifications are suggested."),
            ("5-6", "Findings are discussed in relation to the theory or model; strengths and limitations of the design, sample and procedure are explained and relevant to the investigation; modifications are explicitly linked to the limitations."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-psych-2027",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Psychology",
    task="Research proposal (the study is designed but not carried out)",
    version="New guide: first assessment May 2027 onwards",
    max_marks=24,
    word_limit=2200,
    limit_note="2,200 words; examiners stop reading at the limit. References and appendices (including the data collection tool with at least five items) are excluded.",
    evidence_note="Upload the proposal including the appendix with the data collection tool.",
    weighting="30% at SL, 20% at HL. Same task and criteria at both levels.",
    fidelity="summarised",
    criteria=[
        C("A", "Introduction", 6, "A focused aim or research question; the real-life problem and how it affects the population of interest; two pieces of relevant research explained and linked to the investigation.", [
            ("1-2", "The aim is broad or unclear; the problem and population are described superficially; research is mentioned but not linked to the investigation."),
            ("3-4", "The aim is stated; the problem's effect on the population is described; two pieces of research are described with some links to the investigation."),
            ("5-6", "The aim or research question is clear and focused; the impact of the problem on the population is explained; both pieces of research are explained and clearly linked to the proposed investigation."),
        ]),
        C("B", "Research methodology", 6, "Justified choice of method (experiment, interview, observation or survey), sampling, participants, procedure and ethical considerations explicitly linked to the proposal.", [
            ("1-2", "The method is stated with limited justification; procedure, sampling and ethics are incomplete or generic."),
            ("3-4", "The method and procedure are described with some justification; ethical considerations are relevant but only partly linked to the investigation."),
            ("5-6", "The choice of method and the procedure are explained and justified; sampling and participants are appropriate; relevant ethical considerations are explicitly linked to the investigation."),
        ]),
        C("C", "Data collection", 6, "An appropriate, effective data collection tool with justified design decisions, and explanation of potential challenges in collecting data.", [
            ("1-2", "The tool is incomplete or inappropriate; design decisions are not explained; challenges are stated generically."),
            ("3-4", "The tool is appropriate; some design decisions are explained; relevant challenges are described."),
            ("5-6", "The tool is appropriate and effective; its design (items, scales, operationalisation of variables) is justified; potential challenges (for example demand characteristics, social desirability, researcher bias, validity) are explained in relation to this investigation."),
        ]),
        C("D", "Discussion", 6, "Potential findings and their implications or applications, relevant researcher bias, and the usefulness of an additional research method.", [
            ("1-2", "Potential findings are stated without implications; bias and an additional method are mentioned only."),
            ("3-4", "Potential findings and some implications are described; researcher bias is identified; an additional method is described."),
            ("5-6", "Potential findings are discussed in detail with their implications and applications; the effect of relevant researcher bias on the investigation is discussed; the usefulness of an additional method is explained."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-sca-sl",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Social and cultural anthropology (SL)",
    task="Doing anthropology: limited fieldwork (four activities)",
    version="Guide in force (first assessment 2019)",
    levels=["SL"],
    max_marks=26,
    limit_note="Observation and report 450 words; methodological and conceptual extension 300 words; second data collection and analysis 400 words; critical reflection 850 words.",
    evidence_note="Upload all four activities in one file.",
    weighting="20% at SL.",
    fidelity="summarised",
    criteria=[
        C("A", "Observation and report", 4, "A detailed, descriptive report of the observation with the observer's position recognised.", [
            ("1", "The report is brief and partial."), ("2", "The report describes the observation with some detail."), ("3", "The report is detailed and organised."), ("4", "The report is detailed, well organised and recognises the position of the observer.")]),
        C("B", "Methodological and conceptual extension of initial fieldwork", 6, "Reflection on the method used, identification of an anthropological concept or area of inquiry, and a justified plan for a second method.", [
            ("1-2", "Limited reflection on the method; a concept is named; the second method is stated without justification."),
            ("3-4", "Some reflection on the initial method's strengths and limitations; a relevant concept is identified; the second method is partly justified."),
            ("5-6", "Clear reflection on the initial method; a relevant concept or area of inquiry is identified and explained; the choice of a second data collection method is well justified."),
        ]),
        C("C", "Second fieldwork data collection and analysis", 4, "Presentation and analysis of data from the second method in relation to the chosen concept.", [
            ("1", "Data is presented with little analysis."), ("2", "Data is presented and partly analysed."), ("3", "Data is presented and analysed in relation to the concept."), ("4", "Data is presented clearly and analysed effectively in relation to the chosen concept.")]),
        C("D", "Concepts", 12, "Critical reflection on the fieldwork, methods and concepts, using anthropological concepts and comparison with ethnographic material.", [
            ("1-3", "Reflection is descriptive; concepts are used loosely; little comparison with ethnography."),
            ("4-6", "Some critical reflection; concepts are applied with partial accuracy; limited comparison."),
            ("7-9", "Critical reflection on methods and concepts; concepts are applied accurately; relevant comparison with ethnographic material."),
            ("10-12", "Sustained critical reflection; anthropological concepts are applied accurately and insightfully; effective comparison with ethnographic material and awareness of the researcher's position."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-sca-hl",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="Social and cultural anthropology (HL)",
    task="Doing anthropology: fieldwork (critical reflection and research report)",
    version="Guide in force (first assessment 2019)",
    levels=["HL"],
    max_marks=33,
    limit_note="Critical reflection 800 words; research report and evaluation 1,600 words; at least two data collection methods.",
    evidence_note="Upload both the critical reflection and the research report.",
    weighting="25% at HL.",
    fidelity="summarised",
    criteria=[
        C("A", "Anthropological nature of the research", 4, "The research question and focus are anthropological and linked to concepts and an area of inquiry.", [
            ("1", "The focus is barely anthropological."), ("2", "The focus is partly anthropological."), ("3", "The focus is clearly anthropological."), ("4", "The focus is clearly anthropological and framed with relevant concepts and area of inquiry.")]),
        C("B", "Appropriateness and justification of methods", 4, "Appropriateness of at least two methods and justification of their choice.", [
            ("1", "Methods are stated without justification."), ("2", "Methods are described with limited justification."), ("3", "Methods are appropriate and justified."), ("4", "Methods are appropriate, well justified and related to the research question.")]),
        C("C", "Awareness of ethical considerations", 4, "Ethical issues identified and addressed (consent, anonymity, harm, position of the researcher).", [
            ("1", "Ethical issues are mentioned."), ("2", "Some ethical issues are identified and partly addressed."), ("3", "Relevant ethical issues are identified and addressed."), ("4", "Relevant ethical issues are identified, addressed and reflected on in relation to the fieldwork.")]),
        C("D", "Critical thinking", 12, "Presentation, interpretation and analysis of data using anthropological concepts and theory, with comparison to ethnographic material.", [
            ("1-3", "Data is presented descriptively with little interpretation; concepts and theory are absent or misused."),
            ("4-6", "Data is interpreted with some use of concepts; limited theoretical framing; limited comparison."),
            ("7-9", "Data is analysed using relevant concepts and some theory; comparison with ethnographic material supports the argument."),
            ("10-12", "Data is analysed critically and insightfully using relevant concepts and theory; comparison with ethnographic material is effective and the argument is coherent."),
        ]),
        C("E", "Evaluation of fieldwork process (doing anthropology)", 9, "Comparative and critical evaluation of the methods and strategies used, the data produced, and reflection on practical and ethical aspects of the fieldwork.", [
            ("1-3", "Evaluation is descriptive; methods are listed with little comparison."),
            ("4-6", "Some comparative evaluation of methods and data; some reflection on practical and ethical issues."),
            ("7-9", "Critical, comparative evaluation of methods and data, with insightful reflection on the practical and ethical experience of doing anthropology."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-wr",
    component="Internal Assessment",
    group="Group 3: Individuals and societies",
    subject="World religions",
    task="Investigative study (written analysis under five headings)",
    version="Guide in force (SL only; replaced by Religion and society from first assessment 2029)",
    levels=["SL"],
    max_marks=30,
    word_limit=1800,
    limit_note="1,500 to 1,800 words, written under the five set headings.",
    evidence_note="Upload the written analysis.",
    weighting="25% (SL only).",
    criteria=[
        C("A", "Rationale and preliminary research", 8, "Rationale for the topic, definition of the focus as a question, and a justified range of sources with supporting evidence.", [
            ("1-2", "The rationale is stated with little evidence of research, or there is limited research but no rationale."),
            ("3-4", "The study has been researched and some supporting evidence produced, though it may not be relevant; the rationale is stated."),
            ("5-6", "The study has been well researched using a range of sources and supporting evidence has been produced; the rationale is clearly stated with some development."),
            ("7-8", "The study has been thoroughly researched using a wide range of sources and excellent supporting evidence has been produced; the rationale is clearly stated and well developed."),
        ]),
        C("B", "Plan for study", 3, "Scope and plan of the study and the focus of the research question.", [
            ("1", "The scope and/or plan are stated but not clearly focused; there is no research question."),
            ("2", "The scope and plan are generally appropriate and focused; the research question is stated and related to the plan."),
            ("3", "The scope and plan are appropriate and focused; the research question is clearly focused and closely related to the scope and plan."),
        ]),
        C("C", "Summary of significant findings", 6, "Significant findings from observation, interview or participation, related to the research question, rationale and plan.", [
            ("1-2", "Little indication of significant findings; findings are not related to the research question, rationale and plan."),
            ("3-4", "Significant findings are stated and related to one or more aspects of the research question, rationale and plan."),
            ("5-6", "Significant findings are clearly stated and well developed, and their relationship to the research question, rationale and plan is fully demonstrated."),
        ]),
        C("D", "Critical reflection and evaluation", 10, "Critical reflection on the findings in relation to the question, how the study deepens understanding of religious experience or belief, misconceptions and inconsistencies identified, and evaluation of the research methods.", [
            ("1-2", "Critical reflection is very limited with no linkage between question and findings."),
            ("3-4", "Some critical reflection with partial linkage; limited evaluation of methods."),
            ("5-6", "Critical reflection links findings to the question and shows how understanding was deepened; some misconceptions identified; methods evaluated in part."),
            ("7-8", "Clear critical reflection; the deepening of understanding is explained; misconceptions and inconsistencies are identified; methods are evaluated."),
            ("9-10", "Thorough, insightful critical reflection fully linking findings to the question; understanding of religious experience is clearly deepened; misconceptions, assumptions and inconsistencies are analysed; the success of the research and directions for future research are evaluated."),
        ]),
        C("E", "References and compliance with format", 3, "Referencing, bibliography, headings and word limit.", [
            ("1", "Referencing is incomplete and the format is only partly followed."), ("2", "Referencing is mostly complete and the format is largely followed."), ("3", "Referencing is complete and accurate; the set format and word limit are followed.")]),
    ],
))

RUBRICS.append(R(
    id="ia-ess-2026",
    component="Internal Assessment",
    group="Group 3 / Group 4 (interdisciplinary)",
    subject="Environmental systems and societies",
    task="Individual investigation",
    version="New guide: first assessment 2026 onwards",
    max_marks=30,
    word_limit=3000,
    limit_note="3,000 words (charts, data tables, equations, citations and bibliography excluded).",
    evidence_note="Upload the full report.",
    weighting="25% at SL, 20% at HL. Same task and criteria at both levels.",
    fidelity="summarised",
    criteria=[
        C("A", "Research question and inquiry", 4, "A local or global environmental issue explained with sufficient background research, leading to a focused research question.", [
            ("1-2", "An environmental issue is identified with limited background; the research question is stated but not focused or only loosely connected to the issue."),
            ("3-4", "A local or global environmental issue is explained with sufficient background research; a focused, relevant research question is stated with a clear connection to the issue."),
        ]),
        C("B", "Strategy", 4, "An existing or developing strategy that addresses an environmental issue linked to the question, and the tension it creates between different perspectives.", [
            ("1-2", "A strategy is identified; the tension between perspectives is mentioned but not explained."),
            ("3-4", "A relevant existing or developing strategy is described and a tension it creates between different perspectives (for example economic, ecological, ethical, social) is explained."),
        ]),
        C("C", "Method", 4, "A repeatable method that collects sufficient relevant data to answer the question, with variables, sampling, controls and risk or ethics considered.", [
            ("1-2", "The method is described but is not fully repeatable or does not collect sufficient relevant data; variables or sampling are incomplete."),
            ("3-4", "The method is repeatable and collects sufficient relevant data to answer the research question; variables, sampling and controls are appropriate and risks or ethics are considered."),
        ]),
        C("D", "Treatment of data", 6, "Clear, correct communication and processing of raw data so that the findings address the research question.", [
            ("1-2", "Raw data is presented unclearly or incompletely; processing has significant errors or is missing."),
            ("3-4", "Data is communicated mostly clearly; processing is mostly correct with some omissions (for example units, uncertainties, appropriate statistics)."),
            ("5-6", "Raw and processed data are communicated clearly and correctly, with units, uncertainties and appropriate graphs or statistics, so that the findings address the research question."),
        ]),
        C("E", "Analysis and conclusion", 6, "Patterns and trends explained, including bias, reliability, validity and uncertainty, leading to a valid, supported conclusion.", [
            ("1-2", "Patterns or trends are identified; a conclusion is stated but weakly supported."),
            ("3-4", "Patterns and trends are described with some consideration of reliability, validity or uncertainty; a valid conclusion related to the research question is reached."),
            ("5-6", "Patterns and trends are explained, including bias, reliability, validity and uncertainty; the conclusion is fully supported by the data and discussed in relation to the environmental issue and strategy."),
        ]),
        C("F", "Evaluation", 6, "Specific weaknesses and limitations, realistic improvements and unresolved questions.", [
            ("1-2", "Generic weaknesses or limitations and improvements are stated."),
            ("3-4", "Specific weaknesses and limitations are described with relevant, realistic improvements."),
            ("5-6", "Specific weaknesses and limitations are evaluated for their impact on the results, realistic relevant improvements are explained, and unresolved questions or further research are identified."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-ess-2017",
    component="Internal Assessment",
    group="Group 3 / Group 4 (interdisciplinary)",
    subject="Environmental systems and societies",
    task="Individual investigation",
    version="Previous guide (last assessment November 2025)",
    levels=["SL"],
    max_marks=30,
    word_limit=2250,
    limit_note="1,500 to 2,250 words.",
    evidence_note="Use only for work assessed under the previous guide.",
    weighting="25% (SL only).",
    criteria=[
        C("CXT", "Identifying the context", 6, "An environmental issue explored to give context, and a relevant, focused research question connected to it.", [
            ("1-2", "The research question is stated but is unfocused; the environmental issue is mentioned with limited connection."),
            ("3-4", "A relevant research question is stated; the environmental issue is described and connections to the question are described with omissions."),
            ("5-6", "A relevant, coherent and focused research question is stated; a relevant environmental issue is discussed as the context and the connections between issue and question are explained."),
        ]),
        C("PLA", "Planning", 6, "A repeatable method appropriate to the question, with sampling strategy and risk assessment.", [
            ("1-2", "The method is outlined; sampling and risks are not addressed; the method does not allow collection of sufficient relevant data."),
            ("3-4", "The method is described and allows collection of relevant data, with some omissions in sampling strategy or risk assessment."),
            ("5-6", "The method is appropriate, repeatable and justified; the sampling strategy allows sufficient relevant data; risk assessment and ethical considerations are addressed."),
        ]),
        C("RAC", "Results, analysis and conclusion", 6, "Construction of appropriate diagrams, charts or graphs, correct and complete analysis, and a valid conclusion deduced from the data.", [
            ("1-2", "Data is presented with errors; analysis is incomplete; the conclusion is not supported."),
            ("3-4", "Appropriate diagrams, charts or graphs are constructed for most data; analysis is mostly correct; a conclusion is reached that is partly supported."),
            ("5-6", "Diagrams, charts or graphs of all relevant data are constructed appropriately; the data is analysed correctly and completely so that all relevant patterns are displayed; trends, patterns or relationships are interpreted so that a valid conclusion is deduced."),
        ]),
        C("DEV", "Discussion and evaluation", 6, "Evaluation of the conclusion in the context of the environmental issue, strengths, weaknesses and limitations of the method, and modifications or further research.", [
            ("1-2", "Some aspects of the conclusion are related to the issue; some strengths and weaknesses identified; superficial modifications."),
            ("3-4", "The conclusion is evaluated in the context of the issue with omissions; some strengths, weaknesses and limitations are described; modifications and further research suggested."),
            ("5-6", "The conclusion is evaluated in the context of the environmental issue; strengths, weaknesses and limitations of the method are explained; relevant, realistic modifications and further research are proposed."),
        ]),
        C("APP", "Applications", 3, "One way of applying the outcomes to the broader environmental issue, with strengths and limitations of that solution.", [
            ("1", "One potential application or solution is stated with some strengths and weaknesses."), ("2", "One application is described and its strengths and weaknesses evaluated in part."), ("3", "One application is justified and its strengths, weaknesses and limitations are evaluated.")]),
        C("COM", "Communication", 3, "Structure, clarity, concision, terminology and referencing.", [
            ("1", "The report is not well structured; terminology and referencing are inconsistent."), ("2", "The report is mostly well structured and clear; terminology is appropriate with some lapses."), ("3", "The report is well structured, clear and concise, uses appropriate terminology and is correctly referenced within the word limit.")]),
    ],
))

# ----- Group 4 ---------------------------------------------------------------

RUBRICS.append(R(
    id="ia-sci-2025",
    component="Internal Assessment",
    group="Group 4: Sciences",
    subject="Biology, Chemistry or Physics",
    task="Scientific investigation",
    version="Guide in force (first assessment 2025)",
    max_marks=24,
    word_limit=3000,
    limit_note="3,000 words (charts, diagrams, data tables, equations, calculations, citations, bibliography and headers excluded).",
    evidence_note="Upload the full report with data tables and graphs.",
    weighting="20% at SL and HL. Same task and criteria at both levels.",
    variants={"label": "Science subject", "options": ["Biology", "Chemistry", "Physics"]},
    criteria=SCI_2025_CRITERIA,
))

RUBRICS.append(R(
    id="ia-sehs-2026",
    component="Internal Assessment",
    group="Group 4: Sciences",
    subject="Sports, exercise and health science",
    task="Scientific investigation",
    version="New guide: first assessment 2026 onwards",
    max_marks=24,
    word_limit=3200,
    limit_note="3,200 words. The investigation must generate quantitative data; human-participant work needs consent and a readiness questionnaire.",
    evidence_note="Upload the full report.",
    weighting="24% at SL and HL.",
    criteria=SCI_2025_CRITERIA,
))

RUBRICS.append(R(
    id="ia-cs-2014",
    component="Internal Assessment",
    group="Group 4: Sciences",
    subject="Computer science",
    task="Solution for a client (documentation, product and video)",
    version="Guide in force for sessions up to and including November 2026",
    max_marks=34,
    word_limit=2000,
    limit_note="2,000 words of documentation (criteria A, B, C and E), plus the product, a video and appendices.",
    evidence_note="Upload the documentation. Criterion D depends on the video and the product and can only be partly judged from text.",
    weighting="30% at SL, 20% at HL.",
    fidelity="summarised",
    criteria=[
        C("A", "Planning", 6, "The scenario and client, the rationale for the solution, and specific, measurable success criteria with evidence of consultation.", [
            ("1-2", "The scenario is unclear; the rationale is limited; success criteria are missing or not measurable."),
            ("3-4", "The scenario and rationale are described; success criteria are stated but some are vague or hard to test."),
            ("5-6", "The scenario and client are clearly identified with evidence of consultation; the rationale is justified; the success criteria are specific, measurable and complete."),
        ]),
        C("B", "Solution overview", 6, "Record of tasks, design overview (structure, algorithms, data, interface) and a test plan matching the success criteria.", [
            ("1-2", "The record of tasks and design are incomplete; little test planning."),
            ("3-4", "The record of tasks and design overview are mostly complete; the test plan covers some success criteria."),
            ("5-6", "A complete record of tasks and a clear, justified design overview; a test plan that covers all success criteria."),
        ]),
        C("C", "Development", 12, "Techniques used, their complexity and ingenuity, with clear explanation of the development of the product.", [
            ("1-3", "Few techniques, explained poorly; the product is largely unoriginal or trivial."),
            ("4-6", "Appropriate techniques are used and partly explained; limited complexity."),
            ("7-9", "A range of appropriate techniques with some complexity, explained clearly with sources acknowledged."),
            ("10-12", "A range of appropriate, complex and ingenious techniques, thoroughly explained and justified, with evidence of understanding of the algorithms and structures used."),
        ]),
        C("D", "Functionality and extensibility of product", 4, "The product functions as demonstrated in the video and is organised so that it can be extended.", [
            ("1-2", "The product is partly functional or poorly organised."),
            ("3-4", "The product is fully functional and its organisation (modularity, comments, naming) supports extension."),
        ], assessable=False),
        C("E", "Evaluation", 6, "Evaluation of the product against the success criteria using client feedback, with justified recommendations for improvement.", [
            ("1-2", "Evaluation is limited and not linked to the success criteria; recommendations are vague."),
            ("3-4", "The product is evaluated against most success criteria with some client feedback; recommendations are appropriate."),
            ("5-6", "The product is evaluated against all success criteria with explicit client feedback; recommendations for further development are justified."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-cs-2027",
    component="Internal Assessment",
    group="Group 4: Sciences",
    subject="Computer science",
    task="Computational solution (documentation, product, video, source code)",
    version="New guide: first assessment May 2027 onwards",
    max_marks=30,
    word_limit=2000,
    limit_note="2,000 words of documentation (code, code comments and diagrams excluded), a video of at most 5 minutes showing functionality and testing, and the full source code as an appendix. No client is required.",
    evidence_note="Upload the documentation (and source code if available). Criterion D also relies on the video.",
    weighting="30% at SL, 20% at HL. Same criteria at both levels.",
    fidelity="summarised",
    criteria=[
        C("A", "Problem specification", 4, "The problem scenario, its computational context, and appropriate, measurable success criteria.", [
            ("1-2", "The problem is described vaguely; the computational context is unclear; success criteria are incomplete or not measurable."),
            ("3-4", "The problem is described in terms of measurable requirements; the fit of a computational solution is explained; success criteria are appropriate and testable."),
        ]),
        C("B", "Planning", 4, "A reasonable decomposition of the problem and a plan that addresses the success criteria.", [
            ("1-2", "The problem is only partly decomposed; the plan is generic and not tied to the success criteria."),
            ("3-4", "The problem is decomposed into components and the plan clearly addresses the success criteria with milestones."),
        ]),
        C("C", "System overview", 6, "A complete system model, algorithms for its components, and a testing strategy aligned with the success criteria.", [
            ("1-2", "The system model is incomplete; algorithms are sketched; testing is not planned."),
            ("3-4", "The system model is mostly complete; algorithms are given for most components; the testing strategy covers some success criteria."),
            ("5-6", "The system model is complete (diagrams, data structures, interfaces); algorithms are given for the components; the testing strategy is aligned with all success criteria."),
        ]),
        C("D", "Development", 12, "A fully functional product built with appropriate techniques, implementation choices evaluated, and the testing strategy justified, evidenced by the documentation and video.", [
            ("1-3", "The product is largely non-functional or techniques are inappropriate and unexplained."),
            ("4-6", "The product is partly functional; some appropriate techniques are described; limited evaluation of implementation choices."),
            ("7-9", "The product is functional; appropriate techniques are explained and most implementation choices evaluated; testing is described."),
            ("10-12", "The product is fully functional; appropriate techniques are explained and justified; implementation choices are evaluated and the testing strategy is justified with evidence."),
        ]),
        C("E", "Evaluation", 4, "The extent to which the success criteria were met, with justified improvements.", [
            ("1-2", "The evaluation is general; success criteria are not systematically assessed; improvements are unjustified."),
            ("3-4", "Each success criterion is evaluated with evidence; limitations are identified honestly and improvements are justified."),
        ]),
    ],
))

DT_2016_AD = [
    C("A", "Analysis of a design opportunity", 9, "Design opportunity or problem, inquiry and research, design brief and specifications.", [
        ("1-3", "The design opportunity is outlined; research is limited; the brief and specifications are incomplete or not justified."),
        ("4-6", "The design opportunity is described with relevant research; a design brief is stated and specifications are listed with some justification."),
        ("7-9", "The design opportunity is explained and justified through detailed, relevant research; the design brief is clear and the specifications are detailed, measurable and justified."),
    ]),
    C("B", "Conceptual design", 9, "Generation of ideas, modelling, and justified selection of an idea for detailed development.", [
        ("1-3", "Few ideas with little development or modelling; the idea for development is chosen with limited justification."),
        ("4-6", "A range of ideas with some annotation and modelling; an idea is selected with some justification against the specifications."),
        ("7-9", "A wide range of feasible, well-annotated ideas; effective modelling to test and develop them; an appropriate idea is justified for detailed development against the specifications."),
    ]),
    C("C", "Development of a detailed design", 9, "Development of the chosen idea, justification of materials, components and techniques, and a manufacturing plan.", [
        ("1-3", "The idea is developed in a limited way; choices of materials and techniques are stated; the plan is incomplete."),
        ("4-6", "The design is developed with some justification of materials, components and techniques; a plan for making the prototype is given."),
        ("7-9", "The design is fully developed with detailed drawings; choices of materials, components and techniques are justified; a detailed, accurate plan for making the prototype is provided."),
    ]),
    C("D", "Testing and evaluation", 9, "Testing strategy and results, evaluation of the prototype against the specifications, and improvements.", [
        ("1-3", "Testing is limited; evaluation is descriptive; improvements are superficial."),
        ("4-6", "Testing is described with results; the prototype is evaluated against some specifications; improvements are suggested."),
        ("7-9", "A justified testing strategy with results; the prototype is evaluated systematically against the specifications and user feedback; improvements are explained and justified."),
    ]),
]

RUBRICS.append(R(
    id="ia-dt-2016",
    component="Internal Assessment",
    group="Group 4: Sciences",
    subject="Design technology",
    task="Design project (SL criteria A to D; HL criteria A to F)",
    version="Guide in force for sessions up to and including November 2026",
    max_marks=36,
    limit_note="Portfolio of pages: 34 pages at SL (criteria A to D) and 54 at HL (A to F). HL total 54 marks.",
    evidence_note="Upload the design folder as a PDF.",
    weighting="40% at SL and HL.",
    fidelity="summarised",
    criteria=DT_2016_AD + [
        C("E", "Detailed development of a commercial product (HL)", 9, "Development of the prototype into a product suitable for commercial production, with justified changes.", [
            ("1-3", "Changes for commercial production are listed with little justification."),
            ("4-6", "The design is developed for commercial production with some justification of changes."),
            ("7-9", "The design is developed in detail for commercial production; changes to design, materials and processes are fully justified."),
        ], levels=["HL"]),
        C("F", "Making choices for commercial production (HL)", 9, "Justified selection of materials, components, processes, scale and volume of production for commercial manufacture.", [
            ("1-3", "Choices are stated with limited justification."),
            ("4-6", "Choices of materials, processes and scale are described with some justification."),
            ("7-9", "Choices of materials, components, processes, scale and volume of production are fully justified with reference to commercial, user and environmental requirements."),
        ], levels=["HL"]),
    ],
))

RUBRICS.append(R(
    id="ia-dt-2027",
    component="Internal Assessment",
    group="Group 4: Sciences",
    subject="Design technology",
    task="Design project (redesign of an existing product for an intended user)",
    version="New guide: first assessment May 2027 onwards",
    max_marks=33,
    word_limit=3500,
    limit_note="Report of at most 3,500 words (about 35 pages); a physical fidelity model is required for testing.",
    evidence_note="Upload the design report as a PDF.",
    weighting="40% at SL, 30% at HL. Same criteria and marks at both levels.",
    fidelity="summarised",
    criteria=[
        C("A", "Empathize", 9, "Understanding the intended user and their needs through research, and analysis of the existing product to be redesigned.", [
            ("1-3", "The user and their needs are described superficially; analysis of the existing product is limited."),
            ("4-6", "The user and their needs are described through some primary and secondary research; the existing product is analysed with some depth."),
            ("7-9", "The intended user and their needs are explained through detailed, relevant primary and secondary research; the existing product is analysed thoroughly, identifying justified opportunities for redesign."),
        ]),
        C("B", "Defining the project", 6, "A design brief and detailed, measurable specifications derived from the empathize stage.", [
            ("1-2", "The brief is vague; specifications are few, generic or not measurable."),
            ("3-4", "A clear brief; specifications are relevant and mostly measurable, partly justified by the research."),
            ("5-6", "A clear, focused brief; detailed, measurable specifications that are explicitly justified by the user research and product analysis."),
        ]),
        C("C", "Ideation and modelling", 6, "A range of distinct ideas, modelling to develop and test them, and justified selection.", [
            ("1-2", "Few or very similar ideas; little modelling; selection unjustified."),
            ("3-4", "A range of ideas with some modelling; selection justified against some specifications."),
            ("5-6", "A wide range of distinct, well-communicated ideas; effective modelling to test and develop them; selection fully justified against the specifications and user needs."),
        ]),
        C("D", "Designing a solution", 6, "Detailed development of the chosen idea, the physical fidelity model, and testing with the user.", [
            ("1-2", "The solution is developed in limited detail; the fidelity model is basic or untested."),
            ("3-4", "The solution is developed with drawings and a fidelity model; some testing with the user."),
            ("5-6", "The solution is developed in detail (drawings, materials, processes); the physical fidelity model is tested with the intended user and the results inform refinements."),
        ]),
        C("E", "Presents a solution", 6, "Communication of the final solution and its evaluation against the specifications and user needs.", [
            ("1-2", "The final solution is presented with little evaluation."),
            ("3-4", "The final solution is clearly presented and evaluated against some specifications."),
            ("5-6", "The final solution is communicated effectively and evaluated systematically against the specifications and the user's needs, with justified recommendations."),
        ]),
    ],
))

# ----- Group 5 ---------------------------------------------------------------

RUBRICS.append(R(
    id="ia-math-2019",
    component="Internal Assessment",
    group="Group 5: Mathematics",
    subject="Mathematics: analysis and approaches / applications and interpretation",
    task="Mathematical exploration",
    version="Guide in force for sessions up to and including November 2028",
    max_marks=20,
    limit_note="About 12 to 20 pages, double spaced; bibliography excluded. Criteria A to D are the same at SL and HL; criterion E differs.",
    evidence_note="Upload the exploration as a PDF so that graphs and notation are preserved.",
    weighting="20% in all four courses.",
    variants={"label": "Course", "options": ["Analysis and approaches", "Applications and interpretation"]},
    criteria=[
        C("A", "Presentation", 4, "Organisation, coherence and concision.", [
            ("1", "The exploration has some organisation."), ("2", "The exploration has some organisation and coherence."), ("3", "The exploration is well organised and coherent."), ("4", "The exploration is well organised, coherent and concise.")]),
        C("B", "Mathematical communication", 4, "Appropriate mathematical language, notation and terminology; defined variables; labelled graphs, tables and diagrams; consistency.", [
            ("1", "Some relevant mathematical communication which is partially appropriate."), ("2", "Some relevant appropriate mathematical communication."), ("3", "Mathematical communication is relevant, appropriate and mostly consistent."), ("4", "Mathematical communication is relevant, appropriate and consistent throughout.")]),
        C("C", "Personal engagement", 3, "The extent to which the student engages with the topic and makes it their own: independent or creative thinking, own perspective, making and testing predictions. Not a measure of effort.", [
            ("1", "There is evidence of some personal engagement."), ("2", "There is evidence of significant personal engagement."), ("3", "There is evidence of outstanding personal engagement.")]),
        C("D", "Reflection", 3, "Reviewing, analysing and evaluating the exploration, including limitations, extensions and implications, throughout the work.", [
            ("1", "There is evidence of limited reflection."), ("2", "There is evidence of meaningful reflection."), ("3", "There is substantial evidence of critical reflection.")]),
        C("E", "Use of mathematics", 6, "Relevance, correctness, level and (at HL) sophistication and rigour of the mathematics, with demonstrated understanding.",
          MATH_2019_E_SL, bands_by_level={"SL": MATH_2019_E_SL, "HL": MATH_2019_E_HL}),
    ],
))

RUBRICS.append(R(
    id="ia-math-2029",
    component="Internal Assessment",
    group="Group 5: Mathematics",
    subject="Mathematics: analysis and approaches / applications and interpretation",
    task="Mathematical exploration (inquiry-cycle criteria)",
    version="New guides: first assessment May 2029 onwards",
    max_marks=20,
    limit_note="Identical criteria at SL and HL; about 30 teaching hours.",
    evidence_note="Only for students assessed from May 2029. Descriptors are summarised from the subject brief.",
    weighting="20%.",
    variants={"label": "Course", "options": ["Analysis and approaches", "Applications and interpretation"]},
    fidelity="summarised",
    criteria=[
        C("A", "Problem specification", 4, "Placing the problem in context and identifying the desired outcomes.", [
            ("1-2", "The problem is stated with limited context; desired outcomes are vague."),
            ("3-4", "The problem is clearly placed in context and the desired outcomes are clearly identified."),
        ]),
        C("B", "Abstraction", 6, "Making assumptions, selecting techniques and tools, and expressing the situation in mathematical form.", [
            ("1-2", "Assumptions are implicit; techniques are chosen without justification; the mathematical formulation is incomplete."),
            ("3-4", "Assumptions are stated; appropriate techniques are selected with some justification; the situation is expressed mathematically with minor gaps."),
            ("5-6", "Assumptions are stated and justified; techniques and tools are well chosen and justified; the situation is expressed in an appropriate and complete mathematical form."),
        ]),
        C("C", "Computation", 4, "Completing the mathematical work correctly and communicating it clearly.", [
            ("1-2", "Calculations contain errors or are incomplete; communication is inconsistent."),
            ("3-4", "Calculations are correct and complete; mathematical communication is clear and consistent."),
        ]),
        C("D", "Interpretation", 6, "Interpreting results, evaluating the desired outcomes and refining the investigation.", [
            ("1-2", "Results are stated with little interpretation; no evaluation or refinement."),
            ("3-4", "Results are interpreted in context; outcomes are evaluated with some limitations noted; some refinement."),
            ("5-6", "Results are interpreted thoroughly in context; outcomes are evaluated critically against the problem; the investigation is refined or extensions are justified."),
        ]),
    ],
))

# ----- Group 6 ---------------------------------------------------------------

RUBRICS.append(R(
    id="ia-theatre-pp",
    component="Internal Assessment",
    group="Group 6: The arts",
    subject="Theatre",
    task="Production proposal",
    version="Guide in force (first assessment 2024)",
    max_marks=20,
    word_limit=4000,
    limit_note="At most 12 pages of text and images, with written text not exceeding 4,000 words, plus a list of sources. The play must not have been previously studied.",
    evidence_note="Upload the proposal as a PDF so images are included.",
    weighting="30% at SL, 20% at HL.",
    fidelity="summarised",
    criteria=[
        C("A", "Ideas and intentions", 8, "Explanation of the key ideas in the play text with examples, and the director/designer intentions for staging the entire play, including performance style and space.", [
            ("1-2", "Ideas in the play are listed with limited explanation; intentions are stated."),
            ("3-4", "Key ideas are outlined with some examples; intentions are described and a performance style or space is identified."),
            ("5-6", "Key ideas are explained with examples; intentions are explained and connected to the chosen style and space."),
            ("7-8", "Key ideas are fully explained with precise examples from the text; director and designer intentions are thoroughly justified and clearly connected to the proposed performance style and space."),
        ]),
        C("B", "The proposed design", 4, "Visual presentation and explanation of how production elements will be used to achieve the intentions across the whole play.", [
            ("1", "Design ideas are presented as a list of information about production elements."),
            ("2", "Design ideas are presented with an outline of how production elements will be used to achieve the intentions."),
            ("3", "Visual design ideas are presented with an explanation of how production elements achieve the intentions."),
            ("4", "Visual design ideas are presented and fully explained in relation to the intentions for the staging of the entire play."),
        ]),
        C("C", "The proposed staging of one moment of the play", 8, "How performance and production elements would create tension, emotion, atmosphere and/or meaning (TEAM) in one chosen moment, linked to the stated intentions.", [
            ("1-2", "A moment is identified; performance and production elements are listed."),
            ("3-4", "The student outlines how performance elements would create TEAM in the chosen moment."),
            ("5-6", "The student explains how performance and production elements would create TEAM in the chosen moment."),
            ("7-8", "The student fully justifies how performance and production elements combine to create TEAM in the chosen moment, explicitly linked to the stated director and designer intentions."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-film-cfp",
    component="Internal Assessment",
    group="Group 6: The arts",
    subject="Film (HL)",
    task="Collaborative film project report",
    version="Guide in force (first assessment 2019)",
    levels=["HL"],
    max_marks=24,
    word_limit=2000,
    limit_note="Project report of at most 2,000 words plus a list of sources; the film itself is at most 7 minutes.",
    evidence_note="Upload the project report. Criterion A is assessed from the film and cannot be marked from the report.",
    weighting="35% at HL.",
    criteria=[
        C("A", "Demonstration of skills in one chosen film production role", 8, "Production skills evidenced in the completed film (assessed from the film).", [
            ("1-2", "Undeveloped skills; rudimentary techniques that detract from the film."), ("3-4", "Acceptable skills; some appropriate techniques that partially contribute."), ("5-6", "Clear proficiency; suitable techniques that mostly contribute to the film's effectiveness."), ("7-8", "Sophisticated proficiency; highly effective techniques that successfully contribute to the film.")], assessable=False),
        C("B", "Justification of creative work in one chosen film production role", 8, "Justification of the creative choices made in the chosen role to convey meaning during the production phases, with reference to the film.", [
            ("1-2", "Creative choices are listed with little justification or link to meaning."),
            ("3-4", "Some creative choices are described with limited justification; some links to meaning."),
            ("5-6", "Creative choices are explained and justified in relation to the intended meaning, citing relevant moments from the film."),
            ("7-8", "Creative choices are thoroughly justified in relation to meaning and the agreed intentions, with informative, precisely cited moments from the completed film."),
        ]),
        C("C", "Reflection on collaboration in the core production team", 8, "Reflection on the successes and challenges of participation in the core team and how the student's collaborations helped fulfil the group's agreed intentions.", [
            ("1-2", "A superficial or unjustified reflection; collaborations are outlined without clear links to the agreed intentions or to moments in the film."),
            ("3-4", "A useful reflection describing how the collaborations helped fulfil the agreed intentions, with some indicative moments from the film."),
            ("5-6", "A meaningful reflection explaining how the collaborations helped fulfil the agreed intentions, citing relevant moments from the film."),
            ("7-8", "An insightful reflection discussing how the collaborations helped fulfil the agreed intentions, citing informative moments from the film."),
        ]),
    ],
))

RUBRICS.append(R(
    id="ia-music-ewm",
    component="Internal Assessment",
    group="Group 6: The arts",
    subject="Music",
    task="Experimenting with music (experimentation report)",
    version="Guide in force (first assessment 2022)",
    max_marks=28,
    word_limit=1500,
    limit_note="Report of at most 1,500 words in two sections (creating, performing), each with a rationale and a commentary; plus three excerpts of creating and three of performing (5 minutes each).",
    evidence_note="Upload the written report. Criteria B and D are assessed from the audio excerpts and cannot be marked from a document.",
    weighting="30% at SL, 20% at HL.",
    criteria=[
        C("A", "Rationale and commentary for musical experiments in creating", 6, "A purposeful rationale justifying the choice of stimuli, contexts and areas of inquiry, and a commentary explaining the experimentation process and musical decision-making in creating.", [
            ("1-2", "The rationale is ineffective; the commentary outlines the process with rudimentary musical decision-making."),
            ("3-4", "The rationale is suitable; the commentary describes the process with reasonable musical decision-making."),
            ("5-6", "The rationale is purposeful; the commentary explains the process with relevant musical decision-making, clearly referenced to the excerpts."),
        ]),
        C("B", "Practical musical experiments in creating", 8, "Transformation of source material and imaginative development of ideas evidenced in the creating excerpts.", [
            ("1-2", "Source material is reproduced with little transformation."), ("3-4", "Some transformation; development is inconsistent."), ("5-6", "Source material is transformed and developed proficiently."), ("7-8", "Source material is transformed imaginatively; practical evidence of decision-making is compelling.")], assessable=False),
        C("C", "Rationale and commentary for musical experiments in performing", 6, "As criterion A, for performing.", [
            ("1-2", "The rationale is ineffective; the commentary outlines the process with rudimentary musical decision-making."),
            ("3-4", "The rationale is suitable; the commentary describes the process with reasonable musical decision-making."),
            ("5-6", "The rationale is purposeful; the commentary explains the process with relevant musical decision-making, clearly referenced to the excerpts."),
        ]),
        C("D", "Practical musical experiments in performing", 8, "Experimentation and development in performing evidenced in the performing excerpts.", [
            ("1-2", "Little experimentation; excerpts are near-identical."), ("3-4", "Some experimentation; development is inconsistent."), ("5-6", "Proficient experimentation with evident decision-making."), ("7-8", "Imaginative, accomplished experimentation with compelling evidence of decision-making.")], assessable=False),
    ],
))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RUBRIC_INDEX = {r["id"]: r for r in RUBRICS}


def get_rubric(rubric_id: str) -> dict[str, Any] | None:
    return RUBRIC_INDEX.get(rubric_id)


def resolve_rubric(rubric: dict[str, Any], level: str | None) -> dict[str, Any]:
    """Return a copy of the rubric with criteria filtered and band text resolved for a level."""
    out = {k: v for k, v in rubric.items() if k != "criteria"}
    crits = []
    for c in rubric["criteria"]:
        if c.get("levels") and level and level not in c["levels"]:
            continue
        cc = {k: v for k, v in c.items() if k != "bands_by_level"}
        if c.get("bands_by_level") and level in c["bands_by_level"]:
            cc["bands"] = c["bands_by_level"][level]
        crits.append(cc)
    out["criteria"] = crits
    out["assessable_max"] = sum(c["max"] for c in crits if c.get("assessable", True))
    out["total_max"] = sum(c["max"] for c in crits)
    return out


def rubric_summaries() -> list[dict[str, Any]]:
    out = []
    for r in RUBRICS:
        out.append({
            "id": r["id"], "component": r["component"], "group": r["group"], "subject": r["subject"],
            "task": r["task"], "version": r["version"], "levels": r["levels"], "max_marks": r["max_marks"],
            "word_limit": r["word_limit"], "limit_note": r["limit_note"], "evidence_note": r["evidence_note"],
            "weighting": r["weighting"], "notes": r["notes"], "fidelity": r["fidelity"], "variants": r["variants"],
            "grade_bands": r.get("grade_bands"), "grade_note": r.get("grade_note"),
            "criteria": r["criteria"],
        })
    return out
