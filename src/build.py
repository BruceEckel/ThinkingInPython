from builder import rule
import os, shutil, glob
# for a complete distribution build from scratch, say 'build clean all'

@rule()
def html():
    "Create html files"
    os.system("make html")

@rule("../winhelp")
def winhelp():
    "Create Windows Help file"
    dest = os.path.join(os.getcwd(), "..", "winhelp")
    os.system("make htmlhelp")
    os.chdir("_build/htmlhelp")
    os.system(r"hhc Python3PatternsIdiomsdoc.hhp")
    if not os.path.exists(dest):
        os.makedirs(dest)
    for f in glob.glob("Python3PatternsIdiomsdoc.*"):
        shutil.move(f, dest)
    os.chdir("../..")

@rule()
def clean():
    "Remove files that have been built"
    os.system("make clean")
    if os.path.exists("_test"):
        shutil.rmtree("_test")
    if os.path.exists("_deltas"):
        shutil.rmtree("_deltas")
    if os.path.exists("../winhelp"):
        shutil.rmtree("../winhelp")

# Bug: This needs to work:
#@rule(["../Python3PatternsAndIdioms-html.zip",
#       "../Python3PatternsAndIdioms-htmlhelp.zip"], html, winhelp)

@rule()
def code():
    "Extract code tree from book"
    os.system("python CodeManager.py extract")

@rule(None, html, winhelp, code)
def all():
    "Build both html and windows help files; extract code from book"

rule.default = all
rule.main() # Does the build, handles command-line arguments
