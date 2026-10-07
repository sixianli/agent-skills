# Verification evidence

Application-specific transcripts, reports and data inventories are kept in local ignored storage. They are not reusable fixtures and are not distributed with this package.

Run `python3 -m unittest discover -s shoshin/tests -v` for the deterministic helper checks, and `python3 shoshin/scripts/validate-skills.py` for resources and declared references. Full repository checks run through `python3 scripts/validate_all.py`. These commands do not prove unexecuted model behavior or installation on another host.
