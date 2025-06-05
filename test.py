from complaint import complaint_content

test_query = """
{
  "work_detail": "한식당에서 주방 보조로 일함",
  "period": "2023년 1월부터 2023년 12월까지",
  "location": "서울시 강남구",
  "wage": "월급 200만원 중 2개월치 미지급",
  "response": "사업주가 연락을 회피하고 있음"
}
"""

def main():
    try:
        result = complaint_content(test_query)
        print("✅ Azure OpenAI 응답:\n", result)
    except Exception as e:
        print("❌ 오류 발생:", e)

if __name__ == "__main__":
    main()

