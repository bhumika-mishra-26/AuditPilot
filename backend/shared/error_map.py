"""
shared/error_map.py

Maps every agent's internal error string to the correct W4 error hash
and error type stored in pattern_memory.

Every agent — W1, W2, W3 — uses its own error string internally.
When they call W4, they must translate that string using this map.

Usage:
    from shared.error_map import get_error_hash

    error_hash, error_type = get_error_hash("KYC_503")
    # returns ("hash_503_kyc", "HTTP_503_kyc_unavailable")

    # If unknown error — returns a generic fallback
    error_hash, error_type = get_error_hash("some_new_error")
    # returns ("hash_unknown", "UNKNOWN_ERROR")
"""

ERROR_MAP: dict[str, tuple[str, str]] = {

    # ── W1 errors ───────────────────────────────────────

    # KYC API returned 503 service unavailable
    "KYC_503": (
        "hash_503_kyc",
        "HTTP_503_kyc_unavailable",
    ),

    # GSTIN is not 15 characters
    "ValidationError": (
        "hash_gstin_val",
        "GSTIN_format_invalid",
    ),

    # Email already registered under another client
    "DuplicateError": (
        "hash_duplicate",
        "DUPLICATE_CLIENT",
    ),

    "Missing Name": (
        "hash_missing_name",
        "NAME_MISSING",
    ),

    "Missing Email": (
        "hash_missing_email",
        "EMAIL_MISSING",
    ),

    # Human reviewer rejected the account creation
    "HumanRejected": (
        "hash_human_rejected",
        "HUMAN_REJECTED_ACTION",
    ),

    # ── W2 errors ───────────────────────────────────────

    # Invoice amount does not match PO amount
    "THREE_WAY_MISMATCH": (
        "hash_invoice_mismatch",
        "INVOICE_AMOUNT_MISMATCH",
    ),

    # Vendor is inactive — returns 403
    "VENDOR_403": (
        "hash_403_vendor",
        "HTTP_403_vendor_inactive",
    ),

    # Vendor ID not found in system — returns 404
    "VENDOR_404": (
        "hash_404_vendor",
        "HTTP_404_vendor_not_found",
    ),

    # Payment API timed out
    "API_TIMEOUT": (
        "hash_408_timeout",
        "HTTP_408_request_timeout",
    ),

    # ── W3 errors ───────────────────────────────────────

    # Two or more team members match the owner name
    "ambiguous": (
        "hash_300_ambiguous",
        "HTTP_300_ambiguous_owner",
    ),

    # No team member found matching the owner name
    "not_found": (
        "hash_404_owner",
        "HTTP_404_owner_not_found",
    ),

    # LLM API timed out during note extraction
    "api_timeout": (
        "hash_408_timeout",
        "HTTP_408_request_timeout",
    ),

    # LLM returned response that could not be parsed as JSON
    "invalid_json": (
        "hash_invalid_json",
        "LLM_INVALID_JSON_RESPONSE",
    ),

    # LLM API returned an error response
    "api_error": (
        "hash_llm_api_error",
        "LLM_API_ERROR",
    ),

    # Meeting notes were empty or too short
    "intake_error": (
        "hash_intake_empty",
        "INTAKE_NOTES_INVALID",
    ),
}

# ─────────────────────────────────────────────────────────
# FALLBACK for unknown errors
# ─────────────────────────────────────────────────────────
UNKNOWN_HASH  = "hash_unknown"
UNKNOWN_TYPE  = "UNKNOWN_ERROR"


def get_error_hash(agent_error: str) -> tuple[str, str]:
    """
    Translates an agent's internal error string into
    the (error_hash, error_type) pair that W4 understands.

    Handles partial matches — if agent_error starts with
    "ValidationError" or "DuplicateError" (W1 sometimes
    appends extra text to these), it still matches correctly.

    Parameters
    ----------
    agent_error : the error string set in state["error"]
                  by any W1/W2/W3 node

    Returns
    -------
    (error_hash, error_type) tuple

    Examples
    --------
    get_error_hash("KYC_503")
        → ("hash_503_kyc", "HTTP_503_kyc_unavailable")

    get_error_hash('ValidationError: "GSTIN must be 15 characters"')
        → ("hash_gstin_val", "GSTIN_format_invalid")

    get_error_hash('DuplicateError: "Email already registered under Mehta"')
        → ("hash_duplicate", "DUPLICATE_CLIENT")

    get_error_hash("some_random_new_error")
        → ("hash_unknown", "UNKNOWN_ERROR")
    """
    if not agent_error:
        return UNKNOWN_HASH, UNKNOWN_TYPE

    # exact match first — fastest path
    if agent_error in ERROR_MAP:
        return ERROR_MAP[agent_error]

    # partial match — W1 appends context after the error key
    # e.g. 'ValidationError: "GSTIN must be 15 characters"'
    for key, value in ERROR_MAP.items():
        if agent_error.startswith(key):
            return value

    # nothing matched — return fallback
    return UNKNOWN_HASH, UNKNOWN_TYPE


def is_retryable(error_hash: str) -> bool:
    """
    Quick check — is this error type ever worth retrying?

    Returns False for errors that are always data problems
    and should always escalate regardless of success rate.

    Used as a fast-path before even querying pattern_memory.
    """
    NEVER_RETRY = {
        "hash_gstin_val",       # format errors — always data problem
        "hash_duplicate",       # duplicates — always data problem
        "hash_missing_name",    # user must provide name
        "hash_missing_email",   # user must provide email
        "hash_403_vendor",      # inactive vendor — needs manual approval
        "hash_404_vendor",      # vendor not found — needs manual correction/approval
        "hash_human_rejected",  # human said no — don't auto-retry
        "hash_intake_empty",    # empty notes — always data problem
    }
    return error_hash not in NEVER_RETRY