const $ = (selector) => document.querySelector(selector);

const copy = {
  ja: {
    introKicker: "MAKE SOMETHING MOVE",
    heroLead: "画像を選んで、", heroAccent: "動かしてみよう", heroTail: "。",
    introBody: "写真でもイラストでもOK。1枚を動かす、AからBへ変える、文字を変身させる。まずは3つから選ぶだけ。",
    trustLocalTitle: "このPCで作る", trustLocalBody: "アカウント・待ち時間なし",
    trustPrivateTitle: "外へ送らない", trustPrivateBody: "写真も文章もローカル",
    trustEasyTitle: "まず1本", trustEasyBody: "短い動画ですぐ試せる",
    creationLegend: "何を作る？", transitionTitle: "A → B 変身",
    transitionSub: "2枚の画像をつないで変化", animateTitle: "画像を動かす",
    animateSub: "1枚から、カメラや被写体を動かす", shortPrompt: "短い一言でOK",
    glyphTitle: "文字を変身", glyphSub: "文字や記号を、不思議に変える",
    glyphSourceTitle: "AIに変化させる文字", glyphSourceHelp: "文字をシートに並べ、変化の途中はNPUが自然に描きます。",
    glyphSourceLabel: "元の文字", glyphStyleTitle: "雰囲気のヒント",
    glyphStyleHelp: "色や雰囲気のヒントです。文字の形はNPUが決めます。",
    glyphImageTitle: "画像の文字シートも使う", glyphImageHelp: "フリー素材・自作・生成画像をクリックまたはドロップ",
    glyphImageRemove: "外す", glyphImageStatus: "画像を選ばなければ、入力文字からシートを作ります。", glyphImagePreview: "画像シートを使用中",
    glyphAlien: "ALIEN", glyphRune: "RUNE", glyphSignal: "SIGNAL", glyphCyber: "CYBER",
    glyphPreviewLabel: "NPUに渡す文字シート", glyphRefresh: "文字シートを作る", glyphCopy: "元の文字をコピー",
    glyphTextDownload: "TXT", glyphSvgDownload: "文字シートSVG", glyphFontDownload: "フォント",
    glyphStatus: "文字シートを作ると、NPUが変化を描く準備ができます。",
    glyphResultTitle: "AI変化の元になる文字シート", glyphResultHelp: "動画ではこのシートを元に、NPUが文字を自然に変化させます。",
    shortcutTail: "で作成", qualityTitle: "どんな感じにする？",
    qualityHelp: "迷ったら「おすすめ」。まずは短い動画で試せます。", fastTitle: "すぐ試す",
    fastSub: "軽く・はやい", funTitle: "おすすめ",
    funSub: "見た目と速さのバランス", wowTitle: "じっくり", wowSub: "より丁寧に仕上げる",
    advanced: "詳細設定", duration: "作品の長さ", loopTitle: "最後から最初へ自然につなぐ",
    loopSub: "繰り返し再生しても切れ目を目立たせません",
    emptyTitle: "変身動画がここに現れます",
    emptyBody: "2枚の画像を選び、動きを一言書いてみてください。",
    promise1: "はじめとおわりを固定", promise2: "途中の変化をAIが描く", promise3: "なめらかな動画に仕上げる",
    seconds: "秒", workingKicker: "ただいま制作中", step1: "文章を理解", step2: "NPUで描く",
    step3: "GPUでつなぐ", step4: "仕上げる",
    workingNote: "迷ったら「おすすめ」。できあがったら、別の動きもすぐ試せます。",
    save: "保存する", remix: "別の動きでもう1本作る", privacy: "入力は外部へ送信しません",
    sceneTransition: "はじめとおわりを選んで、変化を書こう",
    sceneTransitionHelp: "2枚の画像の間に、AIが変身の途中を描きます。",
    sceneAnimate: "どんな動きにする？", sceneAnimateHelp: "文章か画像、どちらか片方だけでも大丈夫です。",
    glyphMotionTitle: "文字の動きを書いてください", glyphMotionHelp: "文字が割れる、伸びる、光になるなど、短い文章で大丈夫です。",
    emptyTransitionTitle: "変身動画がここに現れます", emptyTransitionBody: "2枚の画像を選び、動きを一言書いてみてください。",
    emptyAnimateTitle: "動き出した画像がここに現れます", emptyAnimateBody: "画像か文章を選び、まず1本作ってみてください。",
    emptyGlyphTitle: "変身する文字がここに現れます", emptyGlyphBody: "文字を入力するか、文字シート画像を選んでください。",
    promptTransition: "例：ロボットが部品を展開しながら、赤いスポーツカーへ変形する。",
    promptAnimate: "例：雨の夜。巨大ロボットが勢いよく走り出す。",
    promptLabel: "動きの一言", orTransition: "どんなふうに変わる？", orAnimate: "画像を使うならこちら",
    firstTransition: "はじめの画像", firstAnimate: "動かす画像", targetLabel: "おわりの画像",
    clickDrop: "クリックまたはここへドロップ", removeImage: "画像を外す",
    chooseA: "Aの画像を選ぶ", chooseImage: "画像を選ぶ", chooseB: "Bの画像を選ぶ",
    preparing: "もうすぐ作れます", generateTransition: "A → B の動画を作る",
    generateAnimate: "動画を作ってみる", creating: "動画を作っています",
    glyphPrompt: "任意：文字の変化を文章で追加できます。空欄でもNPUが自動で変化させます。",
    glyphAutoPrompt: "naturally transform each printed character into an expressive alien glyph, preserve the exact character sheet grid and spacing, one symbol per cell, fluid ink metamorphosis, no extra objects",
    glyphPromptDefault: "",
    waitBusy: "続けて押さず、そのままお待ちください", qualityFirst: "選んだ品質で最初から生成します",
    startupWait: "起動時だけ少しお待ちください", genericError: "うまく処理できませんでした。もう一度お試しください。",
    invalidImage: "PNG、JPEG、WebPの画像を選んでください。", imageTooLarge: "画像は5MB以下にしてください。",
    readImageError: "画像を読み込めませんでした。別の画像をお試しください。",
    bothImages: "AとBの画像を2枚とも選んでください。", promptOrImage: "文章を書くか画像を1枚選んでください。",
    stillPreparing: "ローカルAIを準備しています。ボタンが使えるまで少しお待ちください。",
    gettingReady: "準備しています", completed: "できました", completedIn: "{time}秒でできました",
    promptUnderstood: "文章を理解", savedLocal: "NPUとArc GPUで作り、このPCに保存しました",
    generationFailed: "生成に失敗しました。設定を変えてもう一度お試しください。",
    systemReady: "ローカルAI準備OK", demoMode: "お試しモード", installed: "導入済み",
    notInstalled: "未導入（デモは動きます）", noInfo: "情報なし", notDetected: "未検出",
    systemError: "機器情報を取得できませんでした。デモはそのまま試せます。",
    selectedImage: "{name}を選択中。別の画像を選ぶ",
    brushTitle: "動かす場所を指定（Motion Brush）", brushSummary: "赤で動かす・青で固定・矢印で方向",
    brushMove: "激しく動かす", brushLock: "固定する", brushArrow: "方向を引く", brushClear: "全部消す",
    brushTip: "例：車を赤く塗り、背景を青く塗って、右向きの矢印を引きます。",
    suggestionsTitle: "迷ったら、これを押してみて",
    suggestionTransformLabel: "光をまとって変身", suggestionTransformPrompt: "光をまといながら、ゆっくり別の姿へ変身する。",
    suggestionZoomLabel: "ゆっくりズーム", suggestionZoomPrompt: "カメラがゆっくり近づき、主役がこちらを見る。",
    suggestionLoopLabel: "ループっぽく", suggestionLoopPrompt: "ゆっくり近づいて、最後に少しだけ元へ戻る。",
    suggestionWindLabel: "風で揺らす", suggestionWindPrompt: "風が吹き、髪や服と背景の光がやさしく揺れる。",
    suggestionNeonLabel: "ネオンをきらめかせる", suggestionNeonPrompt: "夜のネオンがきらめき、カメラが横へ動く。",
    suggestionBurstLabel: "弾けて変わる", suggestionBurstPrompt: "文字が弾けて光の粒になり、別の記号へ変わる。",
    recommended: "おすすめ",
  },
  en: {
    introKicker: "MAKE SOMETHING MOVE",
    heroLead: "Turn an image into", heroAccent: "a little movie", heroTail: ".",
    introBody: "Photos, illustrations, or text. Choose one playful mode and make your first short video on this PC.",
    trustLocalTitle: "Made on this PC", trustLocalBody: "No account or queue",
    trustPrivateTitle: "Stays local", trustPrivateBody: "Your images stay here",
    trustEasyTitle: "Start with one", trustEasyBody: "Try a short clip first",
    creationLegend: "What do you want to make?", transitionTitle: "Transform A → B",
    transitionSub: "Connect two images and make a change", animateTitle: "Animate an image",
    animateSub: "Move the camera or the subject", shortPrompt: "A few words are enough",
    glyphTitle: "Morph text", glyphSub: "Turn letters and symbols into something strange",
    glyphSourceTitle: "Text for the AI to transform", glyphSourceHelp: "The NPU receives a character sheet and invents the in-between naturally.",
    glyphSourceLabel: "Source text", glyphStyleTitle: "Mood hint",
    glyphStyleHelp: "A color and mood hint; the NPU decides the new character shapes.",
    glyphImageTitle: "Use a character-sheet image", glyphImageHelp: "Drop a free, self-made, or generated image here",
    glyphImageRemove: "Remove", glyphImageStatus: "Without an image, a sheet is made from the source text.", glyphImagePreview: "Using the image sheet",
    glyphAlien: "ALIEN", glyphRune: "RUNE", glyphSignal: "SIGNAL", glyphCyber: "CYBER",
    glyphPreviewLabel: "Character sheet sent to the NPU", glyphRefresh: "Make character sheet", glyphCopy: "Copy source text",
    glyphTextDownload: "TXT", glyphSvgDownload: "CHARACTER SHEET SVG", glyphFontDownload: "FONT",
    glyphStatus: "Make the character sheet, then the NPU will draw the transformation.",
    glyphResultTitle: "Character sheet used by the AI", glyphResultHelp: "The video starts here and the NPU morphs each character naturally.",
    shortcutTail: "to create", qualityTitle: "Pick a feel",
    qualityHelp: "Not sure? Choose Recommended and try a short clip.", fastTitle: "Quick try", fastSub: "Light and fast",
    funTitle: "Recommended", funSub: "Best balance of look and speed", wowTitle: "Take more time",
    wowSub: "A more careful finish", advanced: "Advanced settings", duration: "Video length",
    loopTitle: "Seamlessly return to the first frame", loopSub: "Hide the cut during repeated playback",
    emptyTitle: "Your transformation appears here",
    emptyBody: "Choose two images, add a few words, and make your first clip.",
    promise1: "First and last frames stay put", promise2: "AI draws the in-between", promise3: "Finished as a smooth video",
    seconds: "sec", workingKicker: "CREATING LOCALLY", step1: "Understand prompt", step2: "Draw on NPU",
    step3: "Connect on GPU", step4: "Finish MP4",
    workingNote: "Recommended is a good place to start. When it is done, try another motion.",
    save: "Save video", remix: "Make another clip with a new motion", privacy: "Your inputs never leave this PC",
    sceneTransition: "Choose the start and end, then describe the change",
    sceneTransitionHelp: "Pick two images. AI draws the transformation between them.",
    sceneAnimate: "What should move?", sceneAnimateHelp: "Use a prompt, one image, or both.",
    glyphMotionTitle: "Describe the glyph motion", glyphMotionHelp: "Say what happens: fracture, stretch, glow, or reassemble.",
    emptyTransitionTitle: "Your transformation appears here", emptyTransitionBody: "Choose two images, add a few words, and make your first clip.",
    emptyAnimateTitle: "Your moving image appears here", emptyAnimateBody: "Choose an image or a prompt, then make a first clip.",
    emptyGlyphTitle: "Your morphing text appears here", emptyGlyphBody: "Enter text or choose a character-sheet image to get started.",
    promptTransition: "Example: A robot unfolds its parts and transforms into a red sports car.",
    promptAnimate: "Example: A giant robot bursts into a sprint through a rainy neon street.",
    glyphPrompt: "Optional: describe the change. Leave it blank and the NPU will choose a natural morph.",
    glyphAutoPrompt: "naturally transform each printed character into an expressive alien glyph, preserve the exact character sheet grid and spacing, one symbol per cell, fluid ink metamorphosis, no extra objects",
    glyphPromptDefault: "",
    promptLabel: "A few words about the motion", orTransition: "How should it change?", orAnimate: "Add an image too",
    firstTransition: "Start image", firstAnimate: "Image to animate", targetLabel: "End image",
    clickDrop: "Click or drop an image here", removeImage: "Remove image",
    chooseA: "Choose image A", chooseImage: "Choose an image", chooseB: "Choose image B",
    preparing: "Almost ready", generateTransition: "Create A → B video",
    generateAnimate: "Make a video", creating: "Making your video",
    waitBusy: "Keep this window open while it works", qualityFirst: "Generates at the quality you selected",
    startupWait: "The first launch needs a moment", genericError: "Something went wrong. Please try again.",
    invalidImage: "Choose a PNG, JPEG, or WebP image.", imageTooLarge: "Choose an image under 5 MB.",
    readImageError: "That image could not be read. Try another file.",
    bothImages: "Choose both image A and image B.", promptOrImage: "Write a prompt or choose one image.",
    stillPreparing: "Local AI is still preparing. Please wait until the button is ready.",
    gettingReady: "Getting ready", completed: "Done", completedIn: "Done in {time} seconds",
    promptUnderstood: "Prompt understood", savedLocal: "Created locally with the NPU and Arc GPU",
    generationFailed: "Generation failed. Try a different prompt or quality setting.",
    systemReady: "Local AI ready", demoMode: "Try-it mode", installed: "Installed",
    notInstalled: "Not installed (demo still works)", noInfo: "No information", notDetected: "Not detected",
    systemError: "Hardware details are unavailable. Demo mode still works.",
    selectedImage: "{name} selected. Choose another image",
    brushTitle: "Choose what moves (Motion Brush)", brushSummary: "Red moves · blue locks · arrow directs",
    brushMove: "Move strongly", brushLock: "Keep fixed", brushArrow: "Draw direction", brushClear: "Clear all",
    brushTip: "Example: paint the car red, the background blue, then draw an arrow to the right.",
    suggestionsTitle: "Not sure? Try one of these",
    suggestionTransformLabel: "Transform with light", suggestionTransformPrompt: "The subject slowly transforms into a new form while wrapped in glowing light.",
    suggestionZoomLabel: "Slow zoom", suggestionZoomPrompt: "The camera slowly moves closer as the subject looks toward us.",
    suggestionLoopLabel: "Make it loop", suggestionLoopPrompt: "The camera moves closer, then gently returns toward the starting view.",
    suggestionWindLabel: "Add a breeze", suggestionWindPrompt: "A soft breeze moves the hair, clothing, and lights in the background.",
    suggestionNeonLabel: "Neon shimmer", suggestionNeonPrompt: "Neon lights shimmer while the camera glides sideways through the night.",
    suggestionBurstLabel: "Burst and morph", suggestionBurstPrompt: "The letters burst into glowing particles and reform as new symbols.",
    recommended: "recommended",
  },
};

