from pathlib import Path
import os

source_order = [
   "Contributors",
   "ToDo",
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

source_dir = Path.cwd().parent / "src"
dest_dir = Path.cwd().parent / "Markdown"
source_files = [source_dir / (f + ".rst") for f in source_order]
dest_files =   [dest_dir / (f + ".md") for f in source_order]
assert all([f.exists() for f in source_files])

if not dest_dir.exists():
      dest_dir.mkdir()

for rst, md in zip(source_files, dest_files):
      print(f"{rst.name}:")
      os.system(f"pandoc {rst} -o {md}")
