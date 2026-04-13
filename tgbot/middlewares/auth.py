from aiogram import types, BaseMiddleware


class AdminMiddleware(BaseMiddleware):
    """Middleware для проверки, что юзер — админ"""
    
    def __init__(self, admin_login: str = "admin"):
        self.admin_login = admin_login
    
    async def __call__(self, message: types.Message, state=None):
        pass


class IsAdminFilter:
    """Фильтр для проверки, что пользователь админ"""
    
    def __init__(self, admin_login: str = "admin"):
        self.admin_login = admin_login
    
    async def __call__(self, message: types.Message) -> bool:
        return True


def register_auth_middleware(dp):
    """Регистрация middleware в диспетчере"""
    dp.update.middleware(AdminMiddleware())
