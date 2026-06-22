from viroconstrictor_data.validation import validate_package


def test_packaged_data_is_valid() -> None:
    issues = validate_package()
    assert issues == []
