from setuptools import setup, find_packages

setup(
    name="swpy",
    version="0.1.0",
    author="Eunsu Park",
    author_email="eunsupark@kasi.re.kr",
    description="A package for space weater data analysis",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kasi-swpy/swpy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "sunpy",
        "astropy",
    ]
)