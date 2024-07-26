from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import llm
import calendar
import pymysql
from datetime import datetime
import logging

from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Load environment variables from .env
load_dotenv()

# Define db_config
db_config = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


# Database connection function
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            database=db_config["database"],
            user=db_config["user"],
            password=db_config["password"],
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    print(f"Received login request for user ID: {data.get('id')}")  # 디버깅 메시지

    connection = create_db_connection()
    if connection is None:
        print("Database connection failed")  # 디버깅 메시지
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM USER WHERE ID = %s AND PASSWORD = %s"
        print(f"Executing query: {query}")  # 디버깅 메시지
        cursor.execute(query, (data["id"], data["password"]))
        user = cursor.fetchone()

        if user:
            print(f"Login successful for user: {user['ID']}")  # 디버깅 메시지
            user.pop("PASSWORD", None)
            return jsonify({"message": "Login successful", "user": user}), 200
        else:
            print("Invalid credentials")  # 디버깅 메시지
            return jsonify({"error": "Invalid credentials"}), 401

    except Error as e:
        print(f"Database error occurred: {str(e)}")  # 디버깅 메시지
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed")  # 디버깅 메시지


def insert_test_data():
    print("Inserting test data...")  # 디버깅 메시지

    # 콘솔에서 사용자 입력 받기
    user_id = input("Enter user ID: ")
    user_password = input("Enter user password: ")

    data = {
        "id": user_id,
        "password": user_password,
        "bodyweight": 70,  # 예시 데이터
        "height": 178,  # 예시 데이터
        "age": 30,  # 예시 데이터
    }

    connection = create_db_connection()
    if connection is None:
        print("Database connection failed")
        return

    try:
        cursor = connection.cursor()

        # 아이디 중복 확인
        query = "SELECT * FROM USER WHERE ID = %s"
        cursor.execute(query, (data["id"],))
        existing_user = cursor.fetchone()

        if existing_user:
            print(
                f"User ID {data['id']} already exists. Skipping insertion."
            )  # 디버깅 메시지
        else:
            query = """INSERT INTO USER (ID, PASSWORD, BODY_WEIGHT, HEIGHT, AGE) 
                       VALUES (%s, %s, %s, %s, %s)"""
            values = (
                data["id"],
                data["password"],
                data["bodyweight"],
                data["height"],
                data["age"],
            )
            cursor.execute(query, values)
            connection.commit()
            print("Test user inserted successfully")  # 디버깅 메시지
    except Error as e:
        print(f"An error occurred: {str(e)}")  # 디버깅 메시지
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed")  # 디버깅 메시지


model = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),  # gpt-4o is set by env
    temperature=1.0,
)


class NutritionInfo(BaseModel):
    food_name: str = Field(description="The food name")
    calorie: str = Field(description="The amount of Calories")
    carbohydrate: str = Field(description="The amount of Carbohydrate")
    protein: str = Field(description="The amount of Protein")
    fat: str = Field(description="The amount of Fat")


output_parser = JsonOutputParser(pydantic_object=NutritionInfo)

prompt_template = ChatPromptTemplate.from_template(
    """
    음식이 입력되면 영양정보를 분석해줘
    필수 요소는 음식 이름, 칼로리, 탄수화물, 단백질, 지방이야
    입력: {string}
    
    {format_instructions}
    """
).partial(format_instructions=output_parser.get_format_instructions())


def do(param):
    print(f"Received input: {param}")  # Debugging 출력 추가
    prompt_value = prompt_template.invoke({"string": param})
    model_output = model.invoke(prompt_value)
    output = output_parser.invoke(model_output)
    return output


