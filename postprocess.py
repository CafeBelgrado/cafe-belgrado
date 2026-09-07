#!/usr/bin/env python3
from pathlib import Path
import re, html

OUT = Path('_site')
THEME = Path('theme.css')

PLAYERS = {
    'Allen Iverson': '947',
    'LeBron James': '2544',
    'Michael Jordan': '893',
    'Kobe Bryant': '977',
    'Stephen Curry': '201939',
    'Kevin Durant': '201142',
    'Nikola Jokic': '203999',
    'Giannis Antetokounmpo': '203507',
    'Luka Doncic': '1629029',
    'Victor Wembanyama': '1641705',
    'Shai Gilgeous-Alexander': '1628983',
    'Kawhi Leonard': '202695',
    'James Harden': '201935',
    'Russell Westbrook': '201566',
    'Joel Embiid': '203954',
    'Jayson Tatum': '1628369',
    'Ben Simmons': '1627732',
}

TEAMS = {
    'San Antonio Spurs': '1610612759',
    'Los Angeles Lakers': '1610612747',
    'Boston Celtics': '1610612738',
    'Golden State Warriors': '1610612744',
    'Philadelphia 76ers': '1610612755',
    'New York Knicks': '1610612752',
    'Miami Heat': '1610612748',
    'Chicago Bulls': '1610612741',
    'Cleveland Cavaliers': '1610612739',
    'Milwaukee Bucks': '1610612749',
    'Indiana Pacers': '1610612754',
    'Denver Nuggets': '1610612743',
    'Oklahoma City Thunder': '1610612760',
    'Minnesota Timberwolves': '1610612750',
    'Dallas Mavericks': '1610612742',
    'Houston Rockets': '1610612745',
    'Memphis Grizzlies': '1610612763',
    'Phoenix Suns': '1610612756',
    'Sacramento Kings': '1610612758',
    'Los Angeles Clippers': '1610612746',
}

def topic_card(match):
    href, name, count = match.group(1), html.unescape(match.group(2)), match.group(3)
    safe_name = html.escape(name)
    if name in PLAYERS:
        pid = PLAYERS[name]
        image = f'https://cdn.nba.com/headshots/nba/latest/1040x760/{pid}.png'
        cls = 'topic topic-player'
        media = f'<div class="topic-media"><img loading="lazy" src="{image}" alt="{safe_name}" onerror="this.parentElement.style.display=\'none\'"></div>'
    elif name in TEAMS:
        tid = TEAMS[name]
        image = f'https://cdn.nba.com/logos/nba/{tid}/primary/L/logo.svg'
        cls = 'topic topic-team'
        media = f'<div class="topic-media"><img loading="lazy" src="{image}" alt="Logo {safe_name}" onerror="this.parentElement.style.display=\'none\'"></div>'
    else:
        return match.group(0)
    return f'<a class="{cls}" href="{href}">{media}<div class="topic-copy"><strong>{safe_name}</strong><span>{count} episodios</span></div></a>'

def main():
    theme = THEME.read_text(encoding='utf-8') if THEME.exists() else ''
    pattern = re.compile(r'<a class=topic href=([^ >]+)><strong>(.*?)</strong><span>(\d+) episodios</span></a>', re.S)
    touched = 0
    visual_topics = 0
    for path in OUT.rglob('*.html'):
        txt = path.read_text(encoding='utf-8')
        if theme and 'id="cb-theme"' not in txt:
            txt = txt.replace('</head>', f'<style id="cb-theme">{theme}</style></head>', 1)
        txt, n = pattern.subn(topic_card, txt)
        visual_topics += n
        path.write_text(txt, encoding='utf-8')
        touched += 1
    print(f'Post-processado: {touched} HTMLs; {visual_topics} cards de topicos avaliados para imagens NBA')

if __name__ == '__main__':
    main()
