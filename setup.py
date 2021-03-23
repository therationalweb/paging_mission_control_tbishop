import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='paging_mission_control_tbishop',
    version='0.0.1',
    description='This program generates JSON formatted alerts based on prescribed thresholds',
    long_description=long_description,
    author='Thomas Bishop',
    author_email='therationalweb@gmail.com',
    url="https://github.com/therationalweb/paging_mission_control_tbishop.git",
    project_urls={
        "Bug Tracker":"https://github/pypa/paging_mission_control_tbishop/issues",},
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License"
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires= ">3.6",
)
