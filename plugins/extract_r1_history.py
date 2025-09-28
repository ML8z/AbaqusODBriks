"""Plugin stub for extracting R1 history data from Abaqus."""


def _abaqus_modules_available() -> bool:
    """Return ``True`` if the Abaqus GUI modules can be imported."""
    try:
        __import__("abaqus")
        __import__("abaqusGui")
    except ImportError:
        return False
    else:
        return True


if _abaqus_modules_available():  # pragma: no cover - requires Abaqus runtime
    from abaqus import session  # type: ignore  # pragma: no cover
    from abaqusGui import getAFXApp  # type: ignore  # pragma: no cover

    def register_plugin() -> None:  # pragma: no cover - requires Abaqus runtime
        """Register the plugin inside an Abaqus/CAE session."""
        raise NotImplementedError(
            "This stub must be executed within an Abaqus environment."
        )

else:

    def register_plugin() -> None:
        """Fallback for environments where Abaqus is unavailable."""
        raise ImportError("Abaqus modules are not available")
