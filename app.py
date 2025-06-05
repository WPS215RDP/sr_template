from flask import Flask, render_template, request, jsonify
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def generate_html_content(
    game_name, about_html, sysreq_html=None, genres=None, developer=None,
    game_size="", released_by="", version="", 
    screenshot1_url="", screenshot2_url="",
    gofile_link="", buzzheavier_link=""
):
    """Generate HTML content and return as string instead of writing to file"""
    genres_str = ", ".join(genres) if genres else "N/A"
    developer_str = developer if developer else "N/A"

    html_content = f'''
<h2>{game_name} Direct Download</h2>
<p style="text-align: justify;">{about_html}</p>

[divider style="solid" top="0" bottom="20"]
<h4 style="text-align: center;"><span style="font-size: 18pt;">SCREENSHOTS</span></h4>
<p style="text-align: center;"><a href="{screenshot1_url}"><img class="alignnone size-medium" src="{screenshot1_url}" alt="" width="300" height="169" /></a><a href="{screenshot2_url}"><img class="alignnone size-medium" src="{screenshot2_url}" alt="" width="300" height="169" /></a>
[divider style="solid" top="0" bottom="20"]</p>
'''

    if sysreq_html:
        html_content += '''
[divider style="solid" top="0" bottom="20"]
<h4><span style="font-size: 18pt;">SYSTEM REQUIREMENTS</span></h4>
[tie_list type="checklist"]
''' + sysreq_html + '''
[/tie_list]
'''

    html_content += f'''
[divider style="solid" top="0" bottom="20"]
<h4><span style="font-size: 18pt;">GAME INFO</span></h4>
[tie_list type="plus"]
<ul>
    <li><strong>Genre:</strong> {genres_str}</li>
    <li><strong>Developer:</strong> {developer_str}</li>
    <li><strong>Platform:</strong> PC</li>
    <li><strong>Game Size: </strong>{game_size}</li>
    <li><strong>Released By:</strong> {released_by}</li>
    <li><strong>Version</strong>: {version}</li>
    <li><strong>Pre-Installed Game</strong></li>
</ul>
[/tie_list]
'''

    if gofile_link.strip():
        html_content += f'''
<p style="text-align: center;"><span style="color: #ff9900;"><strong>GOFILE</strong></span>
[button color="purple " size="medium" link="{gofile_link}" icon="" target="true" nofollow="true"]DOWNLOAD HERE[/button]</p>
'''

    if buzzheavier_link.strip():
        html_content += f'''
<p style="text-align: center;"><strong>Buzzheavier</strong>
[button color="purple " size="medium" link="{buzzheavier_link}" icon="" target="true" nofollow="true"]DOWNLOAD HERE[/button]</p>
'''

    return html_content.strip()

def fetch_game_info(appid):
    """Fetch game information from Steam"""
    url = f"https://store.steampowered.com/app/{appid}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')

    # Game Name
    game_name_elem = soup.find("div", id="appHubAppName")
    if not game_name_elem:
        raise ValueError("Game name not found - invalid App ID or game not accessible")
    game_name = game_name_elem.get_text(strip=True)

    # Featured image
    featured_tag = soup.select_one("#gameHeaderImageCtn img.game_header_image_full")
    if not featured_tag or "src" not in featured_tag.attrs:
        raise ValueError("Featured image not found")
    featured_img_url = featured_tag["src"]

    # About
    about = soup.find("div", id="game_area_description")
    if not about:
        raise ValueError("Game description not found")
    
    for tag in about.select("img, .bb_wide_img_ctn"): 
        tag.decompose()
    about_html = ' '.join(str(c) for c in about.contents).replace("<h2>About This Game</h2>", "").strip()

    # System requirements (Windows)
    sysreq = soup.find("div", class_="game_area_sys_req sysreq_content active", attrs={"data-os": "win"})
    min_reqs_html = str(sysreq.find("ul", class_="bb_ul")) if sysreq and sysreq.find("ul", class_="bb_ul") else ""

    # Genre, developer, and publisher
    block = soup.find("div", id="genresAndManufacturer")
    genres = []
    developer = ""
    publisher = ""
    
    if block:
        genre_links = block.select("b:-soup-contains('Genre:') + span a")
        genres = [a.text.strip() for a in genre_links]
        
        dev_tag = block.select_one("b:-soup-contains('Developer:') + a")
        developer = dev_tag.text.strip() if dev_tag else ""
        
        pub_tag = block.select_one("b:-soup-contains('Publisher:') + a")
        publisher = pub_tag.text.strip() if pub_tag else ""

    # Categories
    categories = []
    category_tags = soup.select(".glance_tags.popular_tags a")
    for tag in category_tags:
        category_text = tag.get_text(strip=True)
        if category_text:
            categories.append(category_text)

    # Screenshots
    screenshot_imgs = soup.select(".highlight_strip_item img")
    screenshots = []
    for img in screenshot_imgs[-2:]:  # Get last 2 screenshots
        if "src" in img.attrs:
            screenshot_url = img["src"].split("?")[0].replace("116x65", "600x338")
            screenshots.append(screenshot_url)

    ss1_url, ss2_url = (screenshots + ["", ""])[:2]

    # Generate Focus Keyphrase and Meta Description
    focus_keyphrase = f"{game_name} SteamRIP com"
    meta_description = f"{game_name} Free Download SteamRIP.com Get {game_name} PC game for free instantly and play pre-installed on SteamRIP"

    return {
        "game_name": game_name,
        "featured_img_url": featured_img_url,
        "about_html": about_html,
        "minimum_sysreq_html": min_reqs_html,
        "genres": genres,
        "developer": developer,
        "publisher": publisher,
        "categories": categories,
        "focus_keyphrase": focus_keyphrase,
        "meta_description": meta_description,
        "ss1_url": ss1_url,
        "ss2_url": ss2_url,
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_game_info', methods=['POST'])
def fetch_game_info_route():
    try:
        data = request.get_json()
        appid = data.get('appid', '').strip()
        
        if not appid:
            return jsonify({'error': 'App ID is required'}), 400
            
        info = fetch_game_info(appid)
        return jsonify(info)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch game data: {str(e)}'}), 500
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/generate_page', methods=['POST'])
def generate_page():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['game_name', 'about_html']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate HTML content (get the HTML string instead of writing to file)
        html_content = generate_html_content(
            game_name=data['game_name'],
            about_html=data['about_html'],
            sysreq_html=data.get('minimum_sysreq_html', ''),
            genres=data.get('genres', []),
            developer=data.get('developer', ''),
            game_size=data.get('game_size', ''),
            released_by=data.get('released_by', ''),
            version=data.get('version', ''),
            screenshot1_url=data.get('ss1_url', ''),
            screenshot2_url=data.get('ss2_url', ''),
            gofile_link=data.get('gofile_link', ''),
            buzzheavier_link=data.get('buzzheavier_link', '')
        )
        
        return jsonify({
            'success': True,
            'message': 'HTML code generated successfully!',
            'html_content': html_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate code: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)