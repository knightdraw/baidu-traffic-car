# -*- coding: utf-8 -*-
import erniebot, json
import os ###
import requests ###
import uuid ###
import cv2 ###
from camera.base.camera import Camera ###
from openai import OpenAI
from jsonschema import validate


class PromptJson:
	def __init__(self, rulers) -> None:
		self.rulers_str = '请根据下面的schema描述生成给定格式json,只返回json数据,不要其他内容。'
		self.schema_str = ''
		self.example_str = ''

		self.set_rulers(rulers)
		self.set_scheame(self.json_obj())
		self.set_example(self.example())

	def json_obj(self):
		return '''```{'type':'string'}```'''

	def example(self):
		return '正确的示例如下：'
	
	def __call__(self, *args, **kwargs):
		pass
    
	def set_scheame(self, json_obj):
		# json转字符串去空格,换行，制表符
		json_str = str(json_obj).replace(' ', '').replace('\n', '').replace('\t', '')
		# 加上三个引号
		json_str = '```' + json_str + '```'
		self.schema_str = json_str

	def set_example(self, example_str:str):
		# 去空格,换行，制表符
		example_str = example_str.replace(' ', '').replace('\n', '').replace('\t', '')
		self.example_str = example_str

	def set_rulers(self, rulers):
		self.rulers_str = rulers.replace(' ', '').replace('\n', '').replace('\t', '')

	def __str__(self) -> str:
		return self.__repr__()
	
	def __repr__(self) -> str:
		return self.rulers_str + self.schema_str + self.example_str
	
class ActionPrompt(PromptJson):
	def __init__(self) -> None:
		
		rulers = '''你是一个机器人动作规划者，需要把我的话翻译成机器人动作规划并生成对应的json结果，机器人工作空间参考右手坐标系。
					严格按照下面的scheame描述生成给定格式json，只返回json数据:
				'''
		super().__init__(rulers)
		# self.set_rulers(rulers)
		# self.set_scheame(self.json_obj())
		# self.set_example(self.example())

	def json_obj(self)->dict:
		schema_move = {'type': 'object', 'required': ['func', 'x', 'y', 'angle'],
               'porperties':{
                                'func': {'description': '移动', 'const': 'move'},
                                'x': {'description': 'x坐标, 前后移动, 向前移动正值，向后移动负值', 'type': 'number'},
                                'y': {'description': 'y坐标, 左右移动, 向左移动正值，向右移动负值', 'type': 'number'}, 
                                'angle': {'description': '旋转或者转弯角度，右转顺时针负值，左转逆时针正值', 'type': 'number'}
                            }
            }
		schema_beep = { 'type': 'object', 'required': ['func', 'time_dur'],
				'properties': {'func': {'description': '蜂鸣器,需要发声时', 'const': 'beep'}, 
                   'time_dur': {'description': '蜂鸣器发声持续时间', 'type': 'number'}}
		}

		schema_light = { 'type': 'object', 'required': ['func', 'time_dur'],
						'properties': {'func': {'description': '发光,需要照明时', 'const': 'light'}, 
						'time_dur': {'description': '照亮持续时间', 'type': 'number'}}
		}
		schema_actions = {'type': 'array', 'required': ['items'],
                  'items': {'anyOf': [schema_move, schema_beep, schema_light],
                        'minItems': 1
                    }
		}
		return schema_actions
	
	def example(self)->str:
		example = '''正确的示例如下：
					向左移0.1m, 向左转弯85度: ```[{'func': 'move', 'x': 0, 'y': 0.1, 'angle': 85}]```,
					向右移0.2m, 向前0.1m。 ```[{'func': 'move', 'x': 0.1, 'y': -0.2, 'angle': 0}]```,
					向右转弯85度, 向右移0.1m,。 ```[{'func': 'move', 'x': 0, 'y': -0.1, 'angle': -85}]```,
					蜂鸣器发声5秒。 ```[{'func': 'beep', 'time_dur': 5}]```,
					发光5秒。 ```[{'func': 'light', 'time_dur': 5}]```。
				'''
		return example
	
