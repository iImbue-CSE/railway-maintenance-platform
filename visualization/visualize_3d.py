"""Create a browser-based 3D railway digital-twin demonstration."""

from pathlib import Path


def write_3d_demo_html(output: str | Path = "railway_model_3d.html") -> Path:
    """Write a self-contained Three.js demo backed by the RailSync scenario."""
    output_path = Path(output)
    html = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RailSync 3D railway digital twin</title>
<style>
  :root { color-scheme: dark; }
  body { margin: 0; overflow: hidden; font-family: system-ui, sans-serif; background: #07111f; color: #e5eefb; }
  #hud { position: fixed; z-index: 2; top: 16px; left: 16px; width: min(430px, calc(100vw - 32px)); max-height: calc(100vh - 32px);
    padding: 16px; border: 1px solid #334155; border-radius: 12px; background: rgba(7, 17, 31, .9);
    box-shadow: 0 12px 35px #0007; overflow: hidden; }
  #hud.dragging { opacity: .82; cursor: grabbing; }
  #hud-header { display: flex; align-items: flex-start; gap: 10px; margin: -4px -4px 8px; padding: 4px; cursor: grab; user-select: none; }
  #hud-header:active { cursor: grabbing; }
  #hud-title { flex: 1; }
  h1 { margin: 0 0 6px; font-size: 21px; }
  #minimize { flex: 0 0 auto; margin: 0; padding: 5px 9px; background: #334155; font-size: 16px; line-height: 1; }
  #hud.collapsed { width: 245px; max-height: 60px; }
  #hud.collapsed #hud-content { display: none; }
  p { margin: 6px 0 12px; color: #b6c5da; font-size: 14px; }
  button { margin: 3px 4px 3px 0; padding: 8px 11px; color: #f8fafc; background: #1e40af; border: 0; border-radius: 7px; cursor: pointer; }
  button:hover { background: #2563eb; }
  button:disabled { opacity: .5; cursor: default; }
  #status { margin: 10px 0; padding: 9px; border-radius: 7px; background: #172554; font-weight: 650; }
  #notice { min-height: 20px; margin: 8px 0; padding: 9px; border-radius: 7px; background: #7c2d12; color: #ffedd5; font-weight: 700; }
  #controls, #views { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 8px; }
  #controls label { color: #cbd5e1; font-size: 13px; }
  #speed { width: 100px; vertical-align: middle; }
  #clock { margin-left: auto; color: #93c5fd; font-variant-numeric: tabular-nums; }
  #progress { height: 8px; margin-top: 10px; border-radius: 8px; background: #1e293b; overflow: hidden; }
  #progress-fill { width: 0%; height: 100%; background: linear-gradient(90deg, #f59e0b, #38bdf8); transition: width .2s; }
  #timeline { max-height: 145px; overflow: auto; padding-left: 22px; margin: 7px 0 0; color: #cbd5e1; font-size: 13px; }
  #legend { position: fixed; z-index: 2; right: 16px; bottom: 16px; padding: 9px 12px; border-radius: 8px;
    background: rgba(7, 17, 31, .85); color: #cbd5e1; font-size: 13px; }
  #ops { position: fixed; z-index: 2; top: 16px; right: 16px; width: 250px; padding: 14px; border: 1px solid #334155;
    border-radius: 12px; background: rgba(7, 17, 31, .9); box-shadow: 0 12px 35px #0007; }
  #ops.dragging { opacity: .82; cursor: grabbing; }
  #ops-header { display: flex; align-items: center; justify-content: space-between; margin: -4px -4px 8px; padding: 4px;
    cursor: grab; user-select: none; }
  #ops-header:active { cursor: grabbing; }
  #ops-header h2 { margin: 0; }
  #ops-minimize { margin: 0; padding: 4px 8px; background: #334155; font-size: 15px; line-height: 1; }
  #ops.collapsed { width: 245px; }
  #ops.collapsed #ops-content { display: none; }
  #ops h2 { margin: 0 0 8px; font-size: 16px; color: #93c5fd; }
  #mission { margin: 0 0 10px; padding: 9px; border-radius: 7px; background: #172554; font-size: 13px; line-height: 1.35; }
  #telemetry { display: grid; grid-template-columns: 1fr auto; gap: 5px 10px; margin: 0 0 10px; font-size: 12px; color: #cbd5e1; }
  #telemetry strong { color: #f8fafc; font-variant-numeric: tabular-nums; }
  #job-card { margin: 0 0 10px; padding: 9px; border: 1px solid #334155; border-radius: 7px; background: #0f1f38; font-size: 12px; }
  #job-card h3 { margin: 0 0 7px; color: #93c5fd; font-size: 13px; }
  #job-details { display: grid; grid-template-columns: 1fr auto; gap: 4px 10px; color: #cbd5e1; }
  #job-details strong { color: #f8fafc; text-align: right; }
  #job-feasibility.feasible { color: #86efac; }
  #job-feasibility.infeasible { color: #fca5a5; }
  #job-reason { margin-top: 7px; color: #cbd5e1; line-height: 1.35; }
  #manual { border-top: 1px solid #334155; padding-top: 8px; }
  #manual button { width: calc(50% - 6px); font-size: 12px; }
  #track-help { position: fixed; z-index: 2; left: 50%; bottom: 16px; transform: translateX(-50%); padding: 8px 12px;
    border-radius: 8px; background: rgba(7, 17, 31, .8); color: #cbd5e1; font-size: 12px; }
  .swatch { display: inline-block; width: 11px; height: 11px; margin-right: 4px; border-radius: 50%; }
</style>
</head>
<body>
<section id="hud">
  <div id="hud-header">
    <div id="hud-title">
      <h1>RailSync 3D railway digital twin</h1>
      <p>Drag this header to move the panel. Hold left-click and drag the scene to orbit; right-drag to pan; scroll to zoom.</p>
    </div>
    <button id="minimize" title="Minimize controls" aria-label="Minimize controls">−</button>
  </div>
  <div id="hud-content">
    <button id="start">Start simulation</button>
    <button id="conflict">Test blocked route</button>
    <button id="reset">Reset</button>
    <div id="controls">
      <button id="pause">Pause</button>
      <label>Speed <input id="speed" type="range" min="0.5" max="3" step="0.5" value="1"> <span id="speed-value">1x</span></label>
      <span id="clock">Clock 00:00</span>
    </div>
    <div id="views">
      <button data-view="overview">Overview</button>
      <button data-view="station">Station B</button>
      <button data-view="vehicles">Vehicles</button>
    </div>
    <div id="status">Ready to start the maintenance simulation.</div>
    <div id="notice" hidden></div>
    <div id="progress"><div id="progress-fill"></div></div>
    <ol id="timeline"></ol>
  </div>
</section>
<aside id="ops">
  <div id="ops-header">
    <h2>OPERATIONS CONSOLE</h2>
    <button id="ops-minimize" title="Minimize operations console" aria-label="Minimize operations console">−</button>
  </div>
  <div id="ops-content">
    <div id="mission">Mission: move M1 to C, protect T1 from the maintenance block, and finish with both vehicles safe.</div>
    <div id="telemetry">
      <span>M1 location</span><strong id="m1-location">Station A</strong>
      <span>M2 location</span><strong id="m2-location">Station A</strong>
      <span>T1 location</span><strong id="t1-location">Station A</strong>
      <span>B-C status</span><strong id="bc-status">BLOCKED</strong>
      <span>Signal B</span><strong id="signal-status">RED</strong>
    </div>
    <div id="job-card">
      <h3>MAINTENANCE JOB CARD</h3>
      <div id="job-details">
        <span>Job ID</span><strong id="job-id">J-204</strong>
        <span>Location</span><strong id="job-location">Station C</strong>
        <span>Start time</span><strong id="job-start">08:30</strong>
        <span>Duration</span><strong id="job-duration">60 min</strong>
        <span>Assigned machine</span><strong id="job-machine">M1</strong>
        <span>Feasibility</span><strong id="job-feasibility" class="feasible">FEASIBLE</strong>
      </div>
      <div id="job-reason">Checking route and track reservations…</div>
    </div>
    <div id="manual">
      <h2>MANUAL MOVEMENT</h2>
      <button id="m1-ab">M1 A → B</button><button id="m1-bc">M1 B → C</button>
      <button id="t1-ab">T1 A → B</button><button id="t1-bc">T1 B → C</button>
      <button id="t1-ac">T1 alternate A → C</button>
    </div>
  </div>
</aside>
<div id="track-help">Click a track to inspect it and toggle a maintenance block.</div>
<div id="legend">
  <span class="swatch" style="background:#f59e0b"></span>M1 maintenance machine
  <span class="swatch" style="background:#84cc16"></span>M2 maintenance machine
  <span class="swatch" style="background:#38bdf8"></span>T1 passenger train
  <span class="swatch" style="background:#ef4444"></span>blocked track
</div>
<script type="importmap">
{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js",
              "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/" } }
</script>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07111f);
scene.fog = new THREE.Fog(0x07111f, 500, 1100);
const camera = new THREE.PerspectiveCamera(48, innerWidth / innerHeight, 1, 2000);
camera.position.set(260, 210, 360);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 0);
controls.enableDamping = false;
controls.enableRotate = true;
controls.enablePan = true;
controls.enableZoom = true;
controls.mouseButtons.LEFT = THREE.MOUSE.ROTATE;
controls.mouseButtons.MIDDLE = THREE.MOUSE.DOLLY;
controls.mouseButtons.RIGHT = THREE.MOUSE.PAN;
controls.touches.ONE = THREE.TOUCH.ROTATE;
controls.touches.TWO = THREE.TOUCH.DOLLY_PAN;

