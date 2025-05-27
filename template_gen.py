import requests
from bs4 import BeautifulSoup
from generate_game_page import generate_html_file
from image_processor import process_thumbnail, process_featured_image

def fetch_game_info(appid):
    url = f"https://store.steampowered.com/app/{appid}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')

    game_name = soup.find("div", id="appHubAppName").get_text(strip=True)

    # Featured image
    featured_tag = soup.select_one("#gameHeaderImageCtn img.game_header_image_full")
    if not featured_tag or "src" not in featured_tag.attrs:
        raise ValueError("Featured image not found")
    featured_img_url = featured_tag["src"]

    # Clean 'About This Game'
    about = soup.find("div", id="game_area_description")
    for tag in about.select("img, .bb_wide_img_ctn"): tag.decompose()
    about_html = ' '.join(str(c) for c in about.contents).replace("<h2>About This Game</h2>", "").strip()

    # System requirements (Windows)
    sysreq = soup.find("div", class_="game_area_sys_req sysreq_content active", attrs={"data-os": "win"})
    min_reqs_html = str(sysreq.find("ul", class_="bb_ul")) if sysreq and sysreq.find("ul", class_="bb_ul") else ""

    # Genre and developer
    block = soup.find("div", id="genresAndManufacturer")
    genres = [a.text.strip() for a in block.select("b:-soup-contains('Genre:') + span a")] if block else []
    dev_tag = block.select_one("b:-soup-contains('Developer:') + a") if block else None
    developer = dev_tag.text.strip() if dev_tag else ""

    # Screenshots (last two instead of first two)
    screenshots = [
        img["src"].replace("116x65", "600x338")
        for img in soup.select(".highlight_strip_item img")[-2:]
    ]
    ss1_url, ss2_url = (screenshots + ["", ""])[:2]

    return {
        "game_name": game_name,
        "featured_img_url": featured_img_url,
        "about_html": about_html,
        "minimum_sysreq_html": min_reqs_html,
        "genres": genres,
        "developer": developer,
        "ss1_url": ss1_url,
        "ss2_url": ss2_url,
    }


if __name__ == "__main__":
    appid = input("Enter Steam App ID: ")
    try:
        info = fetch_game_info(appid)
        game_size = input("Enter Game Size: ")
        released_by = input("Enter Released By: ")
        version = input("Enter Version: ")
        gofile = input("link for gofile: ")
        buzz = input("link for buzz: ")

        generate_html_file(
            info["game_name"], info["about_html"], info["minimum_sysreq_html"],
            info["genres"], info["developer"], game_size, released_by, version,
            info["ss1_url"], info["ss2_url"], gofile, buzz
        )

        thumbnail_link = input("Enter thumbnail image link: ")
        process_thumbnail(thumbnail_link, info['game_name'])
        process_featured_image(info['featured_img_url'], info['game_name'])

    except Exception as e:
        print(f"[ERROR] {e}")
