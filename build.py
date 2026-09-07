#!/usr/bin/env python3
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from email.utils import parsedate_to_datetime
from collections import defaultdict
import re, html, unicodedata, hashlib, math

FEED='https://feeds.redcircle.com/3f9ae940-2590-40af-9698-d018fb5c5604'
BASE='https://cafebelgrado.github.io/cafe-belgrado'
PREFIX='/cafe-belgrado'
OUT=Path('_site')
ORELO='https://escute.orelo.audio/cafebelgrado'
ACADEMY='https://cafebelgrado.carrd.co/'
ELASTICO='https://open.spotify.com/show/1bBPqASKPNkLa937oK3jxM'
YOUTUBE='https://www.youtube.com/c/PodcastCaf%C3%A9Belgrado'
NS={'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd','content':'http://purl.org/rss/1.0/modules/content/'}

def txt(node,path):
    el=node.find(path,NS); return (el.text or '').strip() if el is not None and el.text else ''
def clean(s):
    s=re.sub(r'<br\s*/?>',' ',s or '',flags=re.I); s=re.sub(r'<[^>]+>',' ',s); return re.sub(r'\s+',' ',html.unescape(s)).strip()
def norm(s): return unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
def slugify(s): return re.sub(r'[^a-z0-9]+','-',norm(s)).strip('-')[:96] or 'episodio'
def esc(s): return html.escape(str(s or ''),quote=True)
def date_info(s):
    try:
        d=parsedate_to_datetime(s); return d.date().isoformat(),d.strftime('%d/%m/%Y')
    except: return '',''
def duration(s):
    try:
        sec=int(s); h,r=divmod(sec,3600); m,_=divmod(r,60); return f'{h}h {m:02d}min' if h else f'{m}min'
    except: return ''
def tone(slug): return int(hashlib.md5(slug.encode()).hexdigest()[:2],16)%7
RULES={'Allen Iverson':['iverson'],'LeBron James':['lebron'],'Michael Jordan':['michael jordan'],'Kobe Bryant':['kobe'],'Stephen Curry':['curry','steph'],'Kevin Durant':['durant'],'Nikola Jokic':['jokic'],'Giannis Antetokounmpo':['giannis'],'Luka Doncic':['luka','doncic'],'Victor Wembanyama':['wemby','wembanyama'],'Shai Gilgeous-Alexander':['shai'],'Kawhi Leonard':['kawhi'],'James Harden':['harden'],'Russell Westbrook':['westbrook'],'Joel Embiid':['embiid'],'Jayson Tatum':['tatum'],'Ben Simmons':['ben simmons'],'Cooper Flagg':['flagg'],'San Antonio Spurs':['spurs','san antonio'],'Los Angeles Lakers':['lakers'],'Boston Celtics':['celtics'],'Golden State Warriors':['warriors'],'Philadelphia 76ers':['76ers','sixers'],'New York Knicks':['knicks'],'Miami Heat':['miami heat'],'Chicago Bulls':['bulls'],'Cleveland Cavaliers':['cavaliers','cavs'],'Milwaukee Bucks':['bucks'],'Indiana Pacers':['pacers'],'Denver Nuggets':['nuggets'],'Oklahoma City Thunder':['okc','thunder'],'Minnesota Timberwolves':['timberwolves'],'Dallas Mavericks':['mavericks','mavs'],'Houston Rockets':['rockets'],'Memphis Grizzlies':['grizzlies'],'Phoenix Suns':['suns'],'Sacramento Kings':['kings'],'Los Angeles Clippers':['clippers'],'NBA':['nba'],'NBA Draft':['draft'],'Playoffs da NBA':['playoff'],'Trocas da NBA':['troca','trade'],'Selecao Brasileira':['selecao','brasil'],'NBB':['nbb'],'NCAA':['ncaa'],'FIBA':['fiba'],'Basquete europeu':['europeu','europa','euroleague','euroliga'],'WNBA':['wnba'],'Basquete feminino':['feminino','feminina']}
def rel(path=''): return f'{PREFIX}/{path}'.replace('//','/')
def header():
    return f'<a class="top" href="{ORELO}">ASSINE O CONTEUDO EXCLUSIVO DO CAFE BELGRADO <span>ORELO</span></a><header><div class="wrap nav"><a class="brand" href="{rel()}">Cafe Belgrado<small>NBA · Basquete · Vida</small></a><nav><a href="{ACADEMY}">Academy</a><a href="{rel()}#magazine">Magazine</a><a href="{ELASTICO}">Elastico Mental</a><a href="{rel("podcast/")}">Podcast</a><a href="{YOUTUBE}">YouTube</a></nav></div></header>'
