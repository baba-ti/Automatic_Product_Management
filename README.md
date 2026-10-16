# Automatic Product Management

**입출력 채널이 바뀌어도 공통 업무 처리 흐름을 재사용할 수 있도록 설계한 n8n 기반 자동화 도구입니다.**

입력 채널의 요청을 공통 형식으로 변환하고, 업무 처리 결과를 출력 채널에 맞게 전달합니다. 채널을 추가하거나 교체할 때는 입출력 어댑터를 연결하고, 중간의 DB·AI 처리 흐름은 재사용합니다. 입력과 출력이 서로 다른 서비스인 구성도 어댑터에서 라우팅을 설정해 확장할 수 있습니다.

> 사용자의 n8n 환경에 가져와 적용할 수 있는 자동화 워크플로입니다. DB·AI 모델·입출력 채널의 인증 정보를 설정한 뒤 사용할 수 있으며, 실행 환경에 따른 호환성과 데이터 접근 권한을 확인해야 합니다.

> 현재 구성은 가상 쇼핑몰 데이터를 입력한 예시 DB를 기준으로 합니다. 실제 사용 시 사용자의 DB 구조·업무 규칙·접근 권한·입출력 채널에 맞춰 설정하고, 필요한 n8n 노드와 프롬프트를 조정해야 합니다. 인증 정보만 바꾸면 모든 운영 DB에 그대로 적용되는 범용 완제품은 아닙니다.

## 실제 환경에 적용하기

기존 운영 DB가 있다면 제공된 예시 테이블로 변경할 필요 없이, 워크플로를 해당 DB에 맞추어 조정합니다. 제공된 테이블 생성 노트북과 샘플 삽입 코드는 테스트 환경 준비용이며, 기존 운영 DB에 반드시 실행할 필요는 없습니다.

| 적용 항목             | 확인·변경할 내용                                                                                   |
| --------------------- | -------------------------------------------------------------------------------------------------- |
| 데이터베이스 연결     | 사용자의 DB 주소와 읽기 전용 조회 계정으로 Postgres 인증 설정                                      |
| 스키마·테이블 범위    | `List Tables`, `Get Schema`의 `public` 스키마 조건과 조회 가능한 테이블 범위를 실제 DB에 맞게 조정 |
| 테이블 관계·업무 의미 | 필요한 관계·컬럼 설명을 모델에 제공하고, 실제 테이블 구조로 SQL이 올바르게 생성되는지 확인         |
| 업무 규칙             | 매출 계산 방식, 취소·반품 제외 조건, 날짜 기준 등을 프롬프트나 조회 로직에 반영                    |
| 데이터 접근 권한      | 사용자별 조회 범위와 민감 필드 마스킹 구성; 질문에 포함된 사용자 ID만으로 접근을 허용하지 않기     |
| 입출력 채널           | 사용할 서비스의 인증, 입력 어댑터, 응답 목적지와 전송 노드 설정                                    |
| 적용 검증             | 대표 질문의 결과를 직접 실행한 SQL 및 업무 기준과 비교                                             |

테이블 목록과 컬럼은 실행 중 조회하지만, 테이블 관계와 업무 의미까지 자동으로 정확하게 이해한다고 보장하지는 않습니다. DB가 바뀌어도 **입력 변환 → 테이블 선택 → SQL 생성 → DB 조회 → 답변 작성 → 출력 전달**이라는 공통 흐름은 재사용할 수 있으며, 변경 범위는 실제 환경에 따라 달라집니다.

## 주요 기능

- **입출력 채널 교체**: 공통 형식에 맞는 어댑터를 연결해 채널 추가·변경
- **업무 로직 재사용**: 채널별 요청을 동일한 DB·AI 처리 흐름에서 실행
- **결과 전달 분리**: 처리 결과를 공통 응답으로 반환하고 출력 어댑터에서 전달
- **현재 연결 예시**: n8n Chat 응답, Slack 채널 답장, 다른 워크플로 호출·반환
- 전자상거래·고객상담 관련 26개 테이블 및 테스트 데이터 생성

## 아키텍처

![입출력 채널과 공통 처리 흐름을 분리한 자동화 아키텍처](docs/images/architecture.svg)