class HumAttrPrompt(PromptJson):
	def __init__(self) -> None:
		rulers = '''你是一个人特征总结程序，需要根据描述把人的特征生成对应的json结果，如果有对应的描述就写入对应位置。
					严格按照下面的scheame描述生成给定格式json，只返回json数据:
				'''
		super().__init__(rulers)

	def json_obj(self)->dict:
		'''
		0 = Hat - 帽子:0无1有
		1 = Glasses - 眼镜:0无1有
		2 = ShortSleeve - 短袖
		3 = LongSleeve - 长袖
		4 = UpperStride - 有条纹
		5 = UpperLogo - 印有logo/图案
		6 = UpperPlaid - 撞色衣服(多种颜色)
		7 = UpperSplice - 格子衫
		8 = LowerStripe - 有条纹
		9 = LowerPattern - 印有图像
		10 = LongCoat - 长款大衣
		11 = Trousers - 长裤
		12 = Shorts - 短裤
		13 = Skirt&Dress - 裙子/连衣裙
		14 = boots - 鞋子
		15 = HandBag - 手提包
		16 = ShoulderBag - 单肩包
		17 = Backpack - 背包
		18 = HoldObjectsInFront - 手持物品
		19 = AgeOver60 - 大于60
		20 = Age18-60 - =18~60
		21 = AgeLess18 - 小于18
		22 = Female - 0:男性; 1:女性
		23 = Front - 人体朝前
		24 = Side - 人体朝侧
		25 = Back - 人体朝后
		'''
		schema_attr = {'type': 'object', 
                'properties':{
                    'hat':{'type': 'boolean', 'description': '戴帽子真,没戴帽子假'},
					'glasses': {"type": 'boolean', 'description': '戴眼镜真,没戴眼镜假', 'threshold':0.15},
					'sleeve':{'enum': ['Short', 'Long'], 'description': '衣袖长短'},
					# 'UpperStride', 'UpperLogo', 'UpperPlaid', 'UpperSplice'	有条纹		印有logo/图案	撞色衣服(多种颜色) 格子衫
					'color_upper':{'enum':['Stride', 'Logo', 'Plaid', 'Splice'], 'description': '上衣衣服颜色'},
					# 'LowerStripe', 'LowerPattern'		有条纹		印有图像
					'color_lower':{'enum':['Stripe', 'Pattern'], 'description': '下衣衣服长短'},
					# 'LongCoat', 长款大衣
					'clothes_upper':{'enum':['LongCoat'], 'description': '上衣衣服类型', 'threshold':0.8},
					# 'Trousers', 'Shorts', 'Skirt&Dress'  长裤		短裤 	裙子/连衣裙
					'clothes_lower':{'enum':['Trousers', 'Shorts', 'Skirt_dress'], 'description': '下衣衣服类型'},
					'boots':{'type': 'boolean', 'description': '穿着鞋子真,没穿鞋子假'},
					'bag':{'enum': ['HandBag', 'ShoulderBag', 'Backpack'], 'description': '带着包的类型'},
					'holding':{'type': 'boolean', 'description': '持有物品为真', 'threshold':0.5},
					'age':{'enum': ['Old', 'Middle', 'Young'], 'description': '年龄,小于18岁为young, 18到60为middle, 大于60为old'},
					'sex':{'enum': ['Female', 'Male'], 'threshold':0.6},
					'direction':{'enum': ['Front', 'Side', 'Back'], 'description': '人体朝向'},
					},
                "additionalProperties": False
            }
		return schema_attr
	
	def example(self)->str:
		example = '''正确的示例如下：
					一个带着眼镜的老人: ```{'glasses': True, 'age': 'old'}```,
					一个带着帽子的中年人: ```{'hat': True, 'age': 'middle'}``` ,
					穿着短袖的带着眼镜的人: ```{'glasses': True, 'clothes': 'short'}``` 。
				'''
		return example

	