const elements = {
  form: $("#creationForm"), prompt: $("#prompt"), promptLabel: $("#promptLabel"), promptSuggestions: $("#promptSuggestions"),
  imageInput: $("#imageInput"), dropzone: $("#dropzone"), dropPrompt: $("#dropPrompt"),
  imagePreview: $("#imagePreview"), imageShade: $("#imageShade"), removeImage: $("#removeImage"),
  targetImageInput: $("#targetImageInput"), targetDropzone: $("#targetDropzone"),
  targetDropPrompt: $("#targetDropPrompt"), targetImagePreview: $("#targetImagePreview"),
  targetImageShade: $("#targetImageShade"), removeTargetImage: $("#removeTargetImage"),
  transitionTargetGroup: $("#transitionTargetGroup"), imagePair: $("#imagePair"),
  glyphEditor: $("#glyphEditor"), glyphSource: $("#glyphSource"), glyphPreview: $("#glyphPreview"),
  glyphImageInput: $("#glyphImageInput"), glyphImageDropzone: $("#glyphImageDropzone"),
  glyphImagePreview: $("#glyphImagePreview"), glyphImageRemove: $("#glyphImageRemove"), glyphImageStatus: $("#glyphImageStatus"),
  glyphRefresh: $("#glyphRefresh"), glyphCopy: $("#glyphCopy"), glyphStatus: $("#glyphStatus"),
  glyphTextDownload: $("#glyphTextDownload"), glyphSvgDownload: $("#glyphSvgDownload"),
  glyphFontDownload: $("#glyphFontDownload"), glyphResultExports: $("#glyphResultExports"),
  glyphResultSvg: $("#glyphResultSvg"), glyphResultFont: $("#glyphResultFont"), glyphResultText: $("#glyphResultText"),
  firstImageLabel: $("#firstImageLabel"), targetImageLabel: $("#targetImageLabel"),
  sceneTitle: $("#sceneTitle"), sceneHelp: $("#sceneHelp"), orLabel: $("#orLabel"),
  dropHelp: $("#dropHelp"), targetDropHelp: $("#targetDropHelp"), loopOption: $("#loopOption"),
  duration: $("#duration"), seamlessLoop: $("#seamlessLoop"), durationOutput: $("#durationOutput"),
  scaleMin: $("#scaleMin"), scaleMax: $("#scaleMax"), generate: $("#generate"),
  generateLabel: $("#generateLabel"), generateHelp: $("#generateHelp"), error: $("#formError"),
  progressMessage: $("#progressMessage"), progressBar: $("#progressBar"),
  progressTrack: $(".progress-track"), countdown: $("#countdown"), resultVideo: $("#resultVideo"),
  resultImage: $("#resultImage"), resultTime: $("#resultTime"), resultNote: $("#resultNote"),
  download: $("#download"), systemLabel: $("#systemLabel"), systemDot: $("#systemDot"),
  systemPanel: $("#systemPanel"), langJa: $("#langJa"), langEn: $("#langEn"),
  motionBrush: $("#motionBrush"), brushImage: $("#brushImage"),
  brushCanvas: $("#brushCanvas"), clearBrush: $("#clearBrush"),
  emptyTitle: $("#emptyTitle"), emptyBody: $("#emptyBody"),
};

