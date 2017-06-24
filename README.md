# dupe_eraser
## A command-line tool which automate the deletion of duplicate files.

The software will then look for theses files on your current directory and delete automatically all the duplicates found for theses files.
For example, if you want to delete the duplicates of all the files presents in the directory "~/directory", your command will look like this :
```shell
$ dupe_eraser
```
By default, the program delete all the duplicates passed by argument without warning. It'll also delete them only on your current directory and not on sub directories. If non-files are passed by argument, they'll be ignored.

dupe_eraser come with a little bit of options :

| Option        | Shortcut      | Description      |
| ------------- |:-------------:| -----------------|
| safe    | -s | Put duplicate files in a folder instead of delete them (by default, "__safedelete") |
| recursive     | -r     |   Look also for duplicates in the sub directories of your current directory        |
| check | -c     |    Print the duplicates files if they exist whiteout deleting or moving anything      |
| quiet |-q  |    Produce absolutely no output |
| verbose | -v     |   Produce verbose output      |    
| help | -?      |   Give a help list and a short usage message     |   
| version | -V     |    Print program version     | 

___

Feel free to contact me if you have any issue, suggestion or criticism about dupe_eraser.
I'll be glad to help you or to listen to your advices !
___

## Special thanks :
* docopt
* path.py
