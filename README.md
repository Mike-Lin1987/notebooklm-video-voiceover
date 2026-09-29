# notebooklm-video-voiceover

可重用的 Codex skill：將既有影片或 3D 動畫與 NotebookLM 生成的原聲整合。此套件是操作流程與本機檢查工具，不是 Google 官方整合或 NotebookLM API。

將本目錄放入 Codex skills 目錄後，以 `$notebooklm-video-voiceover` 呼叫，並提供原影片／動畫入口、內容來源、授權範圍與期望交付。執行時需能操作使用者已登入的 NotebookLM 瀏覽器；本機媒體工具需另行安裝 Python 3、FFmpeg、FFprobe，或以 `--ffmpeg`、`--ffprobe` 指定執行檔。`notebooklm` skill 若已安裝，可協助 UI 操作；本技能的核心流程不依賴它。

GitHub 安裝示例：從 `https://github.com/Mike-Lin1987/notebooklm-video-voiceover` 取得公開檔案，放入 Codex 的 skills 目錄。此專案目前不聲明授權條款。

`scripts/media_tools.py --help` 列出本機檢查與合成指令。所有來源與成品由使用者的專案自行存放；本套件不附帳戶資料或實例媒體。
