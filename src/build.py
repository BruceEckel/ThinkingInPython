from builder import rule
import os, shutil, glob
# for a complete distribution build from scratch, say 'build clean package'

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
    if os.path.exists("_code"):
        shutil.rmtree("_code")
    if os.path.exists("../winhelp"):
        shutil.rmtree("../winhelp")


# Bug: This needs to work:
#@rule(["../Python3PatternsAndIdioms-html.zip",
#       "../Python3PatternsAndIdioms-htmlhelp.zip"], html, winhelp)

@rule(None, html, winhelp)
def package():
    "Create Zip files for upload to BitBucket; for end-user downloads"
    os.chdir("_build")
    os.system("zip -r ../../Python3PatternsAndIdioms-html.zip html")
    os.system("zip -r ../../Python3PatternsAndIdioms-htmlhelp.zip htmlhelp/Python3PatternsIdiomsdoc.*")
    os.chdir("..")

@rule(None, html, winhelp)
def all():
    "Build both html and windows help files"

rule.default = all
rule.main() # Does the build, handles command-line arguments
