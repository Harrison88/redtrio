"""Automated testing, linting, docs, and other scripts."""

import tempfile

import nox

nox.options.sessions = "safety", "tests"


@nox.session(python=["3.8"])
def tests(session):
    """Run the tests."""
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-trio"
    )
    session.run("pytest", *args)


locations = "src", "tests", "noxfile.py", "docs/conf.py"


@nox.session(python=["3.8"])
def lint(session):
    """Run flake8 with various plugins."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "darglint",
    )
    session.run("flake8", *args)


@nox.session(python="3.8")
def safety(session):
    """Check dependencies for security."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")


@nox.session(python="3.8")
def coverage(session):
    """Upload coverage data."""
    install_with_constraints(session, "coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session(python="3.8")
def docs(session):
    """Build the documentation."""
    install_with_constraints(session, "sphinx", "sphinx-autoapi")
    session.run("sphinx-build", "docs", "docs/_build")


def install_with_constraints(session, *args, **kwargs):
    """Install packages into a session, using poetry to constrain the version."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)