const state = {
  language: "ja", creationMode: "transition", imageDataUrl: null, targetImageDataUrl: null,
  glyphData: null, glyphSignature: "", glyphImageDataUrl: null, glyphCustomImageDataUrl: null, glyphCustomImageName: "",
  busy: false, activeJobId: null, engineReady: false, readinessTimer: null,
  pollTimer: null, countdownTimer: null, countdownStartedAt: null,
  currentStage: "analysis", currentJobMessage: "", system: null,
  resultElapsed: null, resultUnderstood: "", resultJob: null,
  brushTool: "move", moveMaskCanvas: document.createElement("canvas"),
  lockMaskCanvas: document.createElement("canvas"), brushDrawing: false,
  arrowStart: null, motionVector: {x: 0, y: 0},
};

const t = (key) => copy[state.language][key] || key;
const format = (template, values) => Object.entries(values).reduce(
  (result, [key, value]) => result.replace(`{${key}}`, value), template,
);

function show(viewName) {
  for (const id of ["emptyState", "workingState", "resultState"]) {
    $("#" + id).hidden = id !== viewName;
  }
}

function durationText(value) { return state.language === "en" ? `${value} sec` : `${value}秒`; }

function selectedGlyphStyle() {
  return document.querySelector('input[name="glyphStyle"]:checked')?.value || "alien";
}

