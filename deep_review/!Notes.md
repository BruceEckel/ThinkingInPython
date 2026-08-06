Only done through 34 because I'm not finished with the "humanizer" chapters

Chapters 28 have the highest-value proposals.



--------------------
(done)
Add to deep-review skill:

All review files are placed in a directory called deep_review.
If creating a new 'deep_review' directory, add a file named '!Notes.md'. This is for the human to use, do not assume it contains instructions for Claude.
Each review file has the same name as the Chapters file that it reviewed.
Review files contain information to be human-checked/modified.
The human leaves things in that will be performed, and removes those that shouldn't be performed.
When the human finishes editing, they hand the file back to Claude with an instruction such as:
'do deep_review/NN_chaptername.md'
The instructions within the review file include:
"When this file has been applied, change this file's name so it has a leading '~' to indicate completion."
