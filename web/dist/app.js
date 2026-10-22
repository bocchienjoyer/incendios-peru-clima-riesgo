const $ = id => document.getElementById(id);
const fmt = (n, digits=0) => Number(n || 0).toLocaleString('es-ES',{minimumFractionDigits:digits,maximumFractionDigits:digits});
const names={'ANCASH':'Áncash','APURIMAC':'Apurímac','HUANUCO':'Huánuco','JUNIN':'Junín','SAN MARTIN':'San Martín'};
const title = n => names[n] || n.toLowerCase().replace(/(^|\s)\S/g,c=>c.toUpperCase());
const code = n => String(n).padStart(2,'0');
const load = async file => {const r=await fetch(`assets/${file}`);if(!r.ok)throw Error(`No se pudo cargar ${file}`);return r.json();};
let data, departments, points, crops, map, deptLayer, groupLayer, cropLayer, ringLayer, selectedLayer;
let selected='G1184', department='todos', scenario='base';
const current = () => data.agrupaciones.find(g=>g.grupo_id===selected);
const field = () => scenario==='base' ? 'horas_base':'horas_sensibilidad';
const match = g => g.apta_comparacion && g.midagri_agricola_ha>0 && g[field()]>0;
const color = g => !g.apta_comparacion?'#8b9187':match(g)?'#d67639':'#527b5c';
const filtered = () => data.agrupaciones.filter(g=>department==='todos'||code(g.codigo_departamento)===department);
const clear = layer => layer && layer.clearLayers();

function buildMap(){
  map=L.map('mapa',{scrollWheelZoom:false,minZoom:4,maxZoom:17,zoomControl:true}).setView([-9.2,-75.1],5);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map);
  deptLayer=L.geoJSON(departments,{style:f=>({color:'#78927d',weight:.8,fillColor:'#91a986',fillOpacity:.1}),onEachFeature:(f,layer)=>{
    layer.bindTooltip(title(f.properties.NOMBDEP),{sticky:true});
    layer.on('click',()=>setDepartment(code(f.properties.FIRST_IDDP),true));
  }}).addTo(map);
  groupLayer=L.layerGroup().addTo(map);cropLayer=L.layerGroup().addTo(map);ringLayer=L.layerGroup().addTo(map);selectedLayer=L.layerGroup().addTo(map);
  map.fitBounds(deptLayer.getBounds(),{padding:[12,12]});
}

function drawGroups(){
  clear(groupLayer);
  for(const g of filtered()){
    const radius=match(g)?9:Math.min(8,4+Math.sqrt(g.detecciones_48h)/2);
    L.circleMarker([g.latitud,g.longitud],{radius,color:'#fffdf6',weight:1.3,fillColor:color(g),fillOpacity:.92})
      .bindTooltip(`${title(g.departamento)} · ${g.grupo_id}<br>${g.detecciones_48h} detecciones · ${fmt(g.midagri_agricola_ha,2)} ha cercanas`)
      .on('click',()=>{selected=g.grupo_id;$('grupo').value=selected;renderSelected(true);}).addTo(groupLayer);
  }
  deptLayer.setStyle(f=>({fillOpacity:department===code(f.properties.FIRST_IDDP)?.27:.07,weight:department===code(f.properties.FIRST_IDDP)?2:.7}));
}

function setDepartment(value,zoom=true){
  department=value;$('departamento').value=value;
  const available=filtered();
  $('grupo').innerHTML=available.length?available.map(g=>`<option value="${g.grupo_id}">${g.grupo_id} · ${g.detecciones_48h} detecciones${g.apta_comparacion?'':' · revisión'}</option>`).join(''):'<option>Sin detecciones recientes</option>';
  $('grupo').disabled=!available.length;
  if(!available.some(g=>g.grupo_id===selected))selected=available[0]?.grupo_id||null;
  $('grupo').value=selected||'';
  drawGroups();renderSelected(false);renderTable();
  if(zoom){
    const f=departments.features.find(f=>code(f.properties.FIRST_IDDP)===value);
    map.fitBounds(f?L.geoJSON(f).getBounds():deptLayer.getBounds(),{padding:[20,20],animate:!window.matchMedia('(prefers-reduced-motion: reduce)').matches});
  }
}