function resetGlyphAssets() {
  state.glyphData = null; state.glyphSignature = ""; state.glyphImageDataUrl = state.glyphCustomImageDataUrl;
  for (const link of [elements.glyphTextDownload, elements.glyphSvgDownload, elements.glyphFontDownload]) {
    link.hidden = true; link.removeAttribute("href");
  }
  for (const link of [elements.glyphResultSvg, elements.glyphResultFont, elements.glyphResultText]) {
    link.hidden = true; link.removeAttribute("href");
  }
  elements.glyphStatus.textContent = t("glyphStatus");
  if (elements.glyphImageStatus) {
    elements.glyphImageStatus.textContent = state.glyphCustomImageName
      ? `${t("glyphImagePreview")}: ${state.glyphCustomImageName}` : t("glyphImageStatus");
  }
  elements.glyphResultExports.hidden = true;
}

function updateGlyphPreview() {
  if (!elements.glyphSource) return;
  elements.glyphPreview.textContent = state.glyphCustomImageDataUrl
    ? t("glyphImagePreview") : (elements.glyphSource.value.trim() || "NPU MOTION");
  resetGlyphAssets();
}

function svgToPngDataUrl(svg) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener("load", () => {
      const canvas = document.createElement("canvas"); canvas.width = 1024; canvas.height = 576;
      const context = canvas.getContext("2d"); context.fillStyle = "#05070c"; context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0, canvas.width, canvas.height); resolve(canvas.toDataURL("image/png"));
    });
    image.addEventListener("error", () => reject(new Error(t("readImageError"))));
    image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  });
}

function setGlyphAssetLinks(data) {
  elements.glyphPreview.textContent = data.source_text;
  elements.glyphTextDownload.hidden = true;
  elements.glyphFontDownload.hidden = true;
  elements.glyphTextDownload.removeAttribute("href");
  elements.glyphFontDownload.removeAttribute("href");
  elements.glyphSvgDownload.href = data.source_svg_url || data.svg_url;
  elements.glyphSvgDownload.hidden = false;
  elements.glyphStatus.textContent = state.glyphCustomImageDataUrl
    ? (state.language === "ja"
      ? "選んだ画像をNPUへ渡します。文字の形はNPUが自然に変化させます。"
      : "Your image will go to the NPU. It will invent the character morph naturally.")
    : (state.language === "ja"
      ? "NPUに渡す文字シートを作りました。動画ではNPUが形を自然に変化させます。"
      : "The NPU character sheet is ready. The video will let the NPU invent the morph.");
}

async function ensureGlyphAssets(force = false) {
  const source = elements.glyphSource.value.trim();
  if (!source && !state.glyphCustomImageDataUrl) throw new Error(state.language === "ja" ? "文字を入力するか、文字シート画像を選んでください。" : "Enter source text or choose a character-sheet image.");
  const apiSource = source || "NPU MOTION";
  const style = selectedGlyphStyle(); const signature = `${style}:${apiSource}:${state.glyphCustomImageName}:${state.glyphCustomImageDataUrl?.length || 0}`;
  if (!force && state.glyphData && state.glyphSignature === signature) return state.glyphData;
  const data = await readJson(await fetch("/api/glyphs", {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({text: apiSource, style}),
  }));
  data.png_data_url = state.glyphCustomImageDataUrl || await svgToPngDataUrl(data.source_svg || data.svg);
  state.glyphData = data; state.glyphSignature = signature; state.glyphImageDataUrl = data.png_data_url;
  setGlyphAssetLinks(data); return data;
}

function deadlineLabel() {
  if (!state.engineReady) return t("preparing");
  return state.creationMode === "transition" ? t("generateTransition") : t("generateAnimate");
}

function setBusy(busy) {
  state.busy = busy;
  elements.generate.disabled = busy || !state.engineReady;
  elements.generate.setAttribute("aria-busy", String(busy));
  elements.generateLabel.textContent = busy ? t("creating") : deadlineLabel();
  elements.generateHelp.textContent = busy
    ? t("waitBusy") : state.engineReady ? t("qualityFirst") : t("startupWait");
}

function clearError() { elements.error.textContent = ""; elements.error.hidden = true; }
function showError(message) {
  elements.error.textContent = message || t("genericError"); elements.error.hidden = false;
  elements.error.focus({preventScroll: true});
  elements.error.scrollIntoView({behavior: "smooth", block: "nearest"});
}

function selectMode(value) {
  document.querySelectorAll(".mode").forEach((label) => {
    label.classList.toggle("selected", label.querySelector("input").value === value);
  });
}

function renderPromptSuggestions() {
  if (!elements.promptSuggestions) return;
  const suggestions = {
    transition: [
      ["suggestionTransformLabel", "suggestionTransformPrompt"],
      ["suggestionZoomLabel", "suggestionZoomPrompt"],
      ["suggestionNeonLabel", "suggestionNeonPrompt"],
    ],
    animate: [
      ["suggestionZoomLabel", "suggestionZoomPrompt"],
      ["suggestionWindLabel", "suggestionWindPrompt"],
      ["suggestionNeonLabel", "suggestionNeonPrompt"],
    ],
    glyph: [
      ["suggestionTransformLabel", "suggestionTransformPrompt"],
      ["suggestionBurstLabel", "suggestionBurstPrompt"],
      ["suggestionNeonLabel", "suggestionNeonPrompt"],
    ],
  }[state.creationMode] || [];
  const title = document.createElement("span");
  title.className = "prompt-suggestions-title";
  title.textContent = t("suggestionsTitle");
  const buttons = document.createElement("div");
  buttons.className = "prompt-suggestion-list";
  for (const [labelKey, promptKey] of suggestions) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "prompt-suggestion";
    button.textContent = t(labelKey);
    button.title = t(promptKey);
    button.addEventListener("click", () => {
      elements.prompt.value = t(promptKey);
      elements.prompt.focus();
      clearError();
    });
    buttons.append(button);
  }
  elements.promptSuggestions.replaceChildren(title, buttons);
}

