const $ = (selector) => document.querySelector(selector);

const copy = {
  ja: {
    introKicker: "NPUで描き、Arc GPUでつなぐ。",
    heroLead: "AからBへの変化を", heroAccent: "ローカルAI動画", heroTail: "に。",
    introBody: "最初と最後の画像を選ぶだけ。AIが途中の変形や動きを描きます。1枚を動かすモードも選べます。",
    creationLegend: "動画の基本モード", transitionTitle: "AからBへ変化",
    transitionSub: "2枚の間をAIが描く・おすすめ", animateTitle: "1枚を動かす",
    animateSub: "Aを残して大きく動かす", shortPrompt: "短い文章でもOK",
    shortcutTail: "で作成", qualityTitle: "品質を選ぶ",
    qualityHelp: "迷ったら「ダイナミック」がおすすめです。", fastTitle: "すばやく",
    fastSub: "NPU画像4枚・短め", funTitle: "ダイナミック",
    funSub: "NPU画像8枚・おすすめ", wowTitle: "高品質", wowSub: "NPU画像12枚・じっくり",
    advanced: "詳細設定", duration: "作品の長さ", loopTitle: "最後から最初へ自然につなぐ",
    loopSub: "繰り返し再生しても切れ目を目立たせません",
    emptyTitle: "AからBへの変化がここに現れます",
    emptyBody: "2枚の画像と動きを指定して、下の大きなボタンを押してください。",
    promise1: "AとBを正確に固定", promise2: "NPUで途中を描く", promise3: "Arc GPUで滑らかに",
    seconds: "秒", workingKicker: "ただいま制作中", step1: "文章を理解", step2: "NPUで描く",
    step3: "GPUでつなぐ", step4: "仕上げる",
    workingNote: "品質を優先します。高品質は少し長くかかります。",
    save: "保存する", remix: "同じAとBで、別の動きを作る", privacy: "入力は外部へ送信しません",
    sceneTransition: "AとBを選んで、変化を書いてください",
    sceneTransitionHelp: "Aの形と画面比率を保ち、Bまでの途中をAIが描きます。",
    sceneAnimate: "場面を教えてください", sceneAnimateHelp: "文章と画像は、どちらか片方だけでも大丈夫です。",
    promptTransition: "例：ロボットが部品を展開しながら、赤いスポーツカーへ変形する。",
    promptAnimate: "例：雨の夜。巨大ロボットが勢いよく走り出す。",
    promptLabel: "変化や動きの説明", orTransition: "AからBへの動きを文章で指定", orAnimate: "または",
    firstTransition: "A・最初の画像", firstAnimate: "画像を1枚選ぶ", targetLabel: "B・最後の画像",
    clickDrop: "クリックまたはここへドロップ", removeImage: "画像を外す",
    chooseA: "Aの画像を選ぶ", chooseImage: "画像を選ぶ", chooseB: "Bの画像を選ぶ",
    preparing: "AIを準備しています", generateTransition: "AからBの動画を作る",
    generateAnimate: "NPUとGPUで動画を作る", creating: "作品を作っています",
    waitBusy: "続けて押さず、そのままお待ちください", qualityFirst: "速さより、動きと完成度を優先します",
    startupWait: "起動時だけ少しお待ちください", genericError: "うまく処理できませんでした。もう一度お試しください。",
    invalidImage: "PNG、JPEG、WebPの画像を選んでください。", imageTooLarge: "画像は5MB以下にしてください。",
    readImageError: "画像を読み込めませんでした。別の画像をお試しください。",
    bothImages: "AとBの画像を2枚とも選んでください。", promptOrImage: "文章を書くか画像を1枚選んでください。",
    stillPreparing: "AIを準備しています。ボタンが使えるまで少しお待ちください。",
    gettingReady: "準備しています", completed: "できました", completedIn: "{time}秒でできました",
    promptUnderstood: "文章を理解", savedLocal: "NPUとArc GPUで作り、このPCに保存しました",
    generationFailed: "生成に失敗しました。設定を変えてもう一度お試しください。",
    systemReady: "NPUを見つけました", demoMode: "デモモード", installed: "導入済み",
    notInstalled: "未導入（デモは動きます）", noInfo: "情報なし", notDetected: "未検出",
    systemError: "機器情報を取得できませんでした。デモはそのまま試せます。",
    selectedImage: "{name}を選択中。別の画像を選ぶ",
  },
  en: {
    introKicker: "Draw on the NPU. Connect on the Arc GPU.",
    heroLead: "Turn A into B with", heroAccent: "local AI motion", heroTail: ".",
    introBody: "Choose a first and last image. AI draws the transformation in between. A single-image mode is included too.",
    creationLegend: "Creation mode", transitionTitle: "Transform A to B",
    transitionSub: "AI draws between two images · Recommended", animateTitle: "Animate one image",
    animateSub: "Move boldly, then return to A", shortPrompt: "A short prompt works",
    shortcutTail: "to create", qualityTitle: "Choose quality",
    qualityHelp: "Dynamic is the best place to start.", fastTitle: "Fast", fastSub: "4 NPU frames · quicker",
    funTitle: "Dynamic", funSub: "8 NPU frames · recommended", wowTitle: "High quality",
    wowSub: "12 NPU frames · take your time", advanced: "Advanced settings", duration: "Video length",
    loopTitle: "Seamlessly return to the first frame", loopSub: "Hide the cut during repeated playback",
    emptyTitle: "Your A-to-B transformation appears here",
    emptyBody: "Choose two images, describe the motion, and press the big button.",
    promise1: "Exact A and B endpoints", promise2: "NPU-drawn in-betweens", promise3: "Smooth Arc GPU motion",
    seconds: "sec", workingKicker: "CREATING LOCALLY", step1: "Understand prompt", step2: "Draw on NPU",
    step3: "Connect on GPU", step4: "Finish MP4",
    workingNote: "Quality comes first. High quality takes a little longer.",
    save: "Save video", remix: "Try another motion with the same A and B", privacy: "Your inputs never leave this PC",
    sceneTransition: "Choose A and B, then describe the transformation",
    sceneTransitionHelp: "A defines the aspect ratio. AI draws the path toward B.",
    sceneAnimate: "Describe the scene", sceneAnimateHelp: "Use a prompt, one image, or both.",
    promptTransition: "Example: A robot unfolds its parts and transforms into a red sports car.",
    promptAnimate: "Example: A giant robot bursts into a sprint through a rainy neon street.",
    promptLabel: "Motion or transformation prompt", orTransition: "Tell AI how A should become B", orAnimate: "or",
    firstTransition: "A · First image", firstAnimate: "Choose one image", targetLabel: "B · Last image",
    clickDrop: "Click or drop an image here", removeImage: "Remove image",
    chooseA: "Choose image A", chooseImage: "Choose an image", chooseB: "Choose image B",
    preparing: "Preparing local AI", generateTransition: "Create the A-to-B video",
    generateAnimate: "Create with NPU + GPU", creating: "Creating your video",
    waitBusy: "Keep this window open while it works", qualityFirst: "Built for motion quality, not a hard 10-second limit",
    startupWait: "The first launch needs a moment", genericError: "Something went wrong. Please try again.",
    invalidImage: "Choose a PNG, JPEG, or WebP image.", imageTooLarge: "Choose an image under 5 MB.",
    readImageError: "That image could not be read. Try another file.",
    bothImages: "Choose both image A and image B.", promptOrImage: "Write a prompt or choose one image.",
    stillPreparing: "Local AI is still preparing. Please wait until the button is ready.",
    gettingReady: "Getting ready", completed: "Done", completedIn: "Done in {time} seconds",
    promptUnderstood: "Prompt understood", savedLocal: "Created locally with the NPU and Arc GPU",
    generationFailed: "Generation failed. Try a different prompt or quality setting.",
    systemReady: "NPU ready", demoMode: "Demo mode", installed: "Installed",
    notInstalled: "Not installed (demo still works)", noInfo: "No information", notDetected: "Not detected",
    systemError: "Hardware details are unavailable. Demo mode still works.",
    selectedImage: "{name} selected. Choose another image",
  },
};

