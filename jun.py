import base64
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
import json

load_dotenv()

# OpenAI 설정
model = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # gpt-4o is set by env
    temperature=1.0,
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    openai_api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# 영양 정보 모델 정의
class NutritionInfo(BaseModel):
    food_name: str = Field(description="The name of the food")
    calorie: str = Field(description="The amount of Calories")
    carbohydrate: str = Field(description="The amount of Carbohydrate")
    protein: str = Field(description="The amount of Protein")
    fat: str = Field(description="The amount of Fat")

output_parser = JsonOutputParser(pydantic_object=NutritionInfo)

# 프롬프트 템플릿
prompt_template = ChatPromptTemplate.from_template(
    """
    음식이 입력되면 영양정보(이름, 칼로리, 탄수화물, 단백질, 지방)를 분석해줘
    음식 이름을 입력받으면 다음과 같은 조건을 만족하여 추출해줘 
    예를 들어 "돈까스 2개 먹었어"를 입력받으면, (돈까스, 1400,50,90,60) 이런식으로 출력해줘 
    또 다른 예시로 "에너지바 1개 먹었어"를 입력받으면, 출력은 (에너지바, 200,20,12,10) 이런식으로 출력해줘
    
    입력:{string}
    {format_instructions}
    """
).partial(format_instructions=output_parser.get_format_instructions())

def convert_to_base64(image_path):
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

def create_prompt(image_base64, text_prompt):
    message = HumanMessage(
        content=[
            {"type": "text", "text": text_prompt},
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            },
        ]
    )
    return [message]

def invoke_model(message):
    result = model.invoke(message)
    return result

def extract_food_name_from_image(image_path):
    image_base64 = convert_to_base64(image_path)
    text_prompt = """
    다음 이미지를 설명하세요. 음식 이름을 추출하여 JSON 형식으로 반환해주세요.
    추출할 정보:
    - 음식이름: 한글로 음식 이름
    반환 형식:
    {
    "음식": "음식 이름"
    }
    """
    message = create_prompt(image_base64, text_prompt)
    response = invoke_model(message)
    
    # 응답을 JSON 형식으로 변환
    def parse_response_to_json(response):
        try:
            response_text = response.content
            print(f"Response Text: {response_text}")  # Debugging 출력 추가
            response_json = json.loads(response_text)
            return response_json
        except Exception as e:
            return {"error": str(e)}

    response_json = parse_response_to_json(response)
    if "음식" in response_json:
        return response_json["음식"]
    else:
        print(f"Unexpected response format: {response_json}")  # Debugging 출력 추가
        return ""

def do(image_path):
    food_name = extract_food_name_from_image(image_path)
    print(f"Extracted food name: {food_name}")  # Debugging 출력 추가
    
    if not food_name:
        return {"error": "Food name could not be extracted."}
    
    prompt_value = prompt_template.invoke({"string": food_name})
    model_output = model.invoke(prompt_value)
    output = output_parser.invoke(model_output)
    output_dict = output  # 이미 딕셔너리 형태로 반환됨
    output_dict["food_name"] = food_name  # 음식 이름을 추가
    print(f"Parsed output: {output_dict}")  # Debugging 출력 추가
    return output_dict