function selectCreationMode(value) {
  state.creationMode = value;
  const transition = value === "transition";
  const glyph = value === "glyph";
  document.querySelectorAll(".creation-mode").forEach((label) => {
    label.classList.toggle("selected", label.querySelector("input").value === value);
  });
  elements.transitionTargetGroup.hidden = !transition;
  elements.imagePair.classList.toggle("transition-active", transition);
  elements.imagePair.hidden = glyph;
  elements.glyphEditor.hidden = !glyph;
  // The glyph editor is its own input path; the A/B prompt divider would only
  // add noise there. Keep it for the two image modes.
  elements.orLabel.parentElement.hidden = glyph;
  elements.motionBrush.hidden = glyph || !state.imageDataUrl;
  elements.firstImageLabel.textContent = transition ? t("firstTransition") : t("firstAnimate");
  elements.sceneTitle.textContent = transition ? t("sceneTransition") : glyph ? t("glyphMotionTitle") : t("sceneAnimate");
  elements.sceneHelp.textContent = transition ? t("sceneTransitionHelp") : glyph ? t("glyphMotionHelp") : t("sceneAnimateHelp");
  elements.emptyTitle.textContent = transition ? t("emptyTransitionTitle") : glyph ? t("emptyGlyphTitle") : t("emptyAnimateTitle");
  elements.emptyBody.textContent = transition ? t("emptyTransitionBody") : glyph ? t("emptyGlyphBody") : t("emptyAnimateBody");
  elements.orLabel.textContent = transition ? t("orTransition") : t("orAnimate");
  elements.prompt.placeholder = transition ? t("promptTransition") : glyph ? t("glyphPrompt") : t("promptAnimate");
  elements.dropzone.setAttribute("aria-label", transition ? t("chooseA") : t("chooseImage"));
  elements.loopOption.hidden = transition; elements.seamlessLoop.checked = !transition;
  if (glyph && (elements.prompt.value === copy.ja.glyphPromptDefault || elements.prompt.value === copy.en.glyphPromptDefault)) {
    elements.prompt.value = "";
  }
  if (!state.busy) setBusy(false);
  renderPromptSuggestions();
}

function renderSystem() {
  const system = state.system;
  if (!system) return;
  const npu = Array.isArray(system.npu_devices) ? system.npu_devices : [];
  const gpu = Array.isArray(system.gpu_devices) ? system.gpu_devices : [];
  elements.systemLabel.textContent = npu.length ? t("systemReady") : t("demoMode");
  elements.systemDot.classList.toggle("ready", npu.length > 0); elements.systemPanel.innerHTML = "";
  const openvino = system.openvino_installed
    ? (system.openvino_devices.join(", ") || t("installed")) : t("notInstalled");
  for (const [label, value] of [
    ["CPU", system.processor || t("noInfo")], ["NPU", npu.join(", ") || t("notDetected")],
    ["GPU", gpu.join(", ") || t("notDetected")], ["OpenVINO", openvino],
  ]) {
    const row = document.createElement("p"); const title = document.createElement("strong");
    title.textContent = label; row.append(title, document.createTextNode(value)); elements.systemPanel.append(row);
  }
}

function applyLanguage(language) {
  state.language = language; document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  elements.langJa.classList.toggle("active", language === "ja");
  elements.langEn.classList.toggle("active", language === "en");
  elements.langJa.setAttribute("aria-pressed", String(language === "ja"));
  elements.langEn.setAttribute("aria-pressed", String(language === "en"));
  elements.promptLabel.textContent = t("promptLabel"); elements.targetImageLabel.textContent = t("targetLabel");
  elements.dropHelp.textContent = t("clickDrop"); elements.targetDropHelp.textContent = t("clickDrop");
  elements.removeImage.textContent = t("removeImage"); elements.removeTargetImage.textContent = t("removeImage");
  elements.targetDropzone.setAttribute("aria-label", t("chooseB"));
  elements.durationOutput.value = durationText(elements.duration.value);
  elements.scaleMin.textContent = durationText(2); elements.scaleMax.textContent = durationText(10);
  selectCreationMode(state.creationMode); renderGlyphImageStatus(); renderSystem(); clearError();
  if (state.busy) {
    elements.progressMessage.textContent = progressMessageFor(state.currentStage)
      || state.currentJobMessage || t("gettingReady");
  }
  renderResultMeta();
}

document.querySelectorAll('input[name="mode"]').forEach((radio) => {
  radio.addEventListener("change", () => selectMode(radio.value));
});
document.querySelectorAll('input[name="creationMode"]').forEach((radio) => {
  radio.addEventListener("change", () => selectCreationMode(radio.value));
});
elements.langJa.addEventListener("click", () => applyLanguage("ja"));
elements.langEn.addEventListener("click", () => applyLanguage("en"));
elements.duration.addEventListener("input", () => {
  elements.durationOutput.value = durationText(elements.duration.value);
});
elements.glyphSource.addEventListener("input", updateGlyphPreview);
document.querySelectorAll('input[name="glyphStyle"]').forEach((radio) => radio.addEventListener("change", () => {
  document.querySelectorAll(".glyph-style").forEach((label) => label.classList.toggle("selected", label.querySelector("input").checked));
  updateGlyphPreview();
}));
elements.glyphRefresh.addEventListener("click", async () => {
  if (state.busy) return;
  try { await ensureGlyphAssets(true); }
  catch (error) { showError(error.message); }
});
elements.glyphCopy.addEventListener("click", async () => {
  try {
    const data = await ensureGlyphAssets();
    await navigator.clipboard.writeText(data.source_text);
    elements.glyphStatus.textContent = state.language === "ja" ? "元の文字をコピーしました。" : "Source text copied to the clipboard.";
  } catch (error) { showError(error.message); }
});

function renderGlyphImageStatus() {
  if (!elements.glyphImageStatus) return;
  elements.glyphImageStatus.textContent = state.glyphCustomImageName
    ? `${t("glyphImagePreview")}: ${state.glyphCustomImageName}` : t("glyphImageStatus");
}

