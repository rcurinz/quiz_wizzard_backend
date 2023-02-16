# TransQuest Backend
A Natural Language Processing  web with Hugging Face Transformers

## Technologies involved 👩‍💻
```
Git
Python
Flask
*XAMPP
```
* You must create a DB wich should be linked in config.py as :
```py
# DATABASE
# MySQL
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:<PASSWORD>@localhost/<YOUR DB>?charset=utf8mb4'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/<YOUR DB>?charset=utf8mb4'
```
Replacing <YOUR DB> for your DB name.

## RUN PROJECT
* For this proyects you will need the following librarys
```py
   pip install deep_translator
   pip install Flask
   pip install Flask-SQLAlchemy
   pip install Hashids
   pip install pymysql
   pip instal FlaskCors
   pip install PYPDF2
   pip instapp python-docx
   pip install git+https://github.com/PrithivirajDamodaran/Parrot_Paraphraser.git *
```
* We recommend you to follow the installation guide for Parrot provided in https://github.com/PrithivirajDamodaran/Parrot_Paraphraser#install
* You also want to edit your security policies with
```py
  Set-ExecutionPolicy Unrestricted
```

## EXECUTION
Once you had all the items above ready just run the run.py  and you're ready

## Authors ✒️
_Developer_
* **René Curin** - *developer* - [rcurinz](https://github.com/rcurinz)
