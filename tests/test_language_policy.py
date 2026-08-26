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


def test_language_check_allows_unicode_runtime_literals_in_python(tmp_path):
    source = 'LABELS = {"ja": "\u65e5\u672c\u8a9e", "vi": "B\u1ea3ng \u0111i\u1ec1u khi\u1ec3n"}\n'
    (tmp_path / "localization.py").write_text(source, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "pass"
    assert result["finding_count"] == 0


def test_language_check_flags_non_english_python_comment(tmp_path):
    source = "# \u65e5\u672c\u8a9e\u306e\u30b3\u30e1\u30f3\u30c8\nVALUE = 1\n"
    (tmp_path / "app.py").write_text(source, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "fail"
    assert result["findings"][0]["line"] == 1


def test_language_check_flags_non_english_python_docstring(tmp_path):
    source = '"""\u65e5\u672c\u8a9e\u306e\u8aac\u660e\u3002"""\nVALUE = 1\n'
    (tmp_path / "app.py").write_text(source, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "fail"
    assert result["findings"][0]["line"] == 1


def test_language_check_allows_isolated_possessive_proper_noun(tmp_path):
    text = "## Setup for Chu\u1ed9t's LAN Ollama\n"
    (tmp_path / "README.md").write_text(text, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "pass"
    assert result["finding_count"] == 0


def test_language_check_does_not_treat_non_english_prose_as_proper_noun(tmp_path):
    text = "## L\u1ed7i h\u1ec7 th\u1ed1ng\n"
    (tmp_path / "README.md").write_text(text, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "fail"


def test_language_check_allows_explicit_next_line_exception(tmp_path):
    text = "<!-- language-policy: allow-non-english proper noun -->\n## Setup for Chu\u1ed9t's LAN Ollama\n"
    (tmp_path / "README.md").write_text(text, encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["status"] == "pass"
    assert result["finding_count"] == 0
