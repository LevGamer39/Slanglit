from aiogram.fsm.state import State, StatesGroup

class TranslationStates(StatesGroup):
    waiting_for_informal = State()
    waiting_for_formal = State()

class SearchStates(StatesGroup):
    waiting_for_search = State()

class AdminStates(StatesGroup):
    waiting_for_admin_login = State()
    waiting_for_admin_role = State()
    waiting_for_admin_remove = State()

class StatsStates(StatesGroup):
    waiting_for_user_search = State()