def footer(): return '<footer><div class="wrap">Cafe Belgrado · podcast · Academy · Magazine · Elastico Mental</div></footer>'
CSS='''*{box-sizing:border-box}body{margin:0;background:#f4efe5;color:#151515;font-family:Arial,sans-serif;line-height:1.5}a{color:inherit;text-decoration:none}.wrap{width:min(1180px,calc(100% - 32px));margin:auto}.top{display:block;background:#f2b62b;padding:13px;text-align:center;font-weight:900}.top span{font-size:11px;margin-left:9px}header{background:#151515;color:#fff}.nav{min-height:68px;display:flex;align-items:center;gap:28px}.brand{font-family:Georgia,serif;font-weight:900;font-size:24px}.brand small{display:block;font:700 9px Arial;letter-spacing:.12em;color:#aaa}nav{display:flex;gap:18px;margin-left:auto;font-size:12px;font-weight:700}.hero{background:#151515;color:#fff;padding:54px 0}.hero h1{font:900 clamp(48px,7vw,84px)/.95 Georgia,serif;margin:12px 0}.hero p{color:#c9c4ba;max-width:760px;font-size:18px}.cta{display:inline-block;margin-top:20px;background:#f2b62b;color:#111;border-radius:14px;padding:18px 22px;font-weight:900}.products,.episodes,.topics{display:grid;gap:15px}.products{grid-template-columns:repeat(3,1fr);margin:42px 0}.product,.card{background:#fffdf8;border:1px solid #ddd2c2;border-radius:17px;overflow:hidden}.product{padding:26px;min-height:260px;display:flex;flex-direction:column}.product h2,.section h2,.card h3{font-family:Georgia,serif}.product strong{margin-top:auto}.academy{background:#f2b62b}.mag{background:#a63c2c;color:#fff}.elastico{background:#1e342c;color:#fff}.section{padding:36px 0}.section-head{display:flex;justify-content:space-between;align-items:end;margin-bottom:18px}.episodes{grid-template-columns:repeat(3,1fr)}.card .art{height:195px}.art img{width:100%;height:100%;object-fit:cover}.poster{height:100%;padding:21px;color:#fff;display:flex;align-items:end;font:800 27px/.98 Georgia,serif}.t0{background:#a43b2d}.t1{background:#254b58}.t2{background:#a67a24}.t3{background:#594267}.t4{background:#424c28}.t5{background:#6d2c2c}.t6{background:#444}.copy{padding:17px}.meta{font-size:10px;color:#776f64;text-transform:uppercase;font-weight:800}.card h3{font-size:21px;margin:8px 0}.card p{font-size:13px;color:#6e675e}.tags{display:flex;flex-wrap:wrap;gap:6px}.tag{font-size:9px;background:#eee4d4;border-radius:999px;padding:5px 8px}.topics{grid-template-columns:repeat(4,1fr)}.topic{background:#191919;color:#fff;padding:18px;border-radius:14px}.topic strong{font-family:Georgia,serif;display:block;font-size:19px}.detail{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:22px}.article,.side{border-radius:18px;overflow:hidden}.article{background:#fffdf8;border:1px solid #ddd2c2}.article-head{display:grid;grid-template-columns:.9fr 1.1fr}.article-head .art{min-height:360px}.article-copy{padding:35px}.article-copy h1{font:900 clamp(38px,5vw,62px)/1 Georgia,serif}.body{padding:0 35px 36px}.player{background:#191919;color:#fff;padding:21px;border-radius:12px;margin:22px 0}.player audio{width:100%}.side{background:#191919;color:#fff;padding:22px;height:max-content}.related{display:block;padding:12px 0;border-bottom:1px solid #3a3a3a;font-size:12px}.pager{display:flex;flex-wrap:wrap;gap:7px;justify-content:center;margin-top:28px}.pager a{background:#fff;border:1px solid #ddd2c2;padding:8px 10px;border-radius:7px}footer{border-top:1px solid #ddd2c2;padding:28px 0;color:#777;font-size:11px}@media(max-width:900px){nav{display:none}.products,.episodes,.detail,.article-head{grid-template-columns:1fr}.topics{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.topics{grid-template-columns:1fr}}'''
def art(ep):
    if ep['image']: return f'<div class="art"><img loading="lazy" src="{esc(ep["image"])}" alt=""></div>'
    return f'<div class="art"><div class="poster t{tone(ep["slug"])}">{esc(ep["title"])}</div></div>'
