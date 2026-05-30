from taxonomy.rcm_taxonomy import TAXONOMY

EXPECTED_MODES = {
    "GOAL_DRIFT",
    "AUTHORITY_CONFUSION",
    "CONTEXT_LOSS",
    "TOOL_MISUSE",
    "ESCALATION_FAILURE",
}


def test_all_five_modes_defined():
    assert set(TAXONOMY.keys()) == EXPECTED_MODES


def test_each_mode_has_description():
    for mode, data in TAXONOMY.items():
        assert "description" in data, f"{mode} missing description"
        assert isinstance(data["description"], str)
        assert len(data["description"]) > 0


def test_each_mode_has_keywords():
    for mode, data in TAXONOMY.items():
        assert "keywords" in data, f"{mode} missing keywords"


def test_keywords_are_non_empty_lists():
    for mode, data in TAXONOMY.items():
        assert isinstance(data["keywords"], list), f"{mode} keywords not a list"
        assert len(data["keywords"]) > 0, f"{mode} keywords list is empty"


def test_no_legacy_modes_present():
    legacy = {"loss_of_function", "partial_function", "unintended_function",
              "delayed_function", "erratic_function", "hidden_failure"}
    assert not legacy.intersection(set(TAXONOMY.keys())), \
        "Legacy RCM modes still present in taxonomy"