function acceptGlyphImage(file) {
  clearError();
  if (!file || !["image/png", "image/jpeg", "image/webp"].includes(file.type)) {
    showError(t("invalidImage")); return;
  }
  if (file.size > 5 * 1024 * 1024) { showError(t("imageTooLarge")); return; }
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    state.glyphCustomImageDataUrl = reader.result; state.glyphCustomImageName = file.name;
    elements.glyphImagePreview.src = reader.result; elements.glyphImagePreview.hidden = false;
    elements.glyphImageRemove.hidden = false; elements.glyphImageDropzone.classList.add("has-image");
    renderGlyphImageStatus(); updateGlyphPreview();
  });
  reader.addEventListener("error", () => showError(t("readImageError")));
  reader.readAsDataURL(file);
}

function clearGlyphImage() {
  state.glyphCustomImageDataUrl = null; state.glyphCustomImageName = "";
  elements.glyphImageInput.value = ""; elements.glyphImagePreview.removeAttribute("src");
  elements.glyphImagePreview.hidden = true; elements.glyphImageRemove.hidden = true;
  elements.glyphImageDropzone.classList.remove("has-image"); renderGlyphImageStatus(); updateGlyphPreview();
}

elements.glyphImageDropzone.addEventListener("click", (event) => {
  if (event.target !== elements.glyphImageRemove && !state.busy) elements.glyphImageInput.click();
});
elements.glyphImageDropzone.addEventListener("keydown", (event) => {
  if (["Enter", " "].includes(event.key) && !state.busy) {
    event.preventDefault(); elements.glyphImageInput.click();
  }
});
elements.glyphImageInput.addEventListener("change", () => acceptGlyphImage(elements.glyphImageInput.files[0]));
for (const eventName of ["dragenter", "dragover"]) {
  elements.glyphImageDropzone.addEventListener(eventName, (event) => {
    event.preventDefault(); if (!state.busy) elements.glyphImageDropzone.classList.add("dragging");
  });
}
for (const eventName of ["dragleave", "drop"]) {
  elements.glyphImageDropzone.addEventListener(eventName, (event) => {
    event.preventDefault(); elements.glyphImageDropzone.classList.remove("dragging");
  });
}
elements.glyphImageDropzone.addEventListener("drop", (event) => {
  if (!state.busy) acceptGlyphImage(event.dataTransfer.files[0]);
});
elements.glyphImageRemove.addEventListener("click", (event) => { event.stopPropagation(); clearGlyphImage(); });
const imageSlots = {
  start: {stateKey: "imageDataUrl", input: elements.imageInput, dropzone: elements.dropzone,
    prompt: elements.dropPrompt, preview: elements.imagePreview, shade: elements.imageShade,
    remove: elements.removeImage},
  target: {stateKey: "targetImageDataUrl", input: elements.targetImageInput,
    dropzone: elements.targetDropzone, prompt: elements.targetDropPrompt,
    preview: elements.targetImagePreview, shade: elements.targetImageShade,
    remove: elements.removeTargetImage},
};

function emptyAria(slotName) {
  if (slotName === "target") return t("chooseB");
  return state.creationMode === "transition" ? t("chooseA") : t("chooseImage");
}

function acceptImage(file, slotName) {
  const slot = imageSlots[slotName]; clearError();
  if (!file || !["image/png", "image/jpeg", "image/webp"].includes(file.type)) {
    showError(t("invalidImage")); return;
  }
  if (file.size > 5 * 1024 * 1024) { showError(t("imageTooLarge")); return; }
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    state[slot.stateKey] = reader.result; slot.preview.src = state[slot.stateKey];
    slot.preview.hidden = false; slot.shade.hidden = false; slot.remove.hidden = false;
    slot.prompt.hidden = true;
    slot.dropzone.setAttribute("aria-label", format(t("selectedImage"), {name: file.name}));
    if (slotName === "start") setupBrush(state[slot.stateKey]);
  });
  reader.addEventListener("error", () => showError(t("readImageError")));
  reader.readAsDataURL(file);
}

function clearImage(slotName) {
  const slot = imageSlots[slotName]; state[slot.stateKey] = null; slot.input.value = "";
  slot.preview.removeAttribute("src"); slot.preview.hidden = true; slot.shade.hidden = true;
  slot.remove.hidden = true; slot.prompt.hidden = false;
  slot.dropzone.setAttribute("aria-label", emptyAria(slotName));
  if (slotName === "start") resetBrush(true);
}

