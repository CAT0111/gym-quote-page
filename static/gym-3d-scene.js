(function(){
  var canvas = document.getElementById("gym-canvas");
  if (!canvas) return;

  var wrap = canvas.parentElement;
  function sz(){
    var w = wrap.clientWidth, h = Math.min(380, w * 0.55);
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    canvas.width = w * Math.min(window.devicePixelRatio, 2);
    canvas.height = h * Math.min(window.devicePixelRatio, 2);
    return {w:w, h:h};
  }
  var s = sz();

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0d0d1a);
  scene.fog = new THREE.FogExp2(0x0d0d1a, 0.008);

  var camera = new THREE.PerspectiveCamera(48, s.w / s.h, 0.5, 200);
  var renderer = new THREE.WebGLRenderer({canvas:canvas, antialias:true});
  renderer.setSize(s.w, s.h, false);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.4;
  renderer.outputEncoding = THREE.sRGBEncoding;

  /* equipment bounds */
  var eqCenter = {x:8.1, z:0.0};
  var roomW = 46, roomD = 30, roomH = 10;
  var cx = eqCenter.x, cz = eqCenter.z;

  /* env prefixes to hide */
  var envP = ["FloorTile","Walls","polySurface1_W","polySurface2_W",
    "polySurface12_W","polySurface13_W","Windows","door",
    "Outlet","Lightswitch","Mat3_","Mat4_","Mat5_","Mat_Mat"];
  function isEnv(n){ for(var i=0;i<envP.length;i++) if(n.indexOf(envP[i])===0) return true; return false; }

  var loader = new THREE.GLTFLoader();
  loader.load("../static/models/gym-preview.glb", function(gltf){
    gltf.scene.traverse(function(child){
      if(child.isMesh){
        if(isEnv(child.name)){ child.visible=false; }
        else {
          child.castShadow=true;
          child.receiveShadow=true;
          if(child.material){
            child.material.metalness = Math.min(child.material.metalness||0, 0.65);
            child.material.roughness = Math.max(child.material.roughness||0.5, 0.3);
            child.material.envMapIntensity = 1.2;
          }
        }
      }
    });
    scene.add(gltf.scene);
    buildEnv();
  });

  function buildEnv(){
    /* ── FLOOR ── */
    // main floor - dark rubber
    var floorMat = new THREE.MeshStandardMaterial({color:0x111111, roughness:0.92, metalness:0.02});
    var floor = new THREE.Mesh(new THREE.PlaneGeometry(roomW, roomD), floorMat);
    floor.rotation.x = -Math.PI/2;
    floor.position.set(cx, -0.02, cz);
    floor.receiveShadow = true;
    scene.add(floor);

    // strength zone (left) - deep blue
    var z1 = new THREE.Mesh(
      new THREE.PlaneGeometry(roomW*0.47, roomD*0.88),
      new THREE.MeshStandardMaterial({color:0x0a0f1e, roughness:0.88, metalness:0.05})
    );
    z1.rotation.x=-Math.PI/2; z1.position.set(cx-roomW*0.13, 0.005, cz); z1.receiveShadow=true;
    scene.add(z1);

    // cardio zone (right) - warm dark
    var z2 = new THREE.Mesh(
      new THREE.PlaneGeometry(roomW*0.47, roomD*0.88),
      new THREE.MeshStandardMaterial({color:0x1a1008, roughness:0.88, metalness:0.05})
    );
    z2.rotation.x=-Math.PI/2; z2.position.set(cx+roomW*0.13, 0.005, cz); z2.receiveShadow=true;
    scene.add(z2);

    // gold divider line
    var divMat = new THREE.MeshStandardMaterial({color:0xd4a843, emissive:0xd4a843, emissiveIntensity:0.8});
    var div = new THREE.Mesh(new THREE.PlaneGeometry(0.1, roomD*0.85), divMat);
    div.rotation.x=-Math.PI/2; div.position.set(cx, 0.015, cz);
    scene.add(div);

    // border lines along zone edges
    var borderMat = new THREE.MeshStandardMaterial({color:0x333333, emissive:0x222222, emissiveIntensity:0.3});
    [-1,1].forEach(function(side){
      var line = new THREE.Mesh(new THREE.PlaneGeometry(0.06, roomD*0.85), borderMat);
      line.rotation.x=-Math.PI/2;
      line.position.set(cx + side*roomW*0.365, 0.012, cz);
      scene.add(line);
    });

    /* ── WALLS - dark, recessed look ── */
    var wallMat = new THREE.MeshStandardMaterial({color:0x151520, roughness:0.75, metalness:0.15});
    var wallDk = new THREE.MeshStandardMaterial({color:0x101018, roughness:0.7, metalness:0.2});

    // back wall
    var bw = new THREE.Mesh(new THREE.PlaneGeometry(roomW, roomH), wallMat);
    bw.position.set(cx, roomH/2, cz-roomD/2); bw.receiveShadow=true;
    scene.add(bw);

    // left wall
    var lw = new THREE.Mesh(new THREE.PlaneGeometry(roomD, roomH), wallDk);
    lw.position.set(cx-roomW/2, roomH/2, cz); lw.rotation.y=Math.PI/2; lw.receiveShadow=true;
    scene.add(lw);

    // right wall
    var rw = new THREE.Mesh(new THREE.PlaneGeometry(roomD, roomH), wallDk);
    rw.position.set(cx+roomW/2, roomH/2, cz); rw.rotation.y=-Math.PI/2; rw.receiveShadow=true;
    scene.add(rw);

    // front wall - glass
    var glassMat = new THREE.MeshStandardMaterial({
      color:0x88bbdd, roughness:0.05, metalness:0.2, transparent:true, opacity:0.08
    });
    var fw = new THREE.Mesh(new THREE.PlaneGeometry(roomW, roomH), glassMat);
    fw.position.set(cx, roomH/2, cz+roomD/2); fw.rotation.y=Math.PI;
    scene.add(fw);

    /* ── MIRROR on back wall ── */
    var mirrorMat = new THREE.MeshStandardMaterial({
      color:0xc8d8e8, roughness:0.02, metalness:0.97, envMapIntensity:2.0
    });
    var mirror = new THREE.Mesh(new THREE.PlaneGeometry(roomW*0.82, roomH*0.5), mirrorMat);
    mirror.position.set(cx, roomH*0.38, cz-roomD/2+0.06);
    scene.add(mirror);

    // mirror frame
    var fMat = new THREE.MeshStandardMaterial({color:0x222222, roughness:0.35, metalness:0.85});
    var mW = roomW*0.82, mH = roomH*0.5;
    var ft = new THREE.Mesh(new THREE.BoxGeometry(mW+0.2, 0.1, 0.08), fMat);
    ft.position.set(cx, roomH*0.38+mH/2, cz-roomD/2+0.06); scene.add(ft);
    var fb = new THREE.Mesh(new THREE.BoxGeometry(mW+0.2, 0.1, 0.08), fMat);
    fb.position.set(cx, roomH*0.38-mH/2, cz-roomD/2+0.06); scene.add(fb);

    /* ── NO CEILING - open top for better view ── */

    /* ── LED strips at wall-floor junction ── */
    var ledMat = new THREE.MeshStandardMaterial({
      color:0xffcc44, emissive:0xffaa22, emissiveIntensity:2.0
    });
    // back edge
    var ledB = new THREE.Mesh(new THREE.BoxGeometry(roomW, 0.04, 0.08), ledMat);
    ledB.position.set(cx, 0.02, cz-roomD/2+0.04); scene.add(ledB);
    // left edge
    var ledL = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.04, roomD), ledMat);
    ledL.position.set(cx-roomW/2+0.04, 0.02, cz); scene.add(ledL);
    // right edge
    var ledR = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.04, roomD), ledMat);
    ledR.position.set(cx+roomW/2-0.04, 0.02, cz); scene.add(ledR);

    /* ── brand logo glow on back wall ── */
    var logoMat = new THREE.MeshStandardMaterial({
      color:0xd4a843, emissive:0xd4a843, emissiveIntensity:1.0,
      roughness:0.25, metalness:0.85
    });
    var logo = new THREE.Mesh(new THREE.PlaneGeometry(5, 1), logoMat);
    logo.position.set(cx, roomH*0.82, cz-roomD/2+0.07);
    scene.add(logo);

    /* ── skirting boards ── */
    var skMat = new THREE.MeshStandardMaterial({color:0x0a0a0a, roughness:0.5, metalness:0.4});
    var skH = 0.25;
    var skB = new THREE.Mesh(new THREE.BoxGeometry(roomW, skH, 0.1), skMat);
    skB.position.set(cx, skH/2, cz-roomD/2+0.05); scene.add(skB);
    var skL = new THREE.Mesh(new THREE.BoxGeometry(0.1, skH, roomD), skMat);
    skL.position.set(cx-roomW/2+0.05, skH/2, cz); scene.add(skL);
    var skR = new THREE.Mesh(new THREE.BoxGeometry(0.1, skH, roomD), skMat);
    skR.position.set(cx+roomW/2-0.05, skH/2, cz); scene.add(skR);
  }

  /* ── LIGHTING ── */
  // ambient - slightly warm
  scene.add(new THREE.AmbientLight(0x555566, 0.7));

  // hemisphere - sky/ground
  scene.add(new THREE.HemisphereLight(0x8899bb, 0x222211, 0.6));

  // key light - overhead
  var key = new THREE.DirectionalLight(0xfff8ee, 1.5);
  key.position.set(cx, 25, cz+5);
  key.target.position.set(cx, 0, cz);
  key.castShadow=true;
  key.shadow.mapSize.set(2048,2048);
  key.shadow.camera.left=-25; key.shadow.camera.right=30;
  key.shadow.camera.top=18; key.shadow.camera.bottom=-18;
  key.shadow.camera.near=5; key.shadow.camera.far=50;
  key.shadow.bias=-0.001;
  scene.add(key); scene.add(key.target);

  // fill - cool from front-left
  var fill = new THREE.DirectionalLight(0xaabbdd, 0.6);
  fill.position.set(cx-25, 12, cz+20);
  scene.add(fill);

  // accent - warm from front-right
  var acc = new THREE.DirectionalLight(0xffddaa, 0.5);
  acc.position.set(cx+25, 10, cz+20);
  scene.add(acc);

  // rim light from back
  var rim = new THREE.DirectionalLight(0x6688cc, 0.4);
  rim.position.set(cx, 15, cz-25);
  scene.add(rim);

  // ceiling point lights (simulate downlights)
  [[-10,-5],[0,0],[10,5],[cx-5,cz+6],[cx+5,cz-6]].forEach(function(p){
    var pl = new THREE.PointLight(0xfff0dd, 0.9, 22, 2);
    pl.position.set(cx+p[0], 9.5, cz+p[1]);
    scene.add(pl);
  });

  // warm spot on mirror wall
  var spot = new THREE.SpotLight(0xffeedd, 0.6, 30, Math.PI/6, 0.5, 2);
  spot.position.set(cx, 9, cz-roomD/2+3);
  spot.target.position.set(cx, 3, cz-roomD/2);
  scene.add(spot); scene.add(spot.target);

  /* ── CAMERA ORBIT ── */
  var maxDim = Math.max(roomW, roomD);
  var radius = maxDim * 0.78;
  var minR = maxDim * 0.35, maxR = maxDim * 1.6;
  var theta = Math.PI * 0.72;
  var phi = 0.62;

  function upCam(){
    camera.position.x = cx + radius*Math.sin(phi)*Math.cos(theta);
    camera.position.y = radius*Math.cos(phi);
    camera.position.z = cz + radius*Math.sin(phi)*Math.sin(theta);
    camera.lookAt(cx, 3.0, cz);
  }
  upCam();

  /* mouse */
  var drag=false, px=0, py=0;
  canvas.addEventListener("mousedown",function(e){drag=true;px=e.clientX;py=e.clientY;});
  window.addEventListener("mouseup",function(){drag=false;});
  window.addEventListener("mousemove",function(e){
    if(!drag)return;
    theta-=(e.clientX-px)*0.005;
    phi=Math.max(0.15,Math.min(1.4,phi+(e.clientY-py)*0.005));
    px=e.clientX;py=e.clientY;upCam();
  });
  canvas.addEventListener("wheel",function(e){
    e.preventDefault();
    radius=Math.max(minR,Math.min(maxR,radius+e.deltaY*0.06));
    upCam();
  },{passive:false});

  /* touch */
  var td=0;
  canvas.addEventListener("touchstart",function(e){
    if(e.touches.length===1){drag=true;px=e.touches[0].clientX;py=e.touches[0].clientY;}
    if(e.touches.length===2){
      var dx=e.touches[0].clientX-e.touches[1].clientX,dy=e.touches[0].clientY-e.touches[1].clientY;
      td=Math.sqrt(dx*dx+dy*dy);
    }
  },{passive:true});
  canvas.addEventListener("touchmove",function(e){
    e.preventDefault();
    if(e.touches.length===1&&drag){
      theta-=(e.touches[0].clientX-px)*0.005;
      phi=Math.max(0.15,Math.min(1.4,phi+(e.touches[0].clientY-py)*0.005));
      px=e.touches[0].clientX;py=e.touches[0].clientY;upCam();
    }
    if(e.touches.length===2){
      var dx=e.touches[0].clientX-e.touches[1].clientX,dy=e.touches[0].clientY-e.touches[1].clientY;
      var d=Math.sqrt(dx*dx+dy*dy);
      radius=Math.max(minR,Math.min(maxR,radius*(td/d)));
      td=d;upCam();
    }
  },{passive:false});
  canvas.addEventListener("touchend",function(){drag=false;},{passive:true});

  /* render */
  function animate(){ requestAnimationFrame(animate); renderer.render(scene,camera); }
  animate();

  /* resize */
  window.addEventListener("resize",function(){
    var s=sz();
    camera.aspect=s.w/s.h;
    camera.updateProjectionMatrix();
    renderer.setSize(s.w,s.h,false);
  });
})();

/* ── fix canvas overflow ── */
(function(){
  var c = document.getElementById("gym-canvas");
  if(!c) return;
  var p = c.parentElement;
  p.style.overflow = "hidden";
  p.style.position = "relative";
  c.style.display = "block";
  c.style.maxWidth = "100%";
  c.style.boxSizing = "border-box";
})();