def card(ep):
    desc=ep['summary'] or f'Episodio do Cafe Belgrado publicado em {ep["date_br"]}.'
    return f'<a class="card" href="{rel("podcast/"+ep["slug"]+"/")}">{art(ep)}<div class="copy"><div class="meta">{ep["date_br"]}{(" · "+ep["duration"]) if ep["duration"] else ""}</div><h3>{esc(ep["title"])}</h3><p>{esc(desc[:260])}</p><div class="tags">{"".join(f"<span class=tag>{esc(t)}</span>" for t in ep["topics"][:3])}</div></div></a>'
def page(title,desc,body,canonical):
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc[:300])}"><link rel="canonical" href="{canonical}"><style>{CSS}</style></head><body>{header()}{body}{footer()}</body></html>'
def write(path,content):
    p=OUT/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding='utf-8')
raw=urlopen(Request(FEED,headers={'User-Agent':'CafeBelgradoPages/1.0'}),timeout=60).read(); root=ET.fromstring(raw); channel=root.find('./channel')
show_summary=clean(txt(channel,'itunes:summary') or txt(channel,'description'))
episodes=[];seen={}
for item in root.findall('.//item'):
    title=clean(txt(item,'title')); desc=clean(txt(item,'content:encoded') or txt(item,'description')); iso,br=date_info(txt(item,'pubDate')); dur=duration(txt(item,'itunes:duration'))
    enc=item.find('enclosure'); audio=enc.attrib.get('url','') if enc is not None else ''
    img=''; ii=item.find('itunes:image',NS); img=ii.attrib.get('href','') if ii is not None else ''
    ntitle=' '+norm(title)+' '; topics=[t for t,needles in RULES.items() if any(n in ntitle for n in needles)]
    summary='' if re.search(r'assine|pix|podcastbelgrado@gmail',desc,re.I) and len(desc)<300 else desc
    base=slugify(title); n=seen.get(base,0); seen[base]=n+1; slug=base if n==0 else f'{base}-{iso}'
    episodes.append({'title':title,'description':desc,'summary':summary,'date':iso,'date_br':br,'duration':dur,'audio':audio,'image':img,'topics':sorted(set(topics)),'slug':slug})
episodes.sort(key=lambda e:e['date'],reverse=True); topicmap=defaultdict(list)
for ep in episodes:
    for t in ep['topics']: topicmap[t].append(ep)
topic_sorted=sorted(topicmap.items(),key=lambda kv:(-len(kv[1]),kv[0]))
home=f'<section class="hero"><div class="wrap"><div class="meta" style="color:#ee7a38">Cafe Belgrado</div><h1>NBA, Basquete, Vida.</h1><p>Podcast, comunidade e projetos para quem gosta de basquete de verdade. Academy, Magazine, Elastico Mental, conteudo exclusivo e um arquivo de {len(episodes)} episodios.</p><a class="cta" href="{ORELO}">ASSINE O CONTEUDO EXCLUSIVO DO CAFE BELGRADO</a></div></section><main class="wrap"><div class="products"><a class="product academy" href="{ACADEMY}"><h2>Cafe Belgrado Academy</h2><p>Grupo de Estudos Avancados sobre Basquete.</p><strong>Conhecer a Academy</strong></a><div class="product mag" id="magazine"><h2>Cafe Belgrado Magazine</h2><p>Materias, especiais, series e projetos editoriais.</p><strong>Magazine</strong></div><a class="product elastico" href="{ELASTICO}"><h2>Elastico Mental</h2><p>Podcast de cultura da familia Cafe Belgrado.</p><strong>Ouvir</strong></a></div><section class="section"><div class="section-head"><h2>Assuntos</h2><a href="{rel("assuntos/")}">Todos</a></div><div class="topics">{"".join(f"<a class=topic href={esc(rel('assuntos/'+slugify(t)+'/'))}><strong>{esc(t)}</strong><span>{len(es)} episodios</span></a>" for t,es in topic_sorted[:12])}</div></section><section class="section"><div class="section-head"><h2>Episodios recentes</h2><a href="{rel("podcast/")}">Arquivo completo</a></div><div class="episodes">{"".join(card(e) for e in episodes[:18])}</div></section></main>'
write(Path('index.html'),page('Cafe Belgrado — NBA, Basquete, Vida',show_summary,home,BASE+'/'))
PER=60; pages=math.ceil(len(episodes)/PER)
for p in range(1,pages+1):
    chunk=episodes[(p-1)*PER:p*PER]; links=[]
    if p>1: links.append(f'<a href="{rel("podcast/" if p==2 else f"podcast/pagina/{p-1}/")}">anterior</a>')
    if p<pages: links.append(f'<a href="{rel(f"podcast/pagina/{p+1}/")}">proxima</a>')
    body=f'<main class="wrap section"><h1 style="font-family:Georgia,serif;font-size:54px">Arquivo do Cafe Belgrado</h1><p>{len(episodes)} episodios · pagina {p} de {pages}</p><div class="episodes">{"".join(card(e) for e in chunk)}</div><div class="pager">{"".join(links)}</div></main>'
    path=Path('podcast/index.html') if p==1 else Path(f'podcast/pagina/{p}/index.html'); canon=BASE+'/podcast/' if p==1 else BASE+f'/podcast/pagina/{p}/'; write(path,page(f'Arquivo do Cafe Belgrado — pagina {p}',f'Arquivo de episodios do Cafe Belgrado. Pagina {p}.',body,canon))
