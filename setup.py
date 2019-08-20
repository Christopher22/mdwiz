import setuptools

# Create the long description for README
with open("README.md", "r") as fh:
    long_description = fh.read()

# Split the setup and the specification of required packages. More a thing of personal taste.
with open("requirements.txt", "r") as f:
    required_packages = [
        line.strip() for line in f.read().splitlines() if not line.startswith("#")
    ]

setuptools.setup(
    name="mdwiz",
    version="0.0.1",
    author="Christopher Gundler",
    author_email="christopher@gundler.de",
    description="A helper for creating complex documents in Markdown",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Christopher22/mdwiz",
    install_requires=required_packages,
)
