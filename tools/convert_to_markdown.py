from pathlib import Path
import os
import shutil


def main():
    source_dir = Path.cwd().parent / "src"
    temp_dir = Path.cwd().parent / "temp"
    dest_dir = Path.cwd().parent / "Markdown"

    def source_file(f): return source_dir / (f + ".rst")

    def pre_converted(f): return temp_dir / (f + ".rst")

    def converted(f): return temp_dir / (f + ".md")

    def destination(f, n): return dest_dir / ("%02d_" % n + f + ".md")
    assert all([source_file(f).exists() for f in source_order])
    all_files = [
        (source_file(f), pre_converted(f), converted(f), destination(f, n), n)
        for n, f in enumerate(source_order)
    ]

    create_clean_dir(temp_dir)
    create_clean_dir(dest_dir)
    for rst, pre, conv, md, n in all_files:
        print(f"{rst.name} -> {md.name}:")
        pre_convert(rst, pre)
        os.system(f"pandoc {pre} -o {conv}")
        post_convert(conv, md)
        if n > -1:
            os.system(f"subl {md}")


source_order = [
    "Contributors",
    # "ToDo",
    "NoteToReaders",
    "Introduction",
    "TeachingSupport",
    "Rules",
    # "DeveloperGuide",
    "Part1",
    "PythonForProgrammers",
    "InitializationAndCleanup",
    "UnitTesting",
    "LanguageChanges",
    "PythonDecorators",
    "Metaprogramming",
    "GeneratorsIterators",
    "Comprehensions",
    "CoroutinesAndConcurrency",
    "Jython",
    "Part2",
    "MachineDiscovery",
    "CanonicalScript",
    "Messenger",
    "Part3",
    "PatternConcept",
    "Singleton",
    "AppFrameworks",
    "Fronting",
    "StateMachine",
    "Decorator",
    "Iterators",
    "Factory",
    "FunctionObjects",
    "ChangeInterface",
    "TableDriven",
    "Observer",
    "MultipleDispatching",
    "Visitor",
    "PatternRefactoring",
    "Projects",
]


def create_clean_dir(d):
    "Ensure empty directory exists"
    if d.exists():
        try:
            shutil.rmtree(str(d))
        except Exception as e:
            print(f"""Removal failed: {d}
                  Are you inside that directory, or using a file inside it?
                  """)
            print(e)
    d.mkdir()


def pre_convert(rst, pre):
    lines = rst.read_text().splitlines()
    lines = [ln[3:] if ln.startswith(".. ") else ln for ln in lines]
    pre.write_text("\n".join(lines))


def adjust_all_listings(lines):
    n = 1
    while(n < len(lines)):
        # Must be blank line followed by 4-space indented line:
        if lines[n - 1].strip() == "" and lines[n].startswith("    #"):
            # print(f"Listing: {lines[n]}")
            n, lines = adjust_listing(n, lines)
        n += 1
    return lines


def adjust_listing(n, lines):
    result = ["```python"]

    def finish(n, i):
        # Strip trailing blank lines:
        nonlocal result, lines
        result = "\n".join(result).strip().splitlines()
        result.append("```\n")
        # print("\n".join(result))
        lines[n:i] = result
        return i, lines

    # print(f"S{n}: {lines[n]}")
    for i, line in enumerate(lines[n:], n):
        # print(f"> {i}: {line}")
        if line.startswith("    "):
            result.append(line[4:])
        elif line.strip() == "":
            result.append(line)
        else:
            return finish(n, i)
    else:
        return finish(n, i)


def post_convert(conv, md):
    "Fix up markdown produced by Pandoc transformation from restructured text"
    lines = conv.read_text().splitlines()

    def replace(old, new):
        nonlocal lines
        lines = [ln.replace(old, new) for ln in lines]
    replace("\t", "    ")
    lines = adjust_all_listings(lines)
    replace("\_", "_")
    replace("**", "`")
    replace(r"\[\[", "{{")
    replace(r"\]\]", "}}")
    replace(r"( )", "()")
    md.write_text("\n".join(lines))


if __name__ == '__main__':
    main()
