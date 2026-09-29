---
name: notebooklm-video-voiceover
description: 為既有影片或 3D 動畫製作 NotebookLM 原聲解說並依實際音訊配畫、合成與驗證。僅在使用者指定 NotebookLM 配音或保留其原聲整合時使用。
---

# NotebookLM 影片配音

以既有影像為基礎，準備可信來源，取得 NotebookLM 完成的 Audio Overview 原音，按實際內容和音長重排畫面，交付可播放的影片與明確的驗證邊界。這不是逐字稿 TTS，也不保證提示中的時長或措辭會被照做。

1. 盤點原影片、可錄製的動畫入口、使用者指定語言、交付格式及來源授權。保留原片與原聲；來源條件、數值和物理限制以本次專案規格為準，勿把案例參數固定成技能規則。先依 [來源與 Studio](references/source-and-studio.md) 審核術語、單位與可宣稱事項。
2. 優先使用使用者原本已登入的 Chrome 連接 NotebookLM；現成 `notebooklm` skill 可用時參考其 UI 操作。原 Chrome 未登入才請使用者自行登入，不碰密碼、MFA 或切換帳戶。外部上傳、回傳音檔、分享與其他帳戶動作各自核對是否落在使用者當次授權；已有精確授權不重問，回傳音檔也不是一律需確認。
3. 只用已選定且處理完成的來源生成。設定 Studio 的可用語言、形式和內容偏好，按介面狀態合理間隔追蹤，直到取得完成品或遇到時限、配額、登入等阻礙；避免短間隔無變化輪詢與重複生成。不能僅確認「開始生成」便宣稱完成；受阻時保存狀態並明列未完成。下載事件逾時時，先查既有下載檔、大小與格式，再判斷是否需要重試；勿直接重生。
4. 先確認音檔存在、非空、格式與時長，再做語意、順序、術語和限制語審核。自動轉錄可供內容核對，不能單憑辨識錯字判定實際發音。若沒有能聽音訊的能力，明說未人工聽辨。依 [媒體整合](references/media-integration.md) 以實際音長配畫；有可信句級時間戳才宣稱逐句同步，否則標示章節切點為估計並交付章節配畫。
5. 合成保留 NotebookLM 原音，不默默重配、變速、截短或使用 `-shortest`。影像不足長時先重排或重錄畫面。驗證音軌 stream-copy hash、完整解碼、metadata、章節畫面與可播放性；hash 和解碼不能代替內容 QA 或人工聽辨。回報原始輸入、產物、所做與未做的核對及剩餘限制。

需要整理來源時可複製 [來源模板](assets/source-packet-template.md)；可錄製動畫需要章節資料時可改寫 [章節模板](assets/chapters-template.json)。`scripts/media_tools.py` 提供 inspect、mux、verify，使用前讀 [媒體整合](references/media-integration.md)。
