import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import logsumexp

connection = sqlite3.connect("database.db")
cursor = connection.cursor()
connection_2 = sqlite3.connect("tasks.db")
print(connection.total_changes)
cursor_2 = connection_2.cursor()
# получаем лист
coneHeight_db = cursor.execute("SELECT coneHeight FROM constants ORDER BY coneHeight DESC LIMIT 1").fetchall()
cylinderHeight_db = cursor.execute("SELECT cylinderHeight FROM constants ORDER BY cylinderHeight DESC LIMIT 1").fetchall()
Qufeed_db = cursor.execute("SELECT Qufeed FROM constants ORDER BY Qufeed DESC LIMIT 1").fetchall()
Qunderfl_db = cursor.execute("SELECT Qunderfl FROM constants ORDER BY Qunderfl DESC LIMIT 1").fetchall()
Fifeed_db = cursor.execute("SELECT Fifeed FROM constants ORDER BY Fifeed DESC LIMIT 1").fetchall()
psolid_db = cursor.execute("SELECT psolid FROM constants ORDER BY psolid DESC LIMIT 1").fetchall()
pfluid_db = cursor.execute("SELECT pfluid FROM constants ORDER BY pfluid DESC LIMIT 1").fetchall()
muliqour_db = cursor.execute("SELECT muliqour FROM constants ORDER BY muliqour DESC LIMIT 1").fetchall()
Mean_diameter = cursor_2.execute("SELECT Mean_diameter FROM Tasks ORDER BY Mean_diameter").fetchall()
# забираем значение
coneHeight = coneHeight_db[0][0]
cylinderHeight = cylinderHeight_db[0][0]
Qufeed = Qufeed_db[0][0]
Qunderfl = Qunderfl_db[0][0]
Fifeed = Fifeed_db[0][0]
psolid = psolid_db[0][0]
pfluid = pfluid_db[0][0]
muliqour = muliqour_db[0][0]
Mean_diameter = Mean_diameter[0][0]

print(Mean_diameter)
## расчет геометрии сгустителя

# расчет площади для  высоты
i = 0.01
height = []  # Текущая высота сгустителя
D = 30
height_step = 0.3
# coneHeight = 1.35 #м высота конуса
# cylinderHeight = 1 # высота цилиндра или высота ниже основания питающего колодца
lim = coneHeight + cylinderHeight
print(lim)
while i < lim:
    height.append(i)
    i = i + height_step

Diameter = np.zeros(len(height))  # Диаметр цилиндрической части
Square = np.zeros(len(height))

j = 0
while j <= 7:
    if height[j] <= cylinderHeight:
        Diameter[j] = D
    else:
        Diameter[j] = D - (height[j] - cylinderHeight) * D / coneHeight
    Square[j] = (3.14 * Diameter[j] ** 2) / 4
    j = j + 1

# Qufeed=350 #Расход питающего потока
Qinj = 20  # Расход разбавления
Q = Qufeed + Qinj  # Объемный расход всего, что поступает в сгуститель

# Qunderfl=90
QL = Q - Qunderfl  # Расход жидкого из сгустителя
QR = Qunderfl

# Fifeed=0.0159 #Объемная концентраци тв в питающей пульпе
cfeed = Fifeed * Qufeed / (Qufeed + Qinj)  # Объемная доля тв в питании
Qfloc=2 #Расход флокулянта %
Rowater = 1020  # Плотность воды
Cfloc_w = 0.005
Gfloc=Qfloc*Rowater*Cfloc_w #Массовый расход флокулянта
# psolid=3200 #Плотность тв
Gtv = Qufeed * psolid * Fifeed  # Массовый расход тв в питающем потоке
R=Gfloc/Gtv
# pfluid=1240 #Плотность жидкого
cfeed_wt = cfeed * psolid / (psolid * cfeed + (1 - cfeed) * pfluid)
g = 9.81
ccr = 0.03
sigma0 = 2
k = 6.5
# muliqour=0.0021 #Вязкость раствора
dfloc=(708+0.1133*R-112.6*100*cfeed_wt)*0.54*0.00001
pfluidrazbab = (pfluid * Qufeed * (1 - Fifeed) + Rowater * Qinj) / (
        Qufeed * (1 - Fifeed) + Qinj)  # Плотность жидксоти (алюминат+вода)
c_out = Q / Qunderfl * cfeed  # Доля тв на выходе
v = (dfloc ** 2 * g * (psolid - pfluidrazbab)) / (18 * muliqour)  # Скорость осаждения Стокса

