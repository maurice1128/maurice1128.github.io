# Handoff：集體苦難、信仰與教會信任

最後更新：2026-11-07。作者要從雲端工作階段轉到本地。
詳細的歷史紀錄：`HANDOFF_history_2026-11-07.md`（同一個資料夾）。

---

## 0. 給下一個工作階段（本地 Claude）的第一件事

1. 先 `git pull`，分支是 `claude/collective-suffering-faith-comparison-w15eft`。
2. 讀這份交接文件，再看 §4「進行中、尚未完成」。
3. 雲端工作階段已經直接收尾，背景工作都已停止，以下三項沒有完成，請接著做：
   - **論文初稿**：`reports/article/article_draft.md`。最後確認時寫到第 4 節，約 6,500 字。
   - **期刊研究**：`single_article_venues.md`。Studies in Christian Ethics 的投稿規範可能還沒查完。
   - **文獻探討最後一批修正**：`reports/audit/final_assembly_log.md` 的最後一段。
4. Claude Docs 是雲端文件，用 Claude Docs 連接器就能讀寫，不受影響。網址見 §2。

---

## 1. 目前的決定

- **只寫一篇論文**，英文，以台灣為焦點。原本規劃的四篇系列先保留，之後再說。
- **暫定題目**：*Who Holds the Remedy? Collective Suffering, Faith and Trust in the Church, with Reflections for the Church in Taiwan*
- **目標期刊：Studies in Christian Ethics（Sage）**
  - 等級：芬蘭 JUFO 2、挪威 2。
  - 雙盲審查，有自己的引用格式。
  - 投稿規範（Sage 鏡像頁）：https://sage.cnpereading.com/storage/ext/submission-guidelines/page/author-instructions_SCE.html
  - **字數上限、引用格式、APC 都還沒確認。** 要讀完上面那個頁面。
  - Sage 允許 AI 起草的文字，但必須申報。
  - 一般投稿應該免費；開放取用（Sage Choice）才要付 APC。這兩點都待查證。
  - 審查時間：人文期刊一般是第一次審查 3–6 個月，到刊登約 1–2 年。SCE 的實際數字待查證。
- **備選期刊**：Journal of Religious Ethics（Wiley，JUFO 3）→ Theology Today（Sage）或 Practical Theology（T&F）。
- **不要投**：
  - Past & Present：禁止 AI 生成的文字。
  - Brill／De Gruyter 的期刊（IJPT、Mission Studies 等）：不收 AI 生成的論文。
  - Journal of Asian Studies：不收主要由 AI 撰寫的稿件。
  - MDPI 的 Religions：芬蘭 JUFO 為 0 級。
- **AI 申報**：用版本 (b)，也就是「AI 起草、作者修改」，內容必須屬實。作者沒讀過的作品，不能寫「作者讀過每一部引用的作品」。各期刊的規定見 `journal_ai_policies.md`。
- **作者的分工**：作者不親自精讀；由 Claude 精讀公共領域史料和開放取用的論文。作者至少要親自核對論文中每一句直接引文，並且能為每個論點辯護。

---

## 2. 成果位置

**Claude Docs（雲端，用連接器讀寫）**
| 文件 | 網址 | 狀態 |
|---|---|---|
| 論文初稿 | https://claude.ai/artifact/G4DJj3NGdHu6pyQmpvg3Bj | 寫作中，第 5、6 節和參考文獻還沒寫 |
| 文獻探討（正文、References、Verification 三個分頁） | https://claude.ai/artifact/9d44o3yGKzh75XrxRxcArw | 完成，最後一批小修正可能還在進行 |
| 期刊系列計畫 | https://claude.ai/artifact/M44yHzuL9fUYK8gfTrzrPu | 完成，最上面記錄了「只寫一篇」的決定 |

Claude Docs 的 ID：
- 論文初稿：project `79ebe511-fcfc-4590-9dcb-785208d07bfe`，prose 節點 `4a940eda-1946`。未完成區塊的 ID 是 `mqaedx4y3hs.33`（第 5 節）、`.34`（第 6 節）、`.35`（AI 申報與參考文獻），已寫完的區塊會被替換掉，要讀大綱確認。
- 文獻探討：project `45d1c62d-42ea-45fe-b97c-8362d45232bc`，正文節點 `fb0e3d80-fa34`。
- 計畫文件：project `a2647392-ecb0-44e2-a149-7c5f082ca44c`，節點 `3d76fd6a-8142`。

