# SanityCheck.py
#! /usr/bin/env python
# extract: no-run  (build tool: runs every program and rewrites files)
import glob, os
# Do not include the following in the automatic tests:
exclude = ("SanityCheck.py", "BoxObserver.py")

def visit(dirname: str) -> None:
    cwd = os.getcwd()
    os.chdir(dirname)
    try:
        pyprogs = [p for p in glob.glob('*.py') if p not in exclude]
        if not pyprogs:
            return
        print('[' + os.getcwd() + ']')
        for program in pyprogs:
            print('\t', program)
            os.system("python %s > tmp" % program)
            text = open(program).read()
            output = open('tmp').read()
            # Append program output if it's not already there:
            if "output = '''" not in text and len(output) > 0:
                text = text.replace('#' + ':~', '#<hr>\n')
                text += "output = '''\n" + output + "'''\n"
                open(program, 'w').write(text)
    finally:
        os.chdir(cwd)

if __name__ == "__main__":
    for dirpath, dirnames, filenames in os.walk('.'):
        visit(dirpath)
