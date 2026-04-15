Load cached review, apply fixes, re-validate, and update the document.

Steps:
1. Check if `meta/session/review-cache/<filename>.review.md` exists
2. If it exists, read it as the issue list
3. If it does not exist, perform the review internally first (following review-protocol.md)
4. Apply all required fixes to the document
5. Re-validate with `meta/standards/validation/docs-checklist.md`
6. If validation passes:
   a. Write the corrected document to the target path
   b. Delete `meta/session/review-cache/<filename>.review.md` if it exists
   c. Update `meta/session/PROJECT_STATUS.md`
7. If validation fails, report remaining issues and do not delete the cache file