**Git repo 檔案**（都在 `/home/user/maurice1128.github.io/` 底下；本地路徑以自己 clone 的位置為準）
- 論文初稿：`reports/article/article_draft.md`
- 文獻探討各節：`reports/sections/*.md`，參考文獻是同名的 `*_refs.md`。
  - 章節編號以文件裡的為準：檔名保留舊編號，但內文標題已經改成 1–20 的新編號。
  - 對照表：`reports/audit/final_assembly_log.md`。
- 參考文獻總表：`reports/references_master.md`，共 1,072 部作品。查核狀態在 `reports/audit/references_status.tsv`，摘要在 `references_summary.md`。
- 研究筆記：`research_notes/Collective suffering and Christian faith/`
  - 期刊：`journal_rankings.md`、`journal_ai_policies.md`、`single_article_venues.md`
  - 神學院：`seminary_application.md`
  - 撞題檢查：`novelty_prior_art.md`
- 全文精讀筆記：`research_notes/.../reading/`，引文都附頁碼。
  - `black_death_primary_fulltext.md`：黑死病一手史料 15 部。
  - `slavery_primary_fulltext.md`：奴隸宗教史料 12 部，外加 51 份 WPA 訪談編碼。
  - `open_access_studies_fulltext.md`：開放取用研究 11 篇。
- 四篇系列的設計書：`reports/design/article_1.md`～`article_4.md`、`conferences_timeline.md`
- 查核報告：`reports/audit/audit_*.md`，每份最後都有「Fixes applied」。
- 寫作規範：`reports/sections/_WRITER_BRIEF.md`、`_DESIGN_BRIEF.md`、`reports/audit/_FIXER_BRIEF.md`
- 書目自動比對程式：原本在雲端暫存資料夾，已經不在了。需要時依 `reports/audit/*_refcheck.tsv` 的格式重寫即可（Crossref、Open Library、LoC）。

---

## 3. 研究的核心內容

**論點**：集體苦難很少讓基督徒遠離神。它會讓虔誠轉向掌握補救之道、並且實際提供照顧的那個群體。

**條件（7 個）**
1. 受苦者的權力位置
2. 加害者的宗教
3. 苦難的神學詮釋，以及補救之道由誰掌控
4. 教會的角色，包括是否實際提供照顧
5. 有沒有可以轉投的團體
6. 苦難持續多久、是否反覆發生
7. 信仰的世代傳承需要群體

**結果（A–F）**
- A：信仰和教會一起上升
- B：虔誠在教會內部重新分配
- C：流向受苦者自己掌控的群體
- D：拒絕基督教
- E：功能被國家或醫學取代
- F：教會自我修正（使徒行傳 6 章）
- 另有一支少數：失去信仰

**避免循環論證**：教會角色要用跟結果無關的五個指標判定：誰任命神職、誰擁有財產、誰主持聖禮、誰掌控經費、誰提供照顧。

**對立解釋**
- 得到解放：最強的對手，以 Fountain 2010 為代表
- 危機過後虔誠就退了（li Muisis in Lemaître 1906, 258）
- 救濟換信徒：Madsen 反對這種純物質的解讀
- 政治立場
- 人口組成
- 功能被取代

**最接近的前人研究**：Weber、Martin 1978、Casanova 1994、Belloc et al. 2016、Bottan & Perez-Truglia 2015、Ishchuk 2026（只在概念上區分），以及三篇大學部論文：Zacharia 2018、Carmody 2012、Boone 2013。