scene.add(new THREE.HemisphereLight(0xb9d8ff, 0x162033, 2.2));
const sun = new THREE.DirectionalLight(0xffffff, 2.5);
sun.position.set(120, 260, 160);
sun.castShadow = true;
scene.add(sun);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(1000, 700),
  new THREE.MeshStandardMaterial({ color: 0x102b2c, roughness: 1 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -5;
ground.receiveShadow = true;
scene.add(ground);

const points = { A: new THREE.Vector3(-180, 0, 0), B: new THREE.Vector3(0, 0, 0), C: new THREE.Vector3(180, 0, 0) };
const trackMeshes = {};
const stationMeshes = {};
const signalMeshes = {};
const alternateCurve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-180, 0, 0),
  new THREE.Vector3(-176, 0, -14),
  new THREE.Vector3(-160, 0, -34),
  new THREE.Vector3(-125, 0, -52),
  new THREE.Vector3(0, 0, -58),
  new THREE.Vector3(125, 0, -52),
  new THREE.Vector3(160, 0, -34),
  new THREE.Vector3(176, 0, -14),
  new THREE.Vector3(180, 0, 0),
], false, "catmullrom", 0.35);
function makeText(text, color = "#ffffff") {
  const canvas = document.createElement("canvas");
  canvas.width = 512; canvas.height = 128;
  const context = canvas.getContext("2d");
  context.font = "bold 54px system-ui";
  context.textAlign = "center"; context.textBaseline = "middle";
  context.fillStyle = color; context.fillText(text, 256, 64);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
    map: new THREE.CanvasTexture(canvas), transparent: true, depthTest: false
  }));
  sprite.scale.set(70, 18, 1);
  return sprite;
}

