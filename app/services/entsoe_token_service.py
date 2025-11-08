#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service-Layer für Benutzer-spezifische ENTSO-E Tokens
"""

import base64
import hashlib
from datetime import datetime
from typing import Optional, Tuple

import requests
from flask import current_app

from app import db
from models import UserApiToken

try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

ENTSOE_TEST_URL = "https://web-api.tp.entsoe.eu/api"


def _get_secret_bytes() -> bytes:
    secret = current_app.config.get('SECRET_KEY', 'bess-secret-key')
    return hashlib.sha256(secret.encode('utf-8')).digest()


def _get_cipher():
    if Fernet is None:
        return None
    key = base64.urlsafe_b64encode(_get_secret_bytes())
    return Fernet(key)


def _xor_fallback(data: bytes) -> bytes:
    """Einfache XOR-Verschleierung als Fallback, falls cryptography nicht verfügbar ist."""
    secret = _get_secret_bytes()
    return bytes(b ^ secret[i % len(secret)] for i, b in enumerate(data))


def encrypt_token(token: str) -> str:
    """Token verschlüsseln oder wenigstens verschleiern."""
    if not token:
        return ''
    cipher = _get_cipher()
    token_bytes = token.encode('utf-8')
    if cipher:
        return "fernet:" + cipher.encrypt(token_bytes).decode('utf-8')
    obfuscated = base64.urlsafe_b64encode(_xor_fallback(token_bytes)).decode('utf-8')
    return "xor:" + obfuscated


def decrypt_token(token_encrypted: Optional[str]) -> Optional[str]:
    if not token_encrypted:
        return None
    if token_encrypted.startswith("fernet:"):
        cipher = _get_cipher()
        if not cipher:
            return None
        try:
            decrypted = cipher.decrypt(token_encrypted[len("fernet:"):].encode('utf-8'))
            return decrypted.decode('utf-8')
        except InvalidToken:
            return None
    if token_encrypted.startswith("xor:"):
        payload = base64.urlsafe_b64decode(token_encrypted[len("xor:"):].encode('utf-8'))
        return _xor_fallback(payload).decode('utf-8')
    return None


def get_user_entsoe_config(user_id: int) -> dict:
    record = UserApiToken.query.filter_by(user_id=user_id, provider='entsoe').first()
    if not record:
        return {
            'has_token': False,
            'is_active': True,
            'last_updated': None,
            'token_masked': None,
        }
    token_plain = decrypt_token(record.token_encrypted)
    if token_plain:
        masked = token_plain[:4] + "•••" + token_plain[-4:] if len(token_plain) > 8 else "••••"
    else:
        masked = None
    return {
        'has_token': bool(token_plain),
        'is_active': record.is_active,
        'last_updated': record.updated_at,
        'token_masked': masked,
    }


def upsert_user_entsoe_token(user_id: int, token: str, enabled: bool) -> Tuple[bool, str]:
    if enabled and not token:
        return False, "Token darf nicht leer sein, wenn er aktiviert ist."

    record = UserApiToken.query.filter_by(user_id=user_id, provider='entsoe').first()
    token_value = encrypt_token(token) if token else ''
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest() if token else None

    timestamp = datetime.utcnow()

    if record:
        record.token_encrypted = token_value
        record.token_hash = token_hash
        record.is_active = enabled
        record.updated_at = timestamp
    else:
        record = UserApiToken(
            user_id=user_id,
            provider='entsoe',
            token_encrypted=token_value,
            token_hash=token_hash,
            is_active=enabled,
            created_at=timestamp,
            updated_at=timestamp,
        )
        db.session.add(record)

    db.session.commit()

    if token_value:
        return True, "ENTSO-E API Token wurde gespeichert."
    return True, "ENTSO-E API Token wurde deaktiviert."


def get_active_entsoe_token(user_id: int) -> Optional[str]:
    record = UserApiToken.query.filter_by(user_id=user_id, provider='entsoe', is_active=True).first()
    if not record:
        return None
    return decrypt_token(record.token_encrypted)


def test_entsoe_token(token: str) -> Tuple[bool, str]:
    if not token:
        return False, "Kein Token angegeben."

    now = datetime.utcnow()
    period_start = now.strftime("%Y%m%d%H00")
    period_end = now.strftime("%Y%m%d%H59")

    params = {
        "securityToken": token,
        "documentType": "A44",
        "in_Domain": "10YAT-APG------L",
        "out_Domain": "10YAT-APG------L",
        "periodStart": period_start,
        "periodEnd": period_end,
    }

    try:
        response = requests.get(ENTSOE_TEST_URL, params=params, timeout=15)
        if response.status_code == 200:
            return True, "Token ist gültig und funktionsfähig."
        if response.status_code in (401, 403):
            return False, "Token ist ungültig oder nicht freigeschaltet."
        if response.status_code == 429:
            return False, "Rate-Limit erreicht. Bitte später erneut testen."
        return False, f"ENTSO-E API Fehler {response.status_code}: {response.text[:120]}"
    except requests.exceptions.Timeout:
        return False, "Zeitüberschreitung bei der Verbindung zur ENTSO-E API."
    except requests.exceptions.RequestException as exc:  # pragma: no cover - Netzwerkfehler
        return False, f"Verbindungsfehler: {exc}"


