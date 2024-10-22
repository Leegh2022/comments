import streamlit as st
from auth.login import login
from data.database import initialize_db, add_diet, get_diets
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc
from models import Base, Meal
import pandas as pd
import matplotlib.pyplot as plt
import requests  # OpenFoodFacts API 호출을 위한 패키지

# 데이터베이스 초기화
initialize_db()

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''

# 로그인 함수
def handle_login(username):
    success, message = login(username)
    if success:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success(message)
    else:
        st.error(message)

# 로그아웃 함수
def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.experimental_set_query_params(logged_out=True)  # 페이지 새로고침

# OpenFoodFacts API를 사용하여 음식 검색 (캐싱 적용)
@st.cache_data
def search_food(query):
    """
    OpenFoodFacts API를 사용하여 음식 제품을 검색합니다.

    Parameters:
        query (str): 검색어

    Returns:
        list: 검색 결과 목록
    """
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            'search_terms': query,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            '_size': 10  # 검색 결과 수 조정 가능
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        products = data.get('products', [])
        return products
    except requests.exceptions.RequestException as e:
        st.error(f"음식 검색 중 오류가 발생했습니다: {e}")
        return []

# OpenFoodFacts API를 사용하여 특정 제품의 영양소 정보 가져오기 (캐싱 적용)
@st.cache_data
def get_nutrition_info(barcode):
    """
    OpenFoodFacts API를 사용하여 특정 제품의 영양소 정보를 가져옵니다.

    Parameters:
        barcode (str): 제품 바코드

    Returns:
        dict: 영양소 정보
    """
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 1:
            product = data.get('product', {})
            nutriments = product.get('nutriments', {})
            nutrition_info = {
                '칼로리': nutriments.get('energy-kcal_100g', 0),
                '단백질 (g)': nutriments.get('proteins_100g', 0),
                '탄수화물 (g)': nutriments.get('carbohydrates_100g', 0),
                '지방 (g)': nutriments.get('fat_100g', 0)
            }
            return nutrition_info
        else:
            st.error("해당 제품을 찾을 수 없습니다.")
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"제품 정보를 가져오는 중 오류가 발생했습니다: {e}")
        return {}

# 로그인 폼
def login_form():
    st.title("로그인 페이지")
    with st.form(key='login_form'):
        username = st.text_input('사용자 이름')
        submit_button = st.form_submit_button('로그인')
        if submit_button:
            if username.strip() == "":
                st.error("사용자 이름을 입력해주세요.")
            else:
                handle_login(username.strip())

# 식단 입력 폼
def diet_form(username):
    st.header(f"{username}님의 식단 입력")
    with st.form(key='diet_form'):
        diet_content = st.text_area('오늘의 식단 내용을 입력하세요:')
        submit_button = st.form_submit_button('저장')
        if submit_button:
            if diet_content.strip() == "":
                st.error("식단 내용을 입력해주세요.")
            else:
                add_diet(username, diet_content.strip())
                st.success("식단 내용이 저장되었습니다.")

# 식단 내용 조회
def display_diets(username):
    st.header(f"{username}님의 식단 내용")
    diets = get_diets(username)
    if diets:
        for idx, diet in enumerate(diets, start=1):
            st.write(f"{idx}. {diet[0]}")
    else:
        st.info("저장된 식단 내용이 없습니다.")