입출력 어댑터와 공통 처리 구간을 분리했습니다. 위 그림의 외부 입출력은 확장 지점이며, 새 채널은 아래 계약에 맞추어 연결합니다. 해당 서비스의 인증과 수신·전송 노드는 구성해야 합니다. 현재 내장 분기는 Slack 직접 전송과 Chat·호출자 반환을 처리하며, 서로 다른 채널 간 전달은 호출 워크플로의 출력 어댑터에서 구성합니다.

## 현재 예시 DB 구조

아래 그림은 `create_tables_for_supabase.ipynb`에 정의된 26개 테이블과 21개 인덱스를 기준으로 정리한 업무별 구성입니다. 실제 Supabase의 현재 스키마를 직접 조회한 결과는 아닙니다.

![현재 가상 쇼핑몰 DB의 업무별 테이블 구성과 주요 연결](docs/images/database-architecture.svg)

| 영역                | 테이블                                                                                                                           |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 고객·주소           | `users`, `addresses`                                                                                                             |
| 상품·재고           | `categories`, `products`, `inventory`                                                                                            |
| 주문·결제·배송·쿠폰 | `orders`, `order_items`, `payments`, `shipping`, `coupons`, `order_coupons`                                                      |
| 리뷰·반품·고객 문의 | `reviews`, `returns`, `return_items`, `support_tickets`, `ticket_messages`                                                       |
| 세션·대화·작업      | `user_sessions`, `conversation_sessions`, `agent_tasks`                                                                          |
| 상담 운영·AI 기록   | `cs_agents`, `knowledge_base`, `sentiment_analysis`, `escalation_rules`, `escalation_events`, `knowledge_usage`, `llm_responses` |

대표 관계는 `users → orders → order_items`이며, `order_items.product_id`로 상품을 연결합니다. 주문은 결제·배송·반품·문의와 연결되고, 문의는 메시지 및 대화 기록과 연결됩니다. 모든 테이블이 현재 n8n 흐름에서 항상 사용되는 것은 아니며, AI 관련 기록 테이블이 존재한다고 해당 분석·에이전트 기능이 실행되는 것은 아닙니다.

예시 DB에서는 주문 날짜가 `orders.order_date`, 주문 총액이 `orders.total_amount`, 주문 상태가 `orders.order_status`입니다. 사용자 DB의 대응 컬럼과 테이블 관계를 확인하고, 매출 계산·취소·환불 제외 기준 등을 프롬프트 또는 조회 로직에 반영해야 합니다.

## 사용 기술

- 자동화: n8n, Chat Trigger, Slack Trigger, Basic LLM Chain
- 데이터베이스: Supabase PostgreSQL, n8n Postgres 노드, psycopg2
- AI: OpenAI API, Structured Output Parser, LangChain OpenAI
- 샘플 생성: Python, Faker, random
- Python 환경 관리: uv, Python 3.12

테이블 선택·SQL 생성·답변 작성에 사용하는 AI 모델은 모두 `gpt-6-luna`입니다. Python 샘플 데이터의 문장 생성에도 같은 모델을 사용합니다.

| 처리 단계                        | 설정 위치                       | 모델         |
| -------------------------------- | ------------------------------- | ------------ |
| 관련 테이블 선택                 | `Table Model`                   | `gpt-6-luna` |
| SQL 생성                         | `SQL Model`                     | `gpt-6-luna` |
| 조회 결과를 한국어 답변으로 작성 | `Answer Model`                  | `gpt-6-luna` |
| 상품 설명·리뷰·문의글 샘플 생성  | `insert_tables_for_supabase.py` | `gpt-6-luna` |

모델은 각 노드·코드에서 변경할 수 있으며 계정 접근 권한과 n8n 버전에 따른 호환성을 확인해야 합니다. 기존 n8n 워크플로를 사용 중이면 `Answer Model`도 `gpt-6-luna`로 변경하거나 수정된 JSON을 다시 가져와 적용하세요.

## 시작하기

### 1. 실행 환경 준비

n8n 인스턴스, Supabase 프로젝트, OpenAI API 인증을 준비합니다. Slack을 사용하려면 Slack 앱과 봇 인증도 필요합니다. Python 도구 실행에는 Python 3.12와 uv가 필요합니다.

```powershell
git clone https://github.com/baba-ti/Automatic_Product-Management.git
cd Automatic_Product-Management
uv sync --locked --python 3.12
```

