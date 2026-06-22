from viroconstrictor_data.aliases import resolve_pathogen_alias


class TestAliasResolution:
    def test_resolve_known_alias(self) -> None:
        assert resolve_pathogen_alias("covid") == "SARSCOV2"

    def test_resolve_canonical_name(self) -> None:
        assert resolve_pathogen_alias("INFLUENZA") == "INFLUENZA"

    def test_unknown_alias_falls_back_to_default(self) -> None:
        assert resolve_pathogen_alias("definitely-unknown") == "DEFAULT"
