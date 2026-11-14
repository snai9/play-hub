# -*- coding: utf-8 -*-

import re
import json
from urllib.parse import urlencode

# ---- TVBox 内置基类（部署环境必有）；本地测试时降级为 requests fallback ----
try:
    from base.spider import Spider as _BaseSpider
except ImportError:
    _BaseSpider = None

if _BaseSpider is None:
    import requests

    class _FallbackSpider(object):
        def fetch(self, url, headers=None, **kwargs):
            return requests.get(url, headers=headers, timeout=30)

        def post(self, url, headers=None, data=None, **kwargs):
            return requests.post(url, headers=headers, data=data, timeout=30)

        def log(self, msg):
            print(msg)

    _BaseSpider = _FallbackSpider


class Spider(_BaseSpider):
    # ===== 站点配置（改这里即可换站 / 换源）=====
    HOST = "https://eco.fe-spark.cn"
    API = "/api/provide/vod"          # MacCMS V10 兼容 JSON 接口
    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

    # ===== 框架必须：返回源名称 =====
    def getName(self):
        return "🌟 EcoHub 影视"

    # ===== 初始化（extend 可传 JSON 覆盖 host / source）=====
    def init(self, extend=""):
        self.host = self.HOST
        self.source = ""              # 可选：限定某个采集源，如 "2470287370"
        self.headers = {
            "User-Agent": self.UA,
            "Referer": self.host + "/",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        # extend 示例：{"host":"https://你的域名","source":"2470287370"}
        if extend:
            try:
                cfg = json.loads(extend)
                if cfg.get("host"):
                    self.host = str(cfg["host"]).rstrip("/")
                if cfg.get("source"):
                    self.source = str(cfg["source"])
            except Exception:
                pass

    # ===================== 工具方法 =====================
    def _api(self, params):
        """拼接接口地址并用基类 fetch 请求，返回 dict（带 2 次重试）"""
        params = {k: v for k, v in params.items() if v not in (None, "")}
        if self.source:
            params.setdefault("source", self.source)
        url = self.host + self.API + "?" + urlencode(params)
        last = {}
        for _ in range(3):
            try:
                resp = self.fetch(url, headers=self.headers)
            except Exception:
                resp = None
            if resp is None:
                continue
            text = resp.text if hasattr(resp, "text") else resp
            try:
                last = json.loads(text)
                if last.get("code") == 1 or "list" in last or "class" in last:
                    return last
            except Exception:
                last = {}
        return last

    @staticmethod
    def _to_int(v, default=0):
        try:
            return int(v)
        except Exception:
            return default

    def _norm_list(self, data):
        """把接口 list 归一化为 TVBox 卡片字段"""
        items = data.get("list") or data.get("vod") or []
        out = []
        for it in items:
            out.append({
                "vod_id": str(it.get("vod_id")),
                "vod_name": it.get("vod_name", ""),
                "vod_pic": it.get("vod_pic", ""),
                "vod_remarks": it.get("vod_remarks", ""),
            })
        return out

    # ===================== 五大接口 =====================
    def homeContent(self, filter):
        """首页分类 + 筛选条件（filter=True 才返回 filters）"""
        data = self._api({"ac": "class"})
        classes = []
        for c in data.get("class") or []:
            classes.append({
                "type_id": str(c.get("type_id")),
                "type_name": c.get("type_name", ""),
            })
        result = {"class": classes}
        if filter:
            filters = {}
            for tid, flist in (data.get("filters") or {}).items():
                fout = []
                for f in flist:
                    vals = [{"n": v.get("n", ""), "v": v.get("v", "")}
                            for v in f.get("value", [])]
                    fout.append({
                        "key": f.get("key", ""),
                        "name": f.get("name", ""),
                        "value": vals,
                    })
                filters[str(tid)] = fout
            result["filters"] = filters
        return result

    def homeVideoContent(self):
        """首页推荐：取 电影/连续剧/动漫 各若干拼成（首页不走分类）"""
        items = []
        for tid in ("8", "26", "1"):
            data = self._api({"ac": "list", "t": tid, "pg": "1"})
            items.extend(self._norm_list(data)[:8])
            if len(items) >= 24:
                break
        return {"list": items[:24]}

    def categoryContent(self, tid, pg, filter, extend):
        """分类列表：t=分类id，extend 里的筛选项直接转发为查询参数"""
        params = {"ac": "list", "t": str(tid),
                  "pg": str(max(1, self._to_int(pg, 1)))}
        extend = extend or {}
        for k, v in extend.items():
            # 跳过空值与 MacCMS 的「其他」占位 __others__
            if v not in (None, "", "__others__"):
                params[str(k)] = str(v)
        data = self._api(params)
        items = self._norm_list(data)
        return {
            "list": items,
            "page": self._to_int(data.get("page"), 1),
            "pagecount": self._to_int(data.get("pagecount"), 1),
            "limit": self._to_int(data.get("limit"), len(items)),
            "total": self._to_int(data.get("total") or data.get("recordcount"), 0),
        }

    def detailContent(self, ids):
        """详情：取播放线路与剧集（vod_play_url 已是直接 m3u8 直链）"""
        vid = str(ids[0])
        data = self._api({"ac": "detail", "ids": vid})
        items = data.get("list") or data.get("vod") or []
        if not items:
            return {"list": []}
        it = items[0]
        return {"list": [{
            "vod_id": str(it.get("vod_id", vid)),
            "vod_name": it.get("vod_name", ""),
            "vod_pic": it.get("vod_pic", ""),
            "vod_play_from": it.get("vod_play_from", ""),
            "vod_play_url": it.get("vod_play_url", ""),
            "vod_remarks": it.get("vod_remarks", ""),
            "vod_year": it.get("vod_year", ""),
        }]}

    def searchContent(self, key, quick, pg="1"):
        """搜索：wd=关键词"""
        data = self._api({"ac": "search", "wd": str(key),
                          "pg": str(max(1, self._to_int(pg, 1)))})
        items = self._norm_list(data)
        return {
            "list": items,
            "page": self._to_int(data.get("page"), 1),
            "pagecount": self._to_int(data.get("pagecount"), 1),
        }

    def playerContent(self, flag, id, vipFlags):
        """播放：id 已是直链（详情接口给的 m3u8/mp4），直接返回 parse=0"""
        url = (id or "").strip()
        if re.match(r"^https?://", url, re.I) and re.search(
                r"\.(m3u8|mp4|flv|mkv|ts|mpd)([?#]|$)", url, re.I):
            return {"parse": 0, "url": url, "header": self.headers}
        # 兜底：从可能带参数的串里正则提取直链
        m = re.search(r"https?://[^\s\"'<>]+?\.(?:m3u8|mp4)[^\s\"'<>]*", url)
        if m:
            return {"parse": 0, "url": m.group(0), "header": self.headers}
        return {"parse": 1, "url": url, "header": self.headers}

    # ===================== 框架辅助方法 =====================
    def isVideoFormat(self, url):
        return bool(re.search(r"\.(m3u8|mp4|flv|mkv|ts|mpd)([?#]|$)",
                              str(url or ""), re.I))

    def manualVideoCheck(self):
        return False

    def localProxy(self, param):
        return [404, "text/plain", "", ""]

    def destroy(self):
        pass


# ---- TVBox 本地线路过滤（自动生成，勿改） ----
_TVBOX_DROP_LINES = []
_TVBOX_LINE_ORDER = ["速博(SUBO)", "金鹰2(JY)", "光速(GS)", "红牛(HN)", "默认", "樱花(YH)", "HD(IK)", "HD(BF)", "HD(LY)", "HD(SN)", "非凡(FF)"]
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
