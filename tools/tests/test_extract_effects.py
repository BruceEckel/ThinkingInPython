"""extract_effects.py claims a chapter 44 block by language and path line."""

from tools.extract import extract
from tools.extract_effects import EFFECT_LANGS, route_effects
from tools.markdown import Document


def block(text: str):
    return Document.from_text(text).blocks[0]


def test_each_effect_language_routes_under_effects() -> None:
    for lang in sorted(EFFECT_LANGS):
        doc = Document.from_text(f"```{lang}\n// {lang}/x.ext\nbody\n```\n")
        assert route_effects(doc, doc.blocks[0]) == f"effects/{lang}/x.ext"


def test_a_fragment_in_an_effect_language_is_not_claimed() -> None:
    doc = Document.from_text("```flix\ndef greet(): Unit = ()\n```\n")
    assert route_effects(doc, doc.blocks[0]) is None


def test_a_rust_or_python_block_is_left_to_the_other_extractors() -> None:
    for text in ("```rust\n// fastcount/src/lib.rs\n```\n",
                 "```python\n# rust/fastcount/demo.py\n```\n",
                 "```python\n# ask_tell.py\n```\n"):
        doc = Document.from_text(text)
        assert route_effects(doc, doc.blocks[0]) is None


def test_the_path_line_stays_in_the_extracted_file() -> None:
    doc = Document.from_text(
        "```koka\n// koka/greet.kk\nimport std/os/readline\n```\n",
        path=__import__("pathlib").Path("44_Effects--Effect_Management.md"))
    result = extract([doc], [route_effects])
    assert list(result.files) == ["effects/koka/greet.kk"]
    assert result.files["effects/koka/greet.kk"].content == (
        "// koka/greet.kk\nimport std/os/readline\n")
