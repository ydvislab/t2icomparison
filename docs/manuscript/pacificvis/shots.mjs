// Screenshots of the audit tool for the PacificVis paper (cases of Sec. 6 and the interface figure).
// Usage: node shots.mjs [baseURL] [outDir]   (headless Edge or Chrome via the DevTools protocol; the tool must be served,
// e.g. http://localhost:8772/ through the tunnel). Each shot sets the analysis state with the page's own functions.
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, existsSync } from "node:fs";

const BASE = process.argv[2] || "http://localhost:8772/";
const OUT = process.argv[3] || "figures";
const W = 1680, H = 1000, SCALE = 2, PORT = 9339;
const BROWSERS = ["C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Google/Chrome/Application/chrome.exe"];

// state for each shot: a function body evaluated in the page (async allowed)
const SHOTS = {
  "interface_klein_chain": `setPair("G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"); toggleMember("G08_klein4b"); pick(SUBJ.findIndex(s => s.name === "a doctor"), "sat");`,
  "case61_clip_medium": `setPair("G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"); toggleMember("G08_klein4b"); pick(SUBJ.findIndex(s => s.name === "a house"), "medium");`,
  "case61_siglip_medium": `setPair("G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"); toggleMember("G08_klein4b"); setEncoder("siglip"); pick(SUBJ.findIndex(s => s.name === "a house"), "medium");`,
  "case62_turbo_horse": `setPair("G02_sdxl", "G03_sdxl_turbo"); pick(SUBJ.findIndex(s => s.name === "a horse"), "sat");`,
  "case62_turbo_bird": `setPair("G02_sdxl", "G03_sdxl_turbo"); pick(SUBJ.findIndex(s => s.name === "a bird on a branch"), "sat");`,
  "case63_rewrite_bg": `setPair("G05_flux2_dev", "G05_flux2_dev__mistral"); const si = R.bg.cells.slice().sort((a, b) => b.d - a.d)[0].si; pick(si, "bg");`,
  "case64_statements": `setPair("G02_sdxl", "G03_sdxl_turbo"); st.main = "statements"; panelControls(); buildMap(); pick(SUBJ.findIndex(s => s.name === "a restaurant"), "bg");`,
  "case64_trail": `setPair("G02_sdxl", "G03_sdxl_turbo"); st.stSel = STATEMENTS.find(s => s.A === "G02_sdxl" && s.B === "G03_sdxl_turbo" && s.vlm === "mistral" && s.text.includes("arched windows")); st.main = "trail"; st.trailK = 0; panelControls(); buildMap(); pick(st.stSel.si, "bg"); drawTrail();`,
};

const exe = BROWSERS.find(existsSync);
if (!exe) throw new Error("no Edge or Chrome found");
const proc = spawn(exe, ["--headless=new", `--remote-debugging-port=${PORT}`, "--disable-gpu", "--hide-scrollbars", `--window-size=${W},${H}`,
  `--user-data-dir=${process.env.TEMP || "/tmp"}/shots-profile`, "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let i = 0; i < 50 && !target; i++) { await sleep(200); try { target = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json(); } catch (e) { /* not up yet */ } }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r, { once: true }));
let id = 0; const pending = new Map();
ws.addEventListener("message", e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const cdp = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJS = async expr => { const r = await cdp("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result?.result?.value; };

await cdp("Page.enable"); await cdp("Runtime.enable");
await cdp("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: SCALE, mobile: false });
await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
mkdirSync(OUT, { recursive: true });
for (const [name, setup] of Object.entries(SHOTS)) {
  await cdp("Page.navigate", { url: BASE + "?figure" });
  for (let i = 0; i < 100; i++) { await sleep(200); if (await evalJS(`typeof R !== "undefined" && R !== null && document.readyState === "complete"`)) break; }
  await sleep(800);
  await evalJS(`(async () => { ${setup} })()`);
  await sleep(2500);   // transitions and image loading
  const r = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, "base64"));
  console.log("wrote", `${OUT}/${name}.png`);
}
ws.close(); proc.kill();
