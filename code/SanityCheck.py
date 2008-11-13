# SanityCheck.py
#! /usr/bin/env python
import string, glob, os
# Do not include the following in the automatic tests:
exclude = ("SanityCheck.py", "BoxObserver.py",)

def visitor(arg, dirname, names):
    dir = os.getcwd()
    os.chdir(dirname)
    try:
        pyprogs = [p for p in glob.glob('*.py') if p not in exclude ]
        if not pyprogs: return
        print('[' + os.getcwd() + ']')
        for program in pyprogs:
            print('\t', program)
            os.system("python %s > tmp" % program)
            file = open(program).read()
            output = open('tmp').read()
            # Append program output if it's not already there:
            if file.find("output = '''") == -1 and len(output) > 0:
                divider = '#' * 50 + '\n'
                file = file.replace('#' + ':~', '#<hr>\n')
                file += "output = '''\n" + open('tmp').read() + "'''\n"
                open(program,'w').write(file)
    finally:
        os.chdir(dir)

if __name__ == "__main__":
    os.path.walk('.', visitor, None)