**已查證的重要事實，不能寫錯**
- **Belloc et al. 2016**：主教兼掌政權的城市，地震延後了城市自治。正式出版版另外發現這些城市蓋了、裝飾了更多教堂，這只是部分支持宗教權威這條機制。「延後最多約十年」是 2014 年草稿的說法。
- **Madsen 2012**：認為天主教衰退是因為失去對美援的依賴和家長式權威，不是物質因素。第 62 頁記載傳教士擔憂「麵粉基督徒」。新教的「麵粉教」說法沒有來源。
- **長老教會的成長**：1955–65 年的倍增，早於 1971 年長老教會開始公開表態政治立場。
- **長老教會的文件日期**（依官網）：1971/12/29、1975/11/18、1977/8/16、1989 年 228 牧函、1990/2/9 道歉（同時向神和受難者）、2014/6/10 牧函。
- **克萊孟六世**：譴責鞭笞者的教諭是 1349/10/20，Raynaldus 1880 收錄的抄本以 *Molesta nobis* 開頭；「Inter sollicitudines」這個名稱查不到。保護猶太人的兩份教諭是 1348/7/4 和 9/26。
- **Ralph of Shrewsbury**：1349/1/10 的告解許可，全文在 Wilkins 1737, 2:745–46。
- **Robinson 2019**：刊在 *Archives* 54/2。
- **Dittmar & Meisenzahl 2020**：瘟疫使城市採行新教教會條例的機率增加 11–14 個百分點（基準 14），測的是條例的採行，不是有人退出教會。
- **Jedwab et al. 2019**：死亡率越高的城市迫害反而越少，但整體上迫害增加了。
- **Bottan & Perez-Truglia 2015**：分析單位是郵遞區號和郡；「捐款」指的是全部慈善捐款。
- **Fountain 2010**：史料比較能支持「戰後大量轉入黑人自主的教會」，而不是「首次大規模皈依」。
- **WPA 訪談**：51 份中有 26 份提到解放前黑人主導的敬拜，但其中 9 份是刻意挑選的；系統抽樣的部分是 42 份中 19 份。
- **台灣社會變遷調查的信任題**：高度信任從 2009 年 21.5% 降到 2018 年 10.7%，不信任從 16.0% 升到 26.9%。數字未加權，而且題目問的是所有宗教的團體。2018 年反對宗教領袖談政治的比例是 67.6%。

---

## 4. 進行中、尚未完成（下一個工作階段從這裡開始）

1. **完成論文初稿**
   - 第 5 節：給台灣教會的反思，約 1,800 字。要以倫理學的問題意識來寫，對爭議議題保持中立。
   - 第 6 節：限制與結論，約 500 字。
   - AI 申報（版本 b）和參考文獻：只從 `references_master.md` 取。
   - 先確認雲端的寫作線是否已經寫完：讀 Claude Doc 的大綱，看還有沒有 pending 區塊。
2. **查核論文初稿**：每一句直接引文對照精讀筆記和頁碼，數字對照各節，引用對照總表。查核員要另外找人，不能由寫作者自己查。
3. **讀完 SCE 的投稿規範**，然後調整：
   - 字數
   - 引用格式（SCE 有自己的格式）
   - 匿名化
   - 摘要和關鍵字
4. **給作者一份引文核對清單**：每句引文附出處和頁碼。
5. **文獻探討最後一批修正**，看 `final_assembly_log.md` 有沒有寫完：
   - Madsen 的引用
   - 麵粉教
   - 韓國案例的分類代號
   - Bentzen 的措辭
   - Ishchuk 的說法
   - RRCS 改成「高風險」
   - Chaves 移除待查標記

---

## 5. 作者要親自做的事（有截止日的排前面）

- [ ] **政大宗教所碩士考試入學**（如果要報）：報名期間 2026/11/24–12/8，**繳費帳號必須在 12/8 中午 12:00 前取得**，報名費 NT$1,300。筆試 2027/2/1，面試資料 2027/3/2 17:00 前上傳，面試 2027/3/8，名額 3 名。
- [ ] **其他學校的截止日**：Harvard GSAS、普林斯頓神學院博士班、Emory、香港中文大學都是 12/1；Cambridge 獎學金 12/8；UChicago 碩士第二輪 2027/4/5。
- [ ] **申請文件必須本人撰寫**：Cambridge 連英文潤飾都禁止用 AI，Harvard 也禁止。
- [ ] **撞題確認**：用學校帳號查 JSTOR、ProQuest 學位論文、ATLA、華藝、知網。檢索字串見文獻探討的 Verification 分頁，或 `reports/sections/19_novelty.md`。
- [ ] **未核實的 2 部中文作品**：陳南州 2003《認同的神學》、羅光喜 2018《台灣建國神學》。另有 111 筆細節待查，清單在 `references_summary.md`。
- [ ] **投稿前**：
  - 親自核對每一句直接引文
  - 確認 AI 申報內容屬實
  - 問學校圖書館陽明交大有沒有 Sage 的開放取用協議

---

## 6. 查核紀錄摘要

- 共 10 組獨立查核，加上書目自動比對、全文精讀和兩輪 deep-research 事實查核。
- **沒有發現任何捏造的作品或經文。** 每一組都抓到張冠李戴、描述不精確或書目錯誤，全部已修正。修正明細在各查核報告的「Fixes applied」和文獻探討的 Verification 分頁。
- 最常見的錯誤是把學者的論點說錯，或說得太強。例如 Steinmetz 原本被寫反、Belloc 被說過頭、Madsen 被誤讀。寫論文時這類錯誤最要小心。
