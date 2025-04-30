from typing import Any, Dict


def tlform_comparer(form_field: Dict[str, Any], user_prefs: Dict[str, Any]) -> None:
    """Print Jaccard scores for *every* preference key against ``form_field``.

    Args
    ----
    form_field : Dict[str, Any]
        Must contain ``"opt_y"`` and ``"opt_n"`` lists from the extracted field.
    user_prefs : Dict[str, Any]
        Entire JSON object loaded from *usr_prefs.json*.
    """

    # Normalize form options (selected + unselected) to lowercase strings
    form_opts = {
        str(o).strip().lower() for o in (form_field["opt_y"] + form_field["opt_n"])
    }

    def _walk(key: str, val: Any) -> None:
        """Recursively descend prefs and print Jaccard for each leaf key."""
        if isinstance(val, dict):
            for sub_k, sub_v in val.items():
                _walk(sub_k, sub_v)
        else:
            pref_vals = val if isinstance(val, list) else [val]
            pref_opts = {str(v).strip().lower() for v in pref_vals}
            inter = len(form_opts & pref_opts)
            union = len(form_opts | pref_opts)
            score = inter / union if union else 0.0
            print(f"{key}: {score:.2f}")

    # Kick off recursion for each top‑level preference section
    for k, v in user_prefs.items():
        _walk(k, v)
