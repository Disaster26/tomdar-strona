(function(){
  'use strict';
  var d=document, w=window;
  function $(s,c){return (c||d).querySelector(s);}
  function $$(s,c){return [].slice.call((c||d).querySelectorAll(s));}
  function magazyn(k,v){try{ if(v===undefined) return w.localStorage.getItem(k); w.localStorage.setItem(k,v);}catch(e){return null;}}

  // rok w stopce
  $$('[data-rok]').forEach(function(el){el.textContent=new Date().getFullYear();});

  // ---------------------------------------------------------------- menu mobilne
  var burger=$('.burger'), menu=$('#menu-mob');
  function zamknij(){menu.hidden=true;burger.setAttribute('aria-expanded','false');burger.setAttribute('aria-label','Otwórz menu');}
  if(burger&&menu){
    burger.addEventListener('click',function(){
      var otw=menu.hidden; menu.hidden=!otw;
      burger.setAttribute('aria-expanded',String(otw));
      burger.setAttribute('aria-label',otw?'Zamknij menu':'Otwórz menu');
    });
    menu.addEventListener('click',function(e){ if(e.target.closest('a')) zamknij(); });
    d.addEventListener('keydown',function(e){ if(e.key==='Escape' && !menu.hidden) zamknij(); });
  }

  // ---------------------------------------------------------------- dolny pasek na telefonie
  var mob=$('#mob');
  if(mob){
    var prog=$('.hero-akcje')||$('.ph');
    function pasek(pokaz){
      mob.classList.toggle('widac',pokaz);
      mob.setAttribute('aria-hidden',String(!pokaz));
      $$('a',mob).forEach(function(a){a.tabIndex=pokaz?0:-1;});
    }
    if(prog && 'IntersectionObserver' in w){
      new IntersectionObserver(function(wp){
        pasek(!wp[0].isIntersecting && wp[0].boundingClientRect.top<0);
      }).observe(prog);
    }
  }

  // ---------------------------------------------------------------- przeciąganie myszą (palcem działa natywnie)
  function przeciagaj(el){
    var x0=0,s0=0,ruch=false,wcis=false;
    el.addEventListener('pointerdown',function(e){
      if(e.pointerType!=='mouse'||e.button!==0) return;
      wcis=true;ruch=false;x0=e.clientX;s0=el.scrollLeft;
    });
    w.addEventListener('pointermove',function(e){
      if(!wcis) return;
      var dx=e.clientX-x0;
      if(!ruch && Math.abs(dx)>5){ruch=true;el.classList.add('ciag');}
      if(ruch){el.scrollLeft=s0-dx;e.preventDefault();}
    });
    w.addEventListener('pointerup',function(){
      if(!wcis) return; wcis=false;
      if(ruch){
        el.classList.remove('ciag');
        el.dataset.blokuj='1'; setTimeout(function(){delete el.dataset.blokuj;},60);
        el.dispatchEvent(new CustomEvent('puszczono'));
      }
    });
    el.addEventListener('click',function(e){ if(el.dataset.blokuj){e.preventDefault();e.stopPropagation();} },true);
    el.addEventListener('dragstart',function(e){e.preventDefault();});
  }

  // ---------------------------------------------------------------- karuzele w kartach (1 zdjęcie na widok)
  $$('[data-kar]').forEach(function(k){
    var tor=$('.kar-tor',k), zd=$$('img',tor), n=zd.length;
    if(n<2) return;
    var licz=d.createElement('span'); licz.className='kar-licz'; licz.setAttribute('aria-hidden','true'); k.appendChild(licz);
    var l=d.createElement('button'), p=d.createElement('button');
    l.type=p.type='button'; l.className='kar-b l'; p.className='kar-b p';
    l.setAttribute('aria-label','Poprzednie zdjęcie'); p.setAttribute('aria-label','Następne zdjęcie');
    l.innerHTML='<span class="strz-l"></span>'; p.innerHTML='<span class="strz-p"></span>';
    k.appendChild(l); k.appendChild(p);
    function idx(){return Math.round(tor.scrollLeft/Math.max(1,tor.clientWidth));}
    function odswiez(){var i=idx(); licz.textContent=(i+1)+' / '+n; l.disabled=i<=0; p.disabled=i>=n-1;}
    function idz(i){tor.scrollTo({left:Math.max(0,Math.min(n-1,i))*tor.clientWidth,behavior:'smooth'});}
    l.addEventListener('click',function(){idz(idx()-1);});
    p.addEventListener('click',function(){idz(idx()+1);});
    tor.addEventListener('keydown',function(e){
      if(e.key==='ArrowRight'){e.preventDefault();idz(idx()+1);}
      if(e.key==='ArrowLeft'){e.preventDefault();idz(idx()-1);}
    });
    var t; tor.addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(odswiez,60);},{passive:true});
    przeciagaj(tor);
    tor.addEventListener('puszczono',function(){setTimeout(function(){idz(idx());},10);});
    odswiez();
  });

  // ---------------------------------------------------------------- lightbox (wspólny)
  var lb=$('#lb'), lbImg=lb?$('img',lb):null, lbOpis=lb?$('.lb-opis',lb):null, lbLicz=lb?$('.lb-licz',lb):null, lista=[], cur=0;
  function pokaz(i){
    cur=(i+lista.length)%lista.length;
    var im=$('img',lista[cur]);
    lbImg.src=im.currentSrc||im.src; lbImg.alt=im.alt;
    lbOpis.textContent=im.alt; lbLicz.textContent=(cur+1)+' / '+lista.length;
  }
  function otworz(el){
    lista=$$('[data-grupa="'+el.dataset.grupa+'"]'); pokaz(lista.indexOf(el));
    if(lb.showModal){lb.showModal();} else {lb.setAttribute('open','');}
  }
  if(lb){
    $('.lb-x',lb).addEventListener('click',function(){lb.close();});
    $('.lb-prev',lb).addEventListener('click',function(){pokaz(cur-1);});
    $('.lb-next',lb).addEventListener('click',function(){pokaz(cur+1);});
    lb.addEventListener('click',function(e){ if(e.target===lb) lb.close(); });
    lb.addEventListener('keydown',function(e){
      if(e.key==='ArrowLeft') pokaz(cur-1);
      if(e.key==='ArrowRight') pokaz(cur+1);
    });
    var tx=null;
    lb.addEventListener('touchstart',function(e){tx=e.touches[0].clientX;},{passive:true});
    lb.addEventListener('touchend',function(e){
      if(tx===null) return; var dx=e.changedTouches[0].clientX-tx; tx=null;
      if(Math.abs(dx)>40) pokaz(cur+(dx<0?1:-1));
    });
  }

  // ---------------------------------------------------------------- tory zdjęć z licznikiem
  $$('[data-tor]').forEach(function(tor){
    var sek=tor.closest('section'), el=$$('.real',tor), n=el.length;
    var licz=$('.tor-licz',sek), strz=$$('[data-strz]',sek);
    przeciagaj(tor);
    function krok(){return Math.max(260,tor.clientWidth*0.7);}
    strz.forEach(function(b){
      b.addEventListener('click',function(){tor.scrollBy({left:krok()*Number(b.dataset.strz),behavior:'smooth'});});
    });
    function stan(){
      var lewo=tor.scrollLeft, pad=parseFloat(getComputedStyle(tor).paddingLeft)||0, i=0;
      var koniec=lewo+tor.clientWidth>=tor.scrollWidth-4;
      if(koniec){ i=n-1; }
      else {
        for(var j=0;j<n;j++){ if(el[j].offsetLeft-pad>=lewo-el[j].offsetWidth/2){ i=j; break; } }
      }
      if(licz) licz.textContent=(i+1)+' / '+n;
      if(strz.length){ strz[0].disabled=lewo<=2; strz[1].disabled=koniec; }
    }
    var t; tor.addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(stan,50);},{passive:true});
    w.addEventListener('resize',stan); stan();
    el.forEach(function(b){ b.addEventListener('click',function(){ if(lb) otworz(b); }); });
  });

  // ---------------------------------------------------------------- chipsy realizacji: aktywna kategoria
  var chips=$$('.chips a');
  if(chips.length && 'IntersectionObserver' in w){
    var io=new IntersectionObserver(function(wp){
      wp.forEach(function(x){
        if(x.isIntersecting){
          chips.forEach(function(a){
            var ak=a.getAttribute('href')==='#'+x.target.id; a.classList.toggle('akt',ak);
            if(ak){ var p=a.parentNode; p.scrollTo({left:a.offsetLeft-16,behavior:'smooth'}); }
          });
        }
      });
    },{rootMargin:'-40% 0px -55% 0px'});
    $$('.gal').forEach(function(s){io.observe(s);});
  }

  // ---------------------------------------------------------------- cookies + mapa Google
  var KLUCZ='tomdar_zgody', ck=$('#ck');
  function wczytaj(){
    try{ var z=JSON.parse(magazyn(KLUCZ)||'null'); if(z && z.t && Date.now()-z.t<365*864e5) return z; }catch(e){}
    return null;
  }
  function mapy(zgoda){
    $$('[data-mapa]').forEach(function(m){
      var f=$('iframe',m), zast=$('.mapa-zast',m);
      if(zgoda){
        if(!f.getAttribute('src') && f.dataset.src) f.setAttribute('src',f.dataset.src);
        f.hidden=false; zast.hidden=true;
      } else {
        if(f.getAttribute('src')){ f.dataset.src=f.getAttribute('src'); f.removeAttribute('src'); }
        f.hidden=true; zast.hidden=false;
      }
    });
  }
  function zapisz(mapa){
    magazyn(KLUCZ,JSON.stringify({v:1,mapa:!!mapa,t:Date.now()}));
    mapy(!!mapa); if(ck) ck.hidden=true;
  }
  if(ck){
    var opcje=$('.ck-opcje',ck), chk=$('[data-ck-mapa]',ck), bZap=$('[data-ck="zapisz"]',ck), bUst=$('[data-ck="ustawienia"]',ck);
    function pokazBaner(ust){
      var z=wczytaj(); chk.checked=z?!!z.mapa:true;
      opcje.hidden=!ust; bZap.hidden=!ust; bUst.hidden=!!ust; ck.hidden=false;
    }
    ck.addEventListener('click',function(e){
      var b=e.target.closest('[data-ck]'); if(!b) return;
      var a=b.dataset.ck;
      if(a==='wszystkie') zapisz(true);
      else if(a==='niezbedne') zapisz(false);
      else if(a==='zapisz') zapisz(chk.checked);
      else if(a==='ustawienia') pokazBaner(true);
    });
    $$('[data-cookies-ustawienia]').forEach(function(b){b.addEventListener('click',function(){pokazBaner(true);});});
    $$('[data-ck-wlacz-mape]').forEach(function(b){b.addEventListener('click',function(){zapisz(true);});});
    var z=wczytaj();
    if(z){ mapy(!!z.mapa); }
    else {
      // baner po pierwszym przewinięciu lub interakcji, żeby nie zasłaniał pierwszego ekranu
      var pokazano=false;
      var raz=function(){ if(pokazano||wczytaj()) return; pokazano=true; pokazBaner(false);
        w.removeEventListener('scroll',przew); d.removeEventListener('pointerdown',raz); d.removeEventListener('keydown',raz); };
      var przew=function(){ if(w.scrollY>80) raz(); };
      w.addEventListener('scroll',przew,{passive:true}); d.addEventListener('pointerdown',raz); d.addEventListener('keydown',raz);
      if(w.scrollY>80) raz();
    }
  }

  // ---------------------------------------------------------------- formularz
  var f=$('#formularz');
  if(f){
    var info=$('.form-info',f), btn=$('button[type=submit]',f), test=f.dataset.tryb==='test';
    var zp=$('[name=_z]',f), pobrany=false;
    function znacznik(){
      if(test||pobrany) return; pobrany=true;
      fetch(f.dataset.znacznik,{credentials:'same-origin',cache:'no-store'}).then(function(r){return r.ok?r.json():null;})
        .then(function(j){ if(j&&j.z) zp.value=j.z; }).catch(function(){});
    }
    f.addEventListener('focusin',znacznik,{once:true});
    f.addEventListener('pointerdown',znacznik,{once:true});
    function komunikat(t,klasa){info.textContent=t;info.className='form-info'+(klasa?' '+klasa:'');}
    f.addEventListener('submit',function(e){
      e.preventDefault();
      var tel=$('[name=telefon]',f).value.trim(), mail=$('[name=email]',f), plik=$('[name=plik]',f);
      if(!f.checkValidity()){ f.reportValidity(); return; }
      if(!tel && !mail.value.trim()){ komunikat('Podaj numer telefonu lub adres e-mail.','blad'); $('[name=telefon]',f).focus(); return; }
      if(plik.files[0] && plik.files[0].size>10*1024*1024){ komunikat('Plik jest większy niż 10 MB. Wyślij mniejszy albo prześlij go e-mailem.','blad'); return; }
      if(test){ komunikat('To wersja testowa strony: formularz zacznie wysyłać zapytania na tomdar.meble@gmail.com po wgraniu na tomdar-meble.pl.','ok'); return; }
      btn.disabled=true; komunikat('Wysyłanie...');
      fetch(f.action,{method:'POST',body:new FormData(f),headers:{'Accept':'application/json'},credentials:'same-origin'})
        .then(function(r){return r.json().catch(function(){return {success:false};});})
        .then(function(j){
          if(j&&j.success){ f.reset(); komunikat('Dziękujemy, zapytanie zostało wysłane. Odezwiemy się najszybciej, jak to możliwe.','ok'); }
          else { komunikat((j&&j.komunikat)||'Nie udało się wysłać wiadomości. Zadzwoń: 501 156 315 albo napisz na tomdar.meble@gmail.com.','blad'); }
        })
        .catch(function(){ komunikat('Brak połączenia. Spróbuj ponownie albo zadzwoń: 501 156 315.','blad'); })
        .then(function(){ btn.disabled=false; pobrany=false; zp.value=''; znacznik(); });
    });
  }
})();
