from scripts.check_english_docs import scan_repo


def test_language_check_allows_english_text(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n\nThis project uses English documentation.\n", encoding="utf-8")
    (tmp_path / "app.py").write_text('"""English docstring."""\nVALUE = 1\n', encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "pass"
    assert result["finding_count"] == 0


def test_language_check_flags_vietnamese_text(tmp_path):
    text = "# Demo\n\nT\u00e0i li\u1ec7u n\u00e0y d\u00f9ng ti\u1ebfng Vi\u1ec7t.\n"
    (tmp_path / "README.md").write_text(text, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "fail"
    assert result["finding_count"] >= 1
    assert result["findings"][0]["file"] == "README.md"


def test_language_check_flags_cjk_text(tmp_path):
    text = "# Demo\n\n\u65e5\u672c\u8a9e\u306e\u6587\u7ae0\u3067\u3059\u3002\n"
    (tmp_path / "README.md").write_text(text, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "fail"
    assert result["finding_count"] >= 1
