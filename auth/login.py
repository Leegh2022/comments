# auth/authentication.py

from data.database import get_user, add_user

def login(username):
    """사용자를 로그인 처리합니다. 존재하지 않으면 새로 추가합니다."""
    user = get_user(username)
    if not user:
        # 사용자가 존재하지 않으면 새로 추가
        success = add_user(username)
        if success:
            return True, "새로운 사용자로 로그인되었습니다."
        else:
            return False, "사용자 추가에 실패했습니다."
    return True, "로그인 성공!"

