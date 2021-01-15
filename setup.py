import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="map-api",
    version="1.0.0",
    license="BSD",
    description="API for the Embeddable MAP",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "boto3"],
    extras_require={"test": ["pytest"]},
)