function addTrack(id, start, end, blocked, y = 0) {
  if (id === "A-C") {
    addCurvedTrack(id, blocked);
    return;
  }
  const a = points[start].clone(); const b = points[end].clone();
  const zOffset = id === "A-C" ? -70 : 0;
  a.z += zOffset; b.z += zOffset;
  a.y = y; b.y = y;
  const direction = b.clone().sub(a);
  const center = a.clone().add(b).multiplyScalar(.5);
  const angle = Math.atan2(direction.z, direction.x);
  const ballast = new THREE.Mesh(
    new THREE.BoxGeometry(direction.length() + 18, 2, 18),
    new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 1 })
  );
  ballast.position.copy(center); ballast.rotation.y = angle;
  ballast.castShadow = true; ballast.receiveShadow = true; scene.add(ballast);
  const material = new THREE.MeshStandardMaterial({
    color: blocked ? 0xef4444 : 0x38bdf8, metalness: .65, roughness: .35
  });
  const rail = new THREE.Group();
  for (const railOffset of [-5, 5]) {
    const railLine = new THREE.Mesh(new THREE.BoxGeometry(direction.length(), 1.8, 1.5), material);
    railLine.position.set(0, 3, railOffset);
    railLine.castShadow = true; rail.add(railLine);
  }
  for (let x = -direction.length() / 2 + 8; x < direction.length() / 2; x += 18) {
    const sleeper = new THREE.Mesh(
      new THREE.BoxGeometry(5, 1.5, 22),
      new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 1 })
    );
    sleeper.position.set(x, 1, 0); sleeper.castShadow = true; rail.add(sleeper);
  }
  rail.position.copy(center); rail.rotation.y = angle; scene.add(rail);
  trackMeshes[id] = rail;
  const label = makeText(`${id} ${blocked ? "BLOCKED" : "OPEN"}`, blocked ? "#fca5a5" : "#bfdbfe");
  label.position.copy(center); label.position.y = y + 16; label.position.z += id === "A-C" ? -70 : -8;
  scene.add(label); rail.userData.label = label; rail.userData.trackId = id;
}
function addCurvedTrack(id, blocked) {
  const rail = new THREE.Group();
  const material = new THREE.MeshStandardMaterial({
    color: blocked ? 0xef4444 : 0x38bdf8, metalness: .65, roughness: .35
  });
  for (const railOffset of [-5, 5]) {
    const railPath = alternateCurve.getPoints(80).map((point) =>
      new THREE.Vector3(point.x, point.y + 3, point.z + railOffset)
    );
    const geometry = new THREE.TubeGeometry(
      new THREE.CatmullRomCurve3(railPath), 80, 0.9, 8, false
    );
    const railLine = new THREE.Mesh(geometry, material);
    railLine.castShadow = true; rail.add(railLine);
  }
  const sleeperMaterial = new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 1 });
  const ballastMaterial = new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 1 });
  for (let i = 0; i <= 48; i += 1) {
    const t = i / 48;
    const point = alternateCurve.getPoint(t);
    const tangent = alternateCurve.getTangent(t);
    const ballast = new THREE.Mesh(
      new THREE.BoxGeometry(8, 2, 18), ballastMaterial
    );
    ballast.position.copy(point); ballast.position.y = -1;
    ballast.rotation.y = Math.atan2(tangent.z, tangent.x);
    rail.add(ballast);
    const sleeper = new THREE.Mesh(
      new THREE.BoxGeometry(5, 1.5, 22), sleeperMaterial
    );
    sleeper.position.copy(point); sleeper.position.y = 1;
    sleeper.rotation.y = Math.atan2(tangent.z, tangent.x);
    sleeper.castShadow = true; rail.add(sleeper);
  }
  scene.add(rail); trackMeshes[id] = rail;
  const label = makeText(`${id} ${blocked ? "BLOCKED" : "OPEN"}`, blocked ? "#fca5a5" : "#bfdbfe");
  label.position.set(0, 16, -80); scene.add(label);
  rail.userData.label = label; rail.userData.trackId = id;
}
function addConnection(id, start, end, color = 0x38bdf8) {
  const a = start.clone(); const b = end.clone();
  const direction = b.clone().sub(a);
  const center = a.clone().add(b).multiplyScalar(.5);
  const angle = Math.atan2(direction.z, direction.x);
  const ballast = new THREE.Mesh(
    new THREE.BoxGeometry(direction.length() + 10, 2, 18),
    new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 1 })
  );
  ballast.position.copy(center); ballast.rotation.y = angle; scene.add(ballast);
  const rail = new THREE.Group();
  const material = new THREE.MeshStandardMaterial({ color, metalness: .65, roughness: .35 });
  for (const railOffset of [-5, 5]) {
    const railLine = new THREE.Mesh(new THREE.BoxGeometry(direction.length(), 1.8, 1.5), material);
    railLine.position.set(0, 3, railOffset); rail.add(railLine);
  }
  for (let x = -direction.length() / 2 + 8; x < direction.length() / 2; x += 18) {
    const sleeper = new THREE.Mesh(
      new THREE.BoxGeometry(5, 1.5, 22),
      new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 1 })
    );
    sleeper.position.set(x, 1, 0); rail.add(sleeper);
  }
  rail.position.copy(center); rail.rotation.y = angle; scene.add(rail);
  rail.userData.trackId = id;
}
addTrack("A-B", "A", "B", false);
addTrack("B-C", "B", "C", true);
addTrack("A-C", "A", "C", false, -2);
const switchGroup = new THREE.Group();
const switchBase = new THREE.Mesh(
  new THREE.BoxGeometry(24, 2, 20),
  new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: .8 })
);
const switchLever = new THREE.Mesh(
  new THREE.BoxGeometry(18, 1.5, 2),
  new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: .5 })
);
switchLever.position.set(0, 4, 0);
switchGroup.add(switchBase, switchLever);
switchGroup.position.set(-6, 0, -8);
scene.add(switchGroup);
function setSwitch(alternate) {
  switchLever.rotation.y = alternate ? -0.45 : 0;
  switchLever.material.color.set(alternate ? 0x22c55e : 0xfacc15);
}

