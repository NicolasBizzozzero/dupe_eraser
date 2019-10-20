# dupe_eraser
## A command-line tool which automate the deletion of duplicate files.
The software will then look for theses files on your current directory and delete automatically all the duplicates found for theses files.
For example, if you want to delete the duplicates of all the files presents in the directory "~/directory", your command will look like this :
```shell
$ dupe_eraser ~/directory
```
By default, the program print out all the duplicates he find without deleting them. This behavior can be changed with the '--behavior' parameter.
*dupe_eraser* come with a little bit of options :

| Option        | Shortcut      | Description      |
| ------------- |:-------------:| -----------------|
| behavior    | -b | Behavior to adopt when encountering a duplicate file. 'c' for checking, only print the files then exit. 'd' for delete. 's' for safe, move the files in a safe directory. |
| recursive     | -r     |   Look also for duplicates in the sub directories of your current directory        |
| shallow     | -s     |   If two files have the same hash, perform a shallow comparison before acting on them.        |
| safe-directory     | -S     |   The name of the directory used during safe mode.        |
| hashing     | -H    | The hashing algorithm used to compare hashes between files             |
| phashing     |     | Set this flag to enable perceptual hashing on pictures             |
| perceptual-hashing-algorithm     |     | The perceptual hashing algorithm used to compare hashes between files             |
| quiet |-q  |    Produce absolutely no output on stdout |
| help | -h      |   Give a help list and a short usage message     |   
| disable-progress-bar |     | Set this flag if you want to completely disable the progress bar.  | 


## TODO
* Memory_consumption safe parameter for when the hashes cannot be stored all at once. Recompute hashed each time.
* Batch-size of files to inspect
