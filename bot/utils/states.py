from aiogram.fsm.state import State, StatesGroup

class TranslationStates(StatesGroup):
    waiting_for_informal = State()
    waiting_for_formal = State()

class AddWordStates(StatesGroup):
    waiting_for_informal = State()
    waiting_for_formal = State()
    waiting_for_explanation = State()

class SearchStates(StatesGroup):
    waiting_for_search = State()

class AdminStates(StatesGroup):
    waiting_for_admin_login = State()
    waiting_for_admin_role = State()
    waiting_for_admin_remove = State()

class DeleteWordStates(StatesGroup):
    waiting_for_word_input = State()
    waiting_for_confirmation = State()