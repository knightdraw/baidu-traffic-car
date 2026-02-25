from ernie_bot_wrap import BMIPrompt

# === 构建最终 prompt（核心）===
bmi_prompt = BMIPrompt()
prompt_text = str(bmi_prompt) + "\n输入：" + text

# === 配置文心一言 API ===
erniebot.api_type = "aistudio"
erniebot.access_token = "4fe6345ddee61d1c8eacfa3cfab8d5e6d2272e54"  # ✅ 替换为你的 access_token

# === 调用大模型 ===
response = erniebot.ChatCompletion.create(
    model="ernie-4.0",
    messages=[{"role": "user", "content": prompt_text}],
    temperature=0.1,
)

# === 输出结果 ===
print("文心一言返回的结果：")
print(response.get("result"))


# 获取大模型输出文本（result_str 是模型返回的字符串）
result_str = response.get("result")
print("原始模型输出：", result_str)

# 尝试用正则提取出 BMI 数值（例如 22.86）
bmi_match = re.search(r'"bmi"\s*:\s*([0-9.]+)', result_str)  # 匹配 "bmi": 22.86 这种格式

if bmi_match:
    bmi = float(bmi_match.group(1))
    print("提取到的 BMI 值：", bmi)

    # 判断 out 值
    if bmi < 18.5:
        out = 1
    elif bmi <= 24:
        out = 2
    elif bmi <= 28:
        out = 3
    else:
        out = 4

    print("out =", out)
else:
    print("未找到 BMI 值，请检查模型输出格式")