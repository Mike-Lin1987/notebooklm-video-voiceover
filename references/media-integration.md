# 依原音配畫與合成

先用 `python scripts/media_tools.py inspect AUDIO` 讀音軌格式、時長及大小。根據實際語句順序與音長規劃章節。語意切點只有在語句及其時間位置同時有證據時才標為「已核對」，例如可信帶時間轉錄經抽查，或人工聽辨同步對照。播放器時間、波形停頓只能證明時間或停頓位置，據此安排的語意切點仍屬「估計」。沒有句級證據也可交付章節配畫，清楚註明非逐句同步。

既有影片可剪接、延長有意義的畫面；3D 動畫可用專案既有錄製 API 或 renderer 重錄。先使影像至少覆蓋完整原聲；不要為了貼合音長加速或截短音訊。記錄原片和原音路徑、版本與輸出。章節模板只是可改寫的資料示例，不指定 renderer。

`python scripts/media_tools.py mux VIDEO AUDIO OUTPUT.mp4 [--ffmpeg PATH] [--ffprobe PATH]` 僅接受已準備好的 H.264 MP4 影像與 AAC 原聲、近零 stream 起點，且影像長度足夠。會拒絕覆寫輸出或輸入輸出同一路徑。其他 codec 或非近零時間軸應先另行準備；不得默默轉碼。FFmpeg 合成等效於 `-map 0:v:0 -map 1:a:0 -c:v copy -c:a copy`，沒有 `-shortest`。

若合成工具失敗，檢查輸出位置是否留下不完整檔案；工具不自動刪除，以免刪到競態中由其他程序建立的檔案。

`python scripts/media_tools.py verify AUDIO OUTPUT.mp4 [--ffmpeg PATH] [--ffprobe PATH]` 比較來源音軌與成品音軌的壓縮封包 SHA256、stream 起點與時長，並完整解碼成品。另以專案播放器檢查可播放、畫面章節、黑畫面或渲染錯誤；能聽音訊者可做人工聽辨並記錄結果。音軌 hash 相同只證明音軌位元流保留，完整解碼只證明可解碼，兩者都不能證明內容正確或發音自然。

FFmpeg 參考（2026-09-29 查核）：[FFmpeg 指令與 streamcopy](https://ffmpeg.org/ffmpeg.html)、[hash muxer](https://ffmpeg.org/ffmpeg-formats.html)。
