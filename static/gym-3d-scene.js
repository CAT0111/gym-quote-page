// gym-3d-scene.js — ES module, loads optimized GLB with post-processing
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

(function () {
  var canvas = document.getElementById('gym-canvas');
  if (!canvas) return;

  var wrap = canvas.parentElement;

  function getSize() {
    var w = wrap.clientWidth;
    var h = wrap.clientHeight || w; // 彻底解除封印，读取真实 CSS 高度
    return { w: w, h: h };
  }

  var s = getSize();
  var W = s.w, H = s.h;

  // Renderer
  var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: false, powerPreference: 'high-performance' });
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.6;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // Scene
  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a0a);
  scene.fog = new THREE.FogExp2(0x0a0a0a, 0.015);

  // Camera
  var camera = new THREE.PerspectiveCamera(48, W / H, 0.5, 380);

  // Controls
  var ctrl = new OrbitControls(camera, canvas);
  ctrl.enableDamping = true;
  ctrl.dampingFactor = 0.08;
  ctrl.enablePan = false;
  ctrl.minPolarAngle = 0.3;
  ctrl.maxPolarAngle = 1.3;
  ctrl.minDistance = 3;
  ctrl.maxDistance = 30;
  ctrl.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY };

  // Environment map
  var pmrem = new THREE.PMREMGenerator(renderer);
  pmrem.compileEquirectangularShader();
  var envScene = new THREE.Scene();
  var l1 = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), new THREE.MeshBasicMaterial({ color: 0xfff5e6, side: THREE.DoubleSide }));
  l1.position.set(0, 8, 0); l1.rotation.x = Math.PI / 2; envScene.add(l1);
  var l2 = new THREE.Mesh(new THREE.PlaneGeometry(6, 6), new THREE.MeshBasicMaterial({ color: 0x8ab4f8, side: THREE.DoubleSide }));
  l2.position.set(-9, 3, 0); l2.lookAt(0, 1, 0); envScene.add(l2);
  var l3 = new THREE.Mesh(new THREE.PlaneGeometry(5, 5), new THREE.MeshBasicMaterial({ color: 0xffc875, side: THREE.DoubleSide }));
  l3.position.set(9, 2, 5); l3.lookAt(0, 1, 0); envScene.add(l3);
  var bg = new THREE.Mesh(new THREE.SphereGeometry(30, 16, 16), new THREE.MeshBasicMaterial({ color: 0x1a1a1e, side: THREE.BackSide }));
  envScene.add(bg);
  scene.environment = pmrem.fromScene(envScene, 0.04).texture;
  envScene.traverse(function (o) { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
  pmrem.dispose();

  // Lights
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));

  var dirLight = new THREE.DirectionalLight(0xfff5e6, 2.0);
  dirLight.position.set(5, 10, 5);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.set(2048, 2048);
  dirLight.shadow.camera.near = 0.1;
  dirLight.shadow.camera.far = 50;
  dirLight.shadow.camera.left = -15;
  dirLight.shadow.camera.right = 15;
  dirLight.shadow.camera.top = 15;
  dirLight.shadow.camera.bottom = -15;
  dirLight.shadow.bias = -0.001;
  dirLight.shadow.normalBias = 0.02;
  scene.add(dirLight);

  var fillLight = new THREE.DirectionalLight(0xaaccff, 0.4);
  fillLight.position.set(-5, 4, -3);
  scene.add(fillLight);

  var rimLight = new THREE.DirectionalLight(0xc8a44e, 0.3);
  rimLight.position.set(0, 2, -8);
  scene.add(rimLight);

  // Post-processing
  var composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));

  var bloomPass = new UnrealBloomPass(new THREE.Vector2(W, H), 0.4, 0.6, 0.85);
  composer.addPass(bloomPass);

  var pr = renderer.getPixelRatio();
  composer.addPass(new SMAAPass(W * pr, H * pr));
  composer.addPass(new OutputPass());

  // Loader
  var dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath('https://unpkg.com/three@0.160.0/examples/jsm/libs/draco/');
  var gltfLoader = new GLTFLoader();
  gltfLoader.setDRACOLoader(dracoLoader);

  // Load model
  gltfLoader.load('../static/models/changguanhuanjing-optimized.glb', function (gltf) {
    var model = gltf.scene;

    model.traverse(function (o) {
      if (o.isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
        if (o.material) o.material.envMapIntensity = 1.0;
      }
    });

    var box = new THREE.Box3().setFromObject(model);
    var center = new THREE.Vector3();
    var size = new THREE.Vector3();
    box.getCenter(center);
    box.getSize(size);
    model.position.sub(center);
    scene.add(model);

    var maxD = Math.max(size.x, size.y, size.z);
    var dist = maxD * 1.6;
    camera.position.set(dist * 0.5, dist * 0.65, dist * 0.5);
    camera.near = maxD * 0.001;
    camera.far = maxD * 20;
    camera.updateProjectionMatrix();

    ctrl.target.set(0, size.y * 0.1, 0);
    ctrl.update();

    // Fit lights to model
    var r = maxD * 0.8;
    dirLight.shadow.camera.left = -r;
    dirLight.shadow.camera.right = r;
    dirLight.shadow.camera.top = r;
    dirLight.shadow.camera.bottom = -r;
    dirLight.shadow.camera.far = maxD * 3;
    dirLight.shadow.camera.updateProjectionMatrix();
    dirLight.position.set(maxD * 0.5, maxD * 1.2, maxD * 0.5);
    fillLight.position.set(-maxD * 0.5, maxD * 0.5, -maxD * 0.3);
    rimLight.position.set(0, maxD * 0.3, -maxD * 0.8);

    ctrl.minDistance = maxD * 0.3;
    ctrl.maxDistance = maxD * 2;
  }, undefined, function (err) {
    console.error('GLB load error:', err);
  });

  // Animate
  (function animate() {
    requestAnimationFrame(animate);
    ctrl.update();
    composer.render();
  })();

  // Resize
  window.addEventListener('resize', function () {
    var s = getSize();
    W = s.w; H = s.h;
    camera.aspect = W / H;
    camera.updateProjectionMatrix();
    renderer.setSize(W, H);
    composer.setSize(W, H);
    bloomPass.resolution.set(W, H);
  });
})();
