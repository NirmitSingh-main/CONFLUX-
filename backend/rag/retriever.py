from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".pdf"}
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class DocumentChunk:
	chunk_id: str
	title: str
	document_type: str
	section: str | None
	page_number: int | None
	source: str
	text: str
	tokens: frozenset[str]


def _tokens(text: str) -> frozenset[str]:
	return frozenset(TOKEN_PATTERN.findall(text.lower()))


def _read_document(path: Path) -> Iterable[tuple[int | None, str]]:
	if path.suffix.lower() == ".pdf":
		try:
			from pypdf import PdfReader
		except ImportError:
			return
		reader = PdfReader(str(path))
		for page_number, page in enumerate(reader.pages, start=1):
			yield page_number, page.extract_text() or ""
		return

	yield None, path.read_text(encoding="utf-8", errors="replace")


def _chunks_for_text(text: str, max_words: int = 180) -> Iterable[tuple[str | None, str]]:
	current_section: str | None = None
	words: list[str] = []
	for line in text.splitlines():
		stripped = line.strip()
		if not stripped:
			continue
		if stripped.startswith("#"):
			current_section = stripped.lstrip("# ").strip() or current_section
			continue
		words.extend(stripped.split())
		while len(words) >= max_words:
			yield current_section, " ".join(words[:max_words])
			words = words[max_words:]
	if words:
		yield current_section, " ".join(words)


def ingest_knowledge(root: Path = KNOWLEDGE_ROOT) -> list[DocumentChunk]:
	chunks: list[DocumentChunk] = []
	if not root.exists():
		return chunks

	for path in sorted(root.rglob("*")):
		if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
			continue
		title = path.stem.replace("_", " ").replace("-", " ").title()
		document_type = path.suffix.lower().lstrip(".")
		for page_number, page_text in _read_document(path):
			for index, (section, text) in enumerate(_chunks_for_text(page_text)):
				if not text.strip():
					continue
				relative_source = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
				chunks.append(DocumentChunk(
					chunk_id=f"{relative_source}#chunk-{index + 1}",
					title=title,
					document_type=document_type,
					section=section,
					page_number=page_number,
					source=relative_source,
					text=text,
					tokens=_tokens(text),
				))
	return chunks


def _relevant_excerpt(text: str, query_tokens: frozenset[str]) -> str:
	sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]
	ranked = sorted(
		sentences,
		key=lambda sentence: len(query_tokens.intersection(_tokens(sentence))),
		reverse=True,
	)
	selected = [sentence for sentence in ranked if query_tokens.intersection(_tokens(sentence))][:2]
	return " ".join(selected)[:500] or text[:500]


def retrieve(query: str, limit: int = 4, min_score: float = 0.20) -> list[dict]:
	query_tokens = _tokens(query)
	if not query_tokens:
		return []

	scored: list[tuple[float, DocumentChunk]] = []
	for chunk in ingest_knowledge():
		overlap = query_tokens.intersection(chunk.tokens)
		if not overlap:
			continue
		score = len(overlap) / max(len(query_tokens), 1)
		if len(overlap) >= 2:
			score += 0.05
		if score >= min_score:
			scored.append((score, chunk))

	scored.sort(key=lambda item: (-item[0], item[1].chunk_id))
	return [
		{
			"chunk_id": chunk.chunk_id,
			"title": chunk.title,
			"document_type": chunk.document_type,
			"section": chunk.section,
			"page_number": chunk.page_number,
			"source": chunk.source,
			"excerpt": _relevant_excerpt(chunk.text, query_tokens),
			"relevance_score": round(score, 4),
		}
		for score, chunk in scored[:limit]
	]
