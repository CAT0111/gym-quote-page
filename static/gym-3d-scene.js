(function(){
  var canvas = document.getElementById("gym-canvas");
  if (!canvas) return;

  var rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width * 2;
  canvas.height = (rect.width * 10/16) * 2;
  canvas.style.height = (rect.width * 10/16) + "px";

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a1a);
  var aspect = canvas.width / canvas.height;
  var camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 1000);
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
  renderer.setSize(canvas.width, canvas.height);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  scene.add(new THREE.AmbientLight(0xffffff, 0.4));
  var dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(10, 20, 10);
  dir.castShadow = true;
  dir.shadow.mapSize.set(1024, 1024);
  scene.add(dir);
  var fill = new THREE.DirectionalLight(0x4488ff, 0.15);
  fill.position.set(-10, 10, 0);
  scene.add(fill);

  var floorMat = new THREE.MeshLambertMaterial({color:0x2a2a2a});
  var wallMat = new THREE.MeshLambertMaterial({color:0x3a3a3a});
  var machineMat = new THREE.MeshPhongMaterial({color:0x222222,specular:0x444444,shininess:30});
  var accentMat = new THREE.MeshPhongMaterial({color:0xc8a44e,specular:0xffffff,shininess:60});
  var padMat = new THREE.MeshLambertMaterial({color:0x1a1a1a});
  var redMat = new THREE.MeshPhongMaterial({color:0xcc3333,specular:0xff6666,shininess:40});
  var silverMat = new THREE.MeshPhongMaterial({color:0x888888,specular:0xffffff,shininess:80});
  var rackMat = new THREE.MeshPhongMaterial({color:0x111111,specular:0x333333,shininess:20});

  var floor = new THREE.Mesh(new THREE.PlaneGeometry(20,20), floorMat);
  floor.rotation.x = -Math.PI/2;
  floor.receiveShadow = true;
  scene.add(floor);
  var grid = new THREE.GridHelper(20,20,0x333333,0x222222);
  grid.position.y = 0.01;
  scene.add(grid);

  function addWall(w,h,x,y,z,ry) {
    var m = new THREE.Mesh(new THREE.BoxGeometry(w,h,.15), wallMat);
    m.position.set(x,y,z);
    if (ry) m.rotation.y = ry;
    m.receiveShadow = true;
    scene.add(m);
  }
  addWall(20,3,0,1.5,-10,0);
  addWall(20,3,0,1.5,10,0);
  addWall(20,3,-10,1.5,0,Math.PI/2);
  addWall(20,3,10,1.5,0,Math.PI/2);

  function addLabel(t,x,z) {
    var c = document.createElement("canvas");
    c.width = 512; c.height = 64;
    var ctx = c.getContext("2d");
    ctx.fillStyle = "#c8a44e";
    ctx.font = "bold 32px Arial";
    ctx.textAlign = "center";
    ctx.fillText(t, 256, 42);
    var s = new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(c),transparent:true,opacity:.7}));
    s.scale.set(5,.6,1);
    s.position.set(x,.05,z);
    scene.add(s);
  }
  addLabel("SELECTORIZED",-4.5,-7);
  addLabel("PLATE LOADED",-4.5,-1);
  addLabel("FREE WEIGHTS",-4.5,4.5);
  addLabel("CARDIO",5,4.5);

  function addMachine(x,z,w,d,h,ry,col) {
    var g = new THREE.Group();
    var base = new THREE.Mesh(new THREE.BoxGeometry(w,.15,d), machineMat);
    base.position.y = .075; base.castShadow = true; g.add(base);
    var body = new THREE.Mesh(new THREE.BoxGeometry(w*.8,h,d*.6), col||machineMat);
    body.position.y = h/2+.15; body.castShadow = true; g.add(body);
    var stripe = new THREE.Mesh(new THREE.BoxGeometry(w*.82,.05,d*.62), accentMat);
    stripe.position.y = h*.6; g.add(stripe);
    if (h > 1) {
      var seat = new THREE.Mesh(new THREE.BoxGeometry(w*.4,.12,d*.35), padMat);
      seat.position.set(0, h*.35, d*.15); g.add(seat);
    }
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }

  function addRack(x,z,w,d,h,ry) {
    var g = new THREE.Group();
    var r = .06;
    [[-1,-1],[1,-1],[1,1],[-1,1]].forEach(function(p) {
      var u = new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,8), rackMat);
      u.position.set(p[0]*w/2, h/2, p[1]*d/2); u.castShadow = true; g.add(u);
    });
    var bar = new THREE.Mesh(new THREE.CylinderGeometry(r*.7,r*.7,w,8), silverMat);
    bar.rotation.z = Math.PI/2; bar.position.set(0, h-.1, d/2); g.add(bar);
    var pl = new THREE.Mesh(new THREE.BoxGeometry(w*1.3,.08,d*1.5), new THREE.MeshLambertMaterial({color:0x3d2b1f}));
    pl.position.y = .04; g.add(pl);
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }

  function addCardio(x,z,type,ry) {
    var g = new THREE.Group();
    if (type === "treadmill") {
      var belt = new THREE.Mesh(new THREE.BoxGeometry(.6,.2,1.8), machineMat);
      belt.position.y = .3; belt.castShadow = true; g.add(belt);
      var post = new THREE.Mesh(new THREE.CylinderGeometry(.03,.03,1.2,8), silverMat);
      post.position.set(0,.9,-.7); g.add(post);
      var con = new THREE.Mesh(new THREE.BoxGeometry(.5,.35,.08), machineMat);
      con.position.set(0,1.5,-.7); g.add(con);
    } else {
      var bd = new THREE.Mesh(new THREE.BoxGeometry(.3,.6,1), machineMat);
      bd.position.y = .5; bd.castShadow = true; g.add(bd);
      var st = new THREE.Mesh(new THREE.BoxGeometry(.25,.08,.3), padMat);
      st.position.set(0,.9,.2); g.add(st);
    }
    var acc = new THREE.Mesh(new THREE.BoxGeometry(.1,.03,.3), accentMat);
    acc.position.y = .45; g.add(acc);
    g.position.set(x, 0, z);
    if (ry) g.rotation.y = ry;
    scene.add(g);
  }

  var i;
  for (i = 0; i < 6; i++) {
    addMachine(-7+i*2.4, -8, 1.2, 1.6, 1.8, 0);
    var ws = new THREE.Group();
    for (var j = 0; j < 8; j++) {
      var plate = new THREE.Mesh(new THREE.BoxGeometry(.3,.06,.15), silverMat);
      plate.position.y = .5 + j*.07; ws.add(plate);
    }
    ws.position.set(-7+i*2.4-.5, 0, -8.5);
    scene.add(ws);
  }
  for (i = 0; i < 4; i++) addMachine(-7+i*3, -2.5, 1.4, 1.8, 1.5, .1, redMat);

  addRack(-7, 4, 1.6, 1.8, 2.5, 0);
  addRack(-4, 4, 1.6, 1.8, 2.5, 0);
  addRack(-7, 7, 1.6, 1.8, 2.5, 0);

  var dbr = new THREE.Mesh(new THREE.BoxGeometry(3,.9,.6), machineMat);
  dbr.position.set(-2,.45,7); dbr.castShadow = true; scene.add(dbr);
  for (i = 0; i < 10; i++) {
    var db = new THREE.Mesh(new THREE.CylinderGeometry(.06,.06,.25,8), silverMat);
    db.rotation.z = Math.PI/2; db.position.set(-3.2+i*.28, .95, 7); scene.add(db);
  }

  for (i = 0; i < 4; i++) addCardio(4+i*1.5, 3, "treadmill", Math.PI);
  for (i = 0; i < 3; i++) addCardio(4.5+i*1.5, 6, "bike", Math.PI);

  for (i = 0; i < 2; i++) {
    var bn = new THREE.Mesh(new THREE.BoxGeometry(.4,.45,1.2), padMat);
    bn.position.set(-1+i*2, .225, 4); bn.castShadow = true; scene.add(bn);
  }

  var isDrag = false, pX = 0, pY = 0;
  var theta = Math.PI/4, phi = Math.PI/4, radius = 22;
  var tgt = new THREE.Vector3(0, 0, 0);
  var tDist = 0;

  function upCam() {
    camera.position.set(
      tgt.x + radius * Math.sin(phi) * Math.sin(theta),
      tgt.y + radius * Math.cos(phi),
      tgt.z + radius * Math.sin(phi) * Math.cos(theta)
    );
    camera.lookAt(tgt);
  }
  upCam();

  canvas.addEventListener("mousedown", function(e) { isDrag = true; pX = e.clientX; pY = e.clientY; });
  window.addEventListener("mouseup", function() { isDrag = false; });
  window.addEventListener("mousemove", function(e) {
    if (!isDrag) return;
    theta -= (e.clientX - pX) * .005;
    phi = Math.max(.2, Math.min(Math.PI/2.1, phi + (e.clientY - pY) * .005));
    pX = e.clientX; pY = e.clientY; upCam();
  });
  canvas.addEventListener("wheel", function(e) {
    e.preventDefault();
    radius = Math.max(8, Math.min(40, radius + e.deltaY * .02)); upCam();
  }, {passive: false});

  canvas.addEventListener("touchstart", function(e) {
    if (e.touches.length === 1) { isDrag = true; pX = e.touches[0].clientX; pY = e.touches[0].clientY; }
    if (e.touches.length === 2) {
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      tDist = Math.sqrt(dx*dx + dy*dy);
    }
  });
  canvas.addEventListener("touchmove", function(e) {
    e.preventDefault();
    if (e.touches.length === 1 && isDrag) {
      theta -= (e.touches[0].clientX - pX) * .005;
      phi = Math.max(.2, Math.min(Math.PI/2.1, phi + (e.touches[0].clientY - pY) * .005));
      pX = e.touches[0].clientX; pY = e.touches[0].clientY; upCam();
    }
    if (e.touches.length === 2) {
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      var d = Math.sqrt(dx*dx + dy*dy);
      radius = Math.max(8, Math.min(40, radius - (d - tDist) * .05));
      tDist = d; upCam();
    }
  }, {passive: false});
  canvas.addEventListener("touchend", function() { isDrag = false; });

  (function anim() { requestAnimationFrame(anim); renderer.render(scene, camera); })();

  window.addEventListener("resize", function() {
    var r = canvas.parentElement.getBoundingClientRect();
    canvas.width = r.width * 2;
    canvas.height = (r.width * 10/16) * 2;
    canvas.style.height = (r.width * 10/16) + "px";
    camera.aspect = canvas.width / canvas.height;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.width, canvas.height);
  });
})();