# Handoff：集體苦難、信仰與教會信任

最後更新：2026-11-11。作者要從雲端工作階段轉到本地。
詳細的歷史紀錄：`HANDOFF_history_2026-11-07.md`（同一個資料夾）。

---

## ◆ 雲端工作階段已結束（2026-11-11）。作者已轉到本地，從這裡接手
雲端的修訂稿和人工驗證工具包做到一半就停了，所以目前的狀態是：

**已完成、可以直接用**
- SSH 稿第一版：`reports/article/ssh/`
  - manuscript_ssh.md、tables_ssh.md、supplement_ssh.md、title_page_ssh.md、bio_note_ssh.md、cover_letter_ssh.md
  - author_notes_ssh.md：列出 38 部沒有人讀過全文的著作、引文核對表。
- 兩份審查報告：
  - `reports/article/ssh/audit_ssh.md`：獨立查核，最後有依優先順序排列的修正清單。
  - `reports/article/ssh/mock_review_ssh.md`：模擬審稿，最後有 Revision plan，分成 (a) 現在能做、(b) 需要讀文獻、(c) 需要人做。
- 三份資料集和分析：`evidence/{husting_wills,gild_foundations,wpa_religion}/`
- 轉檔與字數工具：`reports/article/ssh/build/`
  - build_docx.py：輸出到 `../submission/`
  - wordcount.py

**做到一半，要注意**
- **倫敦遺囑的資料檔處於中間狀態：**
  - `data.csv` 已經套用 17 筆更正，明細在 `corrections.csv`。主要是埋葬地點的判定規則修正。
  - `analysis.py` 和 `results.md` 還沒重跑。**論文、表格、results.md 裡的數字，對應的是更正前的 `data_v1_as_analysed.csv`。**
  - 下一步：重跑 analysis.py，把 results.md、tables_ssh.md、manuscript_ssh.md 的數字全部更新。同時把 1349 年單獨分期：1320–48／1349／1350–60／1361–75／1376–1400。
- **人工驗證工具包還沒產出：** `reports/article/ssh/human_validation/` 不存在。規格如下：
  - WPA：從已編碼的訪談抽 60 份，再從被關鍵字篩掉的訪談抽 20 份。
  - 遺囑：100 份。
  - 兄弟會：60 個。
  - 各附一個「最低版本」的子樣本。
  - Excel 編碼表不能含模型的編碼。
  - 附中文編碼說明。
  - score_validation.py：計算人與模型的 kappa、precision、recall。
- **修訂稿還沒動到論文本身。** 要做的修訂如下，照 audit_ssh.md 和 mock_review_ssh.md 的 (a) 部分：
  1. 重做遺囑分析，把 1349 年單獨分出來。
  2. 類型學改成「條件」和「反應」用不同的資料判定，補上各團體 × 各時期的矩陣，並改稱「提出的類型學」。
  3. G1–G3 改寫成命題 P1–P3；G4、G5 降為留待研究的問題。1794 年那句「old proverb」講的是黑人護士被忽視，不能當作「虔誠消退」的證據。
  4. 拿掉影子案例表的 Panel B、台灣那一段和註腳 5。
  5. 案例設計：
     - 說明為什麼把瘟疫和奴隸制放在一起比較。
     - 歐陸文本只當背景。
     - 美國案例要分開主人、州法、宗派三個層次。
     - Edenton 拆毀教堂的是奴隸主。
  6. WPA：
     - 加做排除德州的穩健性檢查。
     - 交代訂定類別時用過的 51 份前導樣本。
     - 修正兩處行號：Mathews 是 2120–21，Davis 是 7131–33。
  7. 統計：
     - 寫明分母。
     - 完整母體不做檢定。
     - 兄弟會依地點群聚。
     - 標明未做多重比較校正。
  8. 方法揭露：
     - 編碼由語言模型完成。
     - 翻譯有 AI 協助。
     - 拿掉不屬實的「I read」。
     - 留下 [[HUMAN VALIDATION: …]] 佔位。

**只有作者能做的三件事，沒做不能投稿**
1. 人工驗證編碼，最好再找第二個人一起做。
2. 填 AI 申報的工具名稱、版本、日期。
3. 取得並閱讀專門史學著作。在本地用 Chrome 加學校帳號，可以交給本地 Claude 讀，但論文裡不能宣稱作者讀過。

## ★★★ 現況（2026-11-11 深夜）：SSH 稿第一版經模擬審稿判定「目前不能投」，修訂中
- **模擬審稿**（`reports/article/ssh/mock_review_ssh.md`）：三位審稿人的意見分別是大修、拒絕、大修，編輯的決定是「以目前形式拒絕，歡迎重投」。
- **獨立查核**（`reports/article/ssh/audit_ssh.md`）：
  - 約 780 個數值，除少數幾處外都和程式輸出一致；66 筆文獻都存在；引文正確。
  - 推論有 6 處說過頭。最嚴重的是判定指標和反應用了同一批數字，構成循環論證。
