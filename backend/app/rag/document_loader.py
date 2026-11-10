from pathlib import Path


KNOWLEDGE_BASE_PATH = Path("data/policies/guide.md")


def load_document():
    return KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8")


def split_document(text):
    sections = text.split("\n## ")

    chunks = []

    for section in sections:
        section = section.strip()

        if section:
            chunks.append(section)

    return chunks
