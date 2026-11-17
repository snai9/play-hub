# -*- coding: utf-8 -*-
# 本资源来源于互联网公开渠道，仅可用于个人学习爬虫技术。
# 严禁将其用于任何商业用途，下载后请于 24 小时内删除，搜索结果均来自源站，本人不承担任何责任。

from base.spider import Spider
import sys,time,base64,random,urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append('..')

class Spider(Spider):
    headers,host = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'Referer': 'https://www.duboku.tv/'
    }, 'https://api.dbokutv.com'

    def init(self, extend=""):
        pass

    def homeContent(self, filter):
        if not self.host: return None
        return {'class': [{'type_id': 2, 'type_name': '连续剧'}, {'type_id': 3, 'type_name': '综艺'}, {'type_id': 1, 'type_name': '电影'}, {'type_id': 4, 'type_name': '动漫'}]}

    def homeVideoContent(self):
        response = self.fetch(self.sign(f'{self.host}/home'), headers=self.headers, verify=False).json()
        videos = []
        for i in response:
            for j in i.get('VodList',[]):
                videos.append({
                    'vod_id': self.decode(j.get('DId', j.get('DuId'))),
                    'vod_name': j['Name'],
                    'vod_pic': self.decode(j['TnId']),
                    'vod_remarks': j['Tag']
                })
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        response = self.fetch(self.sign(f"{self.host}/vodshow/{tid}--------{'' if str(pg) == '1' else pg}---"), headers=self.headers, verify=False).json()
        videos,pagecount = [], 0
        for i in response['VodList']:
            videos.append({
                'vod_id': self.decode(i.get('DId',i.get('DuId'))),
                'vod_name': i['Name'],
                'vod_pic': self.decode(i['TnId']),
                'vod_remarks': i['Tag']
            })
        try:
            for j in response['PaginationList']:
                if j['Type'] == 'StartEnd':
                    pgcount = int(self.decode(j.get('PId',j.get('PuId'))).split('-')[8])
                    if pgcount: pagecount = pgcount
        except Exception:
            pass
        if pagecount == 0:
            try:
                for j in response['PaginationList']:
                    if j['Type'] == 'ShortPage':
                        pgcount = int(j['Name'].split('/')[1])
                        if pgcount: pagecount = pgcount
            except Exception:
                pagecount = 1
        return {'list': videos,'pagecount': pagecount, 'page': pg}

    def searchContent(self, key, quick, pg='1'):
        response = self.fetch(f"{self.sign(f'{self.host}/vodsearch')}&wd={key}", headers=self.headers, verify=False).json()
        videos = []
        for i in response:
            videos.append({
                'vod_id': self.decode(i.get('DId', i.get('DuId'))),
                'vod_name': i['Name'],
                'vod_pic': self.decode(i['TnId']),
                'vod_remarks': i['Tag'],
                'vod_actor': i['Actor'],
                'vod_score': i['Rating']
            })
        return {'list': videos, 'page': pg}

    def detailContent(self, ids):
        data = self.fetch(self.sign(f"{self.host}{ids[0]}"), headers=self.headers, verify=False).json()
        play_urls = [f"{i['EpisodeName']}${self.decode(i['VId'])}" for i in data['Playlist']]
        video = {
            'vod_id': ids[0],
            'vod_name': data['Name'],
            'vod_pic': self.decode(data['TnId']),
            'vod_remarks': f"评分：{data['Rating']}",
            'vod_year': data['ReleaseYear'],
            'vod_area': data['Region'],
            'vod_actor': ','.join(data['Actor']),
            'vod_director': data['Director'],
            'vod_content': data['Description'],
            'vod_play_from': '独播库',
            'vod_play_url': '#'.join(play_urls),
            'type_name': f"{data['Genre']},{data['Scenario']},{data['Language']}"
        }
        return {'list': [video]}

    def playerContent(self, flag, video_id, vip_flags):
        res = self.fetch(self.sign(f"{self.host}{video_id}"), headers=self.headers, verify=False).json()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'origin': 'https://w.duboku.io',
            'referer': 'https://w.duboku.io/',
            'priority': 'u=1, i'
        }
        return { 'jx': 0, 'parse': 0, 'url': self.decode(res['HId']), 'header': headers}

    def decode(self, data):
        if not data or not isinstance(data, str): return ''
        stripped_str = data.strip('\'"')
        if not stripped_str: return ''
        segment_length = 10
        try:
            reversed_segments = (stripped_str[i:i + segment_length][::-1] for i in range(0, len(stripped_str), segment_length))
            processed_base64 = ''.join(reversed_segments).replace('.', '=')
        except Exception:
            return ''
        try:
            padding_needed = 4 - len(processed_base64) % 4
            if padding_needed != 4:
                processed_base64 += '=' * padding_needed
            decoded_bytes = base64.b64decode(processed_base64, validate=True)
            return decoded_bytes.decode('utf-8')
        except Exception:
            return ''

    def sign(self,raw):
        random.seed(int(time.time()))
        random_number = random.randint(0, 800000000)
        value_a = random_number + 100000000
        value_b = 900000000 - random_number
        current_unix_timestamp = int(time.time())
        unix_timestamp_str = str(current_unix_timestamp)
        interleaved_str = self.interleave_strings(f'{value_a}{value_b}', unix_timestamp_str)
        ssid_base64_encoded = base64.b64encode(interleaved_str.encode()).decode().replace('=', '.')
        random_sign = self.random_string(60)
        random_token = self.random_string(38)
        return f"{raw}?sign={random_sign}&token={random_token}&ssid={ssid_base64_encoded}"

    def interleave_strings(self,first_str, second_str):
        interleaved_chars = []
        min_length = min(len(first_str), len(second_str))
        for i in range(min_length):
            interleaved_chars.append(first_str[i])
            interleaved_chars.append(second_str[i])
        interleaved_chars.append(first_str[min_length:])
        interleaved_chars.append(second_str[min_length:])
        return ''.join(interleaved_chars)


    def random_string(self, length):
        character = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        random.seed(int(time.time()) + len(character))
        return ''.join(random.choice(character) for _ in range(length))

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def localProxy(self, param):
        pass




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