- **三個只有人能解決的阻礙，沒解決就不能投稿：**
  1. **人工驗證編碼。** 審稿人要求由人獨立編碼一部分樣本，和模型的編碼比對。驗證工具包正在做，位置在 `reports/article/ssh/human_validation/`，內含中文說明、Excel 編碼表、計分程式。有「最低版本」和「完整版本」兩種。作者要親自做，最好再找一個人一起做。
  2. **AI 申報的工具名稱、版本、使用日期。** 作者要填實際的資料。
  3. **閱讀專門史學著作。** 有 38 部引用的二手著作，沒有人讀過全文。優先閱讀清單會放在 `author_notes_ssh.md`。作者在本地用學校帳號取得後，可以交給本地 Claude 讀，但論文裡不能宣稱作者讀過。
- **正在修訂（Claude 可以做的部分）：**
  - 遺囑分析改把 1349 年單獨分出來。初步看，1349 年的遺囑像瘟疫前的樣子，跳升出現在 1350–57 年，1361 年沒有明顯跳升。這會改變原本「第二波瘟疫後上升」的說法。
  - 類型學改成條件和反應分開判定，並改稱「提出的類型學」。
  - G1–G3 改寫成命題 P1–P3；G4、G5 降為留待研究的問題。
  - 影子案例和台灣從論證中移除。
  - WPA 加做排除德州的穩健性檢查。
  - 統計描述修正。

## ★★ 目前方向（2026-11-11 晚，作者決定）：改投 Social Science History
- **作者指示：**「Social Science History，丟這」，全力做這一篇。
- **改投的理由：**
  - 作者要的是歷史考據加歸納。
  - 模擬審稿（`reports/article/mock_review.md`）認為 SCE 那一稿「大幅修改，有一半機會直接退稿」，因為 SCE 要倫理學論證，而且會要求刪掉量化附錄。
  - 我們自己編碼的三份資料集，在社會科學史期刊可以當論文主體。
- **SSH 的投稿規範**（已查證）：`reports/article/_SSH_GUIDELINES.md`
  - 上限 12,000 字，含註腳和參考文獻；摘要 250 字以內。
  - author-date 引用（Chicago 18 版），美式拼字。
  - 雙盲審查；表格另外交檔。
  - 一般刊登不收費。
  - 用 AI 產生文字或分析資料都要申報：文字的部分放致謝或註腳，分析的部分放方法節。
  - 投稿系統：Editorial Manager，https://www.editorialmanager.com/ssha/default.aspx
- **稿件位置：** `reports/article/ssh/`，寫作中。
  - manuscript_ssh.md、tables_ssh.md、title_page_ssh.md、bio_note_ssh.md、supplement_ssh.md
  - author_notes_ssh.md：給作者的開放問題和引文核對表。
- **論文設計：**
  - 性質是比較歷史的類型歸納，不做因果推論。
  - 深度案例：
    1. 瘟疫時期的英格蘭：倫敦遺囑 1,979 份、兄弟會 509 個。
    2. 美國被奴役與獲自由的基督徒：WPA 訪談 400 份，加上一手文本。
  - 影子案例：依二手研究整理成一張表，並標明證據深度。包括愛爾蘭、韓國、盧安達、巴西、Taki Onqoy、台灣長老教會。
  - 台灣只在討論裡寫一小段。
- **五條歸納（G1–G5）：**
  1. 受苦後，對信仰的需求不降反升。
  2. 人對教會的反應，隨「補救之道在誰手上、誰提供照顧」而不同。
  3. 平信徒自己接手時，教會有三種回應：下放再收回、鎮壓、吸收。
  4. 危機過後虔誠會消退，但受苦者建立的組織留了下來。
  5. 教會自我修正可以修復信任（暫定，例子很少）。
- **史學上還有的弱點**（已經向作者說明）：
  - 跨度太大。
  - 用的是摘要和轉錄本，不是原件。
  - 核心史學著作沒有讀過全文。這要靠作者在本地用 Chrome 和學校帳號補讀，清單見下。
- **SCE 那一稿**（`manuscript_sce.md`）保留作為素材；它的查核結果 `audit_manuscript.md` 還在進行中。
- **WPA 的獨立第二編碼者已經完成：** 敬拜掌控和服從講道兩個變項的 κ=1.00；其他變項 κ 在 0.64–0.85 之間。有 5 筆訪談員的種族正在更正。

## ★ 較早的方向（2026-11-11，已被上面取代）
- **改寫成倫理論文。** 作者只會讀這一篇論文，所以論點要靠神學倫理的推理撐起來。歷史只用三個場景，以一手史料的原文為主：黑死病、被奴役的基督徒、台灣長老教會。
- **歷史推論要保守：**
  - 只寫有原文支持的史實。
  - 推論要明說是詮釋，並把對立的解釋寫出來。
  - 不寫因果，例如「長老教會的立場造成了信任」這種說法不能寫。
  - 史實和推論分別有多穩固，見本次對話的評估（第一層：史實穩；第二層：推論中到弱）。