function renderSelected(zoom=false){
  const g=current();clear(cropLayer);clear(ringLayer);clear(selectedLayer);
  if(!g){$('detalle').innerHTML='<span class="eyebrow">SIN DETECCIONES RECIENTES</span><h3>Sin grupos en esta captura.</h3><p class="detail-copy">No se identificaron agrupaciones recientes en este departamento. Esto no garantiza ausencia de fuego o de riesgo agrícola.</p>';$('dias').innerHTML='';$('forecast-title').textContent='Selecciona otra agrupación';return;}
  let status=!g.apta_comparacion?'Revisión pendiente':match(g)?'Coincidencia con agricultura':'Sin coincidencia en este escenario';
  $('detalle').innerHTML=`<div class="eyebrow">${title(g.departamento).toUpperCase()} · ${g.grupo_id}</div><h3>${fmt(g.midagri_agricola_ha,2)} <small>ha</small></h3><p class="subtle">agrícolas cartografiadas a ≤1 km</p><span class="pill ${!g.apta_comparacion?'pending':match(g)?'positive':''}">${status}</span><div class="detail-stats"><div><strong>${g.detecciones_48h}</strong><span>DETECCIONES / 48 H</span></div><div><strong>${g[field()]} h</strong><span>ESCENARIO ${scenario==='base'?'BASE':'ALTERNATIVO'}</span></div><div><strong>${fmt(g.tmax_c,1)}°</strong><span>T. MÁXIMA / 7 DÍAS</span></div><div><strong>${fmt(g.lluvia_7d_mm,1)}</strong><span>LLUVIA / 7 DÍAS (MM)</span></div></div><p class="detail-copy">${g.apta_comparacion?(match(g)?'Coinciden la agricultura cercana y horas secas con viento y poca lluvia previa. Esto orienta una revisión; no estima daños ni probabilidad de propagación.':'La cercanía al fuego y las condiciones meteorológicas son dos lecturas distintas. Aquí no coinciden bajo el escenario elegido.'):'Este grupo se conserva en el mapa y en las tablas, pero no entra en las coincidencias principales.'}</p>${g.revision?`<div class="detail-note">Observación: ${g.revision}. La cartografía de cobertura es de 2021; la causa de las señales sigue sin confirmar.</div>`:''}${g.grupo_id==='G1184'?'<div class="detail-note">Las 5 horas base aparecen el 27–28 oct. En las primeras 72 horas: <strong>0 h</strong>. La incertidumbre aumenta al final del horizonte.</div><p><a class="text-link" href="#terreno">Abrir caso en 3D ↗</a></p>':''}`;
  const subset=points.filter(p=>p.grupo_id===g.grupo_id);
  if($('ver-agricultura').checked){
    L.geoJSON({type:'FeatureCollection',features:crops.features.filter(f=>f.properties.grupo_id===g.grupo_id)},{style:{color:'#087f67',weight:1.6,fillColor:'#31b798',fillOpacity:.27}}).addTo(cropLayer);
  }
  for(const p of subset){
    if($('ver-entorno').checked)L.circle([p.latitude,p.longitude],{radius:1000,color:'#c1793f',weight:1,dashArray:'4 5',fillOpacity:.035}).addTo(ringLayer);
    L.circleMarker([p.latitude,p.longitude],{radius:3,color:'#fff',weight:1,fillColor:'#d86b30',fillOpacity:1}).bindTooltip(`Detección VIIRS · ${new Date(p.fecha_utc).toLocaleString('es-ES',{timeZone:'America/Lima'})} (Lima)<br>FRP: ${fmt(p.frp,2)} MW`).addTo(selectedLayer);
  }
  if(zoom)map.setView([g.latitud,g.longitud],12,{animate:!window.matchMedia('(prefers-reduced-motion: reduce)').matches});
  renderForecast(g);
}

