#!/usr/bin/env python3

# fix broken paths from running rename-to-dots.sh in ~/down/torrent/done/

# https://github.com/rmartin16/qbittorrent-api
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)
# https://qbittorrent-api.readthedocs.io/en/latest/
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#set-torrent-location
# https://qbittorrent-api.readthedocs.io/en/latest/apidoc/torrents.html#qbittorrentapi.torrents.TorrentDictionary.set_location
# https://github.com/rmartin16/qbittorrent-api/raw/main/src/qbittorrentapi/torrents.py

import os
import sys
import time
import qbittorrentapi



# config
conn_info = dict(
    host="localhost",
    # grep '^WebUI\\Port' qBittorrent.conf
    port=1952,
    username="admin",
    password="",
)



with qbittorrentapi.Client(**conn_info) as qbt_client:

    #if qbt_client.torrents_add(urls="...") != "Ok.":
    #    raise Exception("Failed to add torrent.")

    # display qBittorrent info
    if False:
    #if 1:
        print(f"qBittorrent: {qbt_client.app.version}")
        print(f"qBittorrent Web API: {qbt_client.app.web_api_version}")
        for k, v in qbt_client.app.build_info.items():
            print(f"{k}: {v}")

    for torrent in qbt_client.torrents_info():

        if os.path.exists(torrent.content_path):
            continue

        if torrent.state == "metaDL":
            continue

        if not torrent.content_path.startswith("/home/user/down/torrent/done/"):
            print(f"ignoring out of tree path for torrent {torrent.hash} {torrent.name} {torrent.state} {torrent.content_path}")
            continue

        # /home/user/down/torrent/done/fix.me/keep.me
        #bad_content_path = torrent.content_path.replace(" ", ".")
        parts = torrent.content_path.split("/")[0:7]
        #print("parts", parts)
        path_good = "/".join(parts)
        parts[6] = parts[6].replace(" ", ".")
        path_bad = "/".join(parts)

        if os.path.exists(path_bad):
            print()
            print("-", path_bad)
            print("+", path_good)
            os.rename(path_bad, path_good)
            continue

        print(f"torrent {torrent.hash} {torrent.name} {torrent.state} {torrent.content_path}")
        continue