function addSignal(name, position) {
  const pole = new THREE.Mesh(
    new THREE.CylinderGeometry(1.2, 1.2, 25, 12),
    new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: .7 })
  );
  pole.position.copy(position); pole.position.y = 15; scene.add(pole);
  const light = new THREE.Mesh(
    new THREE.SphereGeometry(4, 20, 20),
    new THREE.MeshStandardMaterial({ color: 0xef4444, emissive: 0x550000, emissiveIntensity: 1.5 })
  );
  light.position.copy(position); light.position.y = 31; scene.add(light);
  signalMeshes[name] = light;
}
addSignal("b", new THREE.Vector3(-18, 0, 14));

function addEnvironment() {
  for (const x of [-300, -250, -110, 100, 260, 315]) {
    const trunk = new THREE.Mesh(
      new THREE.CylinderGeometry(2, 3, 18, 10),
      new THREE.MeshStandardMaterial({ color: 0x78350f })
    );
    trunk.position.set(x, 6, 100); scene.add(trunk);
    const leaves = new THREE.Mesh(
      new THREE.ConeGeometry(15, 34, 12),
      new THREE.MeshStandardMaterial({ color: 0x166534, roughness: 1 })
    );
    leaves.position.set(x, 30, 100); leaves.castShadow = true; scene.add(leaves);
  }
  const platform = new THREE.Mesh(
    new THREE.BoxGeometry(115, 5, 35),
    new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: .8 })
  );
  platform.position.set(0, 3, 34); platform.castShadow = true; scene.add(platform);
  const roof = new THREE.Mesh(
    new THREE.BoxGeometry(105, 3, 28),
    new THREE.MeshStandardMaterial({ color: 0x1e3a8a, metalness: .2 })
  );
  roof.position.set(0, 52, 34); roof.castShadow = true; scene.add(roof);
  for (const x of [-45, 0, 45]) {
    const column = new THREE.Mesh(
      new THREE.CylinderGeometry(1.5, 1.5, 48, 10),
      new THREE.MeshStandardMaterial({ color: 0xe2e8f0 })
    );
    column.position.set(x, 27, 34); scene.add(column);
  }
}
addEnvironment();

