import re

from docx import Document


OPTION_PATTERN = re.compile(r"^([A-D])[\.\)]\s*(.+)$", re.IGNORECASE)
INLINE_OPTIONS_PATTERN = re.compile(
    r"^A[\.\)]\s*(.+?)\s+B[\.\)]\s*(.+?)\s+C[\.\)]\s*(.+?)\s+D[\.\)]\s*(.+)$",
    re.IGNORECASE,
)
ANSWER_PATTERN = re.compile(
    r"^(answer|ans|correct)\s*[:\-]?\s*([A-D])$",
    re.IGNORECASE,
)
QUESTION_START_PATTERN = re.compile(
    r"^(?:question\s*)?(\d+)\s*[\.\):\-]\s*(.+)$",
    re.IGNORECASE,
)
ANSWER_KEY_RANGE_PATTERN = re.compile(
    r"^(?:questions?\s*[:\-]?\s*)?(\d+)\s*[-\u2013\u2014]\s*(\d+)\s*:?\s*(.*)$",
    re.IGNORECASE,
)
REQUIRED_OPTION_KEYS = ("A", "B", "C", "D")


def parse_questions_from_docx(file_path):
    document = Document(file_path)
    lines = _extract_document_lines(document)

    if not lines:
        raise ValueError("The uploaded document does not contain readable questions.")

    parsed_questions = []
    current = None
    last_option_key = None
    inside_answer_key = False
    pending_answer_numbers = []
    pending_answer_values = []
    answer_key_map = {}

    def finalize_question():
        nonlocal current, last_option_key
        if not current:
            return

        if not current["question_text"] or any(
            not current["options"].get(key) for key in REQUIRED_OPTION_KEYS
        ):
            raise ValueError(
                "Each question must have text and four options (A-D)."
            )

        parsed_questions.append(
            {
                "question_number": current["question_number"],
                "question_text": current["question_text"].strip(),
                "option_a": current["options"]["A"].strip(),
                "option_b": current["options"]["B"].strip(),
                "option_c": current["options"]["C"].strip(),
                "option_d": current["options"]["D"].strip(),
                "correct_answer": current.get("correct_answer"),
            }
        )
        current = None
        last_option_key = None

    def flush_pending_answer_range():
        nonlocal pending_answer_numbers, pending_answer_values
        if not pending_answer_numbers:
            return

        if len(pending_answer_numbers) != len(pending_answer_values):
            raise ValueError(
                "The answer key does not match the number of questions in the range."
            )

        for question_number, answer in zip(pending_answer_numbers, pending_answer_values):
            answer_key_map[question_number] = answer

        pending_answer_numbers = []
        pending_answer_values = []

    for line in lines:
        if _is_answer_key_header(line):
            finalize_question()
            flush_pending_answer_range()
            inside_answer_key = True
            continue

        if inside_answer_key:
            range_match = ANSWER_KEY_RANGE_PATTERN.match(line)
            if range_match:
                flush_pending_answer_range()
                start_number = int(range_match.group(1))
                end_number = int(range_match.group(2))
                if start_number > end_number:
                    raise ValueError("Answer key ranges must start with the smaller number.")

                pending_answer_numbers = list(range(start_number, end_number + 1))
                pending_answer_values = []

                trailing_answers = _extract_answer_tokens(range_match.group(3))
                if trailing_answers:
                    pending_answer_values.extend(trailing_answers)
                    if len(pending_answer_values) > len(pending_answer_numbers):
                        raise ValueError(
                            "The answer key contains more answers than questions in the range."
                        )
                    if len(pending_answer_values) == len(pending_answer_numbers):
                        flush_pending_answer_range()
                continue

            answer_tokens = _extract_answer_tokens(line)
            if answer_tokens:
                if not pending_answer_numbers:
                    raise ValueError(
                        "Found answer key values before a question range like 1-10."
                    )

                pending_answer_values.extend(answer_tokens)
                if len(pending_answer_values) > len(pending_answer_numbers):
                    raise ValueError(
                        "The answer key contains more answers than questions in the range."
                    )

                if len(pending_answer_values) == len(pending_answer_numbers):
                    flush_pending_answer_range()
                continue

            continue

        question_match = QUESTION_START_PATTERN.match(line)
        if question_match:
            finalize_question()
            current = {
                "question_number": int(question_match.group(1)),
                "question_text": question_match.group(2).strip(),
                "options": {},
                "correct_answer": None,
            }
            last_option_key = None
            continue

        answer_match = ANSWER_PATTERN.match(line)
        if answer_match:
            if not current:
                raise ValueError("Found an answer line before a question.")
            current["correct_answer"] = answer_match.group(2).upper()
            finalize_question()
            continue

        inline_options_match = INLINE_OPTIONS_PATTERN.match(line)
        if inline_options_match:
            if not current:
                raise ValueError("Found options before a question.")

            current["options"]["A"] = inline_options_match.group(1).strip()
            current["options"]["B"] = inline_options_match.group(2).strip()
            current["options"]["C"] = inline_options_match.group(3).strip()
            current["options"]["D"] = inline_options_match.group(4).strip()
            last_option_key = "D"
            continue

        option_match = OPTION_PATTERN.match(line)
        if option_match:
            if not current:
                raise ValueError("Found an option line before a question.")
            option_key = option_match.group(1).upper()
            current["options"][option_key] = option_match.group(2).strip()
            last_option_key = option_key
            continue

        if not current:
            continue

        if _has_all_required_options(current) and _is_metadata_heading(line):
            finalize_question()
            continue

        if last_option_key and current["options"].get(last_option_key):
            current["options"][last_option_key] = (
                f'{current["options"][last_option_key]} {line}'.strip()
            )
        else:
            current["question_text"] = f'{current["question_text"]} {line}'.strip()

    finalize_question()
    flush_pending_answer_range()
    _apply_answer_key(parsed_questions, answer_key_map)

    if not parsed_questions:
        raise ValueError("No valid questions were found in the document.")

    cleaned_questions = []
    for question in parsed_questions:
        if not question["correct_answer"]:
            raise ValueError(
                "Each question must include an ANSWER line or the document must end with an answer key section."
            )

        cleaned_questions.append(
            {
                "question_text": question["question_text"],
                "option_a": question["option_a"],
                "option_b": question["option_b"],
                "option_c": question["option_c"],
                "option_d": question["option_d"],
                "correct_answer": question["correct_answer"],
            }
        )

    return cleaned_questions


