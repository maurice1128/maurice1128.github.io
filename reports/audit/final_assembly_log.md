# Final assembly log

Doc: 45d1c62d-42ea-45fe-b97c-8362d45232bc (https://claude.ai/artifact/9d44o3yGKzh75XrxRxcArw), main tab body fb0e3d80-fa34.
Started 2026-11-05. Starting doc rev: 253.

## Step 1: citation-key fixes

### Section files (reports/sections/*.md)
Applied with scratchpad script keyfix.py (old -> new, count):
- 10ol: Joseph ha-Kohen 1981 -> Almbladh 1981 (2)
- 12: Dyson 1998 -> Augustine of Hippo 1998 (2); Watson and Jenkins 2006 -> Julian of Norwich (2006)/Julian of Norwich 2006 (2); Dols 1974 -> 1974b (4); Thornton 1998 -> 1998b (2); Raynaldus 1872 -> 1880 (1)
- 07: Foreign Policy 2014 -> Caryl 2014 (2); Christianity Today 2011 -> Newhouse 2011 (2); Stern 1982 -> 1982b (2); van 't Spijker n.d. -> 2004 (1)
- 09: Chiu Yun-fang 2014 -> 2013 (1); (Chen 2003) -> (Chen Nan-jou 2003 *[unverified]*); (Lo 2018) -> (Lo Kuang-hsi 2018 *[unverified]*)
- 06: CIASE 2021 -> 2021a (2); Pew Research Center 2021 -> 2021c (2). Kim and Kim 2014 already correct in file.
- 16c: CIASE 2021 -> 2021b (1)
- 03: CTC-CCA 1983 -> 1981 (2); Jones 1973 -> Jones [1973] 1998 (3); Kitamori 1965 -> 1946 (2); Raboteau 2004 -> Raboteau [1978] 2004 (2); Raynaldus 1872 -> 1880 (1)
- 04: Dols 1974 -> 1974a (2); Raynaldus 1872 -> 1880 (7); Nodl 2021 [verify] -> Nodl 2021 (identified, see below)
- 10ol: Dols 1974 -> 1974b (2); Stern 1982 -> 1982a (2)
- 10ps: Dols 1974 -> 1974b (2); Simonsohn 1988 -> 1988–91 (2)
- 05: Reis [1991] 2003 -> Reis 1991; Reis [1986] 1993 -> Reis 1986; Soares [2000] 2011 -> Soares 2000
- 11 (methodology): Reis 2003 -> 1991 (2); Reis 1993 -> 1986; Soares 2011 -> 2000 (2); Weber 1946 -> 1946b
- 08: Runge 1969 -> Runge 1900; Soares ([2000] 2011) -> Soares (2000)
- 15: Raynaldus -> 1880; Reis -> 1991; Stern -> 1982b (Taki Onqoy, follows sec. 07); Weber 1946 -> 1946b
- 02: Weber 1946 -> 1946a (5); 19: Weber 1946 -> 1946b (3); 20: Weber 1946 -> 1946b (3)
- Boone 2013 and Kim and Kim 2014 were already correct in the files.
- PCT and CTC-CCA kept as in-text abbreviations (defined in the text); "See" cross-references added to references_master.md: "CTC-CCA. See Commission on Theological Concerns…" and "PCT. See Presbyterian Church in Taiwan."

### Nodl 2021: identified
Crossref (query author Nodl, plague Bohemia): Nodl, Martin. 2021. "Impacts of the Plague Epidemic on the Kingdom of Bohemia in the Second Half of the XIVth Century and at the Beginning of the XVth Century." Studia Historica Gedanensia 12 (2): 44–62. https://doi.org/10.4467/23916001HG.21.004.14986. Its abstract states that Czech debate concluded plague was not a significant or decisive cause of the Hussite revolution, which is exactly the claim cited in sec. 04. Citation kept, [verify] removed; master and 04 refs entry replaced; master counts now 959 verified / 111 detail pending / 2 unverified.

### Live doc (main tab)
Same changes applied in the doc (rev 253 -> 307), by find/replace ("as":"text") or by character range where the old key is a prefix of the new one (Weber 1946a/b, CIASE 2021a/b, Dols 1974a/b, Stern 1982a/b, Thornton 1998b), so formatting is untouched. Counts in the doc matched the files: Raynaldus 10, Weber 13 (5 a + 8 b), CIASE 3, bare Dols 1974 6, Stern 1982 4 (+ "Stern (1982)" 1), Thornton 1998 1.
- "[unverified]" after Chen Nan-jou 2003 and Lo Kuang-hsi 2018 inserted in italics.
- Nodl 2021: "[verify]" removed in text; its to-verify bullet now says resolved (Studia Historica Gedanensia 12 (2): 44–62).
- Checked afterwards (0 hits): "Kim and Kim 2015", "Boone n.d", "Jones 1973", "2004, 2014"; the only "1872" left is a date range in a table (US South, 1865–1872).