for (const [name, position] of Object.entries(points)) {
  const station = new THREE.Mesh(
    new THREE.CylinderGeometry(17, 17, 10, 32),
    new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: .45 })
  );
  station.position.copy(position); station.position.y = 8;
  station.castShadow = true; scene.add(station); stationMeshes[name] = station;
  const label = makeText(`Station ${name}`, "#f8fafc");
  label.position.copy(position); label.position.y = 28; scene.add(label);
}

function makeVehicle(color, label, passenger) {
  const vehicle = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(passenger ? 40 : 30, 13, 13),
    new THREE.MeshStandardMaterial({ color, metalness: .15, roughness: .55 })
  );
  body.position.y = 14; body.castShadow = true; vehicle.add(body);
  if (passenger) {
    const stripe = new THREE.Mesh(
      new THREE.BoxGeometry(41, 2.5, 13.5),
      new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: .35 })
    );
    stripe.position.set(0, 16, 0); vehicle.add(stripe);
  } else {
    const beacon = new THREE.Mesh(
      new THREE.CylinderGeometry(3, 3, 2, 16),
      new THREE.MeshStandardMaterial({ color: 0xdc2626, emissive: 0x550000 })
    );
    beacon.position.set(-7, 32, 0); vehicle.add(beacon);
    const plow = new THREE.Mesh(
      new THREE.ConeGeometry(7, 12, 4),
      new THREE.MeshStandardMaterial({ color: 0x92400e, metalness: .35 })
    );
    plow.rotation.z = Math.PI / 2; plow.position.set(-19, 10, 0); vehicle.add(plow);
  }
  const cab = new THREE.Mesh(
    new THREE.BoxGeometry(passenger ? 13 : 12, 10, 12),
    new THREE.MeshStandardMaterial({ color: passenger ? 0xbae6fd : 0xfef3c7, roughness: .3 })
  );
  cab.position.set(passenger ? 13 : 3, 25, 0); cab.castShadow = true; vehicle.add(cab);
  for (const x of (passenger ? [-13, 13] : [-9, 9])) {
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(3.5, 3.5, 15, 16), new THREE.MeshStandardMaterial({ color: 0x111827 }));
    wheel.rotation.x = Math.PI / 2; wheel.position.set(x, 5, 0); vehicle.add(wheel);
  }
  const name = makeText(label, passenger ? "#7dd3fc" : "#fbbf24");
  name.position.y = 48; vehicle.add(name);
  scene.add(vehicle); return vehicle;
}
const machine = makeVehicle(0xf59e0b, "M1 • MAINTENANCE", false);
const train = makeVehicle(0x0ea5e9, "T1 • PASSENGER", true);
train.userData.reverseModel = true;

const status = document.getElementById("status");
const notice = document.getElementById("notice");
const timeline = document.getElementById("timeline");
const start = document.getElementById("start");
const conflict = document.getElementById("conflict");
const reset = document.getElementById("reset");
const pause = document.getElementById("pause");
const speed = document.getElementById("speed");
const speedValue = document.getElementById("speed-value");
const clock = document.getElementById("clock");
const progressFill = document.getElementById("progress-fill");
const m1Location = document.getElementById("m1-location");
const t1Location = document.getElementById("t1-location");
const bcStatus = document.getElementById("bc-status");
const signalStatus = document.getElementById("signal-status");
const mission = document.getElementById("mission");
const ops = document.getElementById("ops");
const m1ab = document.getElementById("m1-ab");
const m1bc = document.getElementById("m1-bc");
const t1ab = document.getElementById("t1-ab");
const t1bc = document.getElementById("t1-bc");
const t1ac = document.getElementById("t1-ac");
const hud = document.getElementById("hud");
const hudHeader = document.getElementById("hud-header");
const minimize = document.getElementById("minimize");
const opsHeader = document.getElementById("ops-header");
const opsMinimize = document.getElementById("ops-minimize");
let animationId = 0;
let timers = [];
let running = false;
let paused = false;
let simulationSeconds = 0;
let speedMultiplier = 1;
let clockStarted = 0;
let draggingHud = false;
let dragOffsetX = 0;
let dragOffsetY = 0;
let draggingOps = false;
let opsOffsetX = 0;
let opsOffsetY = 0;

