import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="celldancer",
    version="0.0.1",
    author="Wang Lab",
    author_email="gwang2@houstonmethodist.org",
    description="Study RNA velocity through neural network.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={'': ['model/*.pt']},
    include_package_data=True,
    python_requires=">=3.7.6",
)