class ErnieBotWrap():

	def __init__(self):
		erniebot.api_type = 'aistudio'
		erniebot.access_token = '441a08bc51a0e42a742fab7f2196453dbe276c37'
		models = erniebot.Model.list()
		print(models)
		
		self.msgs = []
		# self.model = 'ernie-4.0'
		self.model = 'ernie-3.5'
		# self.model = 'ernie-turbo'
		# self.model = "ernie-text-embedding"
		# self.model = "ernie-vilg-v2"
		self.prompt_str = '请根据下面的描述生成给定格式json'

	@staticmethod
	def get_mes(role, dilog):
		data = {}
		if role == 0:
			data['role'] = 'user'
		elif role ==1:
			data['role'] = 'assistant'
		data['content'] = dilog	
		return data

	def set_promt(self, prompt_str):
		# str_input = prompt_str
		# self.msgs.append(self.get_mes(0, str_input))
		# response = erniebot.ChatCompletion.create(model=self.model, messages=self.msgs, system=prompt_str)
		# str_res = response.get_result()
		# self.msgs.append(self.get_mes(1, str_res))
		# print(str_res)
		# print("设置成功")
		self.prompt_str = prompt_str
		# print(self.prompt_str)


	def get_res(self, str_input, record=False, request_timeout=5):
		if len(str_input)<1:
			return False, None
		start_str = " ```"
		end_str = " ```, 根据这段描述生成给定格式json"
		str_input = start_str + str_input + end_str
		msg_tmp = self.get_mes(0, str_input)
		if record:
			self.msgs.append(msg_tmp)
			msgs = self.msgs
		else:
			msgs = [msg_tmp]
		# Create a chat completion
		try:
			response = erniebot.ChatCompletion.create(model=self.model, messages=msgs, system=self.prompt_str, top_p=0.1,
											_config_=dict(api_type="AISTUDIO",), request_timeout=request_timeout)
			# print(response)
		except Exception as e:
			# print(e)
			return False, None
		# _config_=dict(api_type="QIANFAN",)
		# _config_=dict(api_type="AISTUDIO",)
		# print(response)
		str_res = response.get_result()
		if record:
			self.msgs.append(self.get_mes(1, str_res))
		return True, str_res
	
	@staticmethod
	def get_json_str(json_str:str):
		try:
			index_s = json_str.find("```json")
			if index_s == -1:
				index_s = json_str.find("```") 
				if index_s == -1:
					return None
				else:
					index_s += 3
					
			else:
				index_s += 7
			# print(json_str[index_s:])
			index_e = json_str[index_s:].find("```") + index_s
			if index_e == -1:
				return None
			# json_str = json_str[index_s:index_e]
			# print(json_str[index_s:index_e])
			# print(index_s, index_e)
			json_str = json_str[index_s:index_e]
			# 找到注释内容并删除
			json_str.replace("\n", "")
			# print(json_str)
			msg_json = json.loads(json_str)
			return msg_json
			# print(index_s)
			# return json_str
		except Exception as e:
			# print(e)
			return json_str
			'''
			try:
				index_s = json_str.find("```json") + 7
				# index_s = json_str.find("```json") + 7
			except Exception as e:
				index_s = 0
			try:
				index_e = json_str[index_s:].find("```") + index_s
			except Exception as e:
				index_e = len(json_str)
			import json
			msg_json = json.loads(json_str[index_s:index_e])
			return msg_json
			'''
	
	def get_res_json(self, str_input, record=False, request_timeout=10):
		state, str_res = self.get_res(str_input, record, request_timeout)
		if state:
			# print(str_res)
			obj_json = self.get_json_str(str_res)
			return obj_json
		else:
			return None



class ImageVisionPrompt:  ###
    def __init__(self, cap, imgbb_api_key: str, ernie_access_token: str, model: str = "ernie-4.5-turbo-vl-32k"):
        """
        cap: Camera类实例，具有 read() 方法
        imgbb_api_key: imgbb 图床的 API key
        ernie_access_token: 百度文心 access_token
        model: 默认使用多模态大模型 ernie-4.5-vl
        """
        self.cap = cap
        self.imgbb_key = imgbb_api_key
        self.ernie_key = ernie_access_token
        self.model = model

    def capture_and_upload(self) -> str:
        """拍照、保存、上传并返回图床URL"""
        image = self.cap.read()
        tmp_filename = f"tmp_{uuid.uuid4().hex[:8]}.jpg"
        tmp_path = os.path.join(".", tmp_filename)
        cv2.imwrite(tmp_path, image)

        try:
            # 上传图片
            with open(tmp_path, "rb") as file:
                res = requests.post(
                    "https://api.imgbb.com/1/upload",
                    params={"key": self.imgbb_key},
                    files={"image": file}
                )
            url = res.json()["data"]["url"]
            return url
        finally:
            # 删除临时文件
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def infer_image(self, prompt: str = "请分析这张图片") -> str:
        """调用文心一言多模态模型进行图文推理"""
        image_url = self.capture_and_upload()

        client = OpenAI(
            base_url="https://aip.baidubce.com/v1",
            api_key=self.ernie_key
        )

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            temperature=0.7,
            top_p=0.9
        )

        return response.jet("result")



