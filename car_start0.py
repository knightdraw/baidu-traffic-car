#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import threading
import os
import numpy as np
from task_func import MyTask
from log_info import logger
from car_wrap import MyCar
from tools import CountRecord
#from camera.base.camera import P_Show_IMG  ###
from ernie_bot.base.ernie_bot_wrap import ImageVisionPrompt  ###
from ernie_bot.base.ernie_bot_wrap import BMIPrompt  ###
from ernie_bot.base.ernie_bot_wrap import EduCounselerPrompt  ###
import re  ###
import math
import sys, os
import erniebot  ###
import random ###

# 添加上本文件对应目录
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # kill_other_python()
    print("car_start")
    my_car = MyCar()
    my_car.STOP_PARAM = False
    my_car.task.reset()
    #cam_thread1 = threading.Thread(target=P_Show_IMG,args=(my_car.cap_front,),daemon=True)
    #cam_thread2 = threading.Thread(target=P_Show_IMG, args=(my_car.cap_side,), daemon=True)
    #cam_thread1.start()
    #cam_thread2.start()


    def hanoi_tower_func():
        try:
            print("Executing haoni_tower")
            my_car.lane_dis_offset(0.3, 0.5)
            # print(my_car.get_odometry())
            my_car.set_pose_offset([0.25, 0, 0], 1)
            # print(my_car.get_odometry())
            det_side = my_car.lane_det_dis2pt(0.2, 0.25)
            side = my_car.get_card_side()
            # print(side)
            # 调整检测方向
            my_car.task.arm.switch_side(side * -1)

            # 调整车子朝向
            my_car.set_pose_offset([0, 0, math.pi / 4 * side], 1)

            # 第一个要抓取的圆柱
            cylinder_id = 1
            # 调整抓手位置，获取要抓取的圆柱信息
            pts = my_car.task.pick_up_cylinder(cylinder_id, True)
            # 走一段距离
            time.sleep(1)
            my_car.lane_dis_offset(0.4, 0.66)

            # 第二次感应到侧面位置
            # my_car.lane_sensor(0.2, value_h=0.3, sides=side*-1)
            my_car.lane_sensor(0.2, value_h=0.3, sides=side * -1, stop=True)
            # return
            # 记录此时的位置
            pose_dict = {}
            pose_last = None
            detected_ids = set()
            print("Pose 15:", pose_dict.get(15, "Not detected"))

            for i in range(3):
                # 根据给定信息定位目标
                index = my_car.lane_det_location(0.1, pts, side=side * -1)
                my_car.beep()
                # pose_dict[index] = my_car.get_odometry().copy()
                cur_pose = my_car.get_odometry().copy()

                if index == 15:
                    angle = cur_pose[2]
                    cur_pose = list(cur_pose)  # 转成可修改列表
                    cur_pose[0] += 0.01 * math.cos(angle)  # x方向前移8厘米
                    cur_pose[1] += 0.01 * math.sin(angle)  # y方向前移8厘米
                    print(f"[加偏移后] pose: {cur_pose}")

                pose_dict[index] = cur_pose
                if i == 2:
                    pose_last = my_car.get_odometry().copy()
                    print(index)
                # pose_list.append([index, my_car.get_odometry().copy()])

                if i < 2:
                    my_car.set_pose_offset([0.09, 0, 0])
                    my_car.beep()

            # print(pose_dict)
            # 根据识别到的位置调整方向位置
            # angle = math.atan((pose_dict[2][1] - pose_dict[0][1]) / (pose_dict[2][0] - pose_dict[0][0]))
            # print(angle)
            # my_car.set_pose_offset([0, 0, -angle])
            # 重新定位最后一个圆柱
            # my_car.lane_det_location(0.2, pts, side=side*-1)
            angle_det = my_car.get_odometry()[2]
            # 计算目的地终点坐标
            pose_end = [0, 0, angle_det]
            pose_end[0] = pose_last[0] + 0.142 * math.cos(angle_det)
            pose_end[1] = pose_last[1] + 0.12 * math.sin(angle_det)
            # print(det)
            # 调整到目的地
            # my_car.set_pose(det)
            for i in range(3):
                det = pose_dict[i]
                det[2] = angle_det
                my_car.set_pose(det)
                # my_car.lane_det_location(0.2, pts, side=side*-1)
                my_car.task.pick_up_cylinder(i)
                my_car.set_pose(pose_end)
                my_car.task.put_down_cylinder(i)
            # return
            my_car.lane_dis_offset(0.3, 0.5)
        except Exception as e:
            print("hanoi_tower error")
        '''
        print("Executing haoni_tower")
        my_car.lane_dis_offset(0.3, 0.5)
        # print(my_car.get_odometry())
        my_car.set_pose_offset([0.25, 0, 0], 1)
        # print(my_car.get_odometry())
        det_side = my_car.lane_det_dis2pt(0.2, 0.25)
        side = my_car.get_card_side()
        # print(side)
        # 调整检测方向
        my_car.task.arm.switch_side(side * -1)

        # 调整车子朝向
        my_car.set_pose_offset([0, 0, math.pi / 4 * side], 1)

        # 第一个要抓取的圆柱
        cylinder_id = 1
        # 调整抓手位置，获取要抓取的圆柱信息
        pts = my_car.task.pick_up_cylinder(cylinder_id, True)
        # 走一段距离
        time.sleep(1)
        my_car.lane_dis_offset(0.4, 0.66)

        # 第二次感应到侧面位置
        # my_car.lane_sensor(0.2, value_h=0.3, sides=side*-1)
        my_car.lane_sensor(0.2, value_h=0.3, sides=side * -1, stop=True)
        # return
        # 记录此时的位置
        pose_dict = {}
        pose_last = None
        detected_ids = set()
        print("Pose 15:", pose_dict.get(15, "Not detected"))

        for i in range(3):
            # 根据给定信息定位目标
            index = my_car.lane_det_location(0.1, pts, side=side * -1)
            my_car.beep()
            #pose_dict[index] = my_car.get_odometry().copy()
            cur_pose = my_car.get_odometry().copy()

            if index == 15:
              angle = cur_pose[2]
              cur_pose = list(cur_pose)  # 转成可修改列表
              cur_pose[0] += 0.01 * math.cos(angle)  # x方向前移8厘米
              cur_pose[1] += 0.01 * math.sin(angle)  # y方向前移8厘米
              print(f"[加偏移后] pose: {cur_pose}")

            pose_dict[index] = cur_pose
            if i == 2:
                pose_last = my_car.get_odometry().copy()
                print(index)
            # pose_list.append([index, my_car.get_odometry().copy()])

            if i < 2:
                my_car.set_pose_offset([0.09, 0, 0])
                my_car.beep()

        # print(pose_dict)
        # 根据识别到的位置调整方向位置
        # angle = math.atan((pose_dict[2][1] - pose_dict[0][1]) / (pose_dict[2][0] - pose_dict[0][0]))
        # print(angle)
        # my_car.set_pose_offset([0, 0, -angle])
        # 重新定位最后一个圆柱
        # my_car.lane_det_location(0.2, pts, side=side*-1)
        angle_det = my_car.get_odometry()[2]
        # 计算目的地终点坐标
        pose_end = [0, 0, angle_det]
        pose_end[0] = pose_last[0] + 0.142 * math.cos(angle_det)
        pose_end[1] = pose_last[1] + 0.12 * math.sin(angle_det)
        # print(det)
        # 调整到目的地
        # my_car.set_pose(det)
        for i in range(3):
            det = pose_dict[i]
            det[2] = angle_det
            my_car.set_pose(det)
            # my_car.lane_det_location(0.2, pts, side=side*-1)
            my_car.task.pick_up_cylinder(i)
            my_car.set_pose(pose_end)
            my_car.task.put_down_cylinder(i)
        # return
        my_car.lane_dis_offset(0.3, 0.5)
        '''


    def bmi_cal():
        # my_car.lane_dis_offset(0.3, 0.8)
        print("Executing bmi_cal")
        print("[bmi_cal] calling with arm_set=True")
        # 准备手臂位置

        pts = my_car.task.bmi_set(arm_set=True)
        print("改变朝向")
        print("[bmi_cal] returned pts:", pts)
        # 巡航到bmi识别附件
        #my_car.lane_time(speed=0.3, time_dur=1)
        my_car.lane_sensor(0.3, value_h=0.3, sides=1)
        # 推开bmi识别标签
        # my_car.lane_dis_offset(0.3, 0.5)
        my_car.set_pose_offset([0.0, -0.03, 0])
        my_car.set_pose_offset([0.05, 0.0, 0])
        my_car.set_pose_offset([0.0, 0.13, 0])
        my_car.set_pose_offset([0.0, -0.09, 0])
        my_car.set_pose_offset([0.13, 0, 0])
        # 调整bmi识别位置
        my_car.lane_det_location(0.2, pts, side=1)
        # 识别相关文字
        text = my_car.get_ocr()
        print("OCR识别结果：", text)
        
        ###
        if not text or text.strip() == "":
          print("OCR识别失败，跳过BMI计算任务")
          return 
        # === 构建最终 prompt（核心）===
        bmi_prompt = BMIPrompt()
        prompt_text = str(bmi_prompt) + "\n输入：" + text

        # === 配置文心一言 API ===
        erniebot.api_type = "aistudio"
        erniebot.access_token = ""  # ✅ 替换为你的 access_token

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
        ###
        # time.sleep(0.3)
        # out = 3
        my_car.task.bmi_set(out)
        time.sleep(0.5)
        # 调整位置准备放置球
        # my_car.lane_dis_offset(0.21, 0.19)
        # my_car.set_pose_offset([0, 0.05, 0], 0.7)
        # my_car.task.put_down_ball()
        
    def camp_fun():
        print("Executing camp_fun")
        angle_offset = -math.pi / 2 * 0.82
        # dis_angle = -math.pi/2*0.3
        # dis = 1.
        dis_x = 1.36
        dis_y = -0.87
        # print(dis_x, dis_y)
        angle_now = my_car.get_odometry()[2]
        x_offset = dis_x * math.cos(angle_now) - dis_y * math.sin(angle_now)
        y_offset = dis_y * math.cos(angle_now) + dis_x * math.sin(angle_now)
        angle_tar = angle_now - math.pi * 2 + angle_offset
        pose = my_car.get_odometry().copy()
        pose[0] = pose[0] + x_offset
        pose[1] = pose[1] + y_offset
        pose[2] = angle_tar
        # print(pose)
        # return

        my_car.lane_sensor(0.25, value_h=1, sides=-1)
        # time.sleep(25)
        # my_car.lane_sensor()

        print("start circle")
        print("1")
        my_car.lane_dis_offset(0.3, 0.5)
        print("2")
        #my_car.set_vel_time(0.3, 0, -0.5, 1.8)
        my_car.set_vel_time(0.3, 0, -0.5, 2.8)
        print("3")
        my_car.lane_dis_offset(0.3, 3.41)
        print("4")
        #my_car.set_pose(pose, vel=[0.2, 0.2, math.pi/3])
        my_car.set_vel_time(0.3, 0, 0, 0.5)

        #my_car.lane_dis_offset(0.3, 0.5)
        #my_car.set_vel_time(0.3, 0, -0.5, 1.8)
        #my_car.lane_dis_offset(0.3, 3.06)
        #my_car.set_vel_time(0.3, 0, 0, 1.7)
        # my_car.set_pose(pose, vel=[0.2, 0.2, math.pi / 3])

        # my_car.
        # my_car.set_vel_time(0.3, 0, -0.1, 1)
        # my_car.move_advance([0.3, 0, 0], value_l=1, sides=-1)
        # my_car.lane_time(0, 1)
        # my_car.move_advance([0.3, 0, -0.2], value_l=1, sides=-1)
        # my_car.move_distance([0.3, 0, 0], 0.25)
        # my_car.move_advance([0.3, 0, 0], value_l=1, sides=-1)
        # my_car.move_advance([0.3, 0, 0], value_l=0.5, sides=-1)


        
    def send_fun():
        print("Executing send_fun")
        # my_car.move_advance([0.3, 0, 0], value_l=1, sides=-1)
        # my_car.move_distance([0.3, 0, -0.1], 0.25)
        # my_car.lane_sensor(0.3, value_l=1.1, sides=-1)
        my_car.lane_dis_offset(0.3, 1.63)
        #right_turn_radians = math.radians(-5)#
        #my_car.set_pose_offset([0, 0, right_turn_radians], 1)###
        time.sleep(1)
        my_car.task.eject(1)


    # 获取食材
    def task_ingredients():
        tar = my_car.task.get_ingredients(side=1, ocr_mode=True, arm_set=True)
        my_car.lane_sensor(0.3, value_h=0.2, sides=1)
        my_car.lane_dis_offset(0.37, 0.17)
        #my_car.lane_det_location(0.2, tar, side=1)
        #text1 = my_car.ez_get_ocr()#新加
        #print(text1)
        #my_car.set_pose_offset([0, -0.04, 0])       
        tar = my_car.task.pick_ingredients(1, 1, arm_set=True)
        #my_car.lane_det_location(0.2, tar, side=1)
        my_car.set_pose_offset([-0.015, -0.04, 0]) 
        my_car.task.pick_ingredients(2, 2)
        my_car.set_pose_offset([0.02, 0, 0]) 
        my_car.task.pick_ingredients(2, 2)
        #my_car.set_pose_offset([0.115, 0, 0])
        #my_car.task.arm.switch_side(-1)
        #my_car.set_pose_offset([0, -0.05, 0])
        #tar = my_car.task.get_ingredients(side=-1, ocr_mode=True, arm_set=True)
        #my_car.lane_det_location(0.2, tar, side=-1)
        #tar = my_car.task.pick_ingredients(2, 2, arm_set=True)
        #my_car.lane_det_location(0.2, tar, side=-1)
        #my_car.task.pick_ingredients(2, 2)
        time.sleep(1)
        my_car.lane_dis_offset(0.3, 0.3)





    
    def task_answer():
        print("Executing task_answer")
        my_car.lane_sensor(0.3, value_h=0.3, sides=1)
        my_car.task.arm.switch_side(1)
        my_car.move_distance([0.3, 0, 0], 0.22)
        
        
        #my_car.task.arm.set_hand_angle(65)
        
        #tar_horiz = my_car.task.arm.horiz_mid###
        #my_car.task.arm.set_offset(tar_horiz, 0.03)  ###
        tar = my_car.task.get_answer(arm_set=True)
        #my_car.lane_det_location(0.2, tar, side=1)
        my_car.set_pose_offset([0, -0.02, 0])###
        left_turn_radians = math.radians(5)
        my_car.set_pose_offset([0, 0, left_turn_radians], 1)###
        time.sleep(1)


        text = my_car.ez_get_ocr()
        #text = my_car.get_ocr()
        print(text)
        time.sleep(1)
        right_turn_radians = math.radians(-5)
        my_car.set_pose_offset([0, 0, right_turn_radians], 1)###
        
      
        # === 构建最终 prompt（核心）===
        educounseler_prompt = EduCounselerPrompt()
        prompt_text = str(educounseler_prompt) + "\n输入：" + text

        # === 配置文心一言 API ===
        erniebot.api_type = "aistudio"
        erniebot.access_token = "4fe6345ddee61d1c8eacfa3cfab8d5e6d2272e54"  # ✅ 替换为你的 access_token
        print( erniebot.Model.list())

        # === 调用大模型 ===
        response = erniebot.ChatCompletion.create(
            model="ernie-4.0",
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.01,
        )

        # === 输出结果 ===
        print("文心一言返回的结果：")
        print(response.get("result"))

        # 尝试用正则提取出答案字母（例如 "A"）
        result_str = response.get("result")
        print("原始模型输出：", result_str)
        answer_match = re.search(r"'answer'\s*:\s*'([A-D])'|\"answer\"\s*:\s*\"([A-D])\"", result_str)

        if answer_match:
            # 获取匹配的答案（group(1)匹配单引号，group(2)匹配双引号）
            answer = answer_match.group(1) if answer_match.group(1) else answer_match.group(2)
            print("提取到的答案：", answer)

            # 将字母转换为数字
            if answer == "A":
                out = 0
            elif answer == "B":
                out = 1
            elif answer == "C":
                out = 2
            elif answer == "D":
                out = 3

            print("out =", out)
        else:
            print("未找到答案，请检查模型输出格式")
            out = random.randint(0,3)
        
        
        '''
        # 图像处理部分
        image_prompt = ImageVisionPrompt(
           cap=my_car.cap_side,
           imgbb_api_key="9e75a9d625b4a2c802248c0856979d14",
           ernie_access_token="bce-v3/ALTAK-Za20WVscPby5UMzmlvfaF/229818f85aaf18472594dd29d291acd78d9bc36b"
        )
        '''
        '''
        try:
            res = image_prompt.infer_image("假如图片上面是问题，下面是A，B，C, D 四个选项，请直接回答出正确选项。只给出A，B，C，D即可。")
            print("文心大模型返回：", res)
            
            if not res or not isinstance(res, str):
                raise ValueError("无效的模型输出")
                
            if "A" in res:
                out = 0
            elif "B" in res:
                out = 1
            elif "C" in res:
                out = 2
            elif "D" in res:
                out = 3
            else:
                raise ValueError("输出不包含有效选项")
                    
        except Exception as e:
            print(f"处理过程中出现错误: {e}")
            print("将随机生成一个结果")
            import random
            out = random.randint(0, 3)
            options = ['A', 'B', 'C', 'D']
            res = options[out]
            print(f"随机生成的结果: {res}")
        '''
        # 最终执行部分
        pose_tar_offset = [0.08 * out - 0.12, 0, 0]
        my_car.set_pose_offset(pose_tar_offset)
        my_car.task.get_answer()  


     
       

    def task_fun2():
        print("Executing task_fun2")
        # 巡航到投掷任务点2
        my_car.lane_sensor(0.3, value_h=0.5, sides=-1)
        # 调整方向
        my_car.lane_time(0, 1)
        my_car.set_pose_offset([-0.07, 0, 0])
        my_car.task.eject(2)
        time.sleep(1)
        my_car.set_pose_offset([0, -0.03, 0])
        # my_car.task.arm.switch_side(-1)
        # my_car.move_distance([0.3, 0, 0], 0.24)
        # tar = my_car.task.get_answer(arm_set=True)
        
    def task_food():
     my_car.lane_sensor(0.3, value_h=0.5, sides=-1)
     #tar = my_car.task.set_food(arm_set=True)
     #my_car.task.arm.switch_side(-1)
     #my_car.set_pose_offset([0.18, 0, 0])
     #my_car.lane_time(0, 1)
     #my_car.lane_det_location(0.2, tar, side=-1)
     #text1 = my_car.ez_get_ocr()#新加
     #print(text1)
     #my_car.set_pose_offset([0.4, 0, 0])
     #my_car.lane_det_location(0.2, tar, side=-1)
     #text2 = my_car.ez_get_ocr()#新加
     #print(text2)
     #out = 3
     #if out in [1, 2]:
     #   my_car.set_pose_offset([-0.31, 0, 0])  # 向后移动0.4米
     #if out in [3, 4]:
     #    my_car.set_pose_offset([-0.14, 0, 0])  # 向后移动0.4米
     #if out in [1, 3]:
     #    cengshu = 2
     #elif out in [2, 4]:
     #    cengshu = 1
     #else:
     #   cengshu = 1  # 默认值，避免未定义
     #my_car.set_pose_offset([0.075, 0, 0])
     #my_car.task.set_food(1, row=cengshu)
     #my_car.set_pose_offset([0.06, 0, 0])
     #my_car.task.set_food(2, row=cengshu)
     # my_car.lane_dis_offset(0.3, 0.17)
     # my_car.lane_det_location(0.2, tar, side=1)
     # my_car.task.pick_ingredients(1, 1)

    def task_help():
        '''
        my_car.lane_dis_offset(0.2, 0) ###
        my_car.lane_sensor(0.2, value_h=0.5, sides=1)
        my_car.task.help_peo(arm_set=True)
        my_car.set_pose_offset([0.1, 0.15, 0])
        my_car.set_pose_offset([-0.1, 0.15, 0], vel=[0.6, 0.6, 0])
        my_car.set_pose_offset([0, -0.3, 0])
        my_car.set_pose_offset([0.65, 0, 0], vel=[0.2, 0.2, 0])
        '''

        my_car.lane_dis_offset(0.2, 0)  ###
        my_car.lane_sensor(0.2, value_h=0.5, sides=1)
        my_car.task.help_peo(arm_set=True)
        print("1")
        my_car.set_pose_offset([0.1, 0.15, 0])
        print("2")
        my_car.set_pose_offset([-0.1, 0.15, 0], vel=[0.6, 0.6, 0])
        print("3")
        my_car.set_pose_offset([0, -0.3, 0])
        print("4")
        my_car.lane_dis_offset(0.3,0.65)
        #my_car.set_pose_offset([0.65, 0, 0], vel=[0.2, 0.2, 0])

    def go_start():
        my_car.lane_sensor(0.3, value_l=0.4, sides=-1)
        my_car.set_pose_offset([0.85, 0, 0], 2.8)
        my_car.set_pose_offset([0.45, -0.09, -0.6], 2.5)
        # 前移
        # my_car.set_pose_offset([0.3, 0, 0], 2.5)
        # my_car.set_pose_offset([0.45, -0.09, -0.6], 2.5)
        # 离开道路到修整营地
        # my_car.set_pose_offset([0.15, -0.4, 0], 2)
        # 做任务
        # my_car.do_action_list(actions_map)


    def car_move():
        my_car.set_pose([0.20, 0, 0], 1)


    my_car.beep()
    time.sleep(0.2)
    functions = [hanoi_tower_func, bmi_cal, camp_fun, send_fun, task_ingredients, task_answer, task_fun2, task_food,
                 task_help]
    my_car.manage(functions, 9)

