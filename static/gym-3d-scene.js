(function(){
  var canvas = document.getElementById("gym-canvas");
  if (!canvas) return;

  var rect = canvas.parentElement.getBoundingClientRect();
  var w = rect.width;
  var h = Math.min(w * 2/5, 200);
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.height = h + "px";

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x111111);
  scene.fog = new THREE.Fog(0x111111, 30, 50);

  var aspect = canvas.width / canvas.height;
  var camera = new THREE.PerspectiveCamera(40, aspect, 0.1, 100);
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
  renderer.setSize(canvas.width, canvas.height);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;

  /* ---- Lighting ---- */
  scene.add(new THREE.AmbientLight(0xffeedd, 0.3));
  var key = new THREE.DirectionalLight(0xfff0dd, 0.7);
  key.position.set(8, 15, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  key.shadow.camera.near = 1; key.shadow.camera.far = 40;
  key.shadow.camera.left = -12; key.shadow.camera.right = 12;
  key.shadow.camera.top = 12; key.shadow.camera.bottom = -12;
  scene.add(key);
  var fill = new THREE.DirectionalLight(0x88aaff, 0.15);
  fill.position.set(-8, 8, -5);
  scene.add(fill);
  var rim = new THREE.DirectionalLight(0xc8a44e, 0.2);
  rim.position.set(0, 3, -12);
  scene.add(rim);

  /* ---- Materials ---- */
  var floorMat = new THREE.MeshLambertMaterial({color: 0x1c1c1c});
  var rubberMat = new THREE.MeshLambertMaterial({color: 0x222222});
  var wallMat = new THREE.MeshLambertMaterial({color: 0x2a2a2a});
  var frameMat = new THREE.MeshPhongMaterial({color: 0x1a1a1a, specular: 0x333333, shininess: 40});
  var goldMat = new THREE.MeshPhongMaterial({color: 0xc8a44e, specular: 0xffeedd, shininess: 80});
  var padMat = new THREE.MeshLambertMaterial({color: 0x111111});
  var plateMat = new THREE.MeshPhongMaterial({color: 0x888888, specular: 0xcccccc, shininess: 60});
  var redMat = new THREE.MeshPhongMaterial({color: 0x993333, specular: 0xcc6666, shininess: 30});
  var rackMat = new THREE.MeshPhongMaterial({color: 0x0a0a0a, specular: 0x222222, shininess: 20});
  var mirrorMat = new THREE.MeshPhongMaterial({color: 0x334455, specular: 0xaabbcc, shininess: 100, opacity: 0.6, transparent: true});
  var lightStripMat = new THREE.MeshBasicMaterial({color: 0xc8a44e, transparent: true, opacity: 0.6});

  /* ---- Floor ---- */
  var floor = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  /* Rubber mats under free weight area */
  var rubberZone = new THREE.Mesh(new THREE.PlaneGeometry(8, 6), rubberMat);
  rubberZone.rotation.x = -Math.PI / 2;
  rubberZone.position.set(-5, 0.01, 5);
  scene.add(rubberZone);

  /* ---- Walls ---- */
  function addWall(w, h, x, y, z, ry) {
    var m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 0.12), wallMat);
    m.position.set(x, y, z);
    if (ry) m.rotation.y = ry;
    m.receiveShadow = true;
    scene.add(m);
  }
  addWall(20, 3.2, 0, 1.6, -10, 0);
  addWall(20, 3.2, 0, 1.6, 10, 0);
  addWall(20, 3.2, -10, 1.6, 0, Math.PI / 2);
  addWall(20, 3.2, 10, 1.6, 0, Math.PI / 2);

  /* Mirror wall (back wall) */
  var mirror = new THREE.Mesh(new THREE.PlaneGeometry(18, 2.2), mirrorMat);
  mirror.position.set(0, 1.5, -9.93);
  scene.add(mirror);

  /* Ceiling light strips */
  for (var li = -8; li <= 8; li += 4) {
    var strip = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.02, 18), lightStripMat);
    strip.position.set(li, 3.15, 0);
    scene.add(strip);
  }

  /* ---- Zone labels on floor ---- */
  function addLabel(text, x, z) {
    var c = document.createElement("canvas");
    c.width = 256; c.height = 32;
    var ctx = c.getContext("2d");
    ctx.fillStyle = "rgba(200,164,78,0.5)";
    ctx.font = "bold 20px Arial";
    ctx.textAlign = "center";
    ctx.fillText(text, 128, 22);
    var s = new THREE.Sprite(new THREE.SpriteMaterial({map: new THREE.CanvasTexture(c), transparent: true}));
    s.scale.set(4, 0.5, 1);
    s.position.set(x, 0.02, z);
    scene.add(s);
  }
  addLabel("SELECTORIZED", -4.5, -7.5);
  addLabel("PLATE LOADED", -4.5, -2);
  addLabel("FREE WEIGHTS", -5, 5);
  addLabel("CARDIO", 5.5, 5);

  /* ---- Selectorized machines (6 units) ---- */
  function addSelectorized(x, z, ry) {
    var g = new THREE.Group();
    // Base frame
    var base = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.08, 1.4), frameMat);
    base.position.y = 0.04; base.castShadow = true; g.add(base);
    // Main upright
    var upright = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.7, 0.12), frameMat);
    upright.position.set(-0.35, 0.93, -0.5); upright.castShadow = true; g.add(upright);
    // Weight stack housing
    var housing = new THREE.Mesh(new THREE.BoxGeometry(0.25, 1.4, 0.3), frameMat);
    housing.position.set(-0.35, 0.78, -0.55); g.add(housing);
    // Weight stack plates
    for (var j = 0; j < 8; j++) {
      var plate = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.04, 0.25), plateMat);
      plate.position.set(-0.35, 0.2 + j * 0.06, -0.55); g.add(plate);
    }
    // Seat
    var seat = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.4), padMat);
    seat.position.set(0.1, 0.5, 0.0); g.add(seat);
    // Back pad
    var back = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.5, 0.06), padMat);
    back.position.set(0.1, 0.8, -0.2); g.add(back);
    // Gold accent stripe
    var accent = new THREE.Mesh(new THREE.BoxGeometry(1.02, 0.02, 0.06), goldMat);
    accent.position.set(0, 0.09, 0.7); g.add(accent);
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }
  for (var si = 0; si < 6; si++) {
    addSelectorized(-7 + si * 2.2, -8, 0.05);
  }

  /* ---- Plate loaded machines (4 units) ---- */
  function addPlateLoaded(x, z, ry) {
    var g = new THREE.Group();
    var base = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.08, 1.6), frameMat);
    base.position.y = 0.04; base.castShadow = true; g.add(base);
    // Main frame posts
    var post1 = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.5, 8), frameMat);
    post1.position.set(-0.4, 0.83, -0.6); post1.castShadow = true; g.add(post1);
    var post2 = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.5, 8), frameMat);
    post2.position.set(0.4, 0.83, -0.6); post2.castShadow = true; g.add(post2);
    // Plate horns
    var horn1 = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.4, 8), plateMat);
    horn1.position.set(-0.5, 1.0, -0.6); horn1.rotation.z = Math.PI / 6; g.add(horn1);
    var horn2 = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.4, 8), plateMat);
    horn2.position.set(0.5, 1.0, -0.6); horn2.rotation.z = -Math.PI / 6; g.add(horn2);
    // Seat
    var seat = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.45), padMat);
    seat.position.set(0, 0.45, 0.15); g.add(seat);
    // Red accent
    var accent = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.3, 0.08), redMat);
    accent.position.set(0, 1.3, -0.6); g.add(accent);
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }
  for (var pi = 0; pi < 4; pi++) {
    addPlateLoaded(-7 + pi * 2.8, -3, 0.05);
  }

  /* ---- Power racks (3 units) ---- */
  function addRack(x, z, ry) {
    var g = new THREE.Group();
    var r = 0.05;
    var hw = 0.7, hd = 0.8, hh = 2.4;
    // 4 uprights
    [[-1,-1],[1,-1],[1,1],[-1,1]].forEach(function(p) {
      var u = new THREE.Mesh(new THREE.BoxGeometry(0.1, hh, 0.1), rackMat);
      u.position.set(p[0] * hw, hh / 2, p[1] * hd); u.castShadow = true; g.add(u);
    });
    // Cross bars top
    var topBar = new THREE.Mesh(new THREE.BoxGeometry(hw * 2, 0.06, 0.06), rackMat);
    topBar.position.set(0, hh - 0.03, -hd); g.add(topBar);
    var topBar2 = new THREE.Mesh(new THREE.BoxGeometry(hw * 2, 0.06, 0.06), rackMat);
    topBar2.position.set(0, hh - 0.03, hd); g.add(topBar2);
    // Barbell
    var barbell = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 2.0, 8), plateMat);
    barbell.rotation.z = Math.PI / 2;
    barbell.position.set(0, 1.5, 0); g.add(barbell);
    // J-hooks
    [[-1,1],[1,1]].forEach(function(p) {
      var jh = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.06, 0.12), goldMat);
      jh.position.set(p[0] * hw, 1.48, p[1] * 0); g.add(jh);
    });
    // Platform
    var plat = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.05, 2.2), rubberMat);
    plat.position.y = 0.025; g.add(plat);
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }
  addRack(-7, 4, 0);
  addRack(-4, 4, 0);
  addRack(-7, 7.5, 0);

  /* ---- Dumbbell rack ---- */
  (function() {
    var g = new THREE.Group();
    var shelf = new THREE.Mesh(new THREE.BoxGeometry(3, 0.8, 0.5), frameMat);
    shelf.position.set(0, 0.4, 0); shelf.castShadow = true; g.add(shelf);
    // Shelf dividers
    for (var d = 0; d < 3; d++) {
      var div = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.06, 0.5), plateMat);
      div.position.set(-1.2 + d * 1.2, 0.83, 0); g.add(div);
    }
    // Dumbbells
    for (var i = 0; i < 10; i++) {
      var dbg = new THREE.Group();
      var handle = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.22, 8), plateMat);
      handle.rotation.z = Math.PI / 2;
      var sz = 0.04 + i * 0.003;
      var end1 = new THREE.Mesh(new THREE.CylinderGeometry(sz, sz, 0.06, 8), frameMat);
      end1.rotation.z = Math.PI / 2; end1.position.x = -0.1;
      var end2 = end1.clone(); end2.position.x = 0.1;
      dbg.add(handle); dbg.add(end1); dbg.add(end2);
      dbg.position.set(-1.3 + i * 0.28, 0.88, 0);
      g.add(dbg);
    }
    g.position.set(-2, 0, 7.5);
    scene.add(g);
  })();

  /* ---- Cardio: Treadmills (4) ---- */
  function addTreadmill(x, z, ry) {
    var g = new THREE.Group();
    // Belt/deck
    var deck = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.15, 1.6), frameMat);
    deck.position.y = 0.2; deck.castShadow = true; g.add(deck);
    // Belt surface
    var belt = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.01, 1.5), rubberMat);
    belt.position.y = 0.28; g.add(belt);
    // Side rails
    [-1, 1].forEach(function(s) {
      var rail = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.03, 1.4), plateMat);
      rail.position.set(s * 0.27, 0.29, 0); g.add(rail);
    });
    // Console post
    var post = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.0, 8), frameMat);
    post.position.set(0, 0.78, -0.7); g.add(post);
    // Console/display
    var console = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.25, 0.04), frameMat);
    console.position.set(0, 1.3, -0.7); g.add(console);
    // Screen
    var screen = new THREE.Mesh(new THREE.PlaneGeometry(0.32, 0.18), new THREE.MeshBasicMaterial({color: 0x113322}));
    screen.position.set(0, 1.32, -0.675); g.add(screen);
    // Handles
    [-1, 1].forEach(function(s) {
      var h = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.6, 8), plateMat);
      h.position.set(s * 0.2, 1.0, -0.6); g.add(h);
    });
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }
  for (var ti = 0; ti < 4; ti++) addTreadmill(3.5 + ti * 1.4, 3, Math.PI);

  /* ---- Cardio: Spin bikes (3) ---- */
  function addBike(x, z, ry) {
    var g = new THREE.Group();
    // Main frame
    var frame = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.5, 0.8), frameMat);
    frame.position.y = 0.4; frame.castShadow = true; g.add(frame);
    // Flywheel
    var fw = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.06, 16), plateMat);
    fw.rotation.x = Math.PI / 2; fw.position.set(0, 0.35, -0.3); g.add(fw);
    // Seat post
    var sp = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.4, 8), frameMat);
    sp.position.set(0, 0.8, 0.2); g.add(sp);
    // Seat
    var seat = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.04, 0.15), padMat);
    seat.position.set(0, 1.0, 0.2); g.add(seat);
    // Handlebar
    var hb = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.35, 8), plateMat);
    hb.rotation.z = Math.PI / 2; hb.position.set(0, 0.9, -0.35); g.add(hb);
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }
  for (var bi = 0; bi < 3; bi++) addBike(4 + bi * 1.4, 6, Math.PI);

  /* ---- Benches (2) ---- */
  function addBench(x, z, ry) {
    var g = new THREE.Group();
    // Legs
    [[-0.15,-0.4],[0.15,-0.4],[-0.15,0.4],[0.15,0.4]].forEach(function(p) {
      var leg = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.4, 0.04), frameMat);
      leg.position.set(p[0], 0.2, p[1]); g.add(leg);
    });
    // Pad
    var pad = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.06, 1.0), padMat);
    pad.position.y = 0.43; pad.castShadow = true; g.add(pad);
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }
  addBench(-1, 4, 0);
  addBench(1, 4, 0);

  /* ---- Camera: orbit control ---- */
  var isDrag = false, pX = 0, pY = 0;
  var theta = Math.PI * 0.25, phi = 0.6, radius = 20;
  var tgt = new THREE.Vector3(0, 0, 0);
  var tDist = 0;
  var dragAxis = null; // 'h' or 'v' or null

  function upCam() {
    camera.position.set(
      tgt.x + radius * Math.sin(phi) * Math.sin(theta),
      tgt.y + radius * Math.cos(phi),
      tgt.z + radius * Math.sin(phi) * Math.cos(theta)
    );
    camera.lookAt(tgt);
  }
  upCam();

  /* Mouse controls */
  canvas.addEventListener("mousedown", function(e) { isDrag = true; pX = e.clientX; pY = e.clientY; });
  window.addEventListener("mouseup", function() { isDrag = false; });
  window.addEventListener("mousemove", function(e) {
    if (!isDrag) return;
    theta -= (e.clientX - pX) * 0.005;
    phi = Math.max(0.3, Math.min(Math.PI / 2.2, phi + (e.clientY - pY) * 0.005));
    pX = e.clientX; pY = e.clientY;
    upCam();
  });
  canvas.addEventListener("wheel", function(e) {
    e.preventDefault();
    radius = Math.max(10, Math.min(35, radius + e.deltaY * 0.02));
    upCam();
  }, {passive: false});

  /* Touch controls — only horizontal drag rotates, vertical passes through to page scroll */
  canvas.addEventListener("touchstart", function(e) {
    if (e.touches.length === 1) {
      pX = e.touches[0].clientX;
      pY = e.touches[0].clientY;
      dragAxis = null;
    }
    if (e.touches.length === 2) {
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      tDist = Math.sqrt(dx * dx + dy * dy);
    }
  }, {passive: true});

  canvas.addEventListener("touchmove", function(e) {
    if (e.touches.length === 1) {
      var dx = e.touches[0].clientX - pX;
      var dy = e.touches[0].clientY - pY;
      // Determine drag direction on first significant move
      if (!dragAxis && (Math.abs(dx) > 5 || Math.abs(dy) > 5)) {
        dragAxis = Math.abs(dx) > Math.abs(dy) ? 'h' : 'v';
      }
      if (dragAxis === 'h') {
        e.preventDefault(); // prevent page scroll, rotate scene
        theta -= dx * 0.005;
        pX = e.touches[0].clientX;
        pY = e.touches[0].clientY;
        upCam();
      }
      // if dragAxis === 'v', do nothing — let browser handle page scroll
    }
    if (e.touches.length === 2) {
      e.preventDefault();
      var dx2 = e.touches[0].clientX - e.touches[1].clientX;
      var dy2 = e.touches[0].clientY - e.touches[1].clientY;
      var d = Math.sqrt(dx2 * dx2 + dy2 * dy2);
      radius = Math.max(10, Math.min(35, radius - (d - tDist) * 0.05));
      tDist = d;
      upCam();
    }
  }, {passive: false});

  canvas.addEventListener("touchend", function() { isDrag = false; dragAxis = null; }, {passive: true});

  /* ---- Render loop ---- */
  (function anim() { requestAnimationFrame(anim); renderer.render(scene, camera); })();

  /* ---- Resize ---- */
  window.addEventListener("resize", function() {
    var r = canvas.parentElement.getBoundingClientRect();
    var nw = r.width;
    var nh = Math.min(nw * 2/5, 200);
    canvas.width = nw * dpr;
    canvas.height = nh * dpr;
    canvas.style.height = nh + "px";
    camera.aspect = canvas.width / canvas.height;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.width, canvas.height);
  });
})();