#BMI,新加
class BMIPrompt(PromptJson):
	def __init__(self) -> None:
		rulers = '''你是一个BMI分析程序，需要根据提供的体检数据计算BMI值并分类。
					严格按照下面的schema描述生成JSON结果，只返回数值和分类，不要解释性文本:
				'''
		super().__init__(rulers)

	def json_obj(self) -> dict:
		"""
		BMI分类标准：
		- <18.5: 营养不良
		- 18.5-24: 健康
		- 24-28: 超重
		- >28: 肥胖
		"""
		schema_bmi = {
			"type": "object",
			"required": ["bmi", "category"],
			"properties": {
				"height": {
					"type": "number",
					"description": "身高(单位:厘米)",
					"minimum": 50,
					"maximum": 250
				},
				"weight": {
					"type": "number",
					"description": "体重(单位:kg)",
					"minimum": 10,
					"maximum": 300
				},
				"bmi": {
					"type": "number",
					"description": "计算得到的BMI值",
					"minimum": 10,
					"maximum": 50
				},
				"category": {
					"enum": ["营养不良", "健康", "超重", "肥胖"],
					"description": "BMI分类结果"
				},
				"advice": {
					"type": "string",
					"description": "健康建议(可选)"
				}
			},
			"additionalProperties": False
		}
		return schema_bmi

	def example(self) -> str:
		example = '''正确的示例如下：
					输入: 身高1.75米，体重70kg → ```{"height":1.75, "weight":70, "bmi":22.86, "category":"健康"}```
					输入: 身高1.65米，体重90kg → ```{"height":1.65, "weight":90, "bmi":33.06, "category":"肥胖"}```
					输入: 身高1.8米，体重50kg → ```{"height":1.8, "weight":50, "bmi":15.43, "category":"营养不良"}```
				'''
		return example

bmi_calculator = BMIPrompt()

# 计算一个人的BMI
# result = bmi_calculator.calculate_bmi(height=1.75, weight=70)
# print(result)
# 输出: {'height': 1.75, 'weight': 70, 'bmi': 22.86, 'category': '健康'}

# 获取JSON schema
print(bmi_calculator.json_obj())

# 获取示例
print(bmi_calculator.example())

### 做题目，新加

class EduCounselerPrompt(PromptJson):
    def __init__(self) -> None:
        rulers = '''你是一个中小学解题程序，需要根据题目描述：
1. 先写出详细的解题步骤（分步骤说明计算过程，比如“第一步：计算总价；第二步：判断是否满足优惠条件”）；
2. 根据计算结果从选项中选择正确答案；
3. 严格按照下方 schema 生成 JSON 格式的结果，**只返回 JSON 数据**，不要包含其他内容。'''
        super().__init__(rulers)

    def json_obj(self) -> dict:
        # 新增 analysis 字段存储解题步骤，保留 answer 字段存储答案
        return {
            "type": "object",
            "required": ["analysis", "answer"],  # 必须包含解题步骤和答案
            "properties": {
                "analysis": {
                    "type": "string",
                    "description": "详细的解题步骤，分步骤说明计算过程，例如：1. 计算商品总价；2. 判断是否满足优惠条件..."
                },
                "answer": {
                    "enum": ["A", "B", "C", "D"],
                    "description": "正确答案对应的选项字母"
                }
            },
            "additionalProperties": False
        }

    def example(self) -> str:
        # 增加更多详细的示例，特别是包含优惠计算的示例
        example = '''
        "analysis": "1. 计算商品总价：60 + 70 = 130元；2. 判断优惠：满100减20，130元满足条件；3. 计算最终价格：130 - 20 = 110元",
  "answer": "A"
        '''
        return example

def test():
	res = '''```json\n[\n  {\n    "func": "my_light",\n    "count": 3\n  },\n  {\n    "func": "beep",\n    "time_dur": 3  // 假设蜂鸣器持续发声3秒作为紧急警示，具体时长可根据实际情况调整\n  }\n]\n```'''
	json_test = ErnieBotWrap.get_json_str(res)
	print(json_test)



if __name__ == "__main__":
	# test()
	str_input = ''' 如果买满200元可优惠40元。购买了3件商品,价格分别为85元、130元和115元。最终支付多少钱?	选项有: A.300元 B.180元 C.130元 D.290元'''
	
	# ernie_edu = EduCounselerPrompt()

	ernie = ErnieBotWrap()
	# 设置prompt
	# ernie.set_promt(str(ActionPrompt()))
	# ernie.set_promt(str(HumAttrPrompt()))
	ernie.set_promt(str(EduCounselerPrompt()))
	json_res = ernie.get_res_json(str_input)
	print(json_res)
	# while True:
	# 	print("用户")
	# 	str_tmp = input("输入:")
	# 	if len(str_tmp)<1:
	# 		continue
	# 	# Create a chat completion
	# 	print("文心一言")
	# 	# _, str_res = ernie.get_res(str_tmp)
	# 	json_res = ernie.get_res_json(str_tmp)
	# 	print("输出:",json_res)
	