const elements = {
  form: $("#creationForm"), prompt: $("#prompt"), promptLabel: $("#promptLabel"),
  imageInput: $("#imageInput"), dropzone: $("#dropzone"), dropPrompt: $("#dropPrompt"),
  imagePreview: $("#imagePreview"), imageShade: $("#imageShade"), removeImage: $("#removeImage"),
  targetImageInput: $("#targetImageInput"), targetDropzone: $("#targetDropzone"),
  targetDropPrompt: $("#targetDropPrompt"), targetImagePreview: $("#targetImagePreview"),
  targetImageShade: $("#targetImageShade"), removeTargetImage: $("#removeTargetImage"),
  transitionTargetGroup: $("#transitionTargetGroup"), imagePair: $("#imagePair"),
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
};

const state = {
  language: "ja", creationMode: "transition", imageDataUrl: null, targetImageDataUrl: null,
  busy: false, activeJobId: null, engineReady: false, readinessTimer: null,
  pollTimer: null, countdownTimer: null, countdownStartedAt: null,
  currentStage: "analysis", currentJobMessage: "", system: null,
  resultElapsed: null, resultUnderstood: "",
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

function selectCreationMode(value) {
  state.creationMode = value;
  const transition = value === "transition";
  document.querySelectorAll(".creation-mode").forEach((label) => {
    label.classList.toggle("selected", label.querySelector("input").value === value);
  });
  elements.transitionTargetGroup.hidden = !transition;
  elements.imagePair.classList.toggle("transition-active", transition);
  elements.firstImageLabel.textContent = transition ? t("firstTransition") : t("firstAnimate");
  elements.sceneTitle.textContent = transition ? t("sceneTransition") : t("sceneAnimate");
  elements.sceneHelp.textContent = transition ? t("sceneTransitionHelp") : t("sceneAnimateHelp");
  elements.orLabel.textContent = transition ? t("orTransition") : t("orAnimate");
  elements.prompt.placeholder = transition ? t("promptTransition") : t("promptAnimate");
  elements.dropzone.setAttribute("aria-label", transition ? t("chooseA") : t("chooseImage"));
  elements.loopOption.hidden = transition; elements.seamlessLoop.checked = !transition;
  if (!state.busy) setBusy(false);
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
  selectCreationMode(state.creationMode); renderSystem(); clearError();
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
  });
  reader.addEventListener("error", () => showError(t("readImageError")));
  reader.readAsDataURL(file);
}