기존 DB와 n8n 워크플로만 사용할 경우 Python 설치·샘플 생성 단계는 생략할 수 있습니다. 위 명령은 n8n을 설치하지 않습니다.

### 2. 환경변수 설정

프로젝트 루트에 `.env`를 만듭니다. 아래 값은 실제 인증 정보가 없는 예시입니다.

```dotenv
SUPABASE_DATABASE_URL=postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@YOUR_DB_HOST:5432/postgres?sslmode=require
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

DB 주소는 Supabase 프로젝트의 **Connect** 화면에서 선택한 연결 방식의 값을 사용합니다. URL 안의 비밀번호 예약 문자는 URL 인코딩해야 합니다.

`.env`는 Python 코드가 읽습니다. n8n 인증은 n8n의 **Credentials**에서 별도로 설정합니다.

### 3. DB 테이블·샘플 준비

1. `create_tables_for_supabase.ipynb`를 열고 `.venv`의 Python을 커널로 선택합니다.
2. 셀을 순서대로 실행해 테이블을 생성합니다.
3. 테스트 데이터가 필요하면 다음 명령을 실행합니다.

```powershell
uv run python insert_tables_for_supabase.py
```

주요 생성 목표는 고객 150명, 상품 300개, 주문 500건, 문의 80건입니다. 결제·배송·리뷰 등 연관 데이터도 추가합니다. 기존 데이터와 실행 결과에 따라 실제 추가량은 달라지며, 날짜는 실행한 달 범위에서 생성합니다.

샘플 생성은 DB에 데이터를 쓰고 AI 문장 생성에 API 사용료가 발생하므로 테스트용 DB에서 실행하세요. 감정 점수·에이전트 작업·응답 추적 기록 등은 무작위 예시이며 실제 분석·운영 측정 결과가 아닙니다.

### 4. n8n 워크플로 가져오기

1. 새 워크플로에서 **Import from File**을 선택합니다.
2. `product_management.json`을 가져옵니다.
3. 다음 인증과 채널 설정을 연결합니다.

| 노드                                          | 필요한 설정                     |
| --------------------------------------------- | ------------------------------- |
| `List Tables`, `Get Schema`, `Run Read Query` | Postgres 인증                   |
| `Table Model`, `SQL Model`, `Answer Model`    | OpenAI 인증 및 사용 가능한 모델 |
| `Slack Input`, `Reply Slack`                  | Slack 인증                      |
| `Slack Input`                                 | 수신할 Slack 채널               |

먼저 Chat으로 테스트합니다. Slack을 아직 사용하지 않으면 Slack Trigger를 비활성화할 수 있습니다. 운영 시 필요한 트리거를 구성하고 워크플로를 게시·활성화하세요. Slack 앱의 이벤트 구독 URL도 새 Trigger에 연결해야 합니다.

Hosted Chat 공개는 기본 OFF입니다. 링크 공유 시 공개 범위와 인증을 별도로 설정하세요.

## 다른 채널 연결

다른 n8n 워크플로에서 **Execute Sub-workflow**로 호출하고 완료를 기다리도록 설정합니다. 한 실행에 요청 한 개를 전달합니다.

입력 예시:

```json
{
  "question": "이번 달 주문은 몇 건인가요?",
  "channel": "telegram",
  "replyTo": "destination-id",
  "userId": "user-id",
  "sessionId": "session-id"
}
```

`question`은 필수입니다. 외부 호출에서 `channel`의 기본값은 `external`입니다. `channel=slack`이면 `replyTo`에 Slack 채널 ID가 필요하며 이 워크플로가 직접 전송합니다. 채널과 목적지는 신뢰할 수 있는 호출자가 설정해야 합니다.

Slack 이외 채널의 반환 예시:

```json
{
  "output": "조회 결과를 설명한 답변",
  "answer": "조회 결과를 설명한 답변",
  "channel": "telegram",
  "replyTo": "destination-id",
  "userId": "user-id",
  "sessionId": "session-id"
}
```

호출자는 `answer`를 해당 채널의 전송 노드에 연결합니다. `output`은 n8n Chat의 응답 필드입니다. 중간 처리 교체 시 `Request Context`를 유지하고, 최종 처리 노드가 `{"text":"답변"}` 또는 `{"output":"답변"}` 한 항목을 반환하도록 맞춥니다.

## 실행 확인

1. n8n Chat에서 “전체 주문은 몇 건인가요?”처럼 간단한 질문을 보냅니다.
2. 테이블 선택 → SQL 생성 → DB 조회 → 답변 작성 순서로 실행되는지 확인합니다.
3. 결과를 DB에서 직접 조회한 값과 비교합니다.
4. Slack 사용 시 지정한 채널에서 봇을 멘션하고 해당 채널로 답장이 오는지 확인합니다.
5. 외부 채널은 호출 워크플로에서 공통 요청 한 개를 전달하고 반환된 `answer`를 전송 노드에 연결해 확인합니다.

현재 폴더에는 별도 검사 스크립트가 없으며, 실제 연결 확인은 n8n 실행 기록과 각 서비스에서 수행합니다.

## Structured Output Parser 오류

파서 입력에 `{"tables":["orders"]}`가 있는데도 빈 응답 오류가 발생하면 `output` 포장 형식을 확인합니다. 현재 수정본의 프롬프트는 아래 형식을 요청합니다.

```json
{ "output": { "tables": ["orders"] } }
```

SQL 생성도 `{"output":{"query":"SELECT ..."}}`를 요청합니다. 파서 Input Schema에는 `tables` 또는 `query`를 정의하며, 같은 `output`을 추가해 이중으로 감싸지 않습니다. 이 동작은 n8n 파서 버전에 영향을 받을 수 있습니다.

실제 모델 응답이 비어 있다면 응답 내용·종료 사유·토큰 제한·모델 호환성을 확인하세요. `On Error: Continue`는 정상적인 테이블 선택·SQL 생성의 대안이 아닙니다.

## 데이터 접근 및 현재 제한

- 테이블 생성 노트북에는 RLS 활성화 및 접근 정책 생성이 포함되어 있지 않습니다. Supabase Data API에 노출할 테이블은 RLS와 필요한 정책·권한을 별도로 설정해야 합니다. 실제 DB의 노출 여부는 Data API 설정과 부여된 권한에 따라 달라집니다. [Supabase RLS 문서](https://supabase.com/docs/guides/database/postgres/row-level-security)
- 테이블 생성·샘플 삽입 계정과 조회 계정을 분리합니다. 조회에는 허용된 테이블에만 SELECT 권한이 있는 계정을 사용합니다.
- SQL 검사는 보수적 문자열 검사이며 완전한 SQL 분석기나 DB 권한 검사를 대신하지 않습니다. 정상 쿼리를 거절할 수도 있습니다.
- 조회 결과는 답변 작성을 위해 OpenAI로 전달됩니다. 실제 개인정보 사용 전 접근 범위와 전달 필드를 정해야 합니다.
- n8n 실행 기록에도 질문과 조회 결과가 저장될 수 있으므로 실데이터 운영 시 기록 접근 권한과 보관 기간을 설정해야 합니다.
- 사용자별 데이터 권한·민감 필드 마스킹·대화 메모리는 구현하지 않았습니다. `sessionId`는 전달만 합니다.
- 조회 결과는 최대 100행입니다. 제한에 도달하면 전체 결과를 받은 것으로 해석하면 안 됩니다.
- Slack 답장은 채널 단위입니다. 스레드 답장은 아직 구현하지 않았습니다.
- SQL·DB·API 오류는 실행 오류로 종료합니다. 사용자용 오류 응답·자동 복구는 아직 없습니다.
- `CREATE TABLE IF NOT EXISTS`는 기존 테이블 구조를 변경하지 않습니다. 구조 변경에는 별도 마이그레이션이 필요합니다.

## GitHub 업로드

공유할 워크플로는 `product_management.json`입니다. 기존 인증 참조·채널 ID·웹훅 ID·인스턴스 ID는 제거했으므로 가져온 환경에서 인증을 다시 연결합니다. README의 그림이 표시되도록 `docs/images/`도 함께 업로드합니다.

`.env`, `.venv/`, 인증 키와 고객 데이터가 담긴 실행 결과는 커밋하지 않습니다. 노트북은 실행 출력도 저장하므로 업로드 전에 확인하세요. `.gitignore`는 이미 커밋된 비밀값을 Git 기록에서 제거하지 않습니다.