function renderForecast(g){
  $('forecast-title').textContent=`${title(g.departamento)} · ${g.grupo_id}`;
  const days=data.meteorologia_diaria.filter(r=>r.grupo_id===g.grupo_id);
  $('dias').innerHTML=days.map(d=>{
    const h=d[field()];const date=new Date(d.dia+'T12:00:00-05:00').toLocaleDateString('es-PE',{weekday:'short',day:'numeric',month:'short',timeZone:'America/Lima'});
    return `<article class="day ${h?'active':''}"><div class="day-date">${date}</div><div class="hour-track" aria-hidden="true"><div class="hour-bar" style="--h:${Math.max(0,h/24*100)}%"></div></div><strong>${h} h <small>de 24</small></strong><dl><dt>T. máx.</dt><dd>${fmt(d.tmax_c,1)} °C</dd><dt>HR mín.</dt><dd>${fmt(d.humedad_min_pct)} %</dd><dt>Viento máx.</dt><dd>${fmt(d.viento_max_kmh,1)} km/h</dd><dt>Lluvia diaria</dt><dd>${fmt(d.lluvia_mm,1)} mm</dd></dl></article>`;
  }).join('');
}

function renderTable(){
  const sort=$('orden').value;
  const rows=[...data.departamentos].sort((a,b)=>b[sort]-a[sort]||b.agricola_cercana_ha_unicas-a.agricola_cercana_ha_unicas);
  $('tabla-dept').innerHTML=rows.map(d=>`<tr class="${department===code(d.codigo_departamento)?'selected':''}"><td><button data-departamento="${code(d.codigo_departamento)}" aria-label="Ver ${title(d.departamento)} en el mapa">${title(d.departamento)} ↗</button></td><td>${d.agrupaciones_recientes}</td><td>${d.agrupaciones_con_agricultura}</td><td>${fmt(d.agricola_cercana_ha_unicas,2)}</td><td>${d.grupos_coincidencia_base?`<span class="badge">${d.grupos_coincidencia_base} caso</span>`:'0'}</td><td>${d.agrupaciones_revision}</td></tr>`).join('');
  $('tabla-dept').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{setDepartment(b.dataset.departamento,true);$('explorar').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}));
}

async function init(){
  try{
    [data,departments,points,crops]=await Promise.all(['dashboard_datos.json','departamentos.geojson','detecciones.json','agricultura.geojson'].map(load));
    $('departamento').insertAdjacentHTML('beforeend',[...data.departamentos].sort((a,b)=>title(a.departamento).localeCompare(title(b.departamento),'es')).map(d=>`<option value="${code(d.codigo_departamento)}">${title(d.departamento)}</option>`).join(''));
    buildMap();setDepartment('todos',false);$('loading').hidden=true;
    $('departamento').addEventListener('change',e=>setDepartment(e.target.value));
    $('grupo').addEventListener('change',e=>{selected=e.target.value;renderSelected(true);});
    $('escenario').addEventListener('change',e=>{scenario=e.target.value;drawGroups();renderSelected(false);});
    $('peru').addEventListener('click',()=>setDepartment('todos'));
    $('orden').addEventListener('change',renderTable);
    for(const id of ['ver-agricultura','ver-entorno'])$(id).addEventListener('change',()=>renderSelected());
    const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){observer.disconnect();initTerrain();}},{rootMargin:'250px'});observer.observe($('terreno'));
  }catch(e){$('loading').className='error';$('loading').textContent=`No se pudo abrir el explorador. Recarga la página o consulta los CSV del repositorio. ${e.message}`;console.error(e);}
}

