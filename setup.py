# type: ignore
"""Super-duper comments about ZFS pools for QubesOS
TODO update this with more info
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qubes-storage-zfs",
    version="0.2.0",
    author="CFCS",
    author_email="cfcs@github.com",
    description="ZFS pool storage for QubesOS VMs",
    license="BSD License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cfcs/qubes-storage-zfs",
    packages=["qubes_storage_zfs"],
    entry_points={
        "qubes.storage":
        ["testzfs = yozfs_qubes:TestZFS"]
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: BSD License",
        "Operating System :: QubesOS",
    ],
    python_requires=">=3.5",
    install_requires=["qubes", "pyzfs"],
    extras_require={'pyzfs': 'pyzfs>=0.8.0', 'qubes': 'qubes>=4.1.0'},
    include_package_data=True,
)