# 음식 관리 기능
def manage_meals():
    # 데이터베이스 설정
    engine = create_engine('sqlite:///meals.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    # Streamlit 애플리케이션 시작
    st.title("건강 식생활 관리 플랫폼")

    # 섹션: 음식 추가
    st.header("음식 추가")

    # 음식 검색
    search_query = st.text_input("음식 이름을 입력하고 검색하세요:")
    if st.button("검색"):
        if search_query.strip() == "":
            st.error("검색어를 입력해주세요.")
        else:
            with st.spinner("음식 검색 중..."):
                products = search_food(search_query.strip())
                if products:
                    product_names = [product.get('product_name', '이름 없음') for product in products]
                    selected_product = st.selectbox("검색 결과에서 선택하세요:", options=product_names)
                    selected_index = product_names.index(selected_product)
                    selected_product_info = products[selected_index]
                    barcode = selected_product_info.get('code', '')
                    if barcode:
                        nutrition = get_nutrition_info(barcode)
                        st.write(f"**제품 이름:** {selected_product}")
                        st.write(f"**칼로리:** {nutrition.get('칼로리', 0)} kcal")
                        st.write(f"**단백질:** {nutrition.get('단백질 (g)', 0)} g")
                        st.write(f"**탄수화물:** {nutrition.get('탄수화물 (g)', 0)} g")
                        st.write(f"**지방:** {nutrition.get('지방 (g)', 0)} g")
                        add_meal = st.button("이 음식 추가하기")
                        if add_meal:
                            new_meal = Meal(
                                name=selected_product,
                                calories=int(nutrition.get('칼로리', 0)),
                                proteins=int(nutrition.get('단백질 (g)', 0)),
                                carbs=int(nutrition.get('탄수화물 (g)', 0)),
                                fats=int(nutrition.get('지방 (g)', 0))
                            )
                            session.add(new_meal)
                            session.commit()
                            st.success(f"{selected_product}이(가) 추가되었습니다.")
                    else:
                        st.error("선택한 제품을 찾을 수 없습니다.")
    else:
        st.info("음식을 검색하여 추가할 수 있습니다.")

    # 기존 방식으로 음식 추가 (직접 입력)
    with st.form(key='meal_form'):
        st.subheader("직접 음식 정보 입력하기")
        name = st.text_input("음식 이름")
        calories = st.number_input("칼로리 (kcal)", min_value=0)
        proteins = st.number_input("단백질 (g)", min_value=0)
        carbs = st.number_input("탄수화물 (g)", min_value=0)
        fats = st.number_input("지방 (g)", min_value=0)
        submit_button = st.form_submit_button(label='추가')

        if submit_button:
            if name:
                new_meal = Meal(
                    name=name,
                    calories=int(calories),
                    proteins=int(proteins),
                    carbs=int(carbs),
                    fats=int(fats)
                )
                session.add(new_meal)
                session.commit()
                st.success(f"{name}이(가) 추가되었습니다.")
            else:
                st.error("음식 이름을 입력해주세요.")

    # 섹션: 섭취 기록 보기
    st.header("섭취 기록")

    
    # 정렬 기준 선택
    sort_options = {
        "ID": Meal.id,
        "이름": Meal.name,
        "칼로리": Meal.calories,
        "단백질": Meal.proteins,
        "탄수화물": Meal.carbs,
        "지방": Meal.fats
    }
    sort_by = st.selectbox("정렬 기준 선택", options=list(sort_options.keys()))
    sort_order = st.radio("정렬 순서", options=["오름차순", "내림차순"])

    # 선택된 기준에 따라 정렬 및 검색어에 따라 필터링
    query = session.query(Meal)
    if search_query:
        query = query.filter(Meal.name.contains(search_query))

    if sort_order == "오름차순":
        meals = query.order_by(asc(sort_options[sort_by])).all()
    else:
        meals = query.order_by(desc(sort_options[sort_by])).all()

    if meals:
        data = {
            'ID': [meal.id for meal in meals],
            '이름': [meal.name for meal in meals],
            '칼로리': [meal.calories for meal in meals],
            '단백질 (g)': [meal.proteins for meal in meals],
            '탄수화물 (g)': [meal.carbs for meal in meals],
            '지방 (g)': [meal.fats for meal in meals],
        }
        df = pd.DataFrame(data)
        st.dataframe(df)

        # 삭제할 음식 선택
        st.header("음식 삭제")
        meal_id_to_delete = st.number_input("삭제할 음식의 ID를 입력하세요", min_value=1, step=1)
        delete_button = st.button("삭제")

        if delete_button:
            meal_to_delete = session.query(Meal).filter(Meal.id == meal_id_to_delete).first()
            if meal_to_delete:
                session.delete(meal_to_delete)
                session.commit()
                st.success(f"ID {meal_id_to_delete} 음식이 삭제되었습니다.")
            else:
                st.error("해당 ID의 음식을 찾을 수 없습니다.")

        # 섹션: 음식 수정
        st.header("음식 수정")

        meal_id_to_update = st.number_input("수정할 음식의 ID를 입력하세요", min_value=1, step=1)
        meal_to_update = session.query(Meal).filter(Meal.id == meal_id_to_update).first()

        if meal_to_update:
            with st.form(key='update_meal_form'):
                new_name = st.text_input("새 음식 이름", value=meal_to_update.name)
                new_calories = st.number_input("새 칼로리", min_value=0, value=meal_to_update.calories)
                new_proteins = st.number_input("새 단백질 (g)", min_value=0, value=meal_to_update.proteins)
                new_carbs = st.number_input("새 탄수화물 (g)", min_value=0, value=meal_to_update.carbs)
                new_fats = st.number_input("새 지방 (g)", min_value=0, value=meal_to_update.fats)
                update_button = st.form_submit_button(label='수정')

                if update_button:
                    meal_to_update.name = new_name
                    meal_to_update.calories = int(new_calories)
                    meal_to_update.proteins = int(new_proteins)
                    meal_to_update.carbs = int(new_carbs)
                    meal_to_update.fats = int(new_fats)
                    session.commit()
                    st.success(f"ID {meal_id_to_update} 음식이 수정되었습니다.")
        else:
            st.info("해당 ID의 음식을 찾을 수 없습니다.")

        # 통계 섹션
        st.header("영양소 섭취 비율")

        total_calories = sum([meal.calories for meal in meals])
        total_proteins = sum([meal.proteins for meal in meals])
        total_carbs = sum([meal.carbs for meal in meals])
        total_fats = sum([meal.fats for meal in meals])

        stats = {
            '칼로리': total_calories,
            '단백질': total_proteins,
            '탄수화물': total_carbs,
            '지방': total_fats
        }

        # 막대 그래프
        fig, ax = plt.subplots()
        ax.bar(stats.keys(), stats.values(), color=['skyblue', 'orange', 'green', 'red'])
        ax.set_ylabel('그램 (g)')
        ax.set_title('영양소 섭취 비율')
        st.pyplot(fig)
    else:
        st.info("아직 추가된 음식이 없습니다.")

# 메인 애플리케이션 로직
if not st.session_state.logged_in:
    login_form()
else:
    st.sidebar.title("메뉴")
    menu = ["식단 입력", "식단 조회", "식단 관리", "하루 통계", "로그아웃"]
    choice = st.sidebar.selectbox("선택하세요", menu)
    
    if choice == "식단 입력":
        diet_form(st.session_state.username)
    elif choice == "식단 조회":
        display_diets(st.session_state.username)
    elif choice == "식단 관리":
        manage_meals()
    elif choice == "하루 통계":
        # 목표 섭취량 예시 (단위: g)
        target_carbs = 130
        target_proteins = 40
        target_fats = 51

        # 현재 섭취량 예시 (단위: g)
        current_carbs = 0  # 데이터에 따라 변경
        current_proteins = 0  # 데이터에 따라 변경
        current_fats = 0  # 데이터에 따라 변경

        # 전체 칼로리 목표 예시
        total_calories = 1800
        current_calories = 0  # 데이터에 따라 변경

        # Streamlit 페이지 설정
        st.title("하루 통계")

        # 칼로리 원형 게이지 스타일 (대신 텍스트로 표시)
        st.metric(label="칼로리", value=f"{current_calories} / {total_calories} kcal")

        # 탄수화물, 단백질, 지방에 대한 목표 및 진행 상태 표시
        st.write("탄수화물")
        st.progress(current_carbs / target_carbs)

        st.write(f"{current_carbs}g / {target_carbs}g")

        st.write("단백질")
        st.progress(current_proteins / target_proteins)

        st.write(f"{current_proteins}g / {target_proteins}g")

        st.write("지방")
        st.progress(current_fats / target_fats)

        st.write(f"{current_fats}g / {target_fats}g")
    elif choice == "로그아웃":
        handle_logout()