- **證據補強（雲端已經開始，進行中）：** 輸出在 `evidence/<project>/`，包括 codebook、data.csv、analysis.py、results.md。
  1. `husting_wills`：倫敦市政法庭（Court of Husting）的遺囑，1320–1400 年，比較兩波瘟疫前後的宗教捐贈去向。
  2. `gild_foundations`：英格蘭堂區兄弟會的成立年份與宗旨，依 1388–89 年的調查申報（Westlake 1919）。
  3. `wpa_religion`：WPA 前奴隸訪談全集，分層隨機抽 400 份，系統編碼。
  - 共同規範：`evidence/_EVIDENCE_BRIEF.md`。每項都要做 10% 雙重編碼並計算 kappa，表格附信賴區間，不寫因果。
  - 結果放進附錄，正文只寫結論和限制。
- **作者要辦的：** 申請 SRDA 會員，才能下載台灣社會變遷調查的原始資料做加權分析。台灣那部分的推論要靠這個補強。
- **在本地用 Chrome 讀付費文章：** 作者的 Chrome 已登入陽明交大圖書館。本地 Claude 若有 Claude in Chrome，請用它讀以下全文（只供個人研究，不得轉傳），並把重點和頁碼寫進 `reading/paywalled_fulltext.md`：
  - Cohn 1992，*The Cult of Remembrance*：查證「1363 年轉折」的說法。
  - Robinson 2019，*Archives* 54/2：神職人員招募。
  - Fountain 2010，*Slavery, Civil War, and Salvation*：方法和那個「不到四成」的數字。
  - Belloc, Drago & Galbiati 2016，QJE 正式版：「延後最多約十年」、教堂興建。
  - Madsen 2012（華藝）、邱凱莉 2021（華藝）、王梅霞 2018：台灣部分。
  - 曾慶豹 2017：黨國基督徒。
  - Raboteau 1978/2004：Invisible Institution。
  - Larkin 1972（AHR）：虔誠革命。
  - Bottan & Perez-Truglia 2015、Frick, Moser & Simmons 2021：當代教會信任。
  - Studies in Christian Ethics 投稿規範（Sage 官網），以及 2022–2026 年類似主題的文章 5–10 篇。
- **作者貼過的連結**（陽明交大 Primo，搜尋 DOI 10.1007/s12311-017-0897-y）：看起來是神經科學期刊 *The Cerebellum* 的文章，和本題無關，可能貼錯了，要跟作者確認。

- **稿件檔案（改寫中）：** 都在 `reports/article/`。
  - `manuscript_sce.md`：匿名正文
  - `title_page_sce.md`：標題頁
  - `quotation_checklist.md`：給作者核對的引文清單
  - `works_cited_check.md`
  - 舊版 `article_draft.md` 是歷史取向的寫法，只當素材用。
- **作者的指示（2026-11-11）：** 一直做到可以投稿為止。順序：
  1. 完成改寫
  2. 補上三項證據，放進附錄
  3. 獨立查核，再做一次模擬審稿
  4. 轉成 Word 檔，寫投稿信
  5. 交給作者核對引文、填個人資料

- **作者再次說明目標（2026-11-11）：** 透過歷史考據，**歸納**出人在受苦後對信仰、對教會的反應。重點是歸納，不是因果。
  - **論文結構因此調整：**
    - 前半：歷史歸納出的反應類型。
      - 深度案例 3 個：一手史料，加上自己編碼的資料（1,979 份倫敦遺囑、509 個兄弟會、400 份 WPA 訪談）。
      - 廣度案例約 15–20 個：依據二手研究，要標明這一層證據比較淺。
      - 必須包含反例：危機過後消退、拒絕、失去信仰。
      - 分類標準不能看結果來定，用那五個指標。
    - 後半：神學倫理的判準，以及給台灣教會的反思。
  - **三項證據的結論**（詳見 `evidence/*/results.md`）：
    - 倫敦遺囑：瘟疫後，捐給堂區、修會、兄弟會的遺囑都變多，沒有集中到追思彌撒。支持「在教會內重新分配」。但紀錄方式有變，不能下定論。
    - 兄弟會：只能說「1389 年還在的兄弟會，多數自稱成立於 1349 年後」，這裡有存活者偏誤。90% 由平信徒創立，自己聘神父，在堂區內運作。
    - WPA：有說明敬拜情況的訪談中，45% 提到黑人自己掌控的敬拜。這和解放前的信仰有關聯，但只算本人或親屬時就不顯著。改宗時間無法檢驗 Fountain 的論點。獨立第二編碼者的信度正在計算。

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
  - 投稿規範已查證（2026-11-11，依 Sage 鏡像頁；官網當時回 403，投稿前要再對一次）。整理在 `reports/article/_SCE_GUIDELINES.md`：
    - **投稿和刊登都不收費**；開放取用（Sage Choice）是自選的。
    - 雙盲審查，兩位審稿人；可能直接被編輯退稿。
    - 摘要 150–200 字，關鍵字 4–6 個。
    - **用註腳，期刊有自己的格式**，不是 author-date。
    - 英式拼字，用 -ise；引文用單引號。
    - 頁面沒寫字數上限、審查時間。
    - 投稿系統：https://mc.manuscriptcentral.com/sce
    - 要交兩份：完全匿名的正文，和另一份標題頁（含各項聲明、AI 申報）。
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
