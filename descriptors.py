# coding: utf-8
#! from prescons.utils import clear_screen; clear_screen()
###
#
# Дескрипторы в теории и на практике
#
# Стас Рудаков
#   s_rudakou@wargaming.net
#
# 15 мая 2013 г.
#
# https://github.com/nott/talks/blob/master/descriptors.py
#
###

##################################
#! clear_screen()
# кто я такой и зачем #
#######################

# 1. меня зовут Стас

# 2. я программирую программы для Wargaming.net

# 3. еще я считаю, что Python крутой

# 4. и у меня есть аргументы!

##################################
#! clear_screen()
# функции против методов #
##########################

def func(x):
    print(repr(x))

class Klass:
    def method(self):
        print(repr(self))

# вызов функции
func(5)

# вызов метода
instance = Klass()
instance.method()
Klass.method(instance)

# функция может быть методом
Klass.func1 = func
instance.func1()

# обратное тоже верно: метод может быть функцией
Klass.method(5)

# но иногда...
instance.func2 = func
instance.func2()

##################################
#! clear_screen()
# методы класса #
#################

class Klass:
    def method(cls):
        print(repr(cls))
    method = classmethod(method)
    # @classmethod
    # def method():
    #     print(repr(cls))

instance = Klass()

# вызываем метод объекта
instance.method()

# вызываем метод класса
Klass.method()

##################################
#! clear_screen()
# свойства #
############

class Klass:
    @property
    def field(self):
        import random
        return random.random()

instance = Klass()

# обращаемся к свойству как к полю
instance.field

# но все-таки свойство вычисляется
instance.field

##################################
#! clear_screen()
# Поля — это не то, чем они кажутся. #
######################################

# класс с разными видами полей
class Klass:
    field = 'field (klass)'
    klass_field = 'klass_field'
    def __init__(self):
        self.field = 'field (instance)'
        self.instance_field = 'instance_field'

# вспоминаем, как получить доступ к полям
instance = Klass()
instance.klass_field
instance.instance_field
instance.field

# Ага!
Klass.field = property(lambda self: 5)
instance.field

# Еще немного магии :)
Klass.field = classmethod(lambda self: 5)
instance.field

##################################
#! clear_screen()
# Descriptor protocol #
#######################

# наследование от object обязательно в Py2, в Py3 его можно опустить
class Descriptor(object):
    def __init__(self, arg):
        print('I\'m init, {0}'. format(arg))
    #
    def __get__(self, obj, objtype=None):
        return 'I\'m get for {0} ({1})'.format(obj, objtype)
    #
    def __set__(self, obj, value):
        print('I\'m set for {0}: {1}'.format(obj, value))
    #
    def __delete__(self, obj):
        print('I\'m delete for {0}'.format(obj))

class Klass:
    field = Descriptor('indeed')

instance = Klass()

# вся магия внутри __getattribute__
instance.field
Klass.field

instance.field = 5

del instance.field
del instance.field

##################################
#! clear_screen()
# Эмулируем classmethod #
#########################

# зададим свой дескриптор для classmethod
class ClassMethod(object):
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        def newfunc(*args):
            return self.func(klass, *args)
        return newfunc

class Klass:
    @ClassMethod
    def method(cls, *args):
        print('Class {0!s}, arguments {1!r}'.format(cls, args))

# хм... действительно newfunc
Klass.method

# проверяем на классе
Klass.method(1, 2, 3)

# проверяем на объекте
Klass().method(3, 2, 1)

##################################
#! clear_screen()
# Функции - это тоже дескрипторы #
##################################

def func(*args):
    print(repr(args))

class Klass:
    method = func

instance = Klass()

# привычный способ обращения к методам
instance.method
Klass.method

# менее привычный способ
func.__get__(instance, Klass)
func.__get__(None, Klass)

# зачем все это было придумано
instance.method()

##################################
#! clear_screen()
# Кэширующее свойство #
#######################

class cached_property(object):
    def __init__(self, func):
        self.func = func
    #
    def __get__(self, instance, type=None):
        print('__get__')
        if instance is None:
            return self
        #
        missing = object()
        cache = instance.__dict__.get(self.func.__name__, missing)
        #
        if cache is missing:
            cache = instance.__dict__[self.func.__name__] = self.func(instance)
        #
        return cache
    #
    def __set__(self, instance, value):
        print('__set__')
        instance.__dict__[self.func.__name__] = value

class Klass:
    @cached_property
    def field(self):
        import random
        return random.random()

instance = Klass()

# где мой random?
instance.field
instance.field

# подменяем значение
instance.field = 1.0
instance.field

##################################
#! clear_screen()
# Правильное кэширующее свойство #
##################################

class cached_property(object):
    ''' cached property without __set__ (non-data descriptor) '''
    def __init__(self, func):
        self.func = func
    def __get__(self, instance, type=None):
        print('__get__')
        if instance is None:
            return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res

class Klass:
    @cached_property
    def field(self):
        import random
        return random.random()

instance = Klass()

# где мой random?
instance.field

# обратите внимание - не будет вызова print
instance.field

# наш cached_property - пример non-data дескрипторов
# встроенный property - это data дескриптор

#######################
#! clear_screen()
# Настраиваемые базовые классы #
################################

#! View, AnotherModel, DjangoModel, ModelForm, cached = object, None, None, object, lambda x: x

class ModelView(View):
    model = DjangoModel
    def get_model(self):
        return self.model
    # cached('X') аналогичен cached_property(get_X)
    cached_model = cached('model')

# легко настраиваем наследников
class AnotherModelView(ModelView):
    model = AnotherModel

# даже когда настройка нетривиальная
class CustomModelView(ModelView):
    def get_model(self):
        if self.cached_user.is_superuser:
            return DjangoModel
        return AnotherModel

# если обращаться только к cached_*, можно автоматически строить граф вызовов!
class FormView(ModelView):
    def get_form_class(self):
        class Form(ModelForm):
            class Meta:
                model = self.cached_model
        return Form
    cached_form_class = cached('form_class')
    def get_form(self):
        return self.cached_form_class(self.request.POST or None)
    cached_form = cached('form')

#######################
#! clear_screen()
# Ну и что делать дальше? #
###########################

# * Почитать The Inside Story on New-Style Classes
#   http://python-history.blogspot.com/2010/06/inside-story-on-new-style-classes.html  
# * Почитать Descriptor HowTo Guide
#   http://docs.python.org/3/howto/descriptor.html
# * grep __get__ внутри site-packages
# * реализовать дескриптор cached из последнего примера
# * Задавать вопросы!

# https://github.com/nott/talks/blob/master/descriptors.py
