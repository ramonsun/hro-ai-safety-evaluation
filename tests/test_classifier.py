"""
Tests for the classifier — focuses on the pre-filter path to avoid API calls.
"""
import pytest
from classifier.pre_filter import pre_filter
from taxonomy.rcm_taxonomy import TAXONOMY

REQUIRED_FIELDS = {"category", "confidence", "reasoning", "is_near_miss", "near_miss_reasoning"}


def _make_log(text: str, log_id: str = "test_001") -> dict:
    return {"log_id": log_id, "input": text, "output": text}


def test_pre_filter_returns_none_on_no_keyword_match():
    log = _make_log("everything was fine and the task completed normally")
    assert pre_filter(log) is None


def test_pre_filter_hits_correct_mode_for_clear_keyword_match():
    # TOOL_MISUSE keywords: "wrong tool", "misapplied", "incorrect parameter", etc.
    log = _make_log("agent used wrong tool with incorrect parameter causing unintended side effect")
    result = pre_filter(log)
    assert result is not None
    assert result["category"] == "TOOL_MISUSE"


def test_pre_filter_result_has_all_required_fields():
    log = _make_log("agent used wrong tool with incorrect parameter causing unintended side effect")
    result = pre_filter(log)
    assert result is not None
    for field in REQUIRED_FIELDS:
        assert field in result, f"Missing field: {field}"


def test_pre_filter_is_near_miss_is_boolean():
    log = _make_log("agent used wrong tool with incorrect parameter causing unintended side effect")
    result = pre_filter(log)
    assert result is not None
    assert isinstance(result["is_near_miss"], bool)


def test_pre_filter_category_is_valid_taxonomy_key():
    log = _make_log("agent used wrong tool with incorrect parameter causing unintended side effect")
    result = pre_filter(log)
    assert result is not None
    assert result["category"] in TAXONOMY, \
        f"Pre-filter returned category '{result['category']}' not in TAXONOMY"
