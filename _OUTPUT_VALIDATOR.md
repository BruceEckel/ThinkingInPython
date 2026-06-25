Here's a problem I'd like to brainstorm with you.
I'd like to include validated output in the example code listings.
This way the reader can see immediately what the output is, and if the output is verified somehow then they know it's correct.

I've struggled with this problem quite a bit in the past, and have tried multiple solutions:

1. A tool that captures all the console output and automatically inserts it as a comment at the end of the file.
2. Alternative approach: If a comment starts with `##` it is an "output comment" so
   all the output up until that point is inserted using successive `##`.
   Further `##` insert all the output in between, etc.
   This output is updated and validated on each build.
   (Note that this approach ended up using a "Concrete Syntax Tree").
3. Hijacking the `print()` statement to have it capture output.
4. One thing I've thought about but haven't tried is using pytest.
   This would mean putting a function named `test_()` at the end of any example where I wanted to show and verify output.
   The `test_()` would be introduced to mean "the test for this file, to demonstrate the output"
5. I've played a little with doctest but didn't find a way that wasn't distracting
   (maybe there's a better way to use it that I don't know about).

Also it occurs to me that it might be useful to have more than one approach available.
For example, in some cases I might want to use the `##` trick, and in others use `test_()`.

I'd like your analysis and ideas about this.
