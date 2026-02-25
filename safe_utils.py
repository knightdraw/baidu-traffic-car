# safe_utils.py
import multiprocessing

def safe_call(func, args=(), kwargs={}, timeout=3):
    def wrapper(return_dict):
        try:
            result = func(*args, **kwargs)
            return_dict["result"] = result
        except Exception as e:
            return_dict["error"] = str(e)

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=wrapper, args=(return_dict,))
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("超时：函数执行超出", timeout, "秒，已强制终止")
        p.terminate()
        p.join()
        return None

    if "error" in return_dict:
        print("函数异常")
        return None

    return return_dict.get("result", None)
class MyTask:
    ...
    def pick_and_drop_block(self,
                           reach=0.12,           # 伸出距离（米）
                           base_height=0.10,     # 抬高到的准备高度（米）
                           descend=0.055,        # 抓取时向下位移（米）
                           lift_after=0.08,      # 抓起后向上位移（米）
                           lower_release=0.03,   # 放下前轻降（米）
                           speed_xy=[0.12, 0.04] # 水平/垂直速度（m/s）
                           ):
        # 1) 转向左侧，手掌朝下（利于垂直抓取）
        self.arm.switch_side(1)          # 1 表示左侧（与你现有注释一致）
        self.arm.set_hand_angle(65)      # 65°：手朝下；若要水平搬运可改为 -65°

        # 2) 到达准备位：水平中线 + 准备高度
        tar_horiz = self.arm.horiz_mid
        self.arm.set(tar_horiz, base_height)

        # 3) 伸出到目标前方
        self.arm.set_offset(reach * self.arm.side, 0, speed=speed_xy)

        # 4) 下降并吸取/夹取
        self.arm.set_offset(0, -abs(descend), speed=speed_xy)
        time.sleep(0.2)
        self.arm.grap(1)                 # 抓住（或吸住）
        time.sleep(0.4)

        # 5) 抬起并收回
        self.arm.set_offset(0, abs(lift_after), speed=speed_xy)
        self.arm.set_offset(-reach * self.arm.side, 0, speed=speed_xy)

        # 6) 轻降并释放
        self.arm.set_offset(0, -abs(lower_release), speed=speed_xy)
        time.sleep(0.2)
        self.arm.grap(0)                 # 释放
        time.sleep(0.3)

