# qubes-storage-zfs - ZFS pool storage for VMs in QubesOS

# THIS IS NOT READY FOR OTHER PEOPLE TO USE

TODO implement all the semantics described in https://dev.qubes-os.org/projects/core-admin/en/latest/qubes-storage.html#storage-pool-driver-api
- [ ] snap_on_start (snapshot on start; should be simple
- [ ] save_on_stop (rollback if no stop?)
  - [ ] presumably this is related to `revert()`
- [ ] fix and test `import()`
- [ ] figure out when the spurious fallback to file-based stuff happens
- [ ] make `resize()` actually resize
- [ ] implement listing of snapshots in `revisions()`
- [ ] `block_device()` and `export()` should block until `udev` gets a chance to catch up

**TODO figure out how to prevent root-cow.img (private-cow.img as well??) from being written to /var/lib/qubes/appvms/{vmname}/ despite using one of the ZFS pool drivers**

TODO address review comments from marek in https://github.com/QubesOS/qubes-core-admin/pull/289

TODO when we try to unload the key, we are relying on potentially outdated information if qubesd has been restarted. we need to check if VMs are actually running.

TODO incorporate descriptions from https://github.com/QubesOS/qubes-core-admin/pull/289

Storage pool drivers implement new ways to store the data related to your VMs in QubesOS; the code in this repository will let you store your VMs on the ZFS file system.

This project implements two "storage pool drivers" for QubesOS.
- [`zfs_zvol`](#zfs_zvol)
- [`zfs_encrypted`](#zfs_encrypted)

See [Installation](#Installation) at the bottom for instructions on installing this pool driver.

TODO clarify zpool vs qubes pool. Clarify what a ZFS dataset is.

## `zfs_zvol`
Given one or more block devices, a ZFS `zpool` is initialized, and VMs created in this pool will be stored in datasets/zvols in that zpool.

There is no additional encryption involved, so it is probably desirable to do this on top of a LUKS-encrypted block device.

```shell
# List options:
qvm-pool --help-drivers

qvm-pool -o block_devices='/dev/mapper/luks-myblock' -a mypool zfs_zvol
qvm-pool -i mypool
qvm-create -P mypool --label red myplainvm

zfs list -r mypool
# mypool
# mypool/vm
# mypool/vm/myplainvm
# mypool/vm/myplainvm/private
# mypool/vm/myplainvm/volatile
```

TODO may want to explain how to make a separate pool for `volatile` volumes.

## `zfs_encrypted`
Given a zfs dataset, an encrypted dataset will be created within the parent dataset. The VMs will be stored inside the encrypted dataset. When VMs within the encrypted storage pool are about to be started, you will be prompted for a decryption passphrase. When there are no running/paused VMs (ie when all VMs are stopped), a countdown starts, after which the encryption keys are unloaded ("forgotten"). This is governed by the `unload_timeout` parameter which defaults to 20 minutes.

Usually you will want to first make a [`zfs_zvol`](#zfs_zvol) pool, then add one or more `zfs_encrypted` pools to that.

A dataset named `encryption` will be added to the root of the `zpool_name` dataset. Under the `encryption` dataset, a dataset bearing the name of the encrypted pool will be created.

TODO document what is/isn't encrypted (dataset names, where metadata is spilled in qubes.xml, volatile vols, dom0 swap, etc etc etc)

```shell
# List options:
qvm-pool --help-drivers

# Create the encrypted pool "myenc" on top of of the "mypool" zpool.
# You can optionally override default values for the arguments
#     ask_password_domain (default: dom0)
#         The GUI-enabled domain that will prompt for passphrases
#     unload_timeout (default: 1200)
#         The number of seconds to wait before forgetting the encryption
#         keys once all VMs in the pool are stopped.
qvm-pool -o zpool_name=mypool,unload_timeout=3600 myenc zfs_encrypted

# Create a new VM "myencvm" inside the "myenc" pool:
qvm-pool -P myenc --label green myencvm

zfs list -r mypool
# mypool
# mypool/encryption
# mypool/encryption/myenc
# mypool/encryption/myenc/myencvm
# mypool/encryption/myenc/myencvm/private
# mypool/encryption/myenc/myencvm/volatile
```

# Secure backups

ZFS comes with a beautiful (from a security point of view) unidirectional backup mechanism in the form of "zfs send" (see `man zfs-send` / `man zfs-recv`).

This makes it easy to design "data diode"-like backup flows, but it poses a problem in terms of verifying backup integrity (ie *"did the other end receive everything we sent?"*), and it precludes automatic resumption of transfers interrupted by transitive network failures. That's an issue when you have a terabyte of data to send over e.g. tor or wifi.

ZFS send/recv comes with a feature designed to deal with this, the *receive resume token* mechanism (`zfs send -t` / `zfs recv -s`), which lets you poll the receiving backup server for a serialized value that details how much data has been received, and what is left to send. Using `zfs get resumetok bla/blah` and `zfs send -t` you can resume an interrupted transfer, generating a new backup stream that starts off where the previous got cut.

If you use the `--raw` argument to `zfs send`, the stream will be sent roughly as it exists on disk. This enables taking backups of encrypted datasets without including the decryption keys in the backup stream (which is otherwise the default).

UNFORTUNATELY the *receive resume token* cannot be trusted when the backup server is an untrusted machine, since the *receive resume token* can ask for data not covered by the snapshot specifications passed on the original command-line. TODO solve that problem, and write up the problem in a more coherent manner.

TODO elaborate on backup/restore

TODO implement the "snapshot before start" / "snapshot after shutdown" features to mimick the thinlvm stuff and give examples of how to roll back

# Installation of this module

- Update your qubes system with `sudo qubes-dom0-update`
  - You specifically want at least version `4.1.x` of the `qubes-core-dom0` package.
  - TODO figure out a way to gracefully handle when we cannot populate the volumes/pools with enough info to ensure safe re-serialization to qubes.xml, see https://github.com/QubesOS/qubes-issues/issues/5723
    - this issue also pops up then the openzfs upstream breaks stuff, which happens.
- Install openzfs/zfsonlinux, at least version `0.8.0` is required. TODO support matrix might be nice. TODO link to instructions
- `make dist`
- copy `.tar.gz` to dom0   TODO howto
- TODO need to detail the installation of ask-password rpc service, and potentially make this repo produce an rpm that installs that.
   - see the files in the `qubes-rpc/` directory in this repo
   - here's an example of an RPM spec https://github.com/Rudd-O/qubes-pass/blob/master/qubes-pass.spec
- `sudo pip3 install qubes-storage-zfs-*.tar.gz`
   - TODO solve issue of how to use the system if the pool driver causes exceptions
- `sudo systemctl restart qubesd`
- `qvm-pool --help-drivers` should now list the `zfs_zvol` and `zfs_encrypted` drivers.
