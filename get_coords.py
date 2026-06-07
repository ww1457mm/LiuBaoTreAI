#!/usr/bin/env python
"""获取六堡茶产区准确坐标"""

import httpx

KEY = "WP6BZ-43AKU-DJTVD-G2KG7-OGDJ7-FGBHB"

ADDRESSES = [
    ("六堡镇核心区", "广西梧州苍梧县六堡镇"),
    ("狮寨产区", "广西梧州苍梧县狮寨镇"),
    ("梨木产区", "广西梧州苍梧县梨木镇"),
    ("沙头产区", "广西梧州苍梧县沙头镇"),
    ("岑溪产区", "广西梧州岑溪市"),
    ("藤县产区", "广西梧州藤县"),
    ("蒙山产区", "广西梧州蒙山县"),
]

print("=" * 50)
print("六堡茶产区坐标查询")
print("=" * 50)

for name, addr in ADDRESSES:
    url = "https://apis.map.qq.com/ws/geocoder/v1/"
    params = {"address": addr, "key": KEY}
    try:
        resp = httpx.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("status") == 0:
            loc = data["result"]["location"]
            print(f"{name}: lat={loc['lat']}, lng={loc['lng']}")
        else:
            print(f"{name}: 获取失败 - {data.get('message', '未知错误')}")
    except Exception as e:
        print(f"{name}: 请求异常 - {e}")

print("=" * 50)
