# Civility App

## Un vistazo a las personas

## Descripción
Civility app es un sistema de calificación de civilidad implementada con blockchain. Los usuarios podrán calificar positiva o negativamente a otros usuarios basados en sus experiencias por medio de una calificación del 1 al 5 y un comentario que justifique su crítica.

Código original en [este tutorial](https://www.ibm.com/developerworks/cloud/library/cl-develop-blockchain-app-in-python/index.html).


## Instrucciones

Clona el proyecto,

```sh
$ git clone https://github.com/sebassilva/civility
```



Crea un ambiente virtual, 
Python 2.7

```bash
pip -h
```
```bash
pip install virtualenv
```
```bash
virtualenv env
```
Mac OS / Linux
```bash
source mypython/bin/activate
```
Windows
```bash
mypthon\Scripts\activate
```

Instalar las dependencias
```bash
pip install -r ./requirements.txt
```



Inicia el primer nodo, repite este paso tantas veces como nodos quieras poner. Se recomiendan por lo menos 3 nodos. Es necesario ir cambiando el puerto, por ejemplo utilizando 8002 y 8003 y así consecutivamente. 

```sh
# Para usuarios de windows: https://flask.palletsprojects.com/en/1.1.x/cli/#application-discovery
$ export FLASK_APP=node_server.py
$ flask run --port 8001
```



Abre otra terminal y corre el cliente. 
Opcionalmente, si deseas probar el frontend para que se conecte a otros nodos, puedes cambiar la línea: 
```sh
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8001"
```
al puerto que necesites.

```sh
$ python run_app.py
```

El cliente estará corriendo en el puerto local[http://localhost:5000](http://localhost:5000). Lo puedes consultar desde tu navegador.




Los pasos más importantes para llevar a cabo el procedimiento básico son: 

1. Registrar dos usuarios. Es importante que en el campo de node address pongas el puerto en el que corre alguno de los otros nodos, por ejemplo. 
```sh
localhost:8002
```
Nota que no se tiene la última diagonal ni tampoco http://.


2. Una vez que tienes los dos usuarios, es necesario dar click en el botón minar en el nodo en el que los registraste. Este nodo avisará a los demás nodos que hayas registrado. Si refrescas tu cliente, podrás ver en la parte de califiicaciones tus dos usuarios.

![image.png](/images/r.png)

3. Ya puedes calificar a unos usuarios con otros. Probablemente habrás notado que en la raíz del proyecto se han guardado llaves privadas. No las borres, pues ya no podrías volver a registrarte.




![image.png](/images/o.png)
![image.png](/images/c.png)


