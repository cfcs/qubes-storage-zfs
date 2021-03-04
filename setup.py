# type: ignore
"""Super-duper comments about ZFS pools for QubesOS
TODO update this with more info
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qubes-storage-zfs",
    python_requires=">=3.5",
    install_requires=["qubes", "pyzfs"],
    extras_require={'pyzfs': 'pyzfs>=0.8.0', 'qubes': 'qubes>=4.1.0'},
    version="0.2.2",
    data_files=[
        ['/etc/qubes-rpc',['qubes-rpc/qubes.AskPassword']],
        ['/etc/qubes-rpc/policy', ['qubes-rpc/policy/qubes.AskPassword']]
    ],
    entry_points={
        "qubes.storage":
        [
            'zfs_zvol = qubes_storage_zfs.zfs:ZFSQPool',
            'zfs_encrypted = qubes_storage_zfs.zfs_encrypted:ZFSQEncryptedPool'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: BSD License",
        "Operating System :: QubesOS",
    ],
    long_description_content_type="text/markdown",
    description="ZFS pool storage for QubesOS VMs",
    author="CFCS",
    author_email="cfcs@github.com",
    url="https://github.com/cfcs/qubes-storage-zfs",
    license="BSD License",
    long_description=long_description,
    packages=setuptools.find_packages(),
)
