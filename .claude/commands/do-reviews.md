---
description: Apply every review file Bruce marked [[Reviewed]], deep_review first, then readability
---

Apply the review files Bruce has finished vetting. A review file is ready
when its first line is `[[Reviewed]]`; a file without that marker is still
awaiting his pass, so leave it alone. Work strictly one file at a time,
finishing each apply before starting the next, so edits cannot collide.

1. Look in `deep_review/` for unprefixed review files whose first line is
   `[[Reviewed]]`. For each one, in order:
   - Apply it following the deep-review skill's Review-file workflow:
     apply the live (`[]`) blocks, skip the `[X] Reject` blocks, run the
     chapter through the verify loop, and rename the file into its `~`
     completed series.
   - Then run the readability skill on that chapter, producing a new
     `readability/NN_name.md` review file for Bruce to vet.
2. Then look in `readability/` for unprefixed review files whose first
   line is `[[Reviewed]]`. Apply each one following the readability
   skill's applying workflow, and rename it into its `~` completed
   series. A readability review file created in step 1 has no
   `[[Reviewed]]` marker yet, so it waits for Bruce's pass rather than
   being applied in the same run.
3. Bruce may mark more files `[[Reviewed]]` while the run is in progress,
   so rescan both directories after finishing step 2. If either holds an
   unprefixed `[[Reviewed]]` file that has not been applied yet, go back
   to step 1 and work through it the same way. Repeat until a full rescan
   of both directories turns up no remaining `[[Reviewed]]` files.
4. When every file is applied, remind Bruce to run `make verify` once,
   rather than after each file.

If neither directory holds a `[[Reviewed]]` file, say so and stop.
