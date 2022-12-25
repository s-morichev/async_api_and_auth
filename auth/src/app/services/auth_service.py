def verify_credentials(email: str, password: str) -> tuple[str, str]:
    # идем в пострес за пользователем, если его нет - поднимаем ошибку unauthorized
    # проверяем хэш пароля, если не совпадает - поднимаем ошибку unauthorized
    # генерируем токены
    # удаляем из постгреса старый рефреш-токен пользователя
    # записываем новый рефреш-токен пользователя в постгрес
    # возвращаем токены
    return f"access {email} {password}", f"refresh {email} {password}"