def _extract_document_lines(document):
    lines = []
    for paragraph in document.paragraphs:
        for raw_line in paragraph.text.splitlines():
            cleaned_line = " ".join(raw_line.split()).strip()
            if cleaned_line:
                lines.append(cleaned_line)
    return lines


def _has_all_required_options(question_data):
    return all(question_data["options"].get(key) for key in REQUIRED_OPTION_KEYS)


def _is_answer_key_header(line):
    normalized = re.sub(r"[^a-z]+", " ", line.lower()).strip()
    return (
        normalized in {"answer key", "answers", "answer"}
        or "answer key" in normalized
    )


def _is_metadata_heading(line):
    normalized = re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()
    if not normalized:
        return True

    return (
        normalized.startswith("part ")
        or normalized.startswith("unit ")
        or normalized.startswith("section ")
        or normalized.startswith("chapter ")
        or "answer key" in normalized
        or "mcq" in normalized
        or normalized.endswith(" test")
    )


def _extract_answer_tokens(line):
    tokens = re.findall(r"[A-D]", line, re.IGNORECASE)
    if not tokens:
        return []

    remainder = re.sub(r"[A-D,\s]", "", line, flags=re.IGNORECASE)
    if remainder:
        return []

    return [token.upper() for token in tokens]


def _apply_answer_key(parsed_questions, answer_key_map):
    for question in parsed_questions:
        mapped_answer = answer_key_map.get(question["question_number"])
        if question["correct_answer"] and mapped_answer and question["correct_answer"] != mapped_answer:
            raise ValueError(
                f"Question {question['question_number']} has conflicting answers in the question block and answer key."
            )

        if not question["correct_answer"] and mapped_answer:
            question["correct_answer"] = mapped_answer
