"""
Rule-based resume analysis. This is the fallback used whenever no LLM API
key is configured, and it is deliberately simple, transparent, and honest
about being non-AI (see ResumeAnalysis.analysis_source).
"""
import re

SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "html",
    "css", "react", "angular", "vue", "node.js", "node", "express", "flask",
    "django", "spring", "mysql", "postgresql", "mongodb", "redis", "docker",
    "kubernetes", "aws", "azure", "gcp", "git", "linux", "rest api",
    "graphql", "machine learning", "deep learning", "data structures",
    "algorithms", "pandas", "numpy", "tensorflow", "pytorch", "excel",
    "power bi", "tableau", "figma", "agile", "scrum", "ci/cd", "testing",
]

SECTION_PATTERNS = {
    "Contact Information": r"(email|phone|linkedin|github)",
    "Education": r"(education|b\.?tech|university|college|degree|cgpa|gpa)",
    "Experience": r"(experience|internship|work history|employment)",
    "Projects": r"(projects?)\b",
    "Skills": r"(skills|technologies|technical skills)",
    "Certifications": r"(certification|certificate|certified)",
    "Achievements": r"(achievements|awards|honors)",
}

WEAK_VERB_PATTERNS = [
    r"\bresponsible for\b", r"\bworked on\b", r"\bhelped with\b", r"\btasked with\b",
]

STRONG_ACTION_VERBS = [
    "built", "developed", "designed", "implemented", "led", "created",
    "improved", "optimized", "launched", "automated", "reduced", "increased",
    "managed", "architected", "deployed",
]


def _detect_sections(text_lower):
    found = []
    for section, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, text_lower):
            found.append(section)
    return found


def _detect_skills(text_lower):
    detected = []
    for skill in SKILL_KEYWORDS:
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            detected.append(skill)
    return detected


def analyze_resume_rule_based(resume_text):
    text_lower = resume_text.lower()
    word_count = len(resume_text.split())

    sections = _detect_sections(text_lower)
    skills = _detect_skills(text_lower)

    strengths = []
    weaknesses = []
    suggestions = []

    # --- Length checks ---
    if 250 <= word_count <= 900:
        strengths.append("Resume length is within a reasonable range.")
    elif word_count < 250:
        weaknesses.append("Resume seems too short to fully showcase your experience.")
        suggestions.append("Add more detail about your projects, skills, and achievements.")
    else:
        weaknesses.append("Resume seems long; recruiters often skim in under a minute.")
        suggestions.append("Trim less relevant content and keep it to 1-2 pages.")

    # --- Section checks ---
    important_sections = ["Education", "Experience", "Projects", "Skills"]
    missing_sections = [s for s in important_sections if s not in sections]
    if not missing_sections:
        strengths.append("All key resume sections were detected.")
    else:
        weaknesses.append(f"Missing or unclear section(s): {', '.join(missing_sections)}.")
        suggestions.append(f"Add clearly labeled section(s): {', '.join(missing_sections)}.")

    if "Contact Information" not in sections:
        weaknesses.append("Contact information (email/phone/LinkedIn) was not clearly detected.")
        suggestions.append("Make sure your email, phone number, and LinkedIn/GitHub are visible near the top.")

    # --- Skills ---
    if len(skills) >= 6:
        strengths.append(f"Detected a solid range of technical skills ({len(skills)} found).")
    elif len(skills) >= 1:
        weaknesses.append("Only a few recognizable technical skills were detected.")
        suggestions.append("List specific tools, languages, and frameworks relevant to your target role.")
    else:
        weaknesses.append("No common technical skills were detected.")
        suggestions.append("Add a dedicated 'Skills' section listing relevant technologies.")

    # --- Action verbs / phrasing ---
    strong_hits = sum(1 for verb in STRONG_ACTION_VERBS if verb in text_lower)
    weak_hits = sum(1 for pattern in WEAK_VERB_PATTERNS if re.search(pattern, text_lower))

    if strong_hits >= 4:
        strengths.append("Bullet points use strong action verbs (e.g. built, led, improved).")
    else:
        suggestions.append("Start bullet points with strong action verbs like 'built', 'led', or 'improved'.")

    if weak_hits > 0:
        weaknesses.append("Some phrasing uses passive language like 'responsible for'.")
        suggestions.append("Replace passive phrases (e.g. 'responsible for') with active, outcome-focused verbs.")

    # --- Numbers / quantified impact ---
    has_numbers = bool(re.search(r"\d", resume_text))
    if has_numbers:
        strengths.append("Resume includes some quantifiable details (numbers/metrics).")
    else:
        weaknesses.append("No quantifiable results or metrics were found.")
        suggestions.append("Quantify impact where possible, e.g. 'reduced load time by 30%'.")

    # --- Score calculation (heuristic, out of 100) ---
    score = 40
    score += min(len(skills), 10) * 2          # up to +20
    score += min(strong_hits, 5) * 2            # up to +10
    score += 15 if not missing_sections else 15 - (len(missing_sections) * 4)
    score += 10 if has_numbers else 0
    score += 5 if "Contact Information" in sections else 0
    score = max(0, min(100, score))

    if not strengths:
        strengths.append("Resume was successfully processed.")
    if not suggestions:
        suggestions.append("Keep refining bullet points with specific, measurable outcomes.")

    return {
        "score": score,
        "skills_detected": skills,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "sections_detected": sections,
    }
