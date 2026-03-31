import subprocess


def collect():
    """Collect installed apt/dpkg packages."""
    packages = []

    try:
        result = subprocess.run(
            ["dpkg-query", "-W", "-f=${Package}\t${Version}\n"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in result.stdout.strip().split("\n"):
            if "\t" in line:
                name, version = line.split("\t", 1)
                if name and version:
                    packages.append({
                        "name": name.strip(),
                        "version": version.strip(),
                        "source": "apt",
                    })
    except Exception:
        pass

    return packages