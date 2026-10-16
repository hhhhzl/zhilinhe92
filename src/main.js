import './style.css';
import './scene.css';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RectAreaLightUniformsLib } from 'three/addons/lights/RectAreaLightUniformsLib.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const $=s=>document.querySelector(s);
const canvas=$('#world'),stage=$('#scene-stage'),eyeMask=$('#eye-mask');
const motionQuery=matchMedia('(prefers-reduced-motion: reduce)');
const state={progress:0,target:0,ready:false,paused:motionQuery.matches,reduced:motionQuery.matches,pointerX:0,pointerY:0};
let renderer,scene,camera,robot,human,mixer,composer,optics,bokeh,raf,lastTime=0,lastProgress=0;
let viewport={width:0,height:0};
const v3=(x,y,z)=>new THREE.Vector3(x,y,z);
// Camera travels beside the shoulder, lowers toward the gesture, and rises into
// a three-quarter composition before entering the other body's eye position.
const positions=new THREE.CatmullRomCurve3([v3(0,1.215,.76),v3(.55,1.54,1.23),v3(1.9,1.13,1.48),v3(3.55,2.05,.65),v3(2.9,1.73,-1.5),v3(.65,1.77,-1.4),v3(0,1.65,-.77)],false,'catmullrom',.42);
const targets=new THREE.CatmullRomCurve3([v3(-.48,1.48,-.95),v3(-.05,1.26,-.45),v3(0,1.13,-.03),v3(0,.99,0),v3(0,1.02,.08),v3(0,1.18,.55),v3(0,.78,.95)],false,'catmullrom',.38);
const pos=new THREE.Vector3(),target=new THREE.Vector3();
const focusPoint=new THREE.Vector3(),viewDirection=new THREE.Vector3();
const humanEyes=v3(0,1.64,-.95),robotEyes=v3(0,1.215,.95);
function setTarget(value){
  state.target=THREE.MathUtils.clamp(value,0,1);
  if(state.reduced)state.progress=state.target;
  requestFrame();
}
function pose(){
  const t=state.progress,mid=Math.sin(Math.PI*t),mobile=viewport.width<680;
  positions.getPoint(t,pos);targets.getPoint(t,target);
  if(mobile){pos.x*=1+.25*mid;target.x*=.4;}
  if(!state.reduced){target.x+=state.pointerX*.024;target.y+=state.pointerY*.016;}
  camera.position.copy(pos);camera.lookAt(target);
  camera.rotateZ(Math.sin(t*Math.PI*2)*.018*mid);
  const base=THREE.MathUtils.lerp(61,44,mid);
  const fov=mobile?base+18*mid+20:Math.max(base,THREE.MathUtils.radToDeg(2*Math.atan(1.5/(Math.max(pos.x,2)*camera.aspect)))*mid);
  if(Math.abs(camera.fov-fov)>.01){camera.fov=fov;camera.updateProjectionMatrix();}
  robot.visible=t>.04;human.visible=t<.955;
  const reveal=THREE.MathUtils.smoothstep(t,.015,.20);
  eyeMask.style.opacity=1-reveal;
  eyeMask.style.transform=`scale(${1+reveal*.34})`;
  const movement=Math.abs(t-lastProgress);lastProgress=t;
  optics.uniforms.aberration.value=state.reduced?.2:Math.min(1.05,.22+movement*85);
  optics.uniforms.lens.value=1-reveal;
  // Pull focus between the actual subjects, rather than empty space at the orbit's centre.
  focusPoint.lerpVectors(humanEyes,robotEyes,THREE.MathUtils.smoothstep(t,.48,.80));
  camera.getWorldDirection(viewDirection);
  bokeh.uniforms.focus.value=Math.max(.1,focusPoint.sub(pos).dot(viewDirection));
  bokeh.uniforms.aperture.value=THREE.MathUtils.lerp(.00125,.00045,mid);
  canvas.setAttribute('aria-valuenow',String(Math.round(t*100)));
  canvas.setAttribute('aria-valuetext',t<.03?'Robot perspective':t>.97?'Human perspective':'Between perspectives');
}
function resize(){
  if(!renderer||!composer||!camera||!optics)return;
  const rect=stage.getBoundingClientRect();viewport={width:rect.width,height:rect.height};
  const ratio=Math.min(devicePixelRatio||1,rect.width<680?1.3:1.5);
  renderer.setPixelRatio(ratio);renderer.setSize(rect.width,rect.height,false);
  composer.setPixelRatio(ratio);composer.setSize(rect.width,rect.height);
  camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();
  const narrow=rect.width<680;
  $('#left-eye').setAttribute('d',narrow?'M50 350 C315 310 560 340 791 449 C776 602 716 666 618 679 C336 705 149 553 50 350Z':'M50 265 C300 205 565 235 791 375 C777 599 715 684 610 704 C340 751 128 556 50 315Z');
  $('#right-eye').setAttribute('d',narrow?'M1550 350 C1285 310 1040 340 809 449 C824 602 884 666 982 679 C1264 705 1451 553 1550 350Z':'M1550 265 C1300 205 1035 235 809 375 C823 599 885 684 990 704 C1260 751 1472 556 1550 315Z');
  optics.uniforms.resolution.value.set(rect.width*ratio,rect.height*ratio);
  requestFrame();
}
function requestFrame(){if(!raf&&state.ready&&!document.hidden)raf=requestAnimationFrame(render);}
function render(time){
  raf=0;if(!state.ready||document.hidden)return;
  const delta=lastTime?Math.min((time-lastTime)/1000,.06):1/60;lastTime=time;
  const difference=state.target-state.progress;
  state.progress=Math.abs(difference)<.0001?state.target:state.progress+difference*(1-Math.exp(-delta*15));
  if(!state.paused)mixer?.update(delta);
  optics.uniforms.frame.value=state.reduced?0:Math.floor(time*.024);
  pose();composer.render();
  if(!state.paused||Math.abs(state.target-state.progress)>.0001)requestFrame();
}
function floorFinish(){
  const shadow=new THREE.ShaderMaterial({transparent:true,depthWrite:false,vertexShader:'varying vec2 v;void main(){v=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec2 v;void main(){vec2 p=(v-.5)*2.;gl_FragColor=vec4(.015,.01,.05,exp(-dot(p,p)*5.)*.32);}'});
  [-.95,.95].forEach(z=>{const mesh=new THREE.Mesh(new THREE.PlaneGeometry(1.0,.8),shadow);mesh.rotation.x=-Math.PI/2;mesh.position.set(0,.013,z);scene.add(mesh);});
}
async function init(){
try{
  renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
  renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.02;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  scene=new THREE.Scene();scene.background=new THREE.Color('#222745');scene.fog=new THREE.Fog('#36334f',12,43);
  camera=new THREE.PerspectiveCamera(55,1,.035,70);
  const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();scene.environment=pmrem.fromScene(room,.04).texture;scene.environmentIntensity=.32;room.dispose();pmrem.dispose();
  scene.add(new THREE.HemisphereLight('#b0b8e7','#453444',.48));
  const sun=new THREE.DirectionalLight('#ffbc9c',3.1);sun.position.set(-16,9,-10);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-8;sun.shadow.camera.right=8;sun.shadow.camera.top=8;sun.shadow.camera.bottom=-8;sun.shadow.camera.far=50;sun.shadow.normalBias=.009;sun.shadow.bias=-.0002;scene.add(sun);
  RectAreaLightUniformsLib.init();
  const key=new THREE.RectAreaLight('#ffd0b9',5.2,3,3);key.position.set(-3.4,3.6,1.0);key.lookAt(0,1.35,-.95);scene.add(key);
  const fill=new THREE.RectAreaLight('#8797ee',1.8,3.5,3);fill.position.set(3.8,2.3,.4);fill.lookAt(0,1.35,-.95);scene.add(fill);
  const rim=new THREE.DirectionalLight('#bcc1f6',1.25);rim.position.set(2,4,6);scene.add(rim);
  const gltf=await new GLTFLoader().loadAsync(`${import.meta.env.BASE_URL}assets/atelier.glb?look=cinematic-polo-v3`);
  robot=gltf.scene.getObjectByName('Robot');human=gltf.scene.getObjectByName('Human');
  if(!robot||!human)throw new Error('The scene is missing a subject root.');
  // Keep the actor's authored skin, hair, and fabric PBR maps intact.
  gltf.scene.traverse(o=>{if(o.isLight||o.isCamera)o.visible=false;if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;for(const m of Array.isArray(o.material)?o.material:[o.material]){if(m.transparent||/glass|glow|sky/i.test(o.name+m.name))o.castShadow=false;if(/floor/i.test(o.name)){m.roughness=.72;m.metalness=.06;}if(m.map)m.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());}});
  scene.add(gltf.scene);
  const hall=new THREE.Group();scene.add(hall);[...gltf.scene.children].filter(o=>/^(Architecture_|Floor)/.test(o.name)).forEach(o=>hall.attach(o));hall.rotation.y=.24;
  floorFinish();
  if(gltf.animations.length){mixer=new THREE.AnimationMixer(gltf.scene);for(const clip of gltf.animations)mixer.clipAction(clip).play();mixer.setTime(.85);mixer.timeScale=.8;}
  const renderTarget=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:2});
  composer=new EffectComposer(renderer,renderTarget);composer.addPass(new RenderPass(scene,camera));
  bokeh=new BokehPass(scene,camera,{focus:1.9,aperture:.00125,maxblur:.009});composer.addPass(bokeh);
  optics=new ShaderPass({uniforms:{tDiffuse:{value:null},resolution:{value:new THREE.Vector2(1,1)},aberration:{value:.2},lens:{value:1},frame:{value:0}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:`
    uniform sampler2D tDiffuse;uniform vec2 resolution;uniform float aberration,lens,frame;varying vec2 vUv;
    float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7))+frame*.71)*43758.5453);}
    void main(){
      vec2 p=vUv-.5;vec2 uv=.5+p*(1.+.013*dot(p,p)*lens);
      vec2 d=vec2(aberration/resolution.x,0.);vec3 c=texture2D(tDiffuse,uv).rgb;
      c.r=texture2D(tDiffuse,uv+d).r;c.b=texture2D(tDiffuse,uv-d).b;
      vec3 halo=vec3(0.);vec2 stepUV=vec2(2.5)/resolution;
      halo+=max(texture2D(tDiffuse,uv+vec2(stepUV.x,0.)).rgb-.8,0.);
      halo+=max(texture2D(tDiffuse,uv-vec2(stepUV.x,0.)).rgb-.8,0.);
      halo+=max(texture2D(tDiffuse,uv+vec2(0.,stepUV.y)).rgb-.8,0.);
      halo+=max(texture2D(tDiffuse,uv-vec2(0.,stepUV.y)).rgb-.8,0.);
      c+=halo*.018*vec3(1.0,.8,.66);
      float lum=dot(c,vec3(.2126,.7152,.0722));c=mix(vec3(lum),c,.93);
      c*=1.-smoothstep(.20,.73,length(p*vec2(.82,1.)))*.22;
      c+=vec3((hash(gl_FragCoord.xy)-.5)*.0017);
      gl_FragColor=vec4(max(c,0.),1.);
    }`});composer.addPass(optics);composer.addPass(new OutputPass());
  state.ready=true;resize();$('#loading').classList.add('is-loaded');setTimeout(()=>$('#loading').hidden=true,950);
}catch(error){console.error('Scene failed:',error);$('#loading').hidden=true;$('#scene-status').textContent='The interactive scene could not load. The Research link remains available.';canvas.setAttribute('aria-disabled','true');}
}
let drag;
canvas.addEventListener('pointerdown',e=>{if(!state.ready||e.button!==0)return;drag={x:e.clientX,start:state.target,lastX:e.clientX,lastTime:e.timeStamp,velocity:0,id:e.pointerId};canvas.setPointerCapture(e.pointerId);canvas.classList.add('is-dragging','pointer-control');canvas.focus({preventScroll:true});});
canvas.addEventListener('pointermove',e=>{
  if(drag){
    const elapsed=Math.max(1,e.timeStamp-drag.lastTime);
    drag.velocity=THREE.MathUtils.lerp(drag.velocity,(drag.lastX-e.clientX)/(viewport.width*.70)*1000/elapsed,.6);
    drag.lastX=e.clientX;drag.lastTime=e.timeStamp;
    setTarget(drag.start+(drag.x-e.clientX)/(viewport.width*.70));
  }else{state.pointerX=e.clientX/viewport.width-.5;state.pointerY=.5-e.clientY/viewport.height;if(!state.reduced)requestFrame();}
});
function endDrag(e){
  if(!drag)return;
  const velocity=(e.timeStamp-drag.lastTime)<90?drag.velocity:0;
  if(canvas.hasPointerCapture(drag.id))canvas.releasePointerCapture(drag.id);
  drag=null;canvas.classList.remove('is-dragging');
  let end=state.target+(state.reduced?0:THREE.MathUtils.clamp(velocity,-1,1)*.10);
  if(end<.025)end=0;else if(end>.975)end=1;setTarget(end);
}
canvas.addEventListener('pointerup',endDrag);canvas.addEventListener('pointercancel',e=>{if(drag){drag.velocity=0;endDrag(e);}});
canvas.addEventListener('wheel',e=>{if(Math.abs(e.deltaX)>Math.abs(e.deltaY)*.65&&Math.abs(e.deltaX)>1){e.preventDefault();setTarget(state.target+e.deltaX/(viewport.width*.85));}},{passive:false});
canvas.addEventListener('keydown',e=>{
  canvas.classList.remove('pointer-control');
  if(e.key==='ArrowLeft'){e.preventDefault();setTarget(state.target+.08);}
  if(e.key==='ArrowRight'){e.preventDefault();setTarget(state.target-.08);}
  if(e.key==='Home'){e.preventDefault();setTarget(0);}
  if(e.key==='End'){e.preventDefault();setTarget(1);}
  if(e.code==='Space'){e.preventDefault();state.paused=!state.paused;$('#scene-status').textContent=state.paused?'Movement paused.':'Movement resumed.';requestFrame();}
});
motionQuery.addEventListener('change',e=>{state.reduced=e.matches;state.paused=e.matches;if(e.matches)state.progress=state.target;requestFrame();});
document.addEventListener('visibilitychange',()=>{lastTime=0;if(document.hidden){cancelAnimationFrame(raf);raf=0;}else requestFrame();});
window.addEventListener('resize',resize,{passive:true});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();state.ready=false;$('#loading').hidden=true;$('#scene-status').textContent='The scene is unavailable. You can continue to Research.';});
canvas.addEventListener('webglcontextrestored',()=>location.reload());
init();
