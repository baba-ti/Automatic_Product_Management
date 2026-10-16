import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
import os
import random
import json
import uuid
from datetime import datetime, timedelta
import hashlib
import calendar
from faker import Faker
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
fake = Faker('ko_KR')  # Korean locale
DATABASE_URL= os.getenv("SUPABASE_DATABASE_URL")

small_llm = ChatOpenAI(
    model="gpt-6-luna",
    reasoning_effort="none",  
    temperature=0,         
)

# # Initialize Azure OpenAI for generating realistic Korean text
# small_llm = AzureChatOpenAI(
#     azure_deployment='gpt-4.1-mini',
#     api_version='2024-08-01-preview',
#     streaming=False,
# )

class KoreanEcommerceDataGenerator:
    def __init__(self, start_date, end_date):
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Korean data lists - Expanded for more unique combinations
        self.korean_surnames = [
            '김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전',
            '홍', '고', '문', '양', '손', '배', '조', '백', '허', '유', '남', '심', '노', '정', '하', '곽', '성', '차', '주', '우',
            '구', '신', '임', '나', '전', '민', '유', '진', '지', '엄', '채', '원', '천', '방', '공', '강', '현', '함', '변', '염'
        ]
        self.korean_given_names = [
            '민수', '영희', '철수', '순영', '지훈', '수진', '동현', '미영', '성민', '혜진', '현우', '소영', '준호', '은지', '태현', '유진', '승호', '나영', '정우', '하늘',
            '서연', '도윤', '예준', '시우', '하준', '주원', '지호', '지우', '준서', '건우', '현준', '민준', '서준', '예원', '지민', '서현', '수빈', '지원', '채원', '다은',
            '은서', '소율', '지안', '윤서', '시연', '채은', '하은', '유나', '서영', '예린', '수연', '가은', '나윤', '다인', '하린', '소은', '예나', '주하', '서윤', '민서'
        ]
        
        self.seoul_districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', 
            '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
            '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        self.korean_cities = [
            '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시',
            '울산광역시', '경기도', '강원도', '충청북도', '충청남도', '전라북도', '전라남도',
            '경상북도', '경상남도', '제주특별자치도'
        ]
        
        self.product_categories = [
            '전자제품', '의류', '신발', '가방', '화장품', '식품', '도서', '스포츠용품', 
            '가구', '생활용품', '주방용품', '문구용품', '완구', '건강용품', '자동차용품'
        ]
        
        self.product_names = {
            '전자제품': ['갤럭시 스마트폰', 'LG 노트북', '삼성 태블릿', '애플 아이패드', 'LG 모니터', '삼성 TV', '소니 이어폰', 'JBL 스피커'],
            '의류': ['유니클로 셔츠', '자라 원피스', 'H&M 청바지', '무신사 후드티', '스파오 티셔츠', '탑텐 슬랙스', '코오롱 점퍼', '빈폴 코트'],
            '신발': ['나이키 운동화', '아디다스 스니커즈', '컨버스 올스타', '반스 슬립온', '뉴발란스 러닝화', '퓨마 농구화', '리복 크로스핏', '호카 등산화'],
            '가방': ['에르메스 핸드백', '루이비통 지갑', '구찌 백팩', '샤넬 숄더백', '프라다 토트백', '버버리 크로스백', '코치 클러치', '마이클코어스 파우치'],
            '화장품': ['설화수 스킨케어 세트', '에스티로더 파운데이션', '랑콤 립스틱', '클라란스 아이크림', '이니스프리 마스크팩', '에뛰드 틴트', '더페이스샵 클렌저', 'too cool for school BB크림'],
            '식품': ['백설 쌀', '오뚜기 라면', '농심 과자', '롯데 초콜릿', 'CJ 냉동식품', '풀무원 두부', '동원 참치', '오리온 비스킷'],
            '도서': ['해리포터 시리즈', '어린왕자', '데미안', '노르웨이의 숲', '1984', '위대한 개츠비', '호밀밭의 파수꾼', '백년의 고독'],
            '스포츠용품': ['윌슨 테니스 라켓', '미즈노 야구 글러브', '몰텐 농구공', '아디다스 축구공', '요넥스 배드민턴 라켓', '던롭 골프공', '나이키 요가매트', '리복 덤벨'],
            '가구': ['이케아 책상', '한샘 의자', '리바트 침대', '시디즈 책상의자', '에몬스 소파', '현대리바트 식탁', '일룸 옷장', '카리모쿠 원목가구'],
            '생활용품': ['LG 세탁기', '삼성 냉장고', '다이슨 청소기', '쿠쿠 밥솥', '위닉스 공기청정기', '브라운 면도기', '오스터 믹서기', '테팔 후라이팬'],
            '주방용품': ['테팔 후라이팬', '쿠쿠 밥솥', '필립스 에어프라이어', '브라운 믹서기', '키친에이드 스탠드믹서', '르크루제 냄비', '스테들러 칼세트', '옥소 도마'],
            '문구용품': ['모나미 볼펜', '제브라 샤프', '스테들러 연필', '유니 지우개', '3M 포스트잇', '아트박스 노트', '알파 계산기', '펜텔 마커'],
            '완구': ['레고 블록', '바비 인형', '토미카 자동차', '포켓몬 피규어', '뽀로로 장난감', '타요 버스', '헬로키티 인형', '변신로봇'],
            '건강용품': ['오메가3', '비타민C', '프로틴 파우더', '홍삼 진액', '유산균', '루테인', '마그네슘', '콜라겐'],
            '자동차용품': ['블랙박스', '네비게이션', '카매트', '방향제', '핸드폰 거치대', '충전기', '선팅필름', '타이어']
        }
        
        self.support_subjects = [
            '주문 배송 문의', '상품 불량 신고', '반품 요청', '교환 문의', '결제 오류', 
            '배송지 변경 요청', '상품 사용법 문의', '할인쿠폰 사용 문의', '회원가입 문제', '로그인 오류'
        ]
        
        self.support_descriptions = [
            '주문한 상품이 아직 배송되지 않았습니다. 확인 부탁드립니다.',
            '받은 상품에 불량이 있어서 교환을 요청드립니다.',
            '사이즈가 맞지 않아 반품하고 싶습니다.',
            '다른 색상으로 교환 가능한가요?',
            '결제가 두 번 처리된 것 같습니다.',
            '배송지를 변경하고 싶은데 가능한가요?',
            '상품 사용법을 알고 싶습니다.',
            '할인쿠폰이 적용되지 않습니다.',
            '회원가입이 되지 않습니다.',
            '비밀번호를 잊어버렸습니다.'
        ]

    def random_date_between(self):
        """Generate random date between start_date and end_date"""
        delta = self.end_date - self.start_date
        random_days = random.randint(0, delta.days)
        return self.start_date + timedelta(days=random_days)

    def random_datetime_between(self):
        """Generate random datetime between start_date and end_date"""
        random_date = self.random_date_between()
        random_time = random.randint(0, 24*60*60-1)  # seconds in a day
        return datetime.combine(random_date, datetime.min.time()) + timedelta(seconds=random_time)

    def generate_korean_name(self, counter=None):
        """Generate realistic Korean name with optional counter for uniqueness"""
        surname = random.choice(self.korean_surnames)
        given_name = random.choice(self.korean_given_names)
        base_name = surname + given_name
        
        if counter is not None:
            # Add numeric suffix for guaranteed uniqueness
            return f"{base_name}{counter}"
        return base_name

    def generate_korean_address(self):
        """Generate realistic Korean address"""
        if random.random() < 0.6:  # 60% chance for Seoul address
            city = '서울특별시'
            district = random.choice(self.seoul_districts)
            street_num = random.randint(1, 999)
            building_num = random.randint(1, 50)
            street_address = f'{district} {fake.street_name()} {street_num}-{building_num}'
        else:
            city = random.choice(self.korean_cities)
            district = f'{fake.city()}시' if '도' in city else f'{fake.city()}구'
            street_num = random.randint(1, 999)
            building_num = random.randint(1, 50)
            street_address = f'{district} {fake.street_name()} {street_num}-{building_num}'
        
        postal_code = fake.postcode()
        return street_address, city, district, postal_code

    def generate_korean_review_text(self, rating, product_name):
        """Generate realistic Korean review text using LLM based on rating"""
        try:
            prompt = f"""당신은 한국 온라인 쇼핑몰의 실제 고객입니다. 
            제품명: {product_name}
            평점: {rating}점 (5점 만점)
            
            이 제품에 대한 자연스럽고 실제 고객이 쓸 법한 한국어 리뷰를 작성해주세요.
            - 평점에 맞는 감정과 의견을 표현하세요
            - 2-3문장 정도로 작성하세요
            - 실제 쇼핑몰 리뷰처럼 자연스럽게 작성하세요
            - 리뷰 내용만 반환하고 다른 설명은 하지 마세요"""
            
            response = small_llm.invoke(prompt)
            return response.content.strip()
        
        except Exception as e:
            print(f"❌ Error generating review with LLM: {e}")
            # Fallback to predefined reviews
            if rating >= 4:
                return f"{product_name} 정말 만족스럽습니다. 품질이 좋아요!"
            elif rating == 3:
                return f"{product_name} 평범한 편이에요. 나쁘지는 않습니다."
            else:
                return f"{product_name} 기대에 못 미쳤어요. 실망스럽습니다."

    def generate_support_ticket_description(self, subject, product_name=None):
        """Generate realistic Korean support ticket description using LLM"""
        try:
            if product_name:
                prompt = f"""당신은 한국 온라인 쇼핑몰의 실제 고객입니다.
                구매한 상품: {product_name}
                문의 제목: {subject}
                
                이 상품과 관련해서 위 제목에 해당하는 자연스러운 고객 문의글을 한국어로 작성해주세요.
                - 실제 고객이 쓸 법한 자연스러운 문체로 작성하세요
                - 3-4문장 정도로 작성하세요
                - 구체적인 상황을 포함해주세요
                - 문의 내용만 반환하고 다른 설명은 하지 마세요"""
            else:
                prompt = f"""당신은 한국 온라인 쇼핑몰의 실제 고객입니다.
                문의 제목: {subject}
                
                위 제목에 해당하는 자연스러운 고객 문의글을 한국어로 작성해주세요.
                - 실제 고객이 쓸 법한 자연스러운 문체로 작성하세요
                - 3-4문장 정도로 작성하세요
                - 구체적인 상황을 포함해주세요
                - 문의 내용만 반환하고 다른 설명은 하지 마세요"""
            
            response = small_llm.invoke(prompt)
            return response.content.strip()
        
        except Exception as e:
            print(f"❌ Error generating support ticket with LLM: {e}")
            # Fallback to predefined descriptions
            return random.choice(self.support_descriptions)

    def generate_unique_product_name(self, category, attempt=0):
        """Generate unique product name with variations"""
        base_products = self.product_names[category]
        base_name = random.choice(base_products)
        
        # Add variations to create unique names
        variations = [
            f"{base_name} 프리미엄",
            f"{base_name} 플러스",
            f"{base_name} 에디션",
            f"{base_name} 2024",
            f"{base_name} 스페셜",
            f"{base_name} 디럭스",
            f"{base_name} 라이트",
            f"{base_name} 프로",
            f"{base_name} 울트라",
            f"{base_name} 맥스",
            f"신상품 {base_name}",
            f"한정판 {base_name}",
            f"베스트셀러 {base_name}",
            f"인기 {base_name}",
            f"추천 {base_name}"
        ]
        
        if attempt == 0:
            # First try the base name
            return base_name
        elif attempt <= len(variations):
            # Try variations
            return variations[attempt - 1]
        else:
            # Generate with random numbers/colors/sizes
            colors = ['블랙', '화이트', '그레이', '네이비', '브라운', '레드', '블루', '그린']
            sizes = ['S', 'M', 'L', 'XL', '슬림', '레귤러', '와이드']
            numbers = ['V1', 'V2', 'V3', 'MK-1', 'MK-2', 'Gen2', 'Neo']
            
            modifier = random.choice(colors + sizes + numbers)
            return f"{base_name} {modifier} ({attempt})"

    def generate_product_description(self, product_name, category):
        """Generate realistic Korean product description using LLM"""
        try:
            prompt = f"""당신은 한국 온라인 쇼핑몰의 상품 기획자입니다.
            상품명: {product_name}
            카테고리: {category}
            
            이 상품에 대한 자연스럽고 매력적인 한국어 상품 설명을 작성해주세요.
            - 고객이 구매하고 싶어할 만한 매력적인 설명으로 작성하세요
            - 2-3문장 정도로 작성하세요
            - 상품의 특징과 장점을 포함해주세요
            - 상품 설명만 반환하고 다른 내용은 포함하지 마세요"""
            
            response = small_llm.invoke(prompt)
            return response.content.strip()
        
        except Exception as e:
            print(f"❌ Error generating product description with LLM: {e}")
            # Fallback to simple description
            return f'{product_name} - 고품질 {category} 상품입니다.'

    def check_existing_data(self, cursor):
        """Check what data already exists in the database"""
        existing_counts = {}
        
        tables_to_check = ['categories', 'users', 'addresses', 'products', 'inventory', 'cs_agents', 'orders', 'order_items', 'support_tickets', 'reviews']
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                existing_counts[table] = count
                if count > 0:
                    print(f"  📊 {table}: {count}개 기존 데이터 발견")
            except Exception as e:
                print(f"  ⚠️ {table} 테이블 확인 실패: {e}")
                existing_counts[table] = 0
                
        return existing_counts

    def safe_batch_insert(self, cursor, query, batch_data, batch_name="데이터"):
        """Safely insert batch data with duplicate key handling"""
        try:
            cursor.executemany(query, batch_data)
            return True
        except Exception as e:
            if "duplicate key value" in str(e).lower() or "unique constraint" in str(e).lower():
                print(f"  ⚠️ {batch_name} 배치에서 중복 키 감지, 개별 삽입으로 전환...")
                # Try inserting each row individually
                success_count = 0
                # Convert executemany query to single execute query
                single_query = query.replace("executemany", "execute") if "executemany" in query else query
                
                for row_data in batch_data:
                    try:
                        cursor.execute(single_query, row_data)
                        success_count += 1
                    except Exception as row_error:
                        if "duplicate key value" not in str(row_error).lower() and "unique constraint" not in str(row_error).lower():
                            print(f"    ❌ 개별 행 삽입 실패: {row_error}")
                        # Continue with next row even if this one fails
                        continue
                print(f"  ✅ {batch_name} 배치 중 {success_count}/{len(batch_data)}개 성공적으로 삽입")
                return True
            else:
                print(f"  ❌ {batch_name} 배치 삽입 실패: {e}")
                return False

    def insert_data(self, num_users=100, num_products=200, num_orders=300, num_tickets=50, batch_size=25):
        connection = None
        cursor = None
        
        # Initialize variables to avoid 'in locals()' checks
        paid_orders = []
        shipped_orders = []
        return_ids = []
        conversation_ids = []
        escalated_tickets = []
        
        try:
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()
            print("데이터베이스 연결 성공!")
            
            
            print(f"\n🚀 데이터 삽입 시작 (배치 크기: {batch_size})")
            print("=" * 60)
            
            # Insert Categories
            print("카테고리 데이터 삽입 중...")
            try:
                for category in self.product_categories:
                    cursor.execute("""
                        INSERT INTO categories (name, description, is_active, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (category, f'{category} 관련 상품들', True, self.random_datetime_between()))
                connection.commit()
                print("✅ 카테고리 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 카테고리 삽입 실패: {e}")
                connection.rollback()
                return

            # Insert Users in batches
            print(f"사용자 데이터 삽입 중... (배치 크기: {batch_size})")
            user_ids = []
            user_batch = []
            
            try:
                generated_names = set()  # Track generated names to reduce duplicates
                generated_emails = set()  # Track generated emails to reduce duplicates
                name_counter = 1  # Counter for guaranteed unique names
                
                for i in range(num_users):
                    # Generate unique name with improved strategy
                    attempt = 0
                    max_attempts = 5  # Reduced attempts, faster fallback
                    name = None
                    
                    while attempt < max_attempts:
                        candidate_name = self.generate_korean_name()
                        if candidate_name not in generated_names:
                            name = candidate_name
                            generated_names.add(name)
                            break
                        attempt += 1
                    
                    if name is None:
                        # Use counter for guaranteed uniqueness
                        name = self.generate_korean_name(name_counter)
                        generated_names.add(name)
                        name_counter += 1
                    
                    # Generate unique email
                    email_attempt = 0
                    while email_attempt < 10:
                        email = f"{fake.user_name()}{random.randint(1000, 9999)}@{random.choice(['gmail.com', 'naver.com', 'daum.net', 'kakao.com'])}"
                        if email not in generated_emails:
                            generated_emails.add(email)
                            break
                        email_attempt += 1
                    else:
                        # Fallback with timestamp
                        email = f"user{i}_{int(datetime.now().timestamp())}@gmail.com"
                        generated_emails.add(email)
                    
                    phone = fake.phone_number()
                    reg_date = self.random_datetime_between()
                    tier = random.choices(['bronze', 'silver', 'gold', 'platinum'], weights=[50, 30, 15, 5])[0]
                    
                    user_batch.append((email, name[:1], name[1:], phone, reg_date, 
                                     reg_date + timedelta(days=random.randint(0, 30)), True, tier))
                    
                    # Insert batch when full or at the end
                    if len(user_batch) >= batch_size or i == num_users - 1:
                        try:
                            cursor.executemany("""
                                INSERT INTO users (email, first_name, last_name, phone, registration_date, 
                                                 last_login, is_active, customer_tier)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (email) DO NOTHING
                            """, user_batch)
                            
                            # Get user IDs by querying the database (more reliable than RETURNING with batch)
                            cursor.execute("SELECT user_id FROM users ORDER BY user_id DESC LIMIT %s", (len(user_batch),))
                            batch_user_ids = [row[0] for row in cursor.fetchall()]
                            user_ids.extend(reversed(batch_user_ids))  # Reverse to maintain insertion order
                            
                        except Exception as batch_error:
                            if "duplicate key value" in str(batch_error).lower() or "unique constraint" in str(batch_error).lower():
                                print(f"  ⚠️ 배치에서 중복 키 감지, 개별 삽입으로 전환...")
                                # CRITICAL: Rollback the failed transaction first
                                connection.rollback()
                                
                                # Insert each user individually to handle name conflicts
                                for user_data in user_batch:
                                    try:
                                        cursor.execute("""
                                            INSERT INTO users (email, first_name, last_name, phone, registration_date, 
                                                             last_login, is_active, customer_tier)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                            ON CONFLICT (email) DO NOTHING
                                            RETURNING user_id
                                        """, user_data)
                                        result = cursor.fetchone()
                                        if result:
                                            user_ids.append(result[0])
                                        connection.commit()  # Commit each individual insert
                                    except Exception as individual_error:
                                        if "duplicate key value" not in str(individual_error).lower():
                                            print(f"    ❌ 개별 사용자 삽입 실패: {individual_error}")
                                        connection.rollback()  # Rollback failed individual insert
                                        continue
                            else:
                                connection.rollback()
                                raise batch_error
                        else:
                            # Batch insert succeeded
                            connection.commit()
                        
                        print(f"  사용자 배치 {len(user_ids)}/{num_users} 삽입 완료")
                        user_batch = []
                        
                print("✅ 사용자 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 사용자 삽입 실패: {e}")
                if "duplicate key value" in str(e).lower() or "unique constraint" in str(e).lower():
                    print("  ℹ️ 중복 키 오류 - 개별 삽입으로 재시도합니다...")
                    connection.rollback()
                    # Continue with individual insertions using improved name generation
                    user_ids = []
                    fallback_name_counter = 1000  # Start high to avoid conflicts
                    fallback_emails = set()
                    
                    for i in range(num_users):
                        try:
                            # Use counter-based names for guaranteed uniqueness
                            name = self.generate_korean_name(fallback_name_counter)
                            fallback_name_counter += 1
                            
                            # Generate unique email with timestamp fallback
                            email_attempt = 0
                            while email_attempt < 5:
                                email = f"{fake.user_name()}{random.randint(10000, 99999)}@{random.choice(['gmail.com', 'naver.com', 'daum.net', 'kakao.com'])}"
                                if email not in fallback_emails:
                                    fallback_emails.add(email)
                                    break
                                email_attempt += 1
                            else:
                                email = f"fallback_user{i}_{int(datetime.now().timestamp())}@gmail.com"
                                fallback_emails.add(email)
                            
                            phone = fake.phone_number()
                            reg_date = self.random_datetime_between()
                            tier = random.choices(['bronze', 'silver', 'gold', 'platinum'], weights=[50, 30, 15, 5])[0]
                            
                            cursor.execute("""
                                INSERT INTO users (email, first_name, last_name, phone, registration_date, 
                                                 last_login, is_active, customer_tier)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (email) DO NOTHING
                                RETURNING user_id
                            """, (email, name[:1], name[1:], phone, reg_date,
                                 reg_date + timedelta(days=random.randint(0, 30)), True, tier))
                            
                            result = cursor.fetchone()
                            if result:
                                user_ids.append(result[0])
                                if len(user_ids) % 25 == 0:
                                    print(f"  개별 사용자 삽입 {len(user_ids)}/{num_users} 완료")
                            connection.commit()
                        except Exception as individual_error:
                            if "duplicate key value" not in str(individual_error).lower():
                                print(f"  ⚠️ 사용자 {i+1} 삽입 중 오류: {individual_error}")
                            connection.rollback()
                            continue
                    print(f"✅ 사용자 데이터 삽입 완료 (총 {len(user_ids)}명 성공)")
                else:
                    connection.rollback()
                    print("  ❌ 사용자 삽입에서 복구할 수 없는 오류 발생, 계속 진행합니다...")
                    user_ids = []  # Empty list to continue with other data

            # Insert Addresses in batches
            print(f"주소 데이터 삽입 중... (배치 크기: {batch_size})")
            address_batch = []
            
            try:
                for user_id in user_ids:
                    for addr_type in ['shipping', 'billing']:
                        street_address, city, district, postal_code = self.generate_korean_address()
                        address_batch.append((user_id, addr_type, street_address, city, district, postal_code, 
                                            '대한민국', addr_type == 'shipping', self.random_datetime_between()))
                        
                        # Insert batch when full
                        if len(address_batch) >= batch_size:
                            cursor.executemany("""
                                INSERT INTO addresses (user_id, address_type, street_address, city, state, 
                                                     postal_code, country, is_default, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (street_address, city, state, postal_code, country) DO NOTHING
                            """, address_batch)
                            connection.commit()
                            print(f"  주소 배치 {len(address_batch)} 개 삽입 완료")
                            address_batch = []
                
                # Insert remaining addresses
                if address_batch:
                    cursor.executemany("""
                        INSERT INTO addresses (user_id, address_type, street_address, city, state, 
                                             postal_code, country, is_default, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (street_address, city, state, postal_code, country) DO NOTHING
                    """, address_batch)
                    connection.commit()
                    print(f"  주소 배치 {len(address_batch)} 개 삽입 완료")
                    
                print("✅ 주소 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 주소 삽입 실패: {e}")
                if "duplicate key value" in str(e).lower() or "unique constraint" in str(e).lower():
                    print("  ℹ️ 중복 주소 오류 - 계속 진행합니다...")
                    connection.rollback()
                else:
                    connection.rollback()
                    print("  ❌ 주소 삽입에서 복구할 수 없는 오류 발생, 계속 진행합니다...")

            # Insert Products in batches (with LLM generation)
            print(f"상품 데이터 삽입 중... (배치 크기: {batch_size})")
            product_ids = []
            product_batch = []
            
            # Get category mappings
            cursor.execute("SELECT name, category_id FROM categories")
            category_map = dict(cursor.fetchall())
            
            try:
                used_names = set()  # Track used product names
                
                for i in range(num_products):
                    category = random.choice(self.product_categories)
                    category_id = category_map[category]
                    
                    # Generate unique product name with retry logic
                    attempt = 0
                    max_attempts = 50
                    while attempt < max_attempts:
                        product_name = self.generate_unique_product_name(category, attempt)
                        if product_name not in used_names:
                            used_names.add(product_name)
                            break
                        attempt += 1
                    else:
                        # If we couldn't find a unique name after max_attempts, use a UUID suffix
                        base_name = random.choice(self.product_names[category])
                        product_name = f"{base_name} - {str(uuid.uuid4())[:8]}"
                        used_names.add(product_name)
                    
                    price = random.randint(10000, 500000)
                    cost_price = int(price * random.uniform(0.5, 0.8))
                    
                    # Generate unique SKU
                    sku = f"SKU{random.randint(10000, 99999)}-{random.randint(100, 999)}"
                    
                    brand = product_name.split()[0]
                    
                    # Generate realistic product description using LLM
                    try:
                        product_description = self.generate_product_description(product_name, category)
                    except Exception as llm_error:
                        print(f"  ⚠️ LLM 오류 (상품 {i+1}): {llm_error}, 기본 설명 사용")
                        product_description = f'{product_name} - 고품질 {category} 상품입니다.'
                    
                    product_batch.append((product_name, product_description, category_id, sku, price, cost_price,
                                        random.uniform(0.1, 5.0), 
                                        f'{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)}cm',
                                        brand, True, self.random_datetime_between(), self.random_datetime_between()))
                    
                    # Insert batch when full or at the end
                    if len(product_batch) >= batch_size or i == num_products - 1:
                        cursor.executemany("""
                            INSERT INTO products (name, description, category_id, sku, price, cost_price,
                                                weight, dimensions, brand, is_active, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (name) DO NOTHING
                        """, product_batch)
                        
                        # Get the inserted product IDs
                        cursor.execute("SELECT product_id FROM products ORDER BY product_id DESC LIMIT %s", (len(product_batch),))
                        batch_product_ids = [row[0] for row in cursor.fetchall()]
                        product_ids.extend(reversed(batch_product_ids))
                        
                        connection.commit()
                        print(f"  상품 배치 {len(product_ids)}/{num_products} 삽입 완료 (고유 이름 {len(used_names)}개 생성)")
                        product_batch = []
                        
                print(f"✅ 상품 데이터 삽입 완료 (총 {len(used_names)}개 고유 상품명 생성)")
            except Exception as e:
                print(f"❌ 상품 삽입 실패: {e}")
                if "duplicate key value" in str(e).lower() or "unique constraint" in str(e).lower():
                    print("  ℹ️ 중복 상품 오류 - 계속 진행합니다...")
                    connection.rollback()
                    # Get existing product IDs to continue
                    cursor.execute("SELECT product_id FROM products")
                    product_ids = [row[0] for row in cursor.fetchall()]
                else:
                    connection.rollback()
                    print("  ❌ 상품 삽입에서 복구할 수 없는 오류 발생, 계속 진행합니다...")
                    product_ids = []

            # Insert Inventory in batches
            print(f"재고 데이터 삽입 중... (배치 크기: {batch_size})")
            inventory_batch = []
            
            try:
                for i, product_id in enumerate(product_ids):
                    quantity = random.randint(0, 100)
                    inventory_batch.append((product_id, quantity, random.randint(0, min(5, quantity)), 
                                          random.randint(5, 20), random.choice(['서울창고', '부산창고', '대구창고']), 
                                          self.random_datetime_between()))
                    
                    # Insert batch when full or at the end
                    if len(inventory_batch) >= batch_size or i == len(product_ids) - 1:
                        cursor.executemany("""
                            INSERT INTO inventory (product_id, quantity_available, quantity_reserved, 
                                                 reorder_level, warehouse_location, last_updated)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, inventory_batch)
                        connection.commit()
                        print(f"  재고 배치 {i + 1}/{len(product_ids)} 삽입 완료")
                        inventory_batch = []
                        
                print("✅ 재고 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 재고 삽입 실패: {e}")
                connection.rollback()
                print("  ❌ 재고 삽입 오류 발생, 계속 진행합니다...")

            # Insert CS Agents
            print("고객서비스 상담원 데이터 삽입 중...")
            agent_names = ['김상담', '이지원', '박도움', '최서비스', '정상담']
            agent_ids = []
            for name in agent_names:
                try:
                    cursor.execute("""
                        INSERT INTO cs_agents (agent_name, agent_email, agent_type, specialization, 
                                             max_concurrent_tickets, is_active, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (agent_email) DO NOTHING
                        RETURNING agent_id
                    """, (name, f"{name.lower()}@company.com", 'human', 
                         random.choice(['일반상담', '기술지원', '반품처리', '결제문의']), 
                         random.randint(5, 15), True, self.random_datetime_between()))
                    result = cursor.fetchone()
                    if result:
                        agent_ids.append(result[0])
                    else:
                        # If conflict occurred, get existing agent_id
                        cursor.execute("SELECT agent_id FROM cs_agents WHERE agent_email = %s", (f"{name.lower()}@company.com",))
                        existing_result = cursor.fetchone()
                        if existing_result:
                            agent_ids.append(existing_result[0])
                except Exception as e:
                    print(f"  ⚠️ 상담원 {name} 삽입 중 오류 (건너뛰기): {e}")
                    continue

            # Insert Orders
            print("주문 데이터 삽입 중...")
            order_ids = []
            
            # Get all existing users from database (both new and existing)
            cursor.execute("SELECT user_id FROM users")
            all_user_ids = [row[0] for row in cursor.fetchall()]
            
            # Safety check: ensure we have users before creating orders
            if not all_user_ids:
                print("  ⚠️ 사용자가 없어서 주문을 생성할 수 없습니다. 건너뛰기...")
            else:
                print(f"  📊 {len(all_user_ids)}명의 사용자로 주문 생성 중...")
                for i in range(num_orders):
                    user_id = random.choice(all_user_ids)
                    order_number = f"ORD{self.random_date_between().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
                    order_date = self.random_datetime_between()
                    
                    # Get user addresses
                    cursor.execute("SELECT address_id FROM addresses WHERE user_id = %s AND address_type = 'shipping'", (user_id,))
                    shipping_result = cursor.fetchone()
                    cursor.execute("SELECT address_id FROM addresses WHERE user_id = %s AND address_type = 'billing'", (user_id,))
                    billing_result = cursor.fetchone()
                    
                    # Skip if user doesn't have addresses
                    if not shipping_result or not billing_result:
                        continue
                        
                    shipping_addr = shipping_result[0]
                    billing_addr = billing_result[0]
                    
                    subtotal = random.randint(20000, 300000)
                    tax_amount = int(subtotal * 0.1)
                    shipping_cost = 3000 if subtotal < 50000 else 0
                    discount_amount = random.randint(0, int(subtotal * 0.1))
                    total_amount = subtotal + tax_amount + shipping_cost - discount_amount
                    
                    cursor.execute("""
                        INSERT INTO orders (user_id, order_number, order_status, order_date,
                                          shipping_address_id, billing_address_id, subtotal, tax_amount,
                                          shipping_cost, discount_amount, total_amount, payment_status, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (order_number) DO NOTHING
                        RETURNING order_id
                    """, (user_id, order_number, 
                             random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered']),
                             order_date, shipping_addr, billing_addr, subtotal, tax_amount,
                             shipping_cost, discount_amount, total_amount,
                             random.choice(['pending', 'paid', 'failed']), 
                             '고객 요청사항: 문 앞에 배치해주세요'))
                    
                    result = cursor.fetchone()
                    if result:
                        order_id = result[0]
                        order_ids.append(order_id)
                        if len(order_ids) % 50 == 0:
                            print(f"    주문 {len(order_ids)}/{num_orders} 생성 완료")
                    else:
                        # If conflict occurred, get existing order_id
                        cursor.execute("SELECT order_id FROM orders WHERE order_number = %s", (order_number,))
                        existing_result = cursor.fetchone()
                        if existing_result:
                            order_ids.append(existing_result[0])
                
                connection.commit()
                print(f"✅ 주문 데이터 삽입 완료 (총 {len(order_ids)}건 생성)")

            # Insert Order Items
            print("주문 상품 데이터 삽입 중...")
            
            # Get all existing products from database
            cursor.execute("SELECT product_id FROM products")
            all_product_ids = [row[0] for row in cursor.fetchall()]
            
            # Safety check: ensure we have orders and products
            if not order_ids:
                print("  ⚠️ 주문이 없어서 주문 상품을 생성할 수 없습니다. 건너뛰기...")
            elif not all_product_ids:
                print("  ⚠️ 상품이 없어서 주문 상품을 생성할 수 없습니다. 건너뛰기...")
            else:
                print(f"  📊 {len(all_product_ids)}개의 상품으로 주문 상품 생성 중...")
                for i, order_id in enumerate(order_ids):
                    num_items = random.randint(1, 5)
                    selected_products = random.sample(all_product_ids, min(num_items, len(all_product_ids)))
                    
                    for product_id in selected_products:
                        cursor.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
                        unit_price = cursor.fetchone()[0]
                        quantity = random.randint(1, 3)
                        total_price = unit_price * quantity
                        
                        cursor.execute("""
                            INSERT INTO order_items (order_id, product_id, quantity, unit_price, 
                                                    total_price, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (order_id, product_id, quantity, unit_price, total_price, self.random_datetime_between()))
                    
                    if (i + 1) % 100 == 0:
                        print(f"    주문 상품 {i + 1}/{len(order_ids)} 완료")
                
                connection.commit()
                print(f"✅ 주문 상품 데이터 삽입 완료")

            # Insert Support Tickets in batches (with LLM generation)
            print(f"고객지원 티켓 데이터 삽입 중... (배치 크기: {batch_size})")
            ticket_batch = []
            
            # Get all existing orders from database for ticket references
            cursor.execute("SELECT order_id FROM orders")
            all_order_ids = [row[0] for row in cursor.fetchall()]
            
            # Safety check: ensure we have users before creating tickets
            if not all_user_ids:
                print("  ⚠️ 사용자가 없어서 지원 티켓을 생성할 수 없습니다. 건너뛰기...")
                ticket_ids = []
            else:
                print(f"  📊 {len(all_user_ids)}명의 사용자와 {len(all_order_ids)}건의 주문으로 티켓 생성 중...")
                try:
                    for i in range(num_tickets):
                        user_id = random.choice(all_user_ids)
                        order_id = random.choice(all_order_ids) if all_order_ids and random.random() < 0.7 else None
                        ticket_number = f"TKT{self.random_date_between().strftime('%Y%m%d')}{random.randint(100, 999)}"
                        subject = random.choice(self.support_subjects)
                        
                        # Get product name if order exists for more realistic description
                        product_name = None
                        if order_id:
                            cursor.execute("""
                                SELECT p.name FROM products p 
                                JOIN order_items oi ON p.product_id = oi.product_id 
                                WHERE oi.order_id = %s LIMIT 1
                            """, (order_id,))
                            result = cursor.fetchone()
                            if result:
                                product_name = result[0]
                        
                        # Generate realistic support ticket description using LLM
                        try:
                            description = self.generate_support_ticket_description(subject, product_name)
                        except Exception as llm_error:
                            print(f"  ⚠️ LLM 오류 (티켓 {i+1}): {llm_error}, 기본 설명 사용")
                            description = random.choice(self.support_descriptions)
                        
                        # Safely choose agent_id
                        assigned_agent = random.choice(agent_ids) if agent_ids else None
                        
                        ticket_batch.append((user_id, order_id, ticket_number, subject, description,
                                           random.choice(['low', 'medium', 'high']),
                                           random.choice(['open', 'in_progress', 'resolved']),
                                           random.choice(['order_inquiry', 'product_issue', 'shipping_problem', 'payment_issue']),
                                           assigned_agent, self.random_datetime_between()))
                        
                        # Insert batch when full or at the end
                        if len(ticket_batch) >= batch_size or i == num_tickets - 1:
                            cursor.executemany("""
                                INSERT INTO support_tickets (user_id, order_id, ticket_number, subject, description,
                                                            priority, status, category, assigned_agent_id, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (ticket_number) DO NOTHING
                            """, ticket_batch)
                            connection.commit()
                            print(f"  지원 티켓 배치 {i + 1}/{num_tickets} 삽입 완료")
                            ticket_batch = []
                            
                    print("✅ 지원 티켓 데이터 삽입 완료")
                    
                    # Get ticket IDs for later use
                    cursor.execute("SELECT ticket_id FROM support_tickets")
                    ticket_ids = [row[0] for row in cursor.fetchall()]
                except Exception as e:
                    print(f"❌ 지원 티켓 삽입 실패: {e}")
                    connection.rollback()

            # Insert Reviews in batches (with LLM generation)
            print(f"리뷰 데이터 삽입 중... (배치 크기: {batch_size})")
            review_batch = []
            review_count = 0
            
            # Safety check: ensure we have orders before creating reviews  
            if not all_order_ids:
                print("  ⚠️ 주문이 없어서 리뷰를 생성할 수 없습니다. 건너뛰기...")
            else:
                total_review_orders = min(50, len(all_order_ids))
                print(f"  📊 {len(all_order_ids)}건의 주문 중 {total_review_orders}건으로 리뷰 생성 중...")
                
                try:
                    for order_id in random.sample(all_order_ids, total_review_orders):
                        cursor.execute("SELECT user_id FROM orders WHERE order_id = %s", (order_id,))
                        user_id = cursor.fetchone()[0]
                        
                        cursor.execute("""
                            SELECT oi.product_id, p.name FROM order_items oi 
                            JOIN products p ON oi.product_id = p.product_id 
                            WHERE oi.order_id = %s
                        """, (order_id,))
                        products = cursor.fetchall()
                        
                        for product_id, product_name in products:
                            if random.random() < 0.3:  # 30% chance of review
                                rating = random.randint(1, 5)
                                
                                # Generate realistic review text using LLM
                                try:
                                    review_text = self.generate_korean_review_text(rating, product_name)
                                except Exception as llm_error:
                                    print(f"  ⚠️ LLM 오류 (리뷰 {review_count + 1}): {llm_error}, 기본 리뷰 사용")
                                    if rating >= 4:
                                        review_text = f"{product_name} 정말 만족스럽습니다. 품질이 좋아요!"
                                    elif rating == 3:
                                        review_text = f"{product_name} 평범한 편이에요. 나쁘지는 않습니다."
                                    else:
                                        review_text = f"{product_name} 기대에 못 미쳤어요. 실망스럽습니다."
                                
                                # Generate appropriate title based on rating
                                if rating >= 4:
                                    title = random.choice(['만족스러운 구매', '좋은 상품입니다', '추천해요', '재구매 예정'])
                                elif rating == 3:
                                    title = random.choice(['평범한 상품', '그럭저럭', '무난합니다', '보통 수준'])
                                else:
                                    title = random.choice(['아쉬운 상품', '기대에 못 미침', '별로예요', '실망'])
                                
                                review_batch.append((product_id, user_id, order_id, rating, title, review_text,
                                                  True, True, random.randint(0, 10), self.random_datetime_between()))
                                review_count += 1
                                
                                # Insert batch when full
                                if len(review_batch) >= batch_size:
                                    cursor.executemany("""
                                        INSERT INTO reviews (product_id, user_id, order_id, rating, title, review_text,
                                                            is_verified_purchase, is_approved, helpful_votes, created_at)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, review_batch)
                                    connection.commit()
                                    print(f"  리뷰 배치 {review_count} 개 삽입 완료")
                                    review_batch = []
                    
                    # Insert remaining reviews
                    if review_batch:
                        cursor.executemany("""
                            INSERT INTO reviews (product_id, user_id, order_id, rating, title, review_text,
                                                is_verified_purchase, is_approved, helpful_votes, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, review_batch)
                        connection.commit()
                        print(f"  리뷰 배치 {len(review_batch)} 개 삽입 완료")
                        
                    print("✅ 리뷰 데이터 삽입 완료")
                except Exception as e:
                    print(f"❌ 리뷰 삽입 실패: {e}")
                    connection.rollback()

            # Insert Ticket Messages
            print(f"티켓 메시지 데이터 삽입 중...")
            
            # Get all existing tickets from database
            cursor.execute("SELECT ticket_id FROM support_tickets")
            all_ticket_ids = [row[0] for row in cursor.fetchall()]
            
            # Get all existing agents from database
            cursor.execute("SELECT agent_id FROM cs_agents")
            all_agent_ids = [row[0] for row in cursor.fetchall()]
            
            try:
                message_batch = []
                print(f"  📊 {len(all_ticket_ids)}개의 티켓으로 메시지 생성 중...")
                
                for ticket_id in all_ticket_ids:
                    # Each ticket has 2-5 messages (customer and agent responses)
                    num_messages = random.randint(2, 5)
                    
                    for i in range(num_messages):
                        if i == 0:  # First message is always from customer
                            sender_type = 'customer'
                            sender_id = None  # We could link to user_id but keeping simple
                            message_text = "안녕하세요. 문의드릴 것이 있어서 연락드렸습니다."
                        elif i % 2 == 1:  # Agent responses
                            sender_type = 'agent'
                            sender_id = random.choice(all_agent_ids) if all_agent_ids else None
                            message_text = "안녕하세요. 고객님의 문의에 대해 확인해드리겠습니다."
                        else:  # Customer follow-up
                            sender_type = 'customer'
                            sender_id = None
                            message_text = "답변 감사합니다. 추가로 궁금한 점이 있습니다."
                        
                        is_internal = sender_type == 'agent' and random.random() < 0.1  # 10% internal notes
                        
                        message_batch.append((ticket_id, sender_type, sender_id, message_text, 
                                            is_internal, self.random_datetime_between()))
                        
                        # Insert batch when full
                        if len(message_batch) >= batch_size:
                            cursor.executemany("""
                                INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, message_text, 
                                                            is_internal, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, message_batch)
                            connection.commit()
                            message_batch = []
                
                # Insert remaining messages
                if message_batch:
                    cursor.executemany("""
                        INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, message_text, 
                                                    is_internal, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, message_batch)
                    connection.commit()
                    
                print("✅ 티켓 메시지 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 티켓 메시지 삽입 실패: {e}")
                connection.rollback()
                print("  ❌ 티켓 메시지 삽입 오류 발생, 계속 진행합니다...")

            # Insert Payments in batches
            print(f"결제 데이터 삽입 중... (배치 크기: {batch_size})")
            payment_batch = []
            
            try:
                # Get all existing orders that are paid/shipped/delivered from database
                cursor.execute("SELECT order_id, total_amount FROM orders WHERE payment_status IN ('paid') OR order_status IN ('shipped', 'delivered')")
                all_paid_orders = cursor.fetchall()
                print(f"  📊 {len(all_paid_orders)}건의 결제 대상 주문으로 결제 데이터 생성 중...")
                
                for i, (order_id, total_amount) in enumerate(all_paid_orders):
                    payment_method = random.choice(['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay', 'bank_transfer'])
                    payment_status = random.choices(['completed', 'pending', 'failed'], weights=[85, 10, 5])[0]
                    transaction_id = f"TXN{random.randint(100000000, 999999999)}"
                    
                    payment_batch.append((order_id, payment_method, payment_status, total_amount, 
                                        transaction_id, self.random_datetime_between(), 
                                        f"Payment processed via {payment_method}", self.random_datetime_between()))
                    
                    # Insert batch when full or at the end
                    if len(payment_batch) >= batch_size or i == len(all_paid_orders) - 1:
                        cursor.executemany("""
                            INSERT INTO payments (order_id, payment_method, payment_status, amount, 
                                                transaction_id, payment_date, processor_response, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, payment_batch)
                        connection.commit()
                        print(f"  결제 배치 {i + 1}/{len(all_paid_orders)} 삽입 완료")
                        payment_batch = []
                        
                print("✅ 결제 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 결제 삽입 실패: {e}")
                connection.rollback()

            # Insert Shipping in batches
            print(f"배송 데이터 삽입 중... (배치 크기: {batch_size})")
            shipping_batch = []
            
            try:
                # Get all existing orders that are shipped/delivered from database
                cursor.execute("SELECT order_id, order_date FROM orders WHERE order_status IN ('shipped', 'delivered')")
                all_shipped_orders = cursor.fetchall()
                print(f"  📊 {len(all_shipped_orders)}건의 배송 대상 주문으로 배송 데이터 생성 중...")
                
                for i, (order_id, order_date) in enumerate(all_shipped_orders):
                    carrier = random.choice(['CJ대한통운', '우체국택배', '한진택배', '로젠택배', '롯데택배'])
                    tracking_number = f"TRK{random.randint(1000000000, 9999999999)}"
                    shipping_method = random.choice(['표준배송', '당일배송', '새벽배송', '택배'])
                    
                    # Calculate realistic shipping dates
                    shipped_at = order_date + timedelta(days=random.randint(1, 3))
                    estimated_delivery = shipped_at.date() + timedelta(days=random.randint(1, 5))
                    actual_delivery = shipped_at + timedelta(days=random.randint(1, 4))
                    shipping_status = random.choices(['delivered', 'in_transit', 'out_for_delivery'], weights=[80, 15, 5])[0]
                    
                    shipping_batch.append((order_id, carrier, tracking_number, shipping_method, 
                                         estimated_delivery, actual_delivery if shipping_status == 'delivered' else None,
                                         shipping_status, shipped_at, shipped_at))
                    
                    # Insert batch when full or at the end
                    if len(shipping_batch) >= batch_size or i == len(all_shipped_orders) - 1:
                        cursor.executemany("""
                            INSERT INTO shipping (order_id, carrier, tracking_number, shipping_method, 
                                                estimated_delivery, actual_delivery_date, shipping_status, 
                                                created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, shipping_batch)
                        connection.commit()
                        print(f"  배송 배치 {i + 1}/{len(all_shipped_orders)} 삽입 완료")
                        shipping_batch = []
                        
                print("✅ 배송 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 배송 삽입 실패: {e}")
                connection.rollback()

            # Insert Coupons
            print("쿠폰 데이터 삽입 중...")
            try:
                coupon_data = [
                    ('WELCOME10', '신규회원 10% 할인', 'percentage', 10.00, 50000),
                    ('SUMMER2025', '여름 시즌 할인', 'percentage', 15.00, 100000),
                    ('FREE_SHIP', '무료배송 쿠폰', 'free_shipping', 3000.00, 30000),
                    ('SAVE5000', '5천원 즉시할인', 'fixed_amount', 5000.00, 50000),
                    ('VIP20', 'VIP 고객 20% 할인', 'percentage', 20.00, 200000),
                    ('FIRST_BUY', '첫 구매 할인', 'percentage', 12.00, 0),
                    ('BULK_ORDER', '대량주문 할인', 'percentage', 25.00, 500000),
                    ('MOBILE_APP', '모바일앱 전용 할인', 'fixed_amount', 3000.00, 0)
                ]
                
                for code, description, discount_type, discount_value, min_order in coupon_data:
                    cursor.execute("""
                        INSERT INTO coupons (code, description, discount_type, discount_value, 
                                           minimum_order_amount, usage_limit, used_count, is_active, 
                                           valid_from, valid_until, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (code) DO NOTHING
                    """, (code, description, discount_type, discount_value, min_order,
                         random.randint(100, 1000), random.randint(0, 50), True,
                         self.random_datetime_between(), 
                         self.random_datetime_between() + timedelta(days=random.randint(30, 365)),
                         self.random_datetime_between()))
                
                connection.commit()
                print("✅ 쿠폰 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 쿠폰 삽입 실패: {e}")
                connection.rollback()

            # Insert Order Coupons (some orders used coupons)
            print(f"주문-쿠폰 연결 데이터 삽입 중...")
            try:
                cursor.execute("SELECT coupon_id, discount_value FROM coupons")
                available_coupons = cursor.fetchall()
                
                # Apply coupons to 20% of orders
                sample_orders = random.sample(all_order_ids, len(all_order_ids) // 5) if all_order_ids else []
                
                for order_id in sample_orders:
                    if random.random() < 0.3:  # 30% chance for each sampled order
                        coupon_id, discount_value = random.choice(available_coupons)
                        discount_applied = min(discount_value, random.randint(1000, 10000))
                        
                        cursor.execute("""
                            INSERT INTO order_coupons (order_id, coupon_id, discount_applied, created_at)
                            VALUES (%s, %s, %s, %s)
                        """, (order_id, coupon_id, discount_applied, self.random_datetime_between()))
                
                connection.commit()
                print("✅ 주문-쿠폰 연결 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 주문-쿠폰 연결 삽입 실패: {e}")
                connection.rollback()

            # Insert Returns
            print(f"반품 데이터 삽입 중...")
            try:
                # Get all existing delivered orders from database for returns
                cursor.execute("SELECT order_id, user_id, total_amount FROM orders WHERE order_status = 'delivered'")
                all_delivered_orders = cursor.fetchall()
                return_orders = random.sample(all_delivered_orders, len(all_delivered_orders) // 20) if all_delivered_orders else []
                print(f"  📊 {len(all_delivered_orders)}건의 배송완료 주문 중 {len(return_orders)}건으로 반품 생성 중...")
                
                return_ids = []
                for order_id, user_id, total_amount in return_orders:
                    return_number = f"RET{self.random_date_between().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
                    return_reason = random.choice(['defective', 'wrong_item', 'not_as_described', 'changed_mind', 'damaged_shipping'])
                    return_status = random.choice(['requested', 'approved', 'in_transit', 'received', 'processed'])
                    return_type = random.choice(['refund', 'exchange', 'store_credit'])
                    
                    cursor.execute("""
                        INSERT INTO returns (order_id, user_id, return_number, return_reason, return_status, 
                                           return_type, requested_amount, approved_amount, return_shipping_cost, 
                                           notes, requested_at, processed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (return_number) DO NOTHING
                        RETURNING return_id
                    """, (order_id, user_id, return_number, return_reason, return_status, return_type,
                         total_amount, float(total_amount) * 0.9, 3000, '고객 요청에 의한 반품',
                         self.random_datetime_between(), 
                         self.random_datetime_between() if return_status == 'processed' else None))
                    
                    result = cursor.fetchone()
                    if result:
                        return_ids.append(result[0])
                    else:
                        # If conflict occurred, get existing return_id
                        cursor.execute("SELECT return_id FROM returns WHERE return_number = %s", (return_number,))
                        existing_result = cursor.fetchone()
                        if existing_result:
                            return_ids.append(existing_result[0])
                
                connection.commit()
                print("✅ 반품 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 반품 삽입 실패: {e}")
                connection.rollback()

            # Insert Return Items
            print(f"반품 상품 데이터 삽입 중...")
            
            # Get all existing returns from database
            cursor.execute("SELECT return_id FROM returns")
            all_return_ids = [row[0] for row in cursor.fetchall()]
            
            try:
                print(f"  📊 {len(all_return_ids)}건의 반품으로 반품 상품 생성 중...")
                for return_id in all_return_ids:
                    # Get the order_id for this return
                    cursor.execute("SELECT order_id FROM returns WHERE return_id = %s", (return_id,))
                    order_id = cursor.fetchone()[0]
                    
                    # Get order items for this order
                    cursor.execute("SELECT order_item_id, quantity FROM order_items WHERE order_id = %s", (order_id,))
                    order_items = cursor.fetchall()
                    
                    # Return 1-2 items from the order
                    items_to_return = random.sample(order_items, min(2, len(order_items)))
                    
                    for order_item_id, original_quantity in items_to_return:
                        return_quantity = random.randint(1, original_quantity)
                        condition = random.choice(['new', 'like_new', 'good', 'fair', 'poor'])
                        
                        cursor.execute("""
                            INSERT INTO return_items (return_id, order_item_id, quantity, reason, 
                                                     condition_received, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (return_id, order_item_id, return_quantity, '사용 후 불만족', 
                             condition, self.random_datetime_between()))
                
                connection.commit()
                print("✅ 반품 상품 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 반품 상품 삽입 실패: {e}")
                connection.rollback()

            # ============= MULTI-AGENT SYSTEM DATA =============
            
            # Insert User Sessions (for Authentication Agent)
            print(f"사용자 세션 데이터 삽입 중...")
            
            # Get all existing users from database for sessions
            cursor.execute("SELECT user_id FROM users")
            all_session_user_ids = [row[0] for row in cursor.fetchall()]
            session_user_ids = random.sample(all_session_user_ids, len(all_session_user_ids) // 3) if all_session_user_ids else []  # Active sessions for 1/3 of users
            
            try:
                session_batch = []
                print(f"  📊 {len(all_session_user_ids)}명의 사용자 중 {len(session_user_ids)}명으로 세션 생성 중...")
                for i, user_id in enumerate(session_user_ids):
                    session_token = f"sess_{random.randint(100000000000, 999999999999)}"
                    ip_address = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
                    user_agent = random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
                    ])
                    auth_method = random.choice(['email', 'phone', 'sms_code', 'oauth'])
                    
                    session_batch.append((user_id, session_token, ip_address, user_agent, True, 
                                        auth_method, self.random_datetime_between(),
                                        self.random_datetime_between() + timedelta(hours=24),
                                        self.random_datetime_between()))
                    
                    if len(session_batch) >= batch_size or i == len(session_user_ids) - 1:
                        cursor.executemany("""
                            INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, 
                                                     is_authenticated, authentication_method, created_at, 
                                                     expires_at, last_activity)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (session_token) DO NOTHING
                        """, session_batch)
                        connection.commit()
                        session_batch = []
                        
                print("✅ 사용자 세션 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 사용자 세션 삽입 실패: {e}")
                connection.rollback()

            # Insert Knowledge Base (for Knowledge Retrieval Agent)
            print(f"지식 베이스 데이터 삽입 중...")
            try:
                # Get all existing CS agent IDs for created_by
                cursor.execute("SELECT agent_id FROM cs_agents")
                kb_agent_ids = [row[0] for row in cursor.fetchall()]
                
                kb_data = [
                    ("주문 취소 방법", "주문 후 24시간 이내에는 마이페이지에서 직접 취소 가능합니다. 그 이후에는 고객센터로 연락해주세요.", "faq", ["주문", "취소", "마이페이지"]),
                    ("배송비 정책", "5만원 이상 주문시 무료배송이며, 그 미만은 3,000원의 배송비가 부과됩니다.", "policy", ["배송", "배송비", "무료배송"]),
                    ("반품/교환 절차", "상품 수령 후 7일 이내 반품 가능하며, 단순 변심의 경우 배송비는 고객 부담입니다.", "policy", ["반품", "교환", "환불"]),
                    ("결제 수단", "신용카드, 체크카드, 계좌이체, 페이팔, 애플페이, 구글페이를 지원합니다.", "faq", ["결제", "카드", "페이팔"]),
                    ("회원 등급 혜택", "브론즈(기본), 실버(5% 할인), 골드(10% 할인), 플래티넘(15% 할인 + 무료배송) 등급이 있습니다.", "policy", ["회원", "등급", "할인"]),
                    ("상품 문의 방법", "상품 상세페이지의 Q&A 탭에서 문의하거나 고객센터 1588-1234로 연락하세요.", "faq", ["문의", "고객센터", "상품"]),
                    ("적립금 사용법", "결제시 적립금을 현금처럼 사용할 수 있으며, 최소 1,000원부터 사용 가능합니다.", "faq", ["적립금", "결제", "할인"]),
                    ("배송 추적", "주문완료 후 발송되면 SMS와 이메일로 송장번호를 안내드립니다.", "faq", ["배송", "추적", "송장"]),
                    ("개인정보 보호", "고객의 개인정보는 개인정보보호법에 따라 안전하게 관리됩니다.", "policy", ["개인정보", "보호", "보안"]),
                    ("쿠폰 사용법", "결제페이지에서 쿠폰코드를 입력하면 자동으로 할인이 적용됩니다.", "faq", ["쿠폰", "할인", "코드"])
                ]
                
                for title, content, category, tags in kb_data:
                    content_hash = hashlib.sha256(content.encode()).hexdigest()
                    pinecone_id = f"kb_{random.randint(100000, 999999)}"
                    agent_id = random.choice(kb_agent_ids) if kb_agent_ids else None
                    
                    cursor.execute("""
                        INSERT INTO knowledge_base (title, content, category, tags, pinecone_vector_id, 
                                                   content_hash, source_url, is_active, created_at, 
                                                   updated_at, created_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (title, content, category, tags, pinecone_id, content_hash,
                         f"https://help.example.com/{category}/{title.replace(' ', '-')}", True,
                         self.random_datetime_between(), self.random_datetime_between(), agent_id))
                
                connection.commit()
                print("✅ 지식 베이스 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 지식 베이스 삽입 실패: {e}")
                connection.rollback()

            # Insert Conversation Sessions (for Orchestrator Agent)
            print(f"대화 세션 데이터 삽입 중...")
            try:
                # Get all existing session tokens and ticket IDs from database
                cursor.execute("SELECT session_token FROM user_sessions")
                all_session_tokens = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT ticket_id, user_id FROM support_tickets")
                all_ticket_data = cursor.fetchall()
                
                # Create conversations for a subset of tickets (up to 50)
                conversation_ticket_data = random.sample(all_ticket_data, min(50, len(all_ticket_data))) if all_ticket_data else []
                print(f"  📊 {len(all_ticket_data)}개의 티켓 중 {len(conversation_ticket_data)}개로 대화 세션 생성 중...")
                
                conversation_ids = []
                for i, (ticket_id, user_id) in enumerate(conversation_ticket_data):
                    session_token = random.choice(all_session_tokens) if all_session_tokens else None
                    intent = random.choice(['order_inquiry', 'complaint', 'return_request', 'product_question', 'billing_issue'])
                    confidence = round(random.uniform(0.7, 0.99), 2)
                    requires_human = random.choice([True, False])
                    
                    state_data = {
                        "current_step": random.choice(["authentication", "issue_identification", "resolution", "followup"]),
                        "collected_info": {"order_id": random.choice(all_order_ids) if all_order_ids else None},
                        "attempted_solutions": random.randint(0, 3)
                    }
                    
                    cursor.execute("""
                        INSERT INTO conversation_sessions (user_id, ticket_id, session_token, conversation_state, 
                                                         current_intent, confidence_score, requires_human, 
                                                         escalation_reason, started_at, last_activity, ended_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING conversation_id
                    """, (user_id, ticket_id, session_token, json.dumps(state_data), intent, confidence,
                         requires_human, "복잡한 문제로 인한 에스컬레이션" if requires_human else None,
                         self.random_datetime_between(), self.random_datetime_between(),
                         self.random_datetime_between() if random.random() < 0.3 else None))
                    
                    conversation_ids.append(cursor.fetchone()[0])
                
                connection.commit()
                print("✅ 대화 세션 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 대화 세션 삽입 실패: {e}")
                connection.rollback()

            # Insert Agent Tasks (for Orchestrator routing)
            print(f"에이전트 작업 데이터 삽입 중...")
            
            # Get all existing conversations from database
            cursor.execute("SELECT conversation_id FROM conversation_sessions")
            all_conversation_ids = [row[0] for row in cursor.fetchall()]
            
            try:
                task_batch = []
                agent_types = ['authentication', 'lookup', 'knowledge', 'llm', 'sentiment', 'escalation']
                print(f"  📊 {len(all_conversation_ids)}개의 대화 세션으로 에이전트 작업 생성 중...")
                
                for conversation_id in all_conversation_ids:
                    # Each conversation has 2-5 agent tasks
                    num_tasks = random.randint(2, 5)
                    for _ in range(num_tasks):
                        agent_type = random.choice(agent_types)
                        task_status = random.choices(['completed', 'pending', 'failed'], weights=[80, 15, 5])[0]
                        
                        input_data = {"query": "고객 문의 처리", "context": "일반적인 문의"}
                        output_data = {"result": "처리 완료", "confidence": 0.95} if task_status == 'completed' else None
                        execution_time = random.randint(100, 5000) if task_status == 'completed' else None
                        
                        task_batch.append((conversation_id, agent_type, task_status, 
                                         json.dumps(input_data), json.dumps(output_data) if output_data else None,
                                         execution_time, self.random_datetime_between(),
                                         self.random_datetime_between() if task_status == 'completed' else None,
                                         "처리 중 오류 발생" if task_status == 'failed' else None))
                        
                        if len(task_batch) >= batch_size:
                            cursor.executemany("""
                                INSERT INTO agent_tasks (conversation_id, agent_type, task_status, input_data, 
                                                        output_data, execution_time_ms, started_at, completed_at, error_message)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, task_batch)
                            connection.commit()
                            task_batch = []
                
                # Insert remaining tasks
                if task_batch:
                    cursor.executemany("""
                        INSERT INTO agent_tasks (conversation_id, agent_type, task_status, input_data, 
                                                output_data, execution_time_ms, started_at, completed_at, error_message)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, task_batch)
                    connection.commit()
                    
                print("✅ 에이전트 작업 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 에이전트 작업 삽입 실패: {e}")
                connection.rollback()

            # Insert Sentiment Analysis (for Sentiment Analysis Agent)
            print(f"감정 분석 데이터 삽입 중...")
            
            # Get all existing ticket messages and conversations from database
            cursor.execute("SELECT message_id FROM ticket_messages WHERE sender_type = 'customer'")
            all_customer_message_ids = [row[0] for row in cursor.fetchall()]
            
            try:
                print(f"  📊 {len(all_conversation_ids)}개의 대화 세션과 {len(all_customer_message_ids)}개의 고객 메시지로 감정 분석 생성 중...")
                
                for conversation_id in all_conversation_ids:
                    # 1-3 sentiment analyses per conversation
                    num_analyses = random.randint(1, 3)
                    for _ in range(num_analyses):
                        message_id = random.choice(all_customer_message_ids) if all_customer_message_ids else None
                        sentiment_score = round(random.uniform(-1.0, 1.0), 2)
                        emotion = random.choice(['angry', 'frustrated', 'happy', 'neutral', 'confused', 'satisfied'])
                        confidence = round(random.uniform(0.6, 0.99), 2)
                        keywords = random.sample(['불만', '만족', '빠른', '늦은', '친절', '불친절', '해결', '문제'], 
                                               random.randint(1, 3))
                        escalation_trigger = sentiment_score < -0.5 or emotion in ['angry', 'frustrated']
                        
                        cursor.execute("""
                            INSERT INTO sentiment_analysis (conversation_id, message_id, sentiment_score, 
                                                           emotion, confidence, keywords, escalation_trigger, analyzed_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (conversation_id, message_id, sentiment_score, emotion, confidence,
                             keywords, escalation_trigger, self.random_datetime_between()))
                
                connection.commit()
                print("✅ 감정 분석 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 감정 분석 삽입 실패: {e}")
                connection.rollback()

            # Insert Escalation Rules (for Escalation Detection Agent)
            print(f"에스컬레이션 규칙 데이터 삽입 중...")
            try:
                escalation_rules_data = [
                    ("부정적 감정 임계값", "sentiment_threshold", {"threshold": -0.7, "emotion": ["angry", "frustrated"]}, 2),
                    ("키워드 매칭", "keyword_match", {"keywords": ["환불", "취소", "불만", "항의"]}, 1),
                    ("응답 시간 초과", "response_time", {"max_minutes": 30}, 1),
                    ("복잡도 점수", "complexity_score", {"threshold": 0.8}, 2),
                    ("반복 문의", "repeat_inquiry", {"max_attempts": 3}, 1)
                ]
                
                # Get agent IDs for auto assignment
                cursor.execute("SELECT agent_id FROM cs_agents WHERE agent_type = 'human' LIMIT 3")
                human_agents = [row[0] for row in cursor.fetchall()]
                
                for rule_name, condition_type, condition_value, priority_boost in escalation_rules_data:
                    auto_assign_agent = random.choice(human_agents) if human_agents and random.random() < 0.7 else None
                    
                    cursor.execute("""
                        INSERT INTO escalation_rules (rule_name, condition_type, condition_value, priority_boost, 
                                                     auto_assign_agent_id, is_active, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (rule_name, condition_type, json.dumps(condition_value), priority_boost,
                         auto_assign_agent, True, self.random_datetime_between()))
                
                connection.commit()
                print("✅ 에스컬레이션 규칙 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 에스컬레이션 규칙 삽입 실패: {e}")
                connection.rollback()

            # Insert Escalation Events
            print(f"에스컬레이션 이벤트 데이터 삽입 중...")
            try:
                # Get rule IDs and agent IDs
                cursor.execute("SELECT rule_id FROM escalation_rules")
                rule_ids = [row[0] for row in cursor.fetchall()]
                
                cursor.execute("SELECT agent_id FROM cs_agents")
                all_agents = [row[0] for row in cursor.fetchall()]
                
                # Get all ticket IDs from database
                cursor.execute("SELECT ticket_id FROM support_tickets")
                all_ticket_ids = [row[0] for row in cursor.fetchall()]
                
                # Create escalation events for some tickets
                escalated_tickets = random.sample(all_ticket_ids, len(all_ticket_ids) // 10) if all_ticket_ids else []  # 10% of tickets escalated
                
                for ticket_id in escalated_tickets:
                    conversation_id = random.choice(conversation_ids) if conversation_ids else None
                    rule_id = random.choice(rule_ids) if rule_ids else None
                    escalation_type = random.choice(['sentiment', 'complexity', 'timeout', 'manual'])
                    
                    if len(all_agents) >= 2:
                        from_agent = random.choice(all_agents)
                        to_agent = random.choice([a for a in all_agents if a != from_agent])
                    else:
                        from_agent = all_agents[0] if all_agents else None
                        to_agent = None
                    
                    cursor.execute("""
                        INSERT INTO escalation_events (ticket_id, conversation_id, rule_id, trigger_reason, 
                                                      escalation_type, escalated_from_agent_id, escalated_to_agent_id, 
                                                      escalated_at, resolved_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (ticket_id, conversation_id, rule_id, f"{escalation_type} 조건에 의한 에스컬레이션",
                         escalation_type, from_agent, to_agent, self.random_datetime_between(),
                         self.random_datetime_between() if random.random() < 0.6 else None))
                
                connection.commit()
                print("✅ 에스컬레이션 이벤트 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 에스컬레이션 이벤트 삽입 실패: {e}")
                connection.rollback()

            # Insert Knowledge Usage and LLM Responses (for LLM Response Agent)
            print(f"지식 사용 및 LLM 응답 데이터 삽입 중...")
            
            # Get all existing KB IDs and agent message IDs from database
            cursor.execute("SELECT kb_id FROM knowledge_base")
            all_kb_ids = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT message_id FROM ticket_messages WHERE sender_type = 'agent'")
            all_agent_message_ids = [row[0] for row in cursor.fetchall()]
            
            try:
                print(f"  📊 {len(all_conversation_ids)}개의 대화 세션, {len(all_kb_ids)}개의 지식 베이스, {len(all_agent_message_ids)}개의 상담원 메시지로 지식 사용 및 LLM 응답 생성 중...")
                
                for conversation_id in all_conversation_ids:
                    # Knowledge usage
                    used_kb_ids = random.sample(all_kb_ids, min(random.randint(1, 3), len(all_kb_ids))) if all_kb_ids else []
                    for kb_id in used_kb_ids:
                        relevance_score = round(random.uniform(0.5, 1.0), 2)
                        was_helpful = random.choice([True, False, None])  # None = no feedback yet
                        
                        cursor.execute("""
                            INSERT INTO knowledge_usage (conversation_id, kb_id, relevance_score, was_helpful, used_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (conversation_id, kb_id, relevance_score, was_helpful, self.random_datetime_between()))
                    
                    # LLM responses
                    num_responses = random.randint(1, 4)
                    for _ in range(num_responses):
                        message_id = random.choice(all_agent_message_ids) if all_agent_message_ids else None
                        prompt_template = random.choice(['customer_inquiry', 'order_status', 'technical_support', 'billing_question'])
                        response_time = random.randint(500, 3000)
                        token_count = random.randint(50, 500)
                        model_name = random.choice(['gpt-4o-mini', 'gpt-4o', 'claude-3-sonnet'])
                        confidence = round(random.uniform(0.7, 0.99), 2)
                        was_accepted = random.choice([True, False, None])
                        
                        cursor.execute("""
                            INSERT INTO llm_responses (conversation_id, message_id, prompt_template, knowledge_sources, 
                                                      response_time_ms, token_count, model_name, confidence_score, 
                                                      was_accepted, generated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (conversation_id, message_id, prompt_template, used_kb_ids, response_time,
                             token_count, model_name, confidence, was_accepted, self.random_datetime_between()))
                
                connection.commit()
                print("✅ 지식 사용 및 LLM 응답 데이터 삽입 완료")
            except Exception as e:
                print(f"❌ 지식 사용 및 LLM 응답 삽입 실패: {e}")
                connection.rollback()

            connection.commit()
            print(f"\n🎉 모든 데이터 삽입 완료!")
            print(f"- 사용자: {num_users}명")
            print(f"- 상품: {num_products}개") 
            print(f"- 주문: {num_orders}건")
            print(f"- 지원 티켓: {num_tickets}건")
            print(f"- 결제: {len(all_paid_orders)}건")
            print(f"- 배송: {len(all_shipped_orders)}건")
            print(f"- 쿠폰: 8개")
            print(f"- 반품: {len(return_orders)}건")
            print(f"- 티켓 메시지: {len(all_ticket_ids)}개 티켓으로 생성")
            print(f"- 사용자 세션: {len(session_user_ids)}개")
            print(f"- 지식 베이스: 10개")
            print(f"- 대화 세션: {len(conversation_ids)}개")
            print(f"- 에스컬레이션 규칙: 5개")
            print(f"- 에스컬레이션 이벤트: {len(escalated_tickets)}개")

        except (Exception, Error) as error:
            print(f"❌ 데이터 삽입 중 오류 발생: {error}")
            if "duplicate key value" in str(error).lower() or "unique constraint" in str(error).lower():
                print("  ℹ️ 중복 키 오류가 발생했지만 계속 진행합니다...")
                if connection:
                    connection.rollback()
                # Continue with a partial rollback and retry mechanism could be implemented here
            else:
                if connection:
                    connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                print("데이터베이스 연결 종료")

def main(start_date, end_date):
    print("한국 전자상거래 샘플 데이터 생성기")
    print("=" * 50)
    
    try:
        # Validate dates
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
        
        generator = KoreanEcommerceDataGenerator(start_date, end_date)
        
        print(f"\n📅 데이터 생성 기간: {start_date} ~ {end_date}")
        print("데이터 생성을 시작합니다...")
        print("-" * 50)
        
        generator.insert_data(
            num_users=150,      # 사용자 150명
            num_products=300,   # 상품 300개
            num_orders=500,     # 주문 500건
            num_tickets=80,     # 지원 티켓 80건
            batch_size=25       # 배치 크기 (LLM 호출이 많으므로 작게 설정)
        )
        
    except ValueError:
        print("❌ 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # Get current date and calculate first and last day of the month
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1).strftime('%Y-%m-%d')
    last_day_num = calendar.monthrange(now.year, now.month)[1]
    last_day = datetime(now.year, now.month, last_day_num).strftime('%Y-%m-%d')
    
    main(first_day, last_day) 