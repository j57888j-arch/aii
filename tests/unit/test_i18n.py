from app.core.i18n.loader import SUPPORTED_LANGUAGES, load_catalog, translate


def test_all_locales_have_same_keys():
    catalogs = [load_catalog(language) for language in SUPPORTED_LANGUAGES]
    expected = set(catalogs[0])
    assert all(set(catalog) == expected for catalog in catalogs[1:])


def test_unknown_language_falls_back_to_uz():
    assert translate("xx", "choose_language") == translate("uz", "choose_language")
