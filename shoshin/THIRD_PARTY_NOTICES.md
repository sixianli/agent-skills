# Third-party notices

Shoshin adapts engineering methods from PStack 0.15.0 by Lauren Tan, licensed under MIT.
The allowed source was the local cursor-plugins/pstack directory at commit
`71ed0d1076fec562c1b74ee353121a8d00f75382` of cursor/plugins.
Upstream: https://github.com/cursor/plugins/tree/main/pstack

The 15 leaf skills, engineering-workflow entrypoint and workflow references adapt the corresponding PStack skills,
principles and Playbooks listed in the design Spec. The decision log helper adapts
`skills/show-me-your-work/scripts/log.sh`, retaining TSV control-character handling and
formula-prefix protection, and adding existing-header validation, empty-file handling, line separation and TSV quote escaping.
Shoshin's package validator and its tests are new code.

Each installable skill carries LICENSE so a copied folder retains attribution.
Original Shoshin additions are MIT, as selected by the user on 2026-09-08.
The upstream MIT notice is reproduced below without alteration.

MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
