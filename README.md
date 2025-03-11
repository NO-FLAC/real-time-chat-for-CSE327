# Real-time chat
## Group-1
### Members
```
Daiyan Hossain Chowdhury 2111279642
Umaira Chowdhury 2020163042
Tanvir Anjum Neon 2131079642
Saif Uz Zaman
```
## Setup

#### - Create Virtual Environment
###### # Mac
```
python3 -m venv venv
source venv/bin/activate
```

###### # Windows
```
python3 -m venv venv
.\venv\Scripts\activate.bat
```

<br>

#### - Install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
pip install -U 'channels[daphne]'
```

<br>

#### - Migrate to database
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

<br>

#### - Run application
```
python manage.py runserver
```

<br>

#### - Generate Secret Key ( ! Important for deployment ! )
```
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
exit()
```