function clearImage(slotName) {
  const slot = imageSlots[slotName]; state[slot.stateKey] = null; slot.input.value = "";
  slot.preview.removeAttribute("src"); slot.preview.hidden = true; slot.shade.hidden = true;
  slot.remove.hidden = true; slot.prompt.hidden = false;
  slot.dropzone.setAttribute("aria-label", emptyAria(slotName));
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
  await loadRuntimeSettings();
  if (!state.engineReady) { showError(t("stillPreparing")); return; }
  setBusy(true); show("workingState"); state.currentStage = "analysis";
  state.currentJobMessage = t("gettingReady"); state.resultElapsed = null; state.resultUnderstood = "";
  updateProgress(4); updatePipeline("analysis"); elements.progressMessage.textContent = t("gettingReady");
  startCountdown();
  try {
    const body = {
      prompt: elements.prompt.value, mode: $('input[name="mode"]:checked').value,
      creation_mode: state.creationMode, duration_seconds: Number(elements.duration.value),
      seamless_loop: state.creationMode === "animate" && elements.seamlessLoop.checked,
      input_image_data_url: state.imageDataUrl, target_image_data_url: state.targetImageDataUrl,
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
$("#remix").addEventListener("click", () => {
  if (state.busy) return; const modes = ["fast", "fun", "wow"];
  const selected = $('input[name="mode"]:checked'); const next = modes[(modes.indexOf(selected.value) + 1) % modes.length];
  document.querySelector(`input[name="mode"][value="${next}"]`).checked = true; selectMode(next); submit();
});

async function loadSystem() {
  try {
    state.system = await readJson(await fetch("/api/system", {cache: "no-store"})); renderSystem();
  } catch {
    elements.systemLabel.textContent = t("demoMode"); elements.systemPanel.textContent = t("systemError");
  }
}

applyLanguage("ja"); selectCreationMode("transition");
Promise.allSettled([loadRuntimeSettings(), loadSystem()]);