function bindImageSlot(slotName) {
  const slot = imageSlots[slotName];
  slot.dropzone.addEventListener("click", (event) => {
    if (event.target !== slot.remove && !state.busy) slot.input.click();
  });
  slot.dropzone.addEventListener("keydown", (event) => {
    if (["Enter", " "].includes(event.key) && !state.busy) {
      event.preventDefault(); slot.input.click();
    }
  });
  slot.input.addEventListener("change", () => acceptImage(slot.input.files[0], slotName));
  for (const eventName of ["dragenter", "dragover"]) {
    slot.dropzone.addEventListener(eventName, (event) => {
      event.preventDefault(); if (!state.busy) slot.dropzone.classList.add("dragging");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    slot.dropzone.addEventListener(eventName, (event) => {
      event.preventDefault(); slot.dropzone.classList.remove("dragging");
    });
  }
  slot.dropzone.addEventListener("drop", (event) => {
    if (!state.busy) acceptImage(event.dataTransfer.files[0], slotName);
  });
  slot.remove.addEventListener("click", (event) => { event.stopPropagation(); clearImage(slotName); });
}
bindImageSlot("start"); bindImageSlot("target");

function brushContexts() {
  return {
    visible: elements.brushCanvas.getContext("2d"),
    move: state.moveMaskCanvas.getContext("2d"),
    lock: state.lockMaskCanvas.getContext("2d"),
  };
}

function resetBrush(hide = false) {
  for (const canvas of [elements.brushCanvas, state.moveMaskCanvas, state.lockMaskCanvas]) {
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
  }
  state.motionVector = {x: 0, y: 0}; state.arrowStart = null;
  if (hide) elements.motionBrush.hidden = true;
}

function setupBrush(source) {
  const image = new Image();
  image.addEventListener("load", () => {
    const scale = Math.min(1, 900 / Math.max(image.naturalWidth, image.naturalHeight));
    const width = Math.max(2, Math.round(image.naturalWidth * scale));
    const height = Math.max(2, Math.round(image.naturalHeight * scale));
    for (const canvas of [elements.brushCanvas, state.moveMaskCanvas, state.lockMaskCanvas]) {
      canvas.width = width; canvas.height = height;
    }
    elements.brushImage.src = source; elements.motionBrush.hidden = false; resetBrush(false);
  });
  image.src = source;
}

function brushPoint(event) {
  const rect = elements.brushCanvas.getBoundingClientRect();
  return {
    x: (event.clientX - rect.left) * elements.brushCanvas.width / rect.width,
    y: (event.clientY - rect.top) * elements.brushCanvas.height / rect.height,
  };
}

function paintBrush(from, to) {
  const contexts = brushContexts();
  const target = state.brushTool === "lock" ? contexts.lock : contexts.move;
  const color = state.brushTool === "lock" ? "white" : "white";
  const overlay = state.brushTool === "lock" ? "rgba(52,140,255,.58)" : "rgba(255,56,92,.58)";
  const width = Math.max(18, elements.brushCanvas.width * 0.065);
  for (const [context, stroke] of [[target, color], [contexts.visible, overlay]]) {
    context.strokeStyle = stroke; context.lineWidth = width; context.lineCap = "round";
    context.lineJoin = "round"; context.beginPath(); context.moveTo(from.x, from.y);
    context.lineTo(to.x, to.y); context.stroke();
  }
}

function drawArrow(from, to) {
  const context = brushContexts().visible; const angle = Math.atan2(to.y - from.y, to.x - from.x);
  context.strokeStyle = "rgba(255,212,91,.96)"; context.fillStyle = "rgba(255,212,91,.96)";
  context.lineWidth = Math.max(4, elements.brushCanvas.width * .012); context.lineCap = "round";
  context.beginPath(); context.moveTo(from.x, from.y); context.lineTo(to.x, to.y); context.stroke();
  const size = Math.max(14, elements.brushCanvas.width * .045);
  context.beginPath(); context.moveTo(to.x, to.y);
  context.lineTo(to.x - size * Math.cos(angle - Math.PI / 6), to.y - size * Math.sin(angle - Math.PI / 6));
  context.lineTo(to.x - size * Math.cos(angle + Math.PI / 6), to.y - size * Math.sin(angle + Math.PI / 6));
  context.closePath(); context.fill();
  const dx = to.x - from.x; const dy = to.y - from.y; const length = Math.hypot(dx, dy) || 1;
  state.motionVector = {x: dx / length, y: dy / length};
}

document.querySelectorAll(".brush-tool").forEach((button) => button.addEventListener("click", () => {
  state.brushTool = button.dataset.tool;
  document.querySelectorAll(".brush-tool").forEach((item) => item.classList.toggle("active", item === button));
}));
elements.clearBrush.addEventListener("click", () => resetBrush(false));
elements.brushCanvas.addEventListener("pointerdown", (event) => {
  if (state.busy) return; elements.brushCanvas.setPointerCapture(event.pointerId);
  state.brushDrawing = true; state.arrowStart = brushPoint(event); state.lastBrushPoint = state.arrowStart;
});
elements.brushCanvas.addEventListener("pointermove", (event) => {
  if (!state.brushDrawing || state.brushTool === "arrow") return;
  const point = brushPoint(event); paintBrush(state.lastBrushPoint, point); state.lastBrushPoint = point;
});
elements.brushCanvas.addEventListener("pointerup", (event) => {
  if (!state.brushDrawing) return; const point = brushPoint(event);
  if (state.brushTool === "arrow") drawArrow(state.arrowStart, point);
  else paintBrush(state.lastBrushPoint, point);
  state.brushDrawing = false;
});

function canvasHasPaint(canvas) {
  const pixels = canvas.getContext("2d").getImageData(0, 0, canvas.width, canvas.height).data;
  for (let index = 3; index < pixels.length; index += 4) if (pixels[index]) return true;
  return false;
}

function brushPayload() {
  return {
    motion_mask_data_url: canvasHasPaint(state.moveMaskCanvas) ? state.moveMaskCanvas.toDataURL("image/png") : null,
    lock_mask_data_url: canvasHasPaint(state.lockMaskCanvas) ? state.lockMaskCanvas.toDataURL("image/png") : null,
    motion_vector_x: state.motionVector.x, motion_vector_y: state.motionVector.y,
  };
}

function errorMessage(detail) {
  const raw = Array.isArray(detail)
    ? detail.map((item) => item.msg || String(item)).join(" / ")
    : typeof detail === "string" ? detail : detail?.message;
  if (state.language === "ja") return raw || t("genericError");
  if (raw?.includes("AとB")) return t("bothImages");
  if (raw?.includes("文章を書くか画像")) return t("promptOrImage");
  if (raw?.includes("準備")) return t("stillPreparing");
  return raw || t("genericError");
}
async function readJson(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(errorMessage(body.detail)); return body;
}

function updatePipeline(stage) {
  const stages = ["analysis", "image", "motion", "encode"]; const current = stages.indexOf(stage);
  stages.forEach((name, index) => {
    const item = $("#step-" + name); item.classList.toggle("active", index === current);
    item.classList.toggle("done", current > index || ["delivery", "completed"].includes(stage));
  });
}
function updateProgress(percent) {
  const safe = Math.max(0, Math.min(100, Number(percent) || 0));
  elements.progressBar.style.width = `${safe}%`; elements.progressTrack.setAttribute("aria-valuenow", String(safe));
}
function stopTimers() {
  clearTimeout(state.pollTimer); clearInterval(state.countdownTimer);
  state.pollTimer = null; state.countdownTimer = null;
}
function startCountdown() {
  state.countdownStartedAt = performance.now(); clearInterval(state.countdownTimer);
  const render = () => {
    elements.countdown.textContent = ((performance.now() - state.countdownStartedAt) / 1000).toFixed(1);
  };
  render(); state.countdownTimer = setInterval(render, 50);
}

function resetMedia() {
  elements.resultVideo.pause(); elements.resultVideo.removeAttribute("src"); elements.resultVideo.load();
  elements.resultVideo.hidden = true; elements.resultImage.removeAttribute("src"); elements.resultImage.hidden = true;
}
function showArtifact(job) {
  resetMedia(); const source = `${job.artifact_url}?v=${Date.now()}`;
  if (String(job.media_type || "").startsWith("video/")) {
    elements.resultVideo.src = source; elements.resultVideo.hidden = false;
    elements.resultVideo.play().catch(() => { /* Controls remain available. */ });
  } else if (String(job.media_type || "").startsWith("image/")) {
    elements.resultImage.src = source; elements.resultImage.hidden = false;
  }
  elements.download.href = job.artifact_url; elements.download.download = "";
  state.resultJob = job;
}
function finishWithError(message) {
  stopTimers(); state.activeJobId = null; setBusy(false); show("emptyState"); showError(message);
}

function progressMessageFor(stage) {
  if (state.language === "ja") return null;
  return {
    analysis: "Understanding your prompt", image: "Drawing the key moments on the NPU",
    motion: "Connecting frames on the Arc GPU", encode: "Finishing the MP4",
    delivery: "Done", completed: "Done",
  }[stage] || t("gettingReady");
}

function renderResultMeta() {
  if (state.resultElapsed !== null) {
    elements.resultTime.textContent = format(t("completedIn"), {time: state.resultElapsed.toFixed(1)});
    elements.resultNote.textContent = state.resultUnderstood
      ? `${t("promptUnderstood")}: ${state.resultUnderstood}` : t("savedLocal");
  }
}

async function pollJob(jobId) {
  if (!state.busy || state.activeJobId !== jobId) return;
  try {
    const job = await readJson(await fetch(`/api/jobs/${jobId}`, {cache: "no-store"}));
    if (!state.busy || state.activeJobId !== jobId) return;
    state.currentStage = job.stage; state.currentJobMessage = job.message;
    elements.progressMessage.textContent = progressMessageFor(job.stage) || job.message;
    updateProgress(job.progress); updatePipeline(job.stage);
    if (job.state === "completed") {
      stopTimers(); state.activeJobId = null; showArtifact(job);
      const elapsed = Number(job.elapsed_seconds);
      state.resultElapsed = Number.isFinite(elapsed) ? elapsed : null;
      const notes = Array.isArray(job.notes) ? job.notes.filter(Boolean) : [];
      const understood = notes.find((note) => note.startsWith("日本語解釈:"));
      state.resultUnderstood = understood
        ? understood.replace("日本語解釈:", "").trim().slice(0, 96) : "";
      if (state.resultElapsed === null) elements.resultTime.textContent = t("completed");
      renderResultMeta();
      if (state.creationMode === "glyph" && state.glyphData) {
        const data = state.glyphData;
        elements.glyphResultSvg.href = data.source_svg_url || data.svg_url;
        elements.glyphResultSvg.hidden = false;
        elements.glyphResultText.hidden = true; elements.glyphResultFont.hidden = true;
        elements.glyphResultExports.hidden = false;
      }
      setBusy(false); show("resultState"); $("#resultState").focus({preventScroll: true}); return;
    }
    if (job.state === "failed") throw new Error(job.error || t("generationFailed"));
    state.pollTimer = setTimeout(() => pollJob(jobId), 220);
  } catch (error) { finishWithError(error.message); }
}

async function loadRuntimeSettings() {
  clearTimeout(state.readinessTimer);
  try {
    const health = await readJson(await fetch("/api/health", {cache: "no-store"}));
    state.engineReady = health.engine_ready !== false;
    if (health.engine_error) showError(`${t("genericError")} ${health.engine_error}`);
  } catch { state.engineReady = false; }
  if (!state.busy) setBusy(false);
  if (!state.engineReady) state.readinessTimer = setTimeout(loadRuntimeSettings, 750);
}

async function submit() {
  if (state.busy) return; clearError();
  if (state.creationMode === "transition" && (!state.imageDataUrl || !state.targetImageDataUrl)) {
    showError(t("bothImages"));
    (state.imageDataUrl ? elements.targetDropzone : elements.dropzone).focus(); return;
  }
  if (state.creationMode === "animate" && !elements.prompt.value.trim() && !state.imageDataUrl) {
    showError(t("promptOrImage")); elements.prompt.focus(); return;
  }
  let glyphData = null;
  if (state.creationMode === "glyph") {
    try { glyphData = await ensureGlyphAssets(); }
    catch (error) { showError(error.message); elements.glyphSource.focus(); return; }
  }
  await loadRuntimeSettings();
  if (!state.engineReady) { showError(t("stillPreparing")); return; }
  setBusy(true); show("workingState"); state.currentStage = "analysis";
  state.currentJobMessage = t("gettingReady"); state.resultElapsed = null; state.resultUnderstood = "";
  updateProgress(4); updatePipeline("analysis"); elements.progressMessage.textContent = t("gettingReady");
  startCountdown();
  try {
    const selectedQuality = $('input[name="mode"]:checked');
    const selectedMode = selectedQuality?.value || "fun";
    const anchorCounts = {fast: 8, fun: 12, wow: 20};
    const promptValue = state.creationMode === "glyph" && !elements.prompt.value.trim()
      ? t("glyphAutoPrompt") : elements.prompt.value;
    const body = {
      prompt: promptValue, mode: selectedMode,
      creation_mode: state.creationMode === "transition" ? "transition" : "animate",
      glyph_mode: state.creationMode === "glyph",
      duration_seconds: Number(elements.duration.value),
      seamless_loop: state.creationMode !== "transition" && elements.seamlessLoop.checked,
      input_image_data_url: glyphData?.png_data_url || state.imageDataUrl,
      target_image_data_url: state.creationMode === "transition" ? state.targetImageDataUrl : null,
      preview_first: false,
      upgrade_anchor_count: anchorCounts[selectedMode],
      ...(state.creationMode === "glyph" ? {motion_mask_data_url: null, lock_mask_data_url: null, motion_vector_x: 0, motion_vector_y: 0} : brushPayload()),
    };
    const job = await readJson(await fetch("/api/jobs", {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body),
    }));
    state.activeJobId = job.id; pollJob(job.id);
  } catch (error) { finishWithError(error.message); }
}

elements.form.addEventListener("submit", (event) => { event.preventDefault(); submit(); });
elements.prompt.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) { event.preventDefault(); submit(); }
});
$("#remix").addEventListener("click", () => { if (!state.busy) submit(); });

async function loadSystem() {
  try {
    state.system = await readJson(await fetch("/api/system", {cache: "no-store"})); renderSystem();
  } catch {
    elements.systemLabel.textContent = t("demoMode"); elements.systemPanel.textContent = t("systemError");
  }
}

applyLanguage("ja"); selectCreationMode("transition");
updateGlyphPreview();
Promise.allSettled([loadRuntimeSettings(), loadSystem()]);