for ep in episodes:
    related=[x for x in episodes if x['slug']!=ep['slug'] and set(x['topics']) & set(ep['topics'])][:7]; desc=ep['summary'] or f'Episodio do Cafe Belgrado: {ep["title"]}. Publicado em {ep["date_br"]}.'
    body=f'<main class="wrap section"><div class="detail"><article class="article"><div class="article-head">{art(ep)}<div class="article-copy"><div class="meta">{ep["date_br"]}{(" · "+ep["duration"]) if ep["duration"] else ""}</div><h1>{esc(ep["title"])}</h1><p>{esc(desc)}</p><div class="tags">{"".join(f"<span class=tag>{esc(t)}</span>" for t in ep["topics"])}</div></div></div><div class="body"><div class="player"><strong>Ouvir este episodio</strong><audio controls preload="none" src="{esc(ep["audio"])}"></audio></div>{f"<p>{esc(ep['description'])}</p>" if ep["description"] else ""}</div></article><aside class="side"><h3>Relacionados</h3>{"".join(f"<a class=related href={esc(rel('podcast/'+x['slug']+'/'))}>{esc(x['title'])}</a>" for x in related)}</aside></div></main>'
    write(Path(f'podcast/{ep["slug"]}/index.html'),page(ep['title']+' — Cafe Belgrado',desc,body,BASE+f'/podcast/{ep["slug"]}/'))
body=f'<main class="wrap section"><h1 style="font-family:Georgia,serif;font-size:54px">Assuntos do Cafe</h1><div class="topics">{"".join(f"<a class=topic href={esc(rel('assuntos/'+slugify(t)+'/'))}><strong>{esc(t)}</strong><span>{len(es)} episodios</span></a>" for t,es in topic_sorted)}</div></main>'
write(Path('assuntos/index.html'),page('Assuntos — Cafe Belgrado','Jogadores, times e temas do arquivo do Cafe Belgrado.',body,BASE+'/assuntos/'))
for t,eps in topicmap.items():
    body=f'<main class="wrap section"><h1 style="font-family:Georgia,serif;font-size:54px">{esc(t)}</h1><p>{len(eps)} episodios relacionados.</p><div class="episodes">{"".join(card(e) for e in eps)}</div></main>'; write(Path(f'assuntos/{slugify(t)}/index.html'),page(t+' — Cafe Belgrado',f'Episodios do Cafe Belgrado relacionados a {t}.',body,BASE+f'/assuntos/{slugify(t)}/'))
urls=[BASE+'/',BASE+'/podcast/',BASE+'/assuntos/']+[BASE+f'/podcast/pagina/{p}/' for p in range(2,pages+1)]+[BASE+f'/podcast/{e["slug"]}/' for e in episodes]+[BASE+f'/assuntos/{slugify(t)}/' for t in topicmap]
write(Path('sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(u)}</loc></url>' for u in urls)+'</urlset>'); write(Path('robots.txt'),f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n'); write(Path('.nojekyll'),'')
print(f'Gerado: {len(episodes)} episodios, {len(topicmap)} assuntos, {len(urls)} URLs')
