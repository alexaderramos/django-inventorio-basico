# Inventario Basico con Django y SQLite
Pasos para poner en funcionamiento el proyecto:
```
python manage.py makemigrations homepage
python manage.py migrate homepage
python manage.py makemigrations inventory
python manage.py migrate inventory
python manage.py makemigrations transactions
python manage.py migrate transactions
```
Después de la primera vez, se puede ejecutar lo siguiente para migrar cambios de modelo en cualquier aplicación
```
python manage.py makemigrations
python manage.py migrate
```
Utilice el siguiente comando para ejecutar el servidor
```
python manage.py runserver
```
Utilice el siguiente comando para crear un usuario administrador 
```
python manage.py createsuperuser
```
