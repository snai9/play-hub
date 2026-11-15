# coding=utf-8
#!/usr/bin/python

"""

作者 丢丢喵推荐 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import datetime
import binascii
import requests
import hashlib
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://api-store.qmplaylet.com"
xurl1 = "https://api-read.qmplaylet.com"
keys = "d3dGiJc651gSQ8w1"

def get_headerx():
    session_id = str(int(time.time() * 1000))
    
    data = {
        "static_score": "0.8",
        "uuid": "00000000-7fc7-08dc-0000-000000000000",
        "device-id": "20250220125449b9b8cac84c2dd3d035c9052a2572f7dd0122edde3cc42a70",
        "mac": "",
        "sourceuid": "aa7de295aad621a6",
        "refresh-type": "0",
        "model": "22021211RC",
        "wlb-imei": "",
        "client-id": "aa7de295aad621a6",
        "brand": "Redmi",
        "oaid": "",
        "oaid-no-cache": "",
        "sys-ver": "12",
        "trusted-id": "",
        "phone-level": "H",
        "imei": "",
        "wlb-uid": "aa7de295aad621a6",
        "session-id": session_id
    }
    
    json_str = json.dumps(data, separators=(',', ':'))
    encoded = base64.b64encode(json_str.encode()).decode()
    
    char_map = {
        '+': 'P', '/': 'X', '0': 'M', '1': 'U', '2': 'l', '3': 'E', '4': 'r',
        '5': 'Y', '6': 'W', '7': 'b', '8': 'd', '9': 'J', 'A': '9', 'B': 's',
        'C': 'a', 'D': 'I', 'E': '0', 'F': 'o', 'G': 'y', 'H': '_', 'I': 'H',
        'J': 'G', 'K': 'i', 'L': 't', 'M': 'g', 'N': 'N', 'O': 'A', 'P': '8',
        'Q': 'F', 'R': 'k', 'S': '3', 'T': 'h', 'U': 'f', 'V': 'R', 'W': 'q',
        'X': 'C', 'Y': '4', 'Z': 'p', 'a': 'm', 'b': 'B', 'c': 'O', 'd': 'u',
        'e': 'c', 'f': '6', 'g': 'K', 'h': 'x', 'i': '5', 'j': 'T', 'k': '-',
        'l': '2', 'm': 'z', 'n': 'S', 'o': 'Z', 'p': '1', 'q': 'V', 'r': 'v',
        's': 'j', 't': 'Q', 'u': '7', 'v': 'D', 'w': 'w', 'x': 'n', 'y': 'L',
        'z': 'e'
    }
    
    qm_params = ''
    for c in encoded:
        qm_params += char_map.get(c, c)
    
    params_str = (
        "AUTHORIZATION=" +
        "app-version=10001" +
        "application-id=com.duoduo.read" +
        "channel=unknown" +
        "is-white=" +
        "net-env=5" +
        "platform=android" +
        f"qm-params={qm_params}" +
        f"reg={keys}"
    )
    
    signs = hashlib.md5(params_str.encode()).hexdigest()
    
    return {
        'net-env': '5',
        'reg': '',
        'channel': 'unknown',
        'is-white': '',
        'platform': 'android',
        'application-id': 'com.duoduo.read',
        'authorization': '',
        'app-version': '10001',
        'user-agent': 'webviewversion/0',
        'qm-params': qm_params,
        'sign': signs
    }

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
}

class Spider(Spider):
    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {"class": []}
        headerx = get_headerx()

        sign_string = f"operation=1playlet_privacy=1tag_id=0{keys}"
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()

        url = f"{xurl}/api/v1/playlet/index?tag_id=0&playlet_privacy=1&operation=1&sign={sign}"
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        data = detail.json()

        duoxuan = ['0', '1', '2', '3', '4']
        for duo in duoxuan:
            js = data['data']['tag_categories'][int(duo)]['tags']

            for vod in js:
                name = vod['tag_name']
                if "推荐" in name:
                    continue

                id = vod['tag_id']
                result["class"].append({"type_id": id, "type_name": name})

        return result

    def homeVideoContent(self):
        videos = []
        headerx = get_headerx()

        sign_string = f"operation=1playlet_privacy=1tag_id=0{keys}"
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()

        url = f"{xurl}/api/v1/playlet/index?tag_id=0&playlet_privacy=1&operation=1&sign={sign}"
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        data = detail.json()

        data = data['data']['list']

        for vod in data:
            name = vod['title']
            id = vod['playlet_id']
            pic = vod['image_link']
            remark = vod['total_episode_num']

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            }
            videos.append(video)

        result = {'list': videos}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []
        headerx = get_headerx()

        if pg:
            page = int(pg)
        else:
            page = 1

        if page == 1:
            sign_string = f"operation=1playlet_privacy=1tag_id={cid}{keys}"
            sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
            url = f'{xurl}/api/v1/playlet/index?tag_id={cid}&playlet_privacy=1&operation=1&sign={sign}'
        else:
            sign_string = f"next_id={str(page)}operation=1playlet_privacy=1tag_id={cid}{keys}"
            sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
            url = f'{xurl}/api/v1/playlet/index?tag_id={cid}&next_id={str(page)}&playlet_privacy=1&operation=1&sign={sign}'

        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        data = detail.json()

        data = data['data']['list']

        for vod in data:
            name = vod['title']
            id = vod['playlet_id']
            pic = vod['image_link']
            remark = vod['total_episode_num']

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            }
            videos.append(video)

        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        did = ids[0]
        result = {}
        videos = []
        headerx = get_headerx()

        sign_string = f"playlet_id={did}{keys}"
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()

        urls = f'{xurl1}/player/api/v1/playlet/info?playlet_id={did}&sign={sign}'
        detail = requests.get(url=urls, headers=headerx)
        detail.encoding = "utf-8"
        detail = detail.json()

        if not detail or 'data' not in detail:
            return {"list": []}
        
        data = detail['data']
        
        blurb = data.get('intro', "未知")
        content = blurb

        jisu = data.get('total_episode_num', "未知")
        jisu = str(jisu) + '全集'

        leixing = data.get('tags', "未知")
        remarks = f"{leixing} {jisu}"

        if 'play_list' in data and data['play_list']:
            play_list = data['play_list']
            play_urls = []
            for item in play_list:
                video_url = item.get('video_url', '')
                sort = item.get('sort', '')
                if video_url:
                    play_urls.append(f"{sort}${video_url}")
            
            if play_urls:
                bofang = "#".join(play_urls)
                xianlu = '七猫短剧'
            else:
                return {"list": []}
        else:
            return {"list": []}

        videos.append({
            "vod_id": did,
            "vod_remarks": remarks,
            "vod_content": content,
            "vod_play_from": xianlu,
            "vod_play_url": bofang
        })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = headers
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        videos = []
        headerx = get_headerx()

        if pg:
            page = int(pg)
        else:
            page = 1

        track_id = "ec1280db127955061754851657967"
        sign_string = f"extend=page={str(page)}read_preference=0track_id={track_id}wd={key}{keys}"
        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()

        url = f'{xurl}/api/v1/playlet/search?extend=&page={str(page)}&wd={key}&read_preference=0&track_id={track_id}&sign={sign}'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        detail = detail.json()

        data = detail['data']['list']

        for vod in data:
            name = vod['title']
            name = re.sub(r'<[^>]+>', '', name)
            name = ' '.join(name.split())

            id = vod['id']
            pic = vod['image_link']
            remark = vod['total_num']

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            }
            videos.append(video)

        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None


# ---- TVBox 本地线路过滤（自动生成，勿改） ----
_TVBOX_DROP_LINES = []
_TVBOX_LINE_ORDER = []
_TVBOX_DROP_SUB = []
_TVBOX_ORDER_SUB = []
_TVBOX_SINK_SUB = []
_TVBOX_LINE_CAP = 4

def _tvbox_filter_lines(result, drop):
    if not isinstance(result, dict):
        return result
    items = result.get('list')
    if isinstance(items, list):
        for item in items:
            _tvbox_filter_item(item, drop)
    else:
        _tvbox_filter_item(result, drop)
    return result

def _tvbox_filter_item(item, drop):
    froms = item.get('vod_play_from') or ''
    urls = item.get('vod_play_url') or ''
    if not isinstance(froms, str) or not isinstance(urls, str):
        return
    if '$$$' not in froms:
        return
    parts_from = [f.strip() for f in froms.split('$$$')]
    parts_url = urls.split('$$$')
    if len(parts_from) != len(parts_url):
        return
    keep = [(f, u) for f, u in zip(parts_from, parts_url) if f not in drop and not any(s in f for s in _TVBOX_DROP_SUB)]
    if not keep or len(keep) == len(parts_from):
        return
    item['vod_play_from'] = '$$$'.join(f for f, _ in keep)
    item['vod_play_url'] = '$$$'.join(u for _, u in keep)

def _tvbox_sort_lines(result, order):
    if not order and not _TVBOX_ORDER_SUB:
        return result
    if not isinstance(result, dict):
        return result
    items = result.get('list')
    if isinstance(items, list):
        for item in items:
            _tvbox_sort_item(item, order)
    else:
        _tvbox_sort_item(result, order)
    return result

def _tvbox_sort_item(item, order):
    froms = item.get('vod_play_from') or ''
    urls = item.get('vod_play_url') or ''
    if not isinstance(froms, str) or not isinstance(urls, str):
        return
    if '$$$' not in froms:
        return
    parts_from = [f.strip() for f in froms.split('$$$')]
    parts_url = urls.split('$$$')
    if len(parts_from) != len(parts_url):
        return
    known = {f: i for i, f in enumerate(order)}
    subs = [p for p in _TVBOX_ORDER_SUB if p]
    sinks = [p for p in _TVBOX_SINK_SUB if p]
    unknown_base = len(order) + len(subs)
    def _tvbox_rank(f):
        for p in sinks:
            if p in f:
                return unknown_base + 1000
        if f in known:
            return known[f]
        for i, pat in enumerate(subs):
            if pat in f:
                return len(order) + i
        return unknown_base
    # 已知线路按 order（画质速度最优在前），未知线路稳定保持原序后置，
    # sink 命中的差线（4K 等）沉到最后但不删除。
    pairs = list(zip(parts_from, parts_url))
    pairs.sort(key=lambda p: _tvbox_rank(p[0]))
    if _TVBOX_LINE_CAP > 0 and len(pairs) > _TVBOX_LINE_CAP:
        pairs = pairs[: _TVBOX_LINE_CAP]
    item['vod_play_from'] = '$$$'.join(f for f, _ in pairs)
    item['vod_play_url'] = '$$$'.join(u for _, u in pairs)

def _tvbox_apply(cls):
    fn = getattr(cls, 'detailContent', None)
    if fn is None:
        return
    def wrapper(self, *a, _fn=fn, **k):
        res = _tvbox_filter_lines(_fn(self, *a, **k), _TVBOX_DROP_LINES)
        return _tvbox_sort_lines(res, _TVBOX_LINE_ORDER)
    setattr(cls, 'detailContent', wrapper)

_tvbox_apply(Spider)
