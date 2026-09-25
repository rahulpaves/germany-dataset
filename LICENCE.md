# Copyright and licence

Copyright (c) 2026 Pave, Dubai, United Arab Emirates.

## The data

Individual facts in this dataset (a deadline, a fee, an entry requirement) are
facts, and are not claimed as copyright.

What is claimed is the compilation: the selection of programmes and
institutions, their arrangement, the wording of every note, correction and
trap, the application and visa chains written as ordered sequences, and the
verification work behind each record. In the UK and the EU this also attracts
the sui generis database right, which covers substantial extraction or re-use
of the contents independently of copyright in any individual entry.

Subscribers may use the data in their own advising work with their own
students. They may not redistribute it, republish it in substantial part,
resell it, build a product on it, or use it as training data, without a written
agreement. Full terms: https://germany.pavetheway.ai/terms.html

## The code

The site, the build scripts, the gate and the checker in this repository are
also (c) 2026 Pave and are not licensed for re-use.

## Traceability

Responses from /api/data carry an X-Trace header: a one-way HMAC of the
requesting subscription's token, truncated to eight characters. It identifies
no person and cannot be reversed, but is stable per subscription.
