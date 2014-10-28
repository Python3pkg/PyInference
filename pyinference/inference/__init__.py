# coding=utf-8

__author__ = 'sejros'

""" Модуль предоставляет возможность работы с логическим выводом.

Смешанная сеть вывода позволяет в произвольном порядке комбинировать детерминистскую, Байесовскую и
лингвистическую схемы логического вывода в единой вероятностной графовой модели, которая, уже не являясь чисто
вероятностной моделью. Применение таких
смешанных графовых сетей позволяет значительно расширить их аппликативность в задачах математического
моделирования социо-экономических процессов, формализации качественных и нечетких экспертных оценок. За счет
предоставления единого интерфейса моделирования при использовании различных математических методов для логического
вывода может улучшить гибкость и вариативность получаемых моделей.


Пример "Студенты"
+++++++++++++++++

.. note::
    Данный пример взят из курса "Probabilistic graphical models" Стэнфордского университета.

Допустим, мы моделируем получение студентом отметки на экзамене. Студент может получить три оценки: "отлично", "хорошо"
и "удовлетворительно". То, какую из них он получит, зависит от двух параметров: интеллекта студента и сложности
предмета. Соответственно, чем умнее студент, тем выше вероятность получения высшей отметки. Однако, чем сложнее курс,
тем эта же вероятность ниже.

Для упрощения, положим что курсы однозначно делятся на сложные и простые (в реальной жизни
можно воспользоваться нечетким классификатором сложности курса, состоящим из двух термов, на дальнейшие рассуждения это
не повлияет), причем из всех возможных курсов 60% - простые, а 40% - сложные. Соответственно, вероятность того, что курс
окажется сложным - 0,4.

Также, положим, что студенты бывают умные (30%) и все остальные (70%).

Зададим вероятность получения той или иной оценки при всех возможных комбинациях заданных параметров:

=========== =========== =================== ===========
Сложность   Интеллект   Оценка              Вероятность
=========== =========== =================== ===========
простой     низкий      отлично             0,3
простой     низкий      хорошо              0,4
простой     низкий      удовлетворительно   0,3
простой     высокий     отлично             0,9
простой     высокий     хорошо              0,08
простой     высокий     удовлетворительно   0,02
сложный     низкий      отлично             0,05
сложный     низкий      хорошо              0,25
сложный     низкий      удовлетворительно   0,7
сложный     высокий     отлично             0,5
сложный     высокий     хорошо              0,3
сложный     высокий     удовлетворительно   0,2
=========== =========== =================== ===========

Приступим к созданию наших переменных.

Импортируем модуль :mod:`numpy`, который нам понадобится для работы с распределениями

    >>> import numpy as np

Создаем переменные и соответствующие им факторы.

    >>> d = Variable(name='Difficulty', terms=['easy', 'hard'])
    >>> D = Factor(name='D', cons=[d])
    >>> D.cpd = np.array([0.6, 0.4])

    >>> i = Variable(name='Intelligence', terms=['low', 'high'])
    >>> I = Factor(name='I', cons=[i])
    >>> D.cpd = np.array([0.7, 0.3])

    >>> g = Variable(name='Grade', terms=['exellent', 'good', 'bad'])
    >>> G = Factor(name='G|I,D', cond=[i, d], cons=[g])
    >>> G.cpd = np.array([0.3, 0.4, 0.3,
    ...                   0.05, 0.25, 0.7,
    ...                   0.9, 0.08, 0.02,
    ...                   0.5, 0.3, 0.2]).reshape((2, 2, 3))

Для усложнения, добавим в модель еще две переменные. Допустим, студент сдает единый экзамен, результат которого зависит
только от его интеллекта, так как экзамен имеет стандартизированную сложность:

    >>> s = Variable(name='SAT', terms=['failed', 'passed'])
    >>> S = Factor(name='S|I', cond=[i], cons=[s])
    >>> S.cpd = np.array([[0.95, 0.05], [0.2, 0.8]])

Также, допустим, что в зависимости от оценки студента по данному предмету ему может быть дано рекомендательное письмо.
Будет ли оно дано, зависит от его оценки: чем выше оценка, тем выше вероятность вручения письма:

    >>> l = Variable(name='Letter', terms=['denied', 'provided'])
    >>> L = Factor(name='L|G', cond=[g], cons=[l])
    >>> L.cpd = np.array([[0.1, 0.9], [0.4, 0.6], [0.99, 0.1]])

Создаем байесовскую сеть, куда включам все созданныем нами факторы:

    >>> BN = Net(name='student', nodes=[D, I, G, S, L])

Таким образом, наша сеть соответствует графу::

    digraph student{
        D -> G;
        I -> G -> L;
        I -> S
    }

Вычисляем и сохраняем запросы к данной сети.

Например, вычислим, какова вероятность того, что студент умный при известных нам сложности курса и его оценке:

    >>> q1 = BN.query(query=[i], evidence=[g, d])
    >>> print q1.cpd
    [[[ 0.85714286  0.14285714]
      [ 0.61538462  0.38461538]
      [ 0.3         0.7       ]]
    <BLANKLINE>
     [[ 0.64285714  0.35714286]
      [ 0.21052632  0.78947368]
      [ 0.09090909  0.90909091]]]

Какова вероятность того, что студент умный, если мы знаем только сложность курса:

    >>> q2 = BN.query(query=[i], evidence=[d])
    >>> print q2.cpd
    [[ 0.49138756  0.50861244]
     [ 0.4959897   0.5040103 ]]

Как мы видим, интеллект не зависит от сложности курса, как и могло быть понятно из описания модели.

Какова вероятность того, что студент умный, если мы знаем только его оценку по предмету, но не знаем трудности этого
предмета:

    >>> q3 = BN.query(query=[i], evidence=[g])
    >>> print q3.cpd
    [[ 0.72180451  0.27819549]
     [ 0.53427065  0.46572935]
     [ 0.28198433  0.71801567]]

Или, например, какова вероятность получения письма в зависимости от интеллекта судента:

    >>> q4 = BN.query(query=[l], evidence=[i])
    >>> print q4.cpd
    [[ 0.37612807  0.62387193]
     [ 0.6374464   0.3625536 ]]


Пример "Диагностика"
++++++++++++++++++++

.. note::
    Данный пример взят из курса "Machine learning" Стэнфордского университета.

Рассмотрим пример, иллюстрирующий пример медицинской диагностики. У нас есть редкая болезнь (вероятность 0,1%) и
медицинский тест на выявление этой болезни. Этот тест имеет определенную точность и в редких случаях может давать
ложноположительные или ложноотрицательные результаты. В частности, вероятность того, что при отсутствии болезни
тест даст ложноположительный результат - 0,2. Вероятность соответственно ложноотрицательного результата - 0,1.
Требуется выяснить, какова вероятность наличия у пациента этой болезни, если тест дал положительный результат.

Представим имеющиеся у нас данные в виде факторов. У нас есть две переменные (и соответствующие им факторы):

- наличие болезни:

=============== ===========
Наличие болезни Вероятность
=============== ===========
есть            0,001
нет             0,999
=============== ===========

- результаты теста:

=============== =============== ===========
Наличие болезни Результат теста Вероятность
=============== =============== ===========
есть            положительный   0,001
есть            отрицательный   0,999
нет             положительный   0,001
нет             отрицательный   0,999
=============== =============== ===========

Построим нашу Байесовскую сеть:

    >>> import numpy as np

    >>> BN = Net()

    >>> c = Variable(name='cander', terms=['no', 'yes'])
    >>> C = Factor(name='C', cons=[c])
    >>> C.cpd = np.array([0.999, 0.001])
    >>> BN.add_node(C)

    >>> t = Variable(name='test', terms=['pos', 'neg'])
    >>> T = Factor(name='T|C', cons=[t], cond=[c])
    >>> T.cpd = np.array([[0.2, 0.8], [0.9, 0.1]])
    >>> BN.add_node(T)

Выполним запрос к сети:

    >>> q1 = BN.query(query=[c], evidence=[t])
    >>> print q1.cpd
    [[  9.95515695e-01   4.48430493e-03]
     [  9.99874891e-01   1.25109471e-04]]

Выведем отдельно только интересующую нас вероятность

    >>> "%0.4f" % q1.cpd[0,1]
    '0.0045'

Как мы видим, несмотря на положительный результат теста, вероятность наличия этой болезни выросла с 0,1% до всего 4,5%.
Несмотря на парадоксальность, это абсолютно верный результат при таких исходных данных. Надежность теста
компенсируется редкостью болезни.

Детерминистический вывод
++++++++++++++++++++++++

Для иллюстрации детерминистического вывода создадим сеть, соответствующую операции конъюнкции алгебры логики.
У нас есть три бинарные переменные (A, B и C), связанные соотношением C = A & B. Напомним таблицу истинности для
конъюнкции

= = =
A B C
= = =
0 0 0
0 1 0
1 0 0
1 1 1
= = =

Эта таблица может быть представлена как фактор P(C|A,B):

= = = ===
A B C P
= = = ===
0 0 0 1.0
0 0 1 0.0
0 1 0 1.0
0 1 1 0.0
1 0 0 1.0
1 0 1 0.0
1 1 0 0.0
1 1 1 1.0
= = = ===

Так как распределение значений переменных A и B нам неизвестно, оставим значения по умолчанию (равномерное
распределение):

    >>> import numpy as np

    >>> BN = Net()

    >>> a = Variable(name='a', terms=[0, 1])
    >>> A = Factor(name='A', cons=[a])
    >>> BN.add_node(A)

    >>> b = Variable(name='b', terms=[0, 1])
    >>> B = Factor(name='B', cons=[b])
    >>> BN.add_node(B)

    >>> c = Variable(name='c', terms=[0, 1])
    >>> C = Factor(name='C', cons=[c], cond=[a, b])
    >>> C.cpd = np.array([1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0]).reshape(C.shape)
    >>> BN.add_node(C)

    >>> q1 = BN.query(query=[a], evidence=[c, b])
    >>> q1
    Conditional:
    [a]|[b, c]
    [b, c, a]
    (2, 2, 2), (2, 2, 2)
    [0, 0, 0]    0.5
    [0, 0, 1]    0.5
    [0, 1, 0]    0.0
    [0, 1, 1]    0.0
    [1, 0, 0]    1.0
    [1, 0, 1]    0.0
    [1, 1, 0]    0.0
    [1, 1, 1]    1.0
    Sum: 3.0
    <BLANKLINE>

Классы модуля
+++++++++++++

"""


# TODO шаблонное задание факторов
# TODO бинарные переменные
# TODO шаблонное добавление переменной (и фактора) в сеть
# TODO вычисление фактора (алгоритм Мамдани)