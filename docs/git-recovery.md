# Broken git repo

## recover files from dangling tree

    # git fsck
    ...
    dangling tree 1401ec5e64c8e1d955b2bc53008c0bb0bb1114e9
    ...
    git cat-file -p 1401ec5e64c8e1d955b2bc53008c0bb0bb1114e9
    ...
    100644 blob 9f17e84461a1d33864d82647819e58d770f070ba        some_lost_file.jpg
    ...
    git cat-file -p 9f17e84461a1d33864d82647819e58d770f070ba > /tmp/some_lost_file.jpg

Or

    git cat-file -p 1401ec5e64c8e1d955b2bc53008c0bb0bb1114e9 | grep blob | awk '{print "git cat-file -p "$3" > ../recover/"$3"_"$4}'


## Recover files without references

    # git fsck --unreachable --no-reflogs --full --name-object
    ....
    unreachable tree deff1f08792c6fa4cbe3e1521bf5e6486306a5ad
    ....


Size of file:

    git cat-file -s deff1f08792c6fa4cbe3e1521bf5e6486306a5ad

Save file:

    git cat-file -p deff1f08792c6fa4cbe3e1521bf5e6486306a5ad > /tmp/somefile
