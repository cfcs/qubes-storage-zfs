#!/usr/bin/env bash
# Generate an image for the dom0 Xorg background wallpaper

dataset='qbs'

{
    date
    echo
    /usr/sbin/zpool status -v 2>&1 | sed 's/^\t/    /g'
    echo
    /usr/sbin/zfs list -o name,keystatus,ratio,lused,avail "${dataset}"
    echo
    df -h /
    echo
    /usr/sbin/zdump 'Europe/London' 'Europe/Moscow'
} \
| convert -family 'DejaVu Sans Mono' -pointsize 16 \
    -background '#152233' \
    -fill white label:@- \
    ~/my-background.png
