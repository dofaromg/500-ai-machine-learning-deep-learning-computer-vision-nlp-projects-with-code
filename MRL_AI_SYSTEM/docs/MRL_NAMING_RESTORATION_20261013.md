# MRL identity restoration — 2026-10-13

origin_signature: MrLiouWord
canonical_authority: Mr.liou

Root instruction: 「我們的命名名稱MRL都被拿掉，幫我把他改回來，然後找出問題出在哪裡」 (2026-10-13, Asia/Taipei).

## Confirmed causes
- PR #6 (merged 2026-07-13T20:33:57Z) explicitly replaced MrLiouWord with MrliouAI across runtime identities, forwarded headers, manifests, tests and documentation: `https://github.com/dofaromg/500-ai-machine-learning-deep-learning-computer-vision-nlp-projects-with-code/pull/6`
- It also rewrote historical claude/ branch names in both 2026-05-31 delivery manifests. A product label is not historical provenance.
- PR #11 (merged 2026-10-13T09:04:39Z) continued the replacement in naming law and ten identity occurrences: `https://github.com/dofaromg/500-ai-machine-learning-deep-learning-computer-vision-nlp-projects-with-code/pull/11`
- Central policy commit ed66662cbf3a422f7435a24331cedf2ac95d2d70 restricts public MRL naming. It separately states MrLiouWord remains an origin signature. Thus PR #6's runtime rename is incompatible even with that policy's identity-preservation provision.
- Platform attribution and GitHub account metadata identify execution and merge actors; they do not establish motive or the complete original authorization conversation.

## Restoration
41 existing files: restore 80 MrliouAI substitutions to MrLiouWord in the traced change scope, including runtime responses, request headers, trace defaults, boot manifest, registry, naming law, tests and source headers.
Restore actual claude/memory-system-rules-prep-EuBXH historical branch names in both delivery manifests.
Preserve MRL paths, timestamps, versions, functionality and Git history; this correction is a new commit.
Keep products and origin in distinct fields. MRL/MRL_ remain native names; product branding cannot rename origin_signature.

## Verification
check_mrl_origin.py checks all 41 paths, signature retention, boot origin, relay namespace and historical branch references. Four regression cases reject identity substitution, deletion and historical branch rewriting.
Existing CI test-collection and secret-scanner findings are independent and remain unresolved by this identity-only patch.
