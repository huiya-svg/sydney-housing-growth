# Decision log

Every choice that changes the results is recorded here, with who decided and why.
Interviewers ask "why did you do it this way?" — this file is the answer.

| ID | Date | Decision | Options considered | Chosen | Why | Decided by |
|---|---|---|---|---|---|---|
| D01 | 2026-11-25 | Houses and units measured separately | Combined / separate | Separate | Mix shift between dwelling types distorts a combined median | Kang (project plan) |
| D02 | 2026-11-25 | Growth definition | Single quarter vs 4-quarter average | Avg of 2019's four quarters → avg of latest four quarters | Smooths noisy single-quarter medians | Kang (project plan) |
| D03 | 2026-11-25 | Who commits | Agent / owner | Owner (Kang) commits after each review | Clean, owned commit history | Kang |
| D04 | _pending_ | Which LGAs count as "Greater Sydney" | (a) DCJ's own 34 LGAs, incl. Central Coast; (b) 33 metro LGAs, excl. Central Coast | _pending_ — Claude recommends (a): matches DCJ's published Greater Sydney row and its Inner/Middle/Outer ring labels, so no averaging of medians and no hand-made regions | | Kang |
| D05 | _pending_ | Wollondilly units: no published 2019 median (all four quarters absent or suppressed) | (a) exclude Wollondilly from unit rankings only; (b) use a later baseline for Wollondilly | _pending_ — Claude recommends (a): a different baseline breaks comparability; state it in Limitations | | Kang |
| D06 | _pending_ | Later issues revise the previous quarter | (a) use each quarter as first published; (b) back out revised values from the change columns | _pending_ — Claude recommends (a), with T03 measuring revision size for medians | | Kang |