function addEvent(text) {
  const item = document.createElement("li"); item.textContent = text; timeline.appendChild(item);
  timeline.scrollTop = timeline.scrollHeight;
}
function showNotice(text, color = "#7c2d12") {
  notice.hidden = false;
  notice.textContent = text;
  notice.style.background = color;
}
function setProgress(percent) {
  progressFill.style.width = `${Math.max(0, Math.min(100, percent))}%`;
}
function updateClock() {
  if (running && !paused) simulationSeconds = (performance.now() - clockStarted) / 1000;
  const minutes = String(Math.floor(simulationSeconds / 60)).padStart(2, "0");
  const seconds = String(Math.floor(simulationSeconds % 60)).padStart(2, "0");
  clock.textContent = `Clock ${minutes}:${seconds}`;
}
function startClock() {
  simulationSeconds = 0; clockStarted = performance.now(); updateClock();
}
function scaledDuration(duration) {
  return duration / speedMultiplier;
}
function setSignal(color, state) {
  const signal = signalMeshes[state];
  if (signal) signal.material.color.set(color);
  signalStatus.textContent = color === 0x22c55e ? "GREEN" : color === 0xf59e0b ? "YELLOW" : "RED";
}
function positionVehicle(vehicle, from, to, progress, zOffset = 0) {
  const position = points[from].clone().lerp(points[to], progress);
  position.z += zOffset; vehicle.position.copy(position);
  const direction = points[to].clone().sub(points[from]);
  orientVehicle(vehicle, direction);
  vehicle.rotation.x = 0;
  vehicle.rotation.z = 0;
}
function orientVehicle(vehicle, direction) {
  const forwardAngle = Math.atan2(-direction.z, direction.x);
  const modelFlip = vehicle.userData.reverseModel ? Math.PI : 0;
  vehicle.rotation.y = forwardAngle + Math.PI + modelFlip;
}
function animateVehicle(vehicle, from, to, duration, done, zOffset = 0) {
  let started = performance.now();
  let previous = started;
  function frame(now) {
    if (paused) started += now - previous;
    previous = now;
    const progress = Math.min((now - started) / scaledDuration(duration), 1);
    positionVehicle(vehicle, from, to, progress, zOffset);
    if (progress < 1) animationId = requestAnimationFrame(frame); else done?.();
  }
  animationId = requestAnimationFrame(frame);
}
function animateOffset(vehicle, fromZ, toZ, duration, done) {
  let started = performance.now();
  let previous = started;
  function frame(now) {
    if (paused) started += now - previous;
    previous = now;
    const progress = Math.min((now - started) / scaledDuration(duration), 1);
    vehicle.position.z = fromZ + (toZ - fromZ) * progress;
    if (progress < 1) animationId = requestAnimationFrame(frame); else done?.();
  }
  animationId = requestAnimationFrame(frame);
}
function animateAlternate(vehicle, duration, done) {
  let started = performance.now();
  let previous = started;
  function frame(now) {
    if (paused) started += now - previous;
    previous = now;
    const progress = Math.min((now - started) / scaledDuration(duration), 1);
    const position = alternateCurve.getPoint(progress);
    position.y = 0;
    const tangent = alternateCurve.getTangent(progress);
    vehicle.position.copy(position);
    orientVehicle(vehicle, tangent);
    vehicle.rotation.x = 0;
    vehicle.rotation.z = 0;
    if (progress < 1) requestAnimationFrame(frame); else done?.();
  }
  requestAnimationFrame(frame);
}
function animateRoute(vehicle, route, durations, done, zOffset = 0, index = 0) {
  if (index >= route.length - 1) { done?.(); return; }
  animateVehicle(vehicle, route[index], route[index + 1], durations[index], () => {
    animateRoute(vehicle, route, durations, done, zOffset, index + 1);
  }, zOffset);
}
function setBlocked(blocked) {
  const track = trackMeshes["B-C"];
  track.children.forEach((part) => {
    if (part.isMesh && part.geometry.type === "BoxGeometry" && part.position.z !== 0) {
      part.material.color.set(blocked ? 0xef4444 : 0x38bdf8);
    }
  });
  track.userData.label.material.opacity = blocked ? 1 : .8;
  bcStatus.textContent = blocked ? "BLOCKED" : "OPEN";
  bcStatus.style.color = blocked ? "#fca5a5" : "#86efac";
}
function updateLocation(vehicle, label, position) {
  const names = { A: "Station A", B: "Station B", C: "Station C" };
  if (position) label.textContent = names[position] || position;
}
function manualMove(vehicle, from, to, duration, zOffset, label, onDone) {
  running = true;
  animateVehicle(vehicle, from, to, duration, () => {
    updateLocation(vehicle, label, to); running = false; onDone?.();
  }, zOffset);
}
function runSimulation() {
  resetSimulation(); running = true; start.disabled = true; conflict.disabled = true;
  startClock(); setProgress(0); setSignal(0xf59e0b, "b"); setSwitch(false);
  addEvent("M1 starts at Station A.");
  animateVehicle(machine, "A", "B", 1800, () => {
    updateLocation(machine, m1Location, "B");
    setProgress(20); setSignal(0xef4444, "b");
    addEvent("M1 reached B. Track B-C is under maintenance.");
    setBlocked(true); setSwitch(false);
    showNotice("Track B-C is under maintenance. T1 will wait at B.", "#7c2d12");
    status.textContent = "M1 is travelling B → C; T1 is now travelling A → B.";
    animateVehicle(train, "A", "B", 2200, () => {
      updateLocation(train, t1Location, "B");
      setProgress(45);
      addEvent("T1 reached B and is waiting safely.");
      status.textContent = "T1 is waiting at B while M1 completes the work.";
    }, 0);
    timers.push(setTimeout(() => {
      animateVehicle(machine, "B", "C", 2200, () => {
        updateLocation(machine, m1Location, "C");
        addEvent("M1 reached C. Maintenance is complete.");
        setBlocked(false); setSwitch(false); setSignal(0x22c55e, "b");
        showNotice("Track B-C released. T1 can continue to C.", "#14532d");
        status.textContent = "T1 is continuing from B → C.";
        animateVehicle(train, "B", "C", 2200, () => {
          updateLocation(train, t1Location, "C");
          addEvent("T1 reached C without reversing.");
          status.textContent = "Simulation complete: M1 and T1 reached C safely.";
          running = false; start.disabled = false; conflict.disabled = false;
        }, 0);
      });
    }, scaledDuration(1800)));
  }, 0);
}
function resetSimulation() {
  cancelAnimationFrame(animationId); timers.forEach(clearTimeout); timers = []; running = false;
  paused = false; pause.textContent = "Pause"; simulationSeconds = 0; updateClock();
  machine.position.copy(points.A); train.position.copy(points.A);
  updateLocation(machine, m1Location, "A"); updateLocation(train, t1Location, "A");
  setBlocked(true); setSignal(0xef4444, "b"); setSwitch(false); setProgress(0); timeline.innerHTML = ""; notice.hidden = true;
  status.textContent = "Ready to start the maintenance simulation.";
  start.disabled = false; conflict.disabled = false;
}
start.addEventListener("click", runSimulation);
reset.addEventListener("click", resetSimulation);
conflict.addEventListener("click", () => {
  resetSimulation(); running = true; start.disabled = true; conflict.disabled = true;
  startClock(); setProgress(5); setSignal(0xef4444, "b"); setSwitch(true);
  addEvent("T1 requested route A → B → C.");
  setBlocked(true);
  showNotice("Track B-C is under maintenance. T1 is taking alternate route A-C.", "#92400e");
  status.textContent = "T1 is travelling directly on the alternate A-C track.";
  addEvent("Maintenance warning shown to the train controller.");
  addEvent("T1 switched directly to alternate route A-C.");
  animateAlternate(train, 6000, () => {
    train.position.copy(alternateCurve.getPoint(1));
    updateLocation(train, t1Location, "C");
    setProgress(100);
    addEvent("T1 reached C using alternate A-C.");
    status.textContent = "Conflict test complete: train avoided the maintenance block.";
    showNotice("Safe reroute complete: T1 avoided blocked B-C.", "#14532d");
    running = false; start.disabled = false; conflict.disabled = false;
  });
});
m1ab.addEventListener("click", () => {
  showNotice("Manual command: M1 moving from A to B.", "#1e3a8a");
  manualMove(machine, "A", "B", 1800, 0, m1Location, () => { setBlocked(true); setSignal(0xef4444, "b"); });
});
m1bc.addEventListener("click", () => {
  if (bcStatus.textContent === "BLOCKED") {
    showNotice("M1 cannot enter B-C while it is blocked.", "#7c2d12"); return;
  }
  showNotice("Manual command: M1 moving from B to C.", "#1e3a8a");
  manualMove(machine, "B", "C", 1800, 0, m1Location);
});
t1ab.addEventListener("click", () => {
  showNotice("Manual command: T1 moving from A to B.", "#1e3a8a");
  manualMove(train, "A", "B", 1800, 0, t1Location);
});
t1bc.addEventListener("click", () => {
  if (bcStatus.textContent === "BLOCKED") {
    showNotice("T1 cannot enter B-C. Use the alternate A-C command.", "#7c2d12"); return;
  }
  showNotice("Manual command: T1 moving from B to C.", "#1e3a8a");
  manualMove(train, "B", "C", 1800, 0, t1Location);
});
t1ac.addEventListener("click", () => {
  setSwitch(true); showNotice("Manual command: T1 taking alternate A-C.", "#14532d");
  running = true;
  animateAlternate(train, 5200, () => {
    train.position.copy(alternateCurve.getPoint(1));
    updateLocation(train, t1Location, "C"); running = false;
  });
});
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
renderer.domElement.addEventListener("click", (event) => {
  pointer.x = (event.clientX / innerWidth) * 2 - 1;
  pointer.y = -(event.clientY / innerHeight) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(Object.values(trackMeshes).flatMap((group) => group.children), false)[0];
  if (!hit) return;
  const track = Object.values(trackMeshes).find((group) => group.children.includes(hit.object));
  if (!track) return;
  if (track === trackMeshes["B-C"]) {
    const blocked = bcStatus.textContent !== "BLOCKED";
    setBlocked(blocked); setSignal(blocked ? 0xef4444 : 0x22c55e, "b");
    showNotice(blocked ? "Operator action: B-C placed under maintenance." : "Operator action: B-C released.", blocked ? "#7c2d12" : "#14532d");
    mission.textContent = blocked ? "Mission update: protect T1 from blocked B-C." : "Mission update: B-C is open for movement.";
  } else {
    showNotice(`${track.userData.trackId} selected.`, "#1e3a8a");
  }
});
pause.addEventListener("click", () => {
  if (!running) return;
  paused = !paused;
  pause.textContent = paused ? "Resume" : "Pause";
  status.textContent = paused ? "Simulation paused." : "Simulation resumed.";
  if (!paused) {
    clockStarted = performance.now() - simulationSeconds * 1000;
  }
});
speed.addEventListener("input", () => {
  speedMultiplier = Number(speed.value);
  speedValue.textContent = `${speedMultiplier}x`;
});
minimize.addEventListener("click", (event) => {
  event.stopPropagation();
  hud.classList.toggle("collapsed");
  minimize.textContent = hud.classList.contains("collapsed") ? "+" : "−";
  minimize.title = hud.classList.contains("collapsed") ? "Expand controls" : "Minimize controls";
});
hudHeader.addEventListener("pointerdown", (event) => {
  if (event.target === minimize) return;
  draggingHud = true;
  const rect = hud.getBoundingClientRect();
  dragOffsetX = event.clientX - rect.left;
  dragOffsetY = event.clientY - rect.top;
  hud.classList.add("dragging");
  hudHeader.setPointerCapture(event.pointerId);
});
hudHeader.addEventListener("pointermove", (event) => {
  if (!draggingHud) return;
  const left = Math.max(8, Math.min(innerWidth - hud.offsetWidth - 8, event.clientX - dragOffsetX));
  const top = Math.max(8, Math.min(innerHeight - 55, event.clientY - dragOffsetY));
  hud.style.left = `${left}px`;
  hud.style.top = `${top}px`;
});
hudHeader.addEventListener("pointerup", (event) => {
  draggingHud = false;
  hud.classList.remove("dragging");
  hudHeader.releasePointerCapture(event.pointerId);
});
opsMinimize.addEventListener("click", (event) => {
  event.stopPropagation();
  ops.classList.toggle("collapsed");
  opsMinimize.textContent = ops.classList.contains("collapsed") ? "+" : "−";
  opsMinimize.title = ops.classList.contains("collapsed")
    ? "Expand operations console" : "Minimize operations console";
});
opsHeader.addEventListener("pointerdown", (event) => {
  if (event.target === opsMinimize) return;
  draggingOps = true;
  const rect = ops.getBoundingClientRect();
  opsOffsetX = event.clientX - rect.left;
  opsOffsetY = event.clientY - rect.top;
  ops.classList.add("dragging");
  opsHeader.setPointerCapture(event.pointerId);
});
opsHeader.addEventListener("pointermove", (event) => {
  if (!draggingOps) return;
  const left = Math.max(8, Math.min(innerWidth - ops.offsetWidth - 8, event.clientX - opsOffsetX));
  const top = Math.max(8, Math.min(innerHeight - 55, event.clientY - opsOffsetY));
  ops.style.left = `${left}px`;
  ops.style.top = `${top}px`;
  ops.style.right = "auto";
});
opsHeader.addEventListener("pointerup", (event) => {
  draggingOps = false;
  ops.classList.remove("dragging");
  opsHeader.releasePointerCapture(event.pointerId);
});
document.querySelectorAll("[data-view]").forEach((button) => {
  button.addEventListener("click", () => {
    const view = button.dataset.view;
    if (view === "overview") { camera.position.set(260, 210, 360); controls.target.set(0, 0, 0); }
    if (view === "station") { camera.position.set(55, 85, 145); controls.target.set(0, 10, 0); }
    if (view === "vehicles") { camera.position.set(80, 55, 105); controls.target.set(30, 12, 0); }
  });
});
resetSimulation();
addEvent("3D scene loaded. Vehicles and tracks are labeled.");

function render() {
  requestAnimationFrame(render); controls.update(); updateClock(); renderer.render(scene, camera);
}
addEvent("Drag to orbit and scroll to zoom.");
addEvent("Use Test blocked route to watch T1 reroute.");
render();
window.addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    path = write_3d_demo_html()
    print(f"Created {path.resolve()}")
