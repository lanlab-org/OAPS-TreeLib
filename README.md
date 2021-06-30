What we architected
TreeLib所有的功能实现都在service.py一个文件中，我们将重构service.py，分出service层，model层和connection层，使服务（对数据库的操作）、模型、连接分离。

How we architected it
①修改了service.py 。service.py由原本的29kb变为26kb。

②增加了model.py。model.py有4k。

③增加了connect.py。connect.py有1k。

我们将原本service.py文件根据功能分为服务（对数据库的操作）、模型、连接三部分。其中模型部分写入model.py，服务部分写入service.py，连接部分写入connect.py。

最终实现接数据库、模型和服务（对数据库的操作）分离。