async function initTerrain(){
  try{
    const [THREE,{OrbitControls},t]=await Promise.all([import('three'),import('./vendor/OrbitControls.js'),load('puno_terreno.json')]);
    const host=$('escena'),scene=new THREE.Scene();scene.background=new THREE.Color('#112a23');
    const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.setSize(host.clientWidth,host.clientHeight);host.appendChild(renderer.domElement);
    const camera=new THREE.PerspectiveCamera(40,host.clientWidth/host.clientHeight,.1,100);const controls=new OrbitControls(camera,renderer.domElement);
    controls.enableDamping=true;controls.minDistance=5;controls.maxDistance=27;controls.maxPolarAngle=Math.PI*.48;controls.target.set(0,.4,0);controls.enablePan=true;
    const reset=()=>{camera.position.set(9,10,12);controls.target.set(0,.4,0);controls.update();};reset();
    const [w,s,e,n]=t.bbox_wgs84,midlat=(s+n)/2,widthM=(e-w)*111320*Math.cos(midlat*Math.PI/180),heightM=(n-s)*111320,scale=10/widthM,depth=heightM*scale;
    const size=t.size,geometry=new THREE.PlaneGeometry(10,depth,size-1,size-1);geometry.rotateX(-Math.PI/2);
    for(let i=0;i<t.heights_m.length;i++)geometry.attributes.position.setY(i,(t.heights_m[i]-t.min_m)*scale*1.3);
    geometry.computeVertexNormals();
    const material=new THREE.MeshStandardMaterial({roughness:1,metalness:0,side:THREE.DoubleSide});const mesh=new THREE.Mesh(geometry,material);scene.add(mesh);
    const loader=new THREE.TextureLoader();const satellite=await loader.loadAsync('assets/puno_satelite.jpg');satellite.colorSpace=THREE.SRGBColorSpace;satellite.anisotropy=renderer.capabilities.getMaxAnisotropy();material.map=satellite;material.color.set('#ffffff');material.needsUpdate=true;
    const wc=await loader.loadAsync('assets/puno_worldcover.png');wc.colorSpace=THREE.SRGBColorSpace;wc.magFilter=THREE.NearestFilter;wc.minFilter=THREE.NearestFilter;
    // Gris en los píxeles fuera del recorte válido, conservando categorías sin interpolar.
    const canvas=document.createElement('canvas');canvas.width=768;canvas.height=768;const ctx=canvas.getContext('2d');ctx.fillStyle='#8a9983';ctx.fillRect(0,0,768,768);ctx.drawImage(wc.image,0,0);const wcTexture=new THREE.CanvasTexture(canvas);wcTexture.colorSpace=THREE.SRGBColorSpace;wcTexture.magFilter=THREE.NearestFilter;wcTexture.minFilter=THREE.NearestFilter;
    const colors=[];for(const h of t.heights_m){const c=new THREE.Color().setHSL(.25,.16,.37+.25*(h-t.min_m)/(t.max_m-t.min_m));colors.push(c.r,c.g,c.b);}geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
    scene.add(new THREE.AmbientLight(0xffffff,2));const sun=new THREE.DirectionalLight(0xfff7df,1.5);sun.position.set(-6,12,5);scene.add(sun);
    function altitude(lon,lat){
      const x=Math.max(0,Math.min(size-1,(lon-w)/(e-w)*(size-1))),y=Math.max(0,Math.min(size-1,(n-lat)/(n-s)*(size-1)));
      const x0=Math.floor(x),y0=Math.floor(y),x1=Math.min(size-1,x0+1),y1=Math.min(size-1,y0+1),a=x-x0,b=y-y0;
      return t.heights_m[y0*size+x0]*(1-a)*(1-b)+t.heights_m[y0*size+x1]*a*(1-b)+t.heights_m[y1*size+x0]*(1-a)*b+t.heights_m[y1*size+x1]*a*b;
    }
    function position(lon,lat,offset=.015){return new THREE.Vector3((lon-(w+e)/2)*111320*Math.cos(midlat*Math.PI/180)*scale,(altitude(lon,lat)-t.min_m)*scale*1.3+offset,((n+s)/2-lat)*111320*scale);}
    const agriculture=new THREE.Group(),fire=new THREE.Group(),rings=new THREE.Group();scene.add(agriculture,fire,rings);
    function terrainLine(coords,mat,parent){
      let segment=[];
      const flush=()=>{if(segment.length>1)parent.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(segment),mat));segment=[];};
      for(let k=0;k<coords.length-1;k++){
        const [lon0,lat0]=coords[k],[lon1,lat1]=coords[k+1];const steps=Math.max(1,Math.ceil(Math.hypot((lon1-lon0)*107000,(lat1-lat0)*111320)/30));
        for(let j=0;j<=steps;j++){const a=j/steps,lon=lon0+(lon1-lon0)*a,lat=lat0+(lat1-lat0)*a;if(lon<w||lon>e||lat<s||lat>n){flush();continue;}segment.push(position(lon,lat,.027));}
      }flush();
    }
    const agMat=new THREE.LineBasicMaterial({color:'#53ffda',depthTest:false,transparent:true,opacity:.95});
    for(const f of crops.features.filter(f=>f.properties.grupo_id==='G1184')){
      const polygons=f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[f.geometry.coordinates];for(const poly of polygons)for(const ring of poly)terrainLine(ring,agMat,agriculture);
    }
    const ringMat=new THREE.LineBasicMaterial({color:'#edc28b',transparent:true,opacity:.55});
    for(const p of points.filter(p=>p.grupo_id==='G1184')){
      const marker=new THREE.Mesh(new THREE.SphereGeometry(.065,16,12),new THREE.MeshBasicMaterial({color:'#ff8e45'}));marker.position.copy(position(p.longitude,p.latitude,.09));fire.add(marker);
      const stem=new THREE.Line(new THREE.BufferGeometry().setFromPoints([position(p.longitude,p.latitude,0),position(p.longitude,p.latitude,.09)]),new THREE.LineBasicMaterial({color:'#ffe8ba'}));fire.add(stem);
      const circle=[];for(let j=0;j<=180;j++){const a=j/180*Math.PI*2;circle.push([p.longitude+1000*Math.cos(a)/(111320*Math.cos(midlat*Math.PI/180)),p.latitude+1000*Math.sin(a)/111320]);}terrainLine(circle,ringMat,rings);
    }
    // Borde del recorte para percibir su escala sin inventar elevaciones.
    const perimeter=[[w,n],[e,n],[e,s],[w,s],[w,n]];terrainLine(perimeter,new THREE.LineBasicMaterial({color:'#8eaa8f',transparent:true,opacity:.6}),scene);
    for(const b of document.querySelectorAll('[data-textura]'))b.addEventListener('click',()=>{
      const mode=b.dataset.textura;material.map=mode==='satelite'?satellite:mode==='worldcover'?wcTexture:null;material.vertexColors=mode==='relieve';material.color.set('#ffffff');material.needsUpdate=true;
      document.querySelectorAll('[data-textura]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});$('leyenda-wc').hidden=mode!=='worldcover';
    });
    $('agri-3d').addEventListener('change',e=>agriculture.visible=e.target.checked);$('fuego-3d').addEventListener('change',e=>fire.visible=e.target.checked);$('anillo-3d').addEventListener('change',e=>rings.visible=e.target.checked);
    $('reset-3d').addEventListener('click',reset);$('vista-plana').addEventListener('click',()=>{camera.position.set(0,17,.01);controls.target.set(0,0,0);controls.update();});
    new ResizeObserver(()=>{camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();renderer.setSize(host.clientWidth,host.clientHeight);}).observe(host);
    let visible=true;new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;}).observe(host);
    renderer.setAnimationLoop(()=>{if(visible&&!document.hidden){controls.update();renderer.render(scene,camera);}});
    $('estado-3d').remove();host.dataset.ready='true';
  }catch(e){console.error(e);$('estado-3d').innerHTML='El visor 3D necesita WebGL. Puedes consultar la imagen y los resultados a continuación.';const image=document.createElement('img');image.src='assets/puno_contexto.jpg';image.alt='Imagen Sentinel-2 de Puno con detecciones y contornos agrícolas';image.className='scene-fallback';$('escena').appendChild(image);}
}

init();
