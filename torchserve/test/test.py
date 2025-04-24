import base64, json, requests

# 1. 读取并编码图片
with open("torchserve/test/test.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# 2. 构造请求
payload = {"data": [img_b64], "threshold": 0.25}
resp = requests.post(
    "http://localhost:9080/predictions/vlm_model",
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload)
)
detections = resp.json()  # e.g. [[ [xmin, ymin, xmax, ymax, score, cls], ... ]]
print(resp.status_code)
print(resp.text)
# 3. 加载类别映射
idx2name = json.load(open("torchserve/test/index_to_name.json"))

# 4. 打印结果
for box in detections[0]:
    xmin, ymin, xmax, ymax, score, cls = box
    print(f"{idx2name[str(int(cls))]}: {score*100:.1f}% at [{xmin:.1f},{ymin:.1f}-{xmax:.1f},{ymax:.1f}]")