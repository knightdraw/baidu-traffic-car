def detect_ingredients(self):
    # 使用侧摄像头读取图像
    img_side = self.cap_side.read()

    # 调用模型接口进行识别（使用的是task_det）
    dets_ret = self.task_det(img_side)

    # 判断有无检测结果
    if not dets_ret:
        print("没有检测到任何菜品")
        return

    # 清空之前的检测数据（如果需要）
    self.detections = []

    print("检测到的食材如下：")
    for det in dets_ret:
        det_cls_id, obj_id, label, score, x, y, w, h = det

        # 将检测结果放入detections列表中
        detection = {
            "label": label,
            "id": obj_id,
            "confidence": score,
            "position": (x, y, w, h)
        }
        self.detections.append(detection)

        # 打印每个检测到的食材信息
        print(f"标签: {label}, ID: {obj_id}, 置信度: {score:.2f}, 位置: ({x:.2f}, {y:.2f}, {w:.2f}, {h:.2f})")

    # Step 0: 丢弃文本类标签（确保变量用的是 filtered_detections）
    filtered_detections = [d for d in self.detections if d["label"].lower() != "text_det"]

    # Step 1: 取出所有 y 坐标
    y_coords = [det["position"][1] for det in filtered_detections]

    # Step 2: 计算中位数作为分层阈值
    threshold_y = np.median(y_coords)

    # Step 3: 分层
    upper_layer = [d for d in filtered_detections if d["position"][1] < threshold_y]
    lower_layer = [d for d in filtered_detections if d["position"][1] >= threshold_y]

    # Step 4: 每层内部按 x 从左到右排序
    upper_layer = sorted(upper_layer, key=lambda d: d["position"][0])
    lower_layer = sorted(lower_layer, key=lambda d: d["position"][0])

    def auto_assign_positions(layer, start_letter='A'):
        # 给每个蔬菜分配字母位置
        labels = [det['label'] for det in layer]
        positions = [chr(i) for i in range(ord(start_letter), ord(start_letter) + len(layer))]
        assigned_positions = dict(zip(positions, labels))

        return assigned_positions

    # 返回上层和下层位置字母（例如：A, B, C...）
    def get_positions():
        upper_positions = auto_assign_positions(upper_layer, 'A')
        lower_positions = auto_assign_positions(lower_layer, 'D')
        return {**upper_positions, **lower_positions}

    # 返回上层和下层的食材位置
    return get_positions()
