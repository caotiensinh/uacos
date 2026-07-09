from scripts.check_english_docs import scan_repo


def test_language_check_allows_english_text(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n\nThis project uses English documentation.\n", encoding="utf-8")
    (tmp_path / "app.py").write_text('"""English docstring."""\nVALUE = 1\n', encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "pass"
    assert result["finding_count"] == 0


def test_language_check_flags_vietnamese_text(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n\nTài liệu này dùng tiếng Việt.\n", encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "fail"
    assert result["finding_count"] >= 1
    assert result["findings"][0]["file"] == "README.md"


def test_language_check_flags_cjk_text(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n\n日本語の文章です。\n", encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "fail"
    assert result["finding_count"] >= 1
