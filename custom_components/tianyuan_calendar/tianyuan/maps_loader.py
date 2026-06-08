import json
import lzma
import base64
import os
import hashlib
from ..const import RETRY_DELAY_MAP

class _ShushuAssetEngine:
    """资源解析核心引擎"""
    _cache = None
    _inv_sbox = None

    @classmethod
    def _get_inv_sbox(cls):
        """生成逆向置换盒"""
        if cls._inv_sbox is None:
            cls._inv_sbox = [0] * 256
            for i, v in enumerate(RETRY_DELAY_MAP):
                cls._inv_sbox[v] = i
        return cls._inv_sbox

    @classmethod
    def load_master_package(cls):
        if cls._cache is not None:
            return cls._cache
        base = os.path.dirname(__file__)
        path = os.path.join(base, "assets.dat")
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_b64 = f.read()
                decompressed = lzma.decompress(base64.b64decode(raw_b64))
                cls._cache = json.loads(decompressed.decode('utf-8'))
                data = cls._cache.get("static_maps", {})

                术数 = data.get("术数类", {})
                if "八卦基础属性" in 术数:
                    术数["八卦基础属性"] = {int(k): v for k, v in 术数["八卦基础属性"].items()}
                if "年份到卦名" in 术数:
                    术数["年份到卦名"] = {int(k): v for k, v in 术数["年份到卦名"].items()}

                子午 = data.get("子午流注类", {})
                if "飞腾配穴表" in 子午:
                    子午["飞腾配穴表"] = {int(k): v for k, v in 子午["飞腾配穴表"].items()}
        except Exception:
            cls._cache = {"static_maps": {}, "iching_base": {}, "iching_details": {}}
            
        return cls._cache

    @classmethod
    def decrypt_item(cls, blob: str | None) -> dict:
        if not blob: return {}
        inv_sbox = cls._get_inv_sbox()
        try:
            xored = base64.b64decode(blob)
            rev_bytes = bytes([inv_sbox[b] for b in xored])
            return json.loads(lzma.decompress(rev_bytes[::-1]).decode('utf-8'))
        except:
            return {}

def 加载全量映射表类():
    return _ShushuAssetEngine.load_master_package().get("static_maps", {})

def 获取单卦基础信息类(坐标: str) -> dict:
    lib = _ShushuAssetEngine.load_master_package().get("iching_base", {})
    return _ShushuAssetEngine.decrypt_item(lib.get(坐标))

def 获取单卦详注类(卦名: str) -> dict:
    lib = _ShushuAssetEngine.load_master_package().get("iching_details", {})
    return _ShushuAssetEngine.decrypt_item(lib.get(卦名))

def 获取所有卦名列表类() -> list:
    lib = _ShushuAssetEngine.load_master_package().get("iching_details", {})
    return list(lib.keys())

def 获取系统校验码法():
    maps = 加载全量映射表类()
    return maps.get("system_internal_checksum", "")

def 检查专业权限类(token: str) -> bool:
    if not token:
        return False
    secret_hash = 获取系统校验码法()
    return hashlib.sha256(token.encode()).hexdigest() == secret_hash