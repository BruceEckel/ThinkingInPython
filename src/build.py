from builder import rule
import os, shutil
# for a complete distribution build from scratch, say 'build clean package'

@rule()
def html():
    "Create html files"
    os.system("make html")

@rule("_build/htmlhelp")
def winhelp():
    "Create Windows Help file"
    os.system("make htmlhelp")
    os.chdir("_build/htmlhelp")
    os.system(r"hhc Python3PatternsIdiomsdoc.hhp")
    os.chdir("../..")

@rule()
def clean():
    "Remove files that have been built"
    os.system("make clean")
    if os.path.exists("_test"):
        shutil.rmtree("_test")
    if os.path.exists("_code"):
        shutil.rmtree("_code")

# Bug: This needs to work:
#@rule(["_build/Python3PatternsAndIdioms-html.zip",
#       "_build/Python3PatternsAndIdioms-htmlhelp.zip"], html, winhelp)

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
