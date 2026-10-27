// Case 6.5 of the PacificVis paper, computational part: define two aspects in words in the running audit tool, score
// every image with the in-browser CLIP text encoder, and read the contrasts. The in-tool human check is NOT done here;
// it must be done by a person in the tool. Usage: node case65.mjs [baseURL]   (prints JSON; writes figures/case65_*.png)
import { spawn } from "node:child_process";
import { mkdirSync, writeFileSync, existsSync } from "node:fs";

const BASE = process.argv[2] || "http://localhost:8772/";
const W = 1680, H = 1000, PORT = 9341;
const exe = ["C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "C:/Program Files/Microsoft/Edge/Application/msedge.exe"].find(existsSync);
const proc = spawn(exe, ["--headless=new", `--remote-debugging-port=${PORT}`, "--disable-gpu", "--hide-scrollbars", `--window-size=${W},${H}`,
  `--user-data-dir=${process.env.TEMP || "/tmp"}/case65-profile`, "about:blank"], { stdio: "ignore" });
process.on("exit", () => { try { proc.kill(); } catch (e) { /* already gone */ } });   // a failed run must not leave the headless browser holding the port
const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let i = 0; i < 50 && !target; i++) { await sleep(200); try { target = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json(); } catch (e) { /* not up yet */ } }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r, { once: true }));
let id = 0; const pending = new Map();
ws.addEventListener("message", e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const cdp = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJS = async expr => { const r = await cdp("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 600)); return r.result?.result?.value; };

await cdp("Page.enable"); await cdp("Runtime.enable"); await cdp("Network.enable"); await cdp("Network.setCacheDisabled", { cacheDisabled: true });
await cdp("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 2, mobile: false });
await cdp("Page.navigate", { url: BASE + "?figure" });
for (let i = 0; i < 100; i++) { await sleep(200); if (await evalJS(`typeof R !== "undefined" && R !== null && document.readyState === "complete"`)) break; }
await evalJS(`localStorage.removeItem("auditUserAspects")`);

// define both aspects with the tool's own functions (the same path as the "+" dialog)
const out = await evalJS(`(async () => {
  const say = () => {};
  await uaEmb(say); await uaEncoder(say); await uaSelfCheck();
  const defs = [["night", "a scene in daylight", "a scene at night"], ["detail", "a simple image with little detail", "a highly detailed, intricate image"]];
  const keys = {};
  for (const [name, left, right] of defs) {
    const [tl, tr] = await UA.enc([left, right]);
    const key = "u_" + name;
    uaInstall({ key, name, left, right, scores: uaScore(tl, tr), check: null });
    keys[name] = key;
  }
  const read = (A, B) => { const Rr = contrast(A, B); return Object.fromEntries(Object.entries(keys).map(([n, k]) => { const p = Rr[k].pool, c = Rr[k].cells;
    return [n, { shift: +p.d.toFixed(2), shiftCI: [+p.dlo.toFixed(2), +p.dhi.toFixed(2)], ratio: +Math.exp(p.lr).toFixed(2), ratioCI: [+Math.exp(p.llo).toFixed(2), +Math.exp(p.lhi).toFixed(2)],
      subjectsUp: c.filter(x => x.d >= .5).length, subjectsDown: c.filter(x => x.d <= -.5).length, valid: valid(k, A, B) }]; })); };
  return { selfCheck: UA.checked, scale: Object.fromEntries(Object.entries(keys).map(([n, k]) => [n, +META.scale[k].toFixed(4)])),
    guidance: read("G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"), distillation: read("G07_klein_base4b_cfg1", "G08_klein4b"),
    sdxlTurbo: read("G02_sdxl", "G03_sdxl_turbo"), fluxRewrite: read("G05_flux2_dev", "G05_flux2_dev__mistral") };
})()`);
console.log(JSON.stringify(out, null, 1));

// screenshot: the klein chain on the new "night" aspect, marked not validated
await evalJS(`(async () => { buildScatters(); setPair("G07_klein_base4b_cfg1", "G06_klein_base4b_cfg4"); toggleMember("G08_klein4b"); pick(SUBJ.findIndex(s => s.name === "a city street"), "u_night"); })()`);
await sleep(3000);
mkdirSync("figures", { recursive: true });
const r = await cdp("Page.captureScreenshot", { format: "png" });
writeFileSync("figures/case65_night.png", Buffer.from(r.result.data, "base64"));
await evalJS(`localStorage.removeItem("auditUserAspects")`);
ws.close(); proc.kill();
