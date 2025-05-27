def generate_html_file(
    game_name, about_html, sysreq_html=None, genres=None, developer=None,
    game_size="", released_by="", version="", 
    screenshot1_url="", screenshot2_url="",
    gofile_link="", buzzheavier_link=""
):
    genres_str = ", ".join(genres) if genres else "N/A"
    developer_str = developer if developer else "N/A"

    html_content = f'''
<h2>{game_name} Direct Download</h2>
<p style="text-align: justify;">{about_html}</p>

[divider style="solid" top="0" bottom="20"]
<h4 style="text-align: center;"><span style="font-size: 18pt;">SCREENSHOTS</span></h4>
<p style="text-align: center;">
    <a href="{screenshot1_url}">
        <img class="alignnone wp-image-42477 size-medium" src="{screenshot1_url}" alt="" width="300" height="169" />
    </a>
    <a href="{screenshot2_url}">
        <img class="alignnone wp-image-42478 size-medium" src="{screenshot2_url}" alt="" width="300" height="169" />
    </a>
</p>
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

    with open("game_page.html", "w", encoding="utf-8") as f:
        f.write(html_content)
