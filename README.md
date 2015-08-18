#Microblog use Flask
A simple blog use Flask framework

#Install
###Create virtualenv 
use easy_install
```
$ easy_install virtualenv
```

or use pip

```
$ pip install virtualenv
```
###Create flask env
```
$ virtualenv flask
```
and activate env
```
$ source flask/bin/activate
```

###Install dependencies packages
```
$ pip install -r requirements.txt
```

###Create database
Windows:
```
$ flask\Scripts\python db_create.py
```

Linux:
```
$ ./flask/bin/python db_create.py
```

###Running server
Windows:
```
$ flask\Scripts\python run.py
```

Linux:
```
$ ./flask/bin/python run.py
```