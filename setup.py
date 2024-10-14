from setuptools import setup, find_packages

setup(
    name='pkg_vlr_player_elo',
    version='0.1',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # List your dependencies here, e.g.:
        # 'numpy>=1.21.0',
    ],
)