## расчет пространственных скоростей
qf = np.zeros(len(height))
qtv_from = np.zeros(len(height))
q = np.zeros(len(height))
qR = np.zeros(len(height))
qL = np.zeros(len(height))
c1 = np.zeros(len(height))
fd = np.zeros(len(height))
ff = np.zeros(len(height))
k = 0
for k in range(len(height)):
    qf[k] = Q / Square[k] / 3600  # Скорость всего, что поступает в сгуститель
    qtv_from[k] = Qunderfl / Square[k] / 3600  # Скорость потока тв из сгустителя
    qL[k] = QL / Square[k] / 3600
    c1[k] = (qtv_from[k] - qL[k]) * cfeed / (qtv_from[k] + v)
    fd[k] = qtv_from[k] * c_out
    ff[k] = qf[k] * Fifeed
    k = k + 1

##значения для функции
dp = psolid - pfluidrazbab  # Разница плотностей тв и жидкого
Cmax = 1  # Максимальная концентрация
n = 87  # Безразмерный индекс стесненного осаждения
eps1 = 10e-4
h = -0.02  # Шаг модели
Fc = c_out
qtvtek = 0.01
x = 2.35
fbk = 0


## функция для расчета концентрации
def fbk__fun(c, Cmax, v, n):
    if (c < Cmax):
        Fun1 = v * c * (1 - c) ** n
    else:
        Fun1 = 0
    return Fun1


def dsigma2__fun(c, ccr, k, sigma0):  # функция для dsigma2
    if c > ccr:
        Fun2 = sigma0 * k / ccr * ((c / ccr) ** (k - 1))
    else:
        Fun2 = 0.00001
    return Fun2


def a_fun(c, fbk, dsigma2, dp, g):  # функция для расчета а
    if c == 0:
        Fun3 = 0
    else:
        Fun3 = fbk * dsigma2 / (dp * g * Fc)
    return Fun3


def FCC_fun(qtv_from, c, c_out, fbk, a, eps1):  # функция для расчета концентрации
    f1 = qtv_from * (c - c_out)
    f11 = fbk
    f2 = a
    f3 = eps1
    Fun4 = (f1 + f11) / (f2 + f3)
    return Fun4


iter1_x = np.zeros(218)
Solution = np.zeros(218)
j = 0
while x > -2:
    if (x <= 2.35) & (x > 2.11):
        qtvtek = qtv_from[7]

    if (x <= 2.11) & (x > 1.81):
        qtvtek = qtv_from[7]

    if (x <= 1.81) & (x > 1.51):
        qtvtek = qtv_from[6]

    if (x <= 1.51) & (x > 1.21):
        qtvtek = qtv_from[5]

    if (x <= 1.21) & (x > 0.91):
        qtvtek = qtv_from[4]

    if (x <= 0.91) & (x > 0.61):
        qtvtek = qtv_from[3]

    if (x <= 0.61) & (x > 0.31):
        qtvtek = qtv_from[2]

    if (x <= 0.31) & (x > 0.01):
        qtvtek = qtv_from[1]

    if x <= 0.01:
        qtvtek = qtv_from[0]

    ## Рунге-Кутт
    # k1
    fbk = fbk__fun(Fc, Cmax, v, n)
    dsigma2 = dsigma2__fun(Fc, Cmax, v, n)
    a = a_fun(Fc, fbk, dsigma2, dp, g)
    k1 = FCC_fun(qtvtek, Fc, c_out, fbk, a, eps1)
    # k2
    k2_Fc = Fc + k1 * h / 2
    fbk = fbk__fun(k2_Fc, Cmax, v, n)
    dsigma2 = dsigma2__fun(k2_Fc, Cmax, v, n)
    a = a_fun(k2_Fc, fbk, dsigma2, dp, g)
    k2 = FCC_fun(qtvtek, k2_Fc, c_out, fbk, a, eps1)
    # k3
    k3_Fc = Fc + k2 * h / 2
    fbk = fbk__fun(k3_Fc, Cmax, v, n)
    dsigma2 = dsigma2__fun(k3_Fc, Cmax, v, n)
    a = a_fun(k3_Fc, fbk, dsigma2, dp, g)
    k3 = FCC_fun(qtvtek, k3_Fc, c_out, fbk, a, eps1)
    # k4
    k4_Fc = Fc + k3 * h / 2
    fbk = fbk__fun(k4_Fc, Cmax, v, n)
    dsigma2 = dsigma2__fun(k4_Fc, Cmax, v, n)
    a = a_fun(k4_Fc, fbk, dsigma2, dp, g)
    k4 = FCC_fun(qtvtek, k4_Fc, c_out, fbk, a, eps1)

    # Fc
    x = x + h
    iter1_x[j] = round(x, 3)
    Solution[j] = (Fc + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4))
    j = j + 1

print(Solution)
x = list(reversed(iter1_x))
plt.plot(x, Solution)
plt.show()
