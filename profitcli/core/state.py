# core/state.py
from threading import Event

login_state = {
    "accounts": [],
    "account_event": Event(),
}