def save_to_db(user_id, nutrition_info):
    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO FOOD (ID, DATE, FOOD_NAME, FOOD_PT, FOOD_FAT, FOOD_CH, FOOD_KCAL)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    user_id,
                    datetime.now(),
                    nutrition_info["food_name"],
                    nutrition_info["protein"],
                    nutrition_info["fat"],
                    nutrition_info["carbohydrate"],
                    nutrition_info["calorie"],
                ),
            )
            print("Data saved to database")  # Debugging 출력 추가
        connection.commit()
    finally:
        connection.close()


@app.route("/api/send", methods=["POST"])
def send():
    data = request.json
    user_id = data.get("user_id")
    food_name = data.get("food_name")

    if not user_id or not food_name:
        return jsonify({"error": "user_id and food_name are required"}), 400

    nutrition_info = do(food_name)

    # save_to_db(user_id, nutrition_info)

    return jsonify(nutrition_info)


@app.route("/api/send2", methods=["POST"])
def send2():
    data = request.json
    user_id = data.get("user_id")
    nutrition_info = data.get("nutrition_info")
    print(data)
    try:
        save_to_db(user_id, nutrition_info)
        return jsonify({"message": "good"}), 200
    except:
        return jsonify({"message": "DB save error"}), 500


@app.route("/api/add_food", methods=["POST"])
def add_food():
    data = request.json

    user_id = data.get("ID")
    date = data.get("DATE")
    food_name = data.get("FOOD_NAME")

    if not user_id or not date or not food_name:
        return jsonify({"error": "필수 정보가 누락되었습니다."}), 400

    # LLM을 통해 음식 영양 정보를 가져옴
    nutrition_info = do(food_name)

    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # FOOD_INDEX를 구함 (해당 날짜의 가장 높은 인덱스를 찾아 +1)
            cursor.execute(
                "SELECT MAX(FOOD_INDEX) FROM FOOD WHERE ID = %s AND DATE = %s",
                (user_id, date),
            )
            max_index = cursor.fetchone()[0]
            food_index = max_index + 1 if max_index is not None else 0

            insert_query = """
            INSERT INTO FOOD (ID, DATE, FOOD_INDEX, FOOD_NAME, FOOD_CH, FOOD_PT, FOOD_FAT, FOOD_KCAL)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                insert_query,
                (
                    user_id,
                    date,
                    food_index,
                    nutrition_info["food_name"],
                    nutrition_info["carbohydrate"],
                    nutrition_info["protein"],
                    nutrition_info["fat"],
                    nutrition_info["calorie"],
                ),
            )
            connection.commit()

            added_food_info = {
                "ID": user_id,
                "DATE": date,
                "FOOD_INDEX": food_index,
                "food_name": nutrition_info["food_name"],
                "carbohydrates": nutrition_info["carbohydrate"],
                "protein": nutrition_info["protein"],
                "fat": nutrition_info["fat"],
                "calorie": nutrition_info["calorie"],
            }
            print(added_food_info)
            return (
                jsonify(
                    {
                        "message": "음식이 성공적으로 추가되었습니다.",
                        "data": added_food_info,
                    }
                ),
                201,
            )

    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()


@app.route("/api/update_food", methods=["POST"])
def update_food():
    data = request.json

    user_id = data.get("ID")
    date = data.get("DATE")
    food_index = data.get("FOOD_INDEX")
    new_food_name = data.get("NEW_FOOD_NAME")

    if not user_id or not date or not food_index or not new_food_name:
        return jsonify({"error": "필수 정보가 누락되었습니다."}), 400

    # LLM을 통해 새로운 음식 영양 정보를 가져옴
    new_nutrition_info = do(new_food_name)

    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            update_query = """
            UPDATE FOOD
            SET FOOD_NAME = %s, FOOD_CH = %s, FOOD_PT = %s, FOOD_FAT = %s, FOOD_KCAL = %s
            WHERE ID = %s AND DATE = %s AND FOOD_INDEX = %s
            """
            cursor.execute(
                update_query,
                (
                    new_nutrition_info["food_name"],
                    new_nutrition_info["carbohydrate"],
                    new_nutrition_info["protein"],
                    new_nutrition_info["fat"],
                    new_nutrition_info["calorie"],
                    user_id,
                    date,
                    food_index,
                ),
            )
            connection.commit()

            updated_food_info = {
                "ID": user_id,
                "DATE": date,
                "FOOD_INDEX": food_index,
                "food_name": new_nutrition_info["food_name"],
                "carbohydrates": new_nutrition_info["carbohydrate"],
                "protein": new_nutrition_info["protein"],
                "fat": new_nutrition_info["fat"],
                "calorie": new_nutrition_info["calorie"],
            }

            return (
                jsonify(
                    {
                        "message": "음식이 성공적으로 수정되었습니다.",
                        "data": updated_food_info,
                    }
                ),
                200,
            )

    except pymysql.MySQLError as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()


@app.route("/api/register", methods=["GET", "POST", "PUT"])
def register():
    if request.method == "GET":
        user_id = request.args.get("id")
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        print(1)
        connection = create_db_connection()
        if connection is None:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            print(2)
            cursor = connection.cursor()
            query_nutrients = (
                """SELECT RD_PROTEIN1, RD_CARBO1, RD_FAT1 FROM USER WHERE ID=%s"""
            )
            cursor.execute(query_nutrients, (user_id,))
            nutrients_result = cursor.fetchone()
            print(3)

            if nutrients_result is None:
                return jsonify({"error": "User NT not found"}), 404
            print(4)
            rd_protein, rd_carbo, rd_fat = nutrients_result
            return (
                jsonify(
                    {
                        "RD_PROTEIN1": rd_protein,
                        "RD_CARBO1": rd_carbo,
                        "RD_FAT1": rd_fat,
                    }
                ),
                200,
            )
        except Error as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Database query failed"}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    data = request.json

    if not data or "id" not in data or "pw" not in data:
        return jsonify({"error": "Invalid input"}), 400

    connection = create_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = connection.cursor()

        if request.method == "PUT":
            query_user = """UPDATE USER SET PASSWORD=%s, BODY_WEIGHT=%s, HEIGHT=%s, AGE=%s, ACTIVITY=%s WHERE ID=%s"""
            values_user = (
                data["pw"],
                data["bodyweight"],
                data["height"],
                data["age"],
                data["activity"],
                data["id"],
            )
            cursor.execute(query_user, values_user)

            query_nt = """UPDATE USER SET RD_PROTEIN1=%s, RD_CARBO1=%s, RD_FAT1=%s WHERE ID=%s"""
            values_nt = (
                data["rd_protein"],
                data["rd_carbo"],
                data["rd_fat"],
                data["id"],
            )
            cursor.execute(query_nt, values_nt)
        else:
            query_user = """INSERT INTO USER (ID, PASSWORD, BODY_WEIGHT, HEIGHT, AGE, GENDER, ACTIVITY, RDI) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            values_user = (
                data["id"],
                data["pw"],
                data["bodyweight"],
                data["height"],
                data["age"],
                data["gender"],
                data["activity"],
                None,  # RDI 값을 기본값으로 설정 (필요에 따라 계산 후 설정 가능)
            )
            cursor.execute(query_user, values_user)

            query_nt = """INSERT INTO USER (ID, RD_PROTEIN1, RD_CARBO1, RD_FAT1) 
                          VALUES (%s, %s, %s, %s)"""
            values_nt = (
                data["id"],
                data["rd_protein"],
                data["rd_carbo"],
                data["rd_fat"],
            )
            cursor.execute(query_nt, values_nt)

        connection.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Error as e:
        print(f"Database query error: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# 특정 음식을 삭제하는 엔드포인트
@app.route("/api/delete_food", methods=["DELETE"])
def delete_food():
    user_id = request.args.get("ID")
    date = request.args.get("DATE")
    food_index = request.args.get("FOOD_INDEX")

    if not user_id or not date or not food_index:
        return jsonify({"error": "필수 정보가 누락되었습니다."}), 400

    connection = create_db_connection()
    if connection is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    try:
        cursor = connection.cursor()
        delete_query = """
        DELETE FROM FOOD
        WHERE ID = %s AND DATE = %s AND FOOD_INDEX = %s
        """
        cursor.execute(delete_query, (user_id, date, food_index))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "삭제할 데이터가 없습니다."}), 404

        return jsonify({"message": "음식이 성공적으로 삭제되었습니다."}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route("/api/monthly", methods=["POST"])
def get_monthly_food():
    data = request.json
    year = data.get("year")
    month = data.get("month")
    UID = data.get("UID")
    if not year or not month:
        return jsonify({"error": "Year and month are required"}), 400

    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT DATE, FOOD_INDEX, FOOD_NAME, FOOD_PT, FOOD_FAT, FOOD_CH, FOOD_KCAL
                FROM FOOD
                WHERE YEAR(DATE) = %s AND MONTH(DATE) = %s
                AND ID = %s
                ORDER BY DATE
            """
            cursor.execute(sql, (year, month, UID))
            results = cursor.fetchall()
            monthly_data = {}

            for row in results:
                day = row[0].day
                food_info = {
                    "food_index": row[1],
                    "food_name": row[2],
                    "protein": row[3],
                    "fat": row[4],
                    "carbohydrates": row[5],
                    "calories": row[6],
                }

                # Ensuring the output order
                food_info_ordered = {
                    "food_index": food_info["food_index"],
                    "food_name": food_info["food_name"],
                    "protein": food_info["protein"],
                    "fat": food_info["fat"],
                    "carbohydrates": food_info["carbohydrates"],
                    "calories": food_info["calories"],
                }

                if day not in monthly_data:
                    monthly_data[day] = []

                monthly_data[day].append(food_info_ordered)

            # Create a list of 31 days, each day is a list of food items (which may be empty)
            grouped_data = [monthly_data.get(day, []) for day in range(1, 32)]

            return jsonify(grouped_data)
    finally:
        connection.close()


def get_user_nutritional_needs(user_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT BODY_WEIGHT, RDI FROM USER WHERE ID = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            if result:
                body_weight, rdi = result
                return body_weight, rdi
            else:
                return None
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        connection.close()


def get_daily_totals(user_id, date):

    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT CARBO, PROTEIN, FAT, RD_CARBO, RD_PROTEIN, RD_FAT FROM USER_NT WHERE ID = %s AND DATE = %s"
            cursor.execute(sql, (user_id, date))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return None
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        connection.close()


def get_monthly_data(year, month, user_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT DATE, FOOD_INDEX, FOOD_NAME, FOOD_PT, FOOD_FAT, FOOD_CH, FOOD_KCAL
                FROM FOOD
                WHERE YEAR(DATE) = %s AND MONTH(DATE) = %s AND ID = %s
                ORDER BY DATE
            """
            cursor.execute(sql, (year, month, user_id))
            results = cursor.fetchall()

            num_days = calendar.monthrange(year, month)[1]  # 해당 월의 일수 계산
            foods_list = [[] for _ in range(num_days)]  # 각 날짜별 음식 리스트
            percentages_list = [{} for _ in range(num_days)]  # 각 날짜별 백분율 리스트

            for row in results:
                day = row[0].day - 1  # 0-based index for lists
                food_info = {
                    "food_index": row[1],
                    "food_name": row[2],
                    "protein": row[3],
                    "fat": row[4],
                    "carbohydrates": row[5],
                    "calories": row[6],
                }
                foods_list[day].append(food_info)

            # Add daily percentages
            for day in range(num_days):
                date_str = f"{year}-{str(month).zfill(2)}-{str(day+1).zfill(2)}"  # 1-based day for dates
                daily_totals = get_daily_totals(user_id, date_str)
                if daily_totals:
                    (
                        carb_total,
                        protein_total,
                        fat_total,
                        rd_carb,
                        rd_protein,
                        rd_fat,
                    ) = daily_totals
                    percentages_list[day] = {
                        "carbohydrates_percentage": (
                            round((carb_total / rd_carb) * 100, 1) if rd_carb > 0 else 0
                        ),
                        "protein_percentage": (
                            round((protein_total / rd_protein) * 100, 1)
                            if rd_protein > 0
                            else 0
                        ),
                        "fat_percentage": (
                            round((fat_total / rd_fat) * 100, 1) if rd_fat > 0 else 0
                        ),
                    }

            return {"foods": foods_list, "percentages": percentages_list}
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return {"error": "Database error"}
    finally:
        connection.close()


def get_user_nutritional_needs(user_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT BODY_WEIGHT, RDI FROM USER WHERE ID = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            if result:
                body_weight, rdi = result
                return body_weight, rdi
            else:
                return None
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        connection.close()


def get_daily_totals(user_id, date):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT CARBO, PROTEIN, FAT, RD_CARBO, RD_PROTEIN, RD_FAT FROM USER_NT WHERE ID = %s AND DATE = %s"
            cursor.execute(sql, (user_id, date))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return None
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        connection.close()


def get_monthly_data(year, month, user_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT DATE, FOOD_INDEX, FOOD_NAME, FOOD_PT, FOOD_FAT, FOOD_CH, FOOD_KCAL
                FROM FOOD
                WHERE YEAR(DATE) = %s AND MONTH(DATE) = %s AND ID = %s
                ORDER BY DATE
            """
            cursor.execute(sql, (year, month, user_id))
            results = cursor.fetchall()

            num_days = calendar.monthrange(year, month)[1]  # 해당 월의 일수 계산
            foods_list = [[] for _ in range(num_days)]  # 각 날짜별 음식 리스트
            percentages_list = [{} for _ in range(num_days)]  # 각 날짜별 백분율 리스트

            for row in results:
                day = row[0].day - 1  # 0-based index for lists
                food_info = {
                    "food_index": row[1],
                    "food_name": row[2],
                    "protein": row[3],
                    "fat": row[4],
                    "carbohydrates": row[5],
                    "calories": row[6],
                }
                foods_list[day].append(food_info)

            # Add daily percentages
            for day in range(num_days):
                date_str = f"{year}-{str(month).zfill(2)}-{str(day+1).zfill(2)}"  # 1-based day for dates
                daily_totals = get_daily_totals(user_id, date_str)

                if daily_totals:
                    (
                        carb_total,
                        protein_total,
                        fat_total,
                        rd_carb,
                        rd_protein,
                        rd_fat,
                    ) = daily_totals
                    logging.debug(
                        f"Daily Totals for {date_str}: {carb_total}, {protein_total}, {fat_total}, {rd_carb}, {rd_protein}, {rd_fat}"
                    )

                    percentages_list[day] = {
                        "carbohydrates_percentage": (
                            round((carb_total / rd_carb) * 100, 1) if rd_carb > 0 else 0
                        ),
                        "protein_percentage": (
                            round((protein_total / rd_protein) * 100, 1)
                            if rd_protein > 0
                            else 0
                        ),
                        "fat_percentage": (
                            round((fat_total / rd_fat) * 100, 1) if rd_fat > 0 else 0
                        ),
                    }

            return {"foods": foods_list, "percentages": percentages_list}
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return {"error": "Database error"}
    finally:
        connection.close()


@app.route("/api/food/quarterly", methods=["POST"])
def get_quarterly_food():
    data = request.json
    year = data.get("year")
    start_month = data.get("month")
    user_id = data.get("UID")

    if not year or not start_month or not user_id:
        return jsonify({"error": "Year, start month, and user_id are required"}), 400

    try:
        year = int(year)
        start_month = int(start_month)
        if start_month < 1 or start_month > 12:
            return (
                jsonify(
                    {"error": "Invalid month. Please enter a value between 1 and 12."}
                ),
                400,
            )
    except ValueError:
        return jsonify({"error": "Year and month must be integers."}), 400

    quarterly_data = {}
    for i in range(-1, 2):  # 이전 달, 현재 달, 다음 달 순서로 데이터를 가져오기
        month = (start_month + i - 1) % 12 + 1
        current_year = year + (start_month + i - 1) // 12
        monthly_data = get_monthly_data(current_year, month, user_id)
        quarterly_data[f"{current_year}-{str(month).zfill(2)}"] = monthly_data

    return jsonify(quarterly_data)


def get_advice(carbohydrates_percentage, protein_percentage, fat_percentage):
    try:
        # Chat API 호출
        messages = [
            SystemMessage(
                content="You are a nutrition expert providing dietary advice based on user's nutrient intake.Give 5 sentences of advice in Korean"
            ),
            HumanMessage(
                content=f"Here are my monthly nutrient intake percentages:\n"
                f"Carbohydrates: {carbohydrates_percentage}%\n"
                f"Protein: {protein_percentage}%\n"
                f"Fat: {fat_percentage}%\n"
                f"Please provide advice on how to improve my diet"
            ),
        ]

        response = model(messages)

        # 응답 객체의 내용을 로그로 출력
        logging.debug(f"LLM Response Object: {response}")

        # 응답 내용을 추출
        response_content = (
            response[0].content if isinstance(response, list) else response.content
        )
        logging.debug(
            f"LLM Response Content: {response_content}"
        )  # LLM 응답을 콘솔에 출력
        return response_content
    except Exception as e:
        logging.error(f"Error in get_advice: {e}")
        logging.debug(
            f"Carbohydrates: {carbohydrates_percentage}, Protein: {protein_percentage}, Fat: {fat_percentage}"
        )  # 입력 데이터 디버깅
        return {"error": f"Failed to get advice from LLM: {str(e)}"}


@app.route("/api/food/advice", methods=["POST"])
def get_advice_route():
    data = request.json
    year = data.get("year")
    month = data.get("month")
    user_id = data.get("UID")
    if not year or not month or not user_id:
        return jsonify({"error": "Year, month, and user_id are required"}), 400

    try:
        year = int(year)
        month = int(month)

        if month < 1 or month > 12:
            return (
                jsonify(
                    {"error": "Invalid month. Please enter a value between 1 and 12."}
                ),
                400,
            )
    except ValueError:
        return jsonify({"error": "Year and month must be integers."}), 400

    # 현재 달의 데이터를 가져옵니다
    monthly_data = get_monthly_data(year, month, user_id)

    if "error" in monthly_data:
        logging.error(f"Failed to get monthly data: {monthly_data['error']}")
        return jsonify(monthly_data), 500
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    # print(monthly_data)
    percentages_list = monthly_data["percentages"]

    # 한 달치 평균 계산
    total_carbs = 0
    total_protein = 0
    total_fat = 0
    count = 0
    # print("###################################")
    # print(percentages_list)
    for day_data in percentages_list:
        if day_data:  # 빈 데이터는 건너뜀
            total_carbs += day_data.get("carbohydrates_percentage", 0)
            total_protein += day_data.get("protein_percentage", 0)
            total_fat += day_data.get("fat_percentage", 0)
            count += 1

    if count == 0:
        logging.error("No valid data to calculate averages")
        return jsonify({"error": "No valid data to calculate averages"}), 404
    print(2)

    average_carbs = total_carbs / count
    average_protein = total_protein / count
    average_fat = total_fat / count

    averages = {
        "average_carbohydrates_percentage": round(average_carbs, 1),
        "average_protein_percentage": round(average_protein, 1),
        "average_fat_percentage": round(average_fat, 1),
    }
    print(3)

    # LLM을 통해 조언을 받습니다
    advice = get_advice(
        averages["average_carbohydrates_percentage"],
        averages["average_protein_percentage"],
        averages["average_fat_percentage"],
    )
    print(4)

    # 콘솔에 출력
    logging.debug(f"LLM Advice: {advice}")

    return jsonify({"averages": averages, "advice": advice})


def get_user_nutritional_needs(user_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT BODY_WEIGHT, RDI FROM USER WHERE ID = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            if result:
                body_weight, rdi = result
                return body_weight, rdi
            else:
                return None
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        connection.close()


def get_daily_totals(user_id, date):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT CARBO, PROTEIN, FAT, RD_CARBO, RD_PROTEIN, RD_FAT FROM USER_NT WHERE ID = %s AND DATE = %s"
            cursor.execute(sql, (user_id, date))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return None
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        connection.close()


def get_foods_by_date(year, month, day, user_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT DATE, FOOD_INDEX, FOOD_NAME, FOOD_PT, FOOD_FAT, FOOGD_CH, FOOD_KCAL
                FROM FOOD
                WHERE YEAR(DATE) = %s AND MONTH(DATE) = %s AND DAY(DATE) = %s AND ID = %s
                ORDER BY DATE
            """
            cursor.execute(sql, (year, month, day, user_id))
            results = cursor.fetchall()
            foods_list = []  # 특정 날짜의 음식 리스트
            percentages = {
                "carbohydrates_percentage": 0,
                "protein_percentage": 0,
                "fat_percentage": 0,
            }  # 기본값 0으로 설정

            for row in results:
                food_info = {
                    "food_index": row[1],
                    "food_name": row[2],
                    "protein": row[3],
                    "fat": row[4],
                    "carbohydrates": row[5],
                    "calories": row[6],
                }
                foods_list.append(food_info)

            # Add daily percentages
            date_str = (
                f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"  # 날짜 문자열
            )
            daily_totals = get_daily_totals(user_id, date_str)
            if daily_totals:
                carb_total, protein_total, fat_total, rd_carb, rd_protein, rd_fat = (
                    daily_totals
                )
                percentages = {
                    "carbohydrates_percentage": (
                        round((carb_total / rd_carb) * 100, 1) if rd_carb > 0 else 0
                    ),
                    "protein_percentage": (
                        round((protein_total / rd_protein) * 100, 1)
                        if rd_protein > 0
                        else 0
                    ),
                    "fat_percentage": (
                        round((fat_total / rd_fat) * 100, 1) if rd_fat > 0 else 0
                    ),
                }

            return {"foods": foods_list, "percentages": percentages}
    except pymysql.MySQLError as e:
        logging.error(f"Database error: {e}")
        return {"error": "Database error"}
    finally:
        connection.close()


@app.route("/api/food/get_day", methods=["POST"])
def get_day_food():
    data = request.json
    year = data.get("year")
    month = data.get("month")
    day = data.get("day")
    user_id = data.get("UID")
    print(data)
    if not year or not month or not day or not user_id:
        return jsonify({"error": "Year, month, day, and user_id are required"}), 400
    print(00)
    try:
        year = int(year)
        month = int(month)
        day = int(day)
        print(year, month, day)
        if month < 1 or month > 12 or day < 1 or day > 31:
            return (
                jsonify({"error": "Invalid month or day. Please enter valid values."}),
                400,
            )
    except ValueError:
        return jsonify({"error": "Year, month, and day must be integers."}), 400

    daily_data = get_foods_by_date(year, month, day, user_id)
    if "error" in daily_data:
        logging.error(f"Failed to get daily data: {daily_data['error']}")
        return jsonify(daily_data), 500

    return jsonify(daily_data)


if __name__ == "__main__":
    print("Starting Flask application")  # 디버깅 메시지
    # insert_test_data()  # 애플리케이션 시작 시 테스트 데이터 삽입
    app.run(host="0.0.0.0", port=5000)
