import numpy as np
import matplotlib.pyplot as plt


def Solver(coneHeight: float,
          cylinderHeight: float,
          Qufeed: int,
          Qunderfl: float,
          Fifeed: float,
          psolid: int,
          pfluid: int,
          muliqour: float) -> tuple[list, list]:

    height_step=0.3
    #coneHeight = 1.35 #м высота конуса
    #cylinderHeight = 1 # 

    I=1

    height=np.zeros(9)#Текущая высота сгустителя
    diameter=np.zeros(9)
    square =np.zeros(9)
    D=30
    height[0]=0.01
    diameter[0]=D
    square[0]=3.14*(diameter[0]**2)/4

    while (I<8):
        height[I] = height[I-1]+height_step
        if (height[I] <= cylinderHeight):
            diameter[I]=D
        else:
            diameter[I]=D-(height[I]-cylinderHeight)*D/coneHeight
        square[I]=3.14 *(diameter[I]**2)/4
        I=I+1

    height[8]=coneHeight+cylinderHeight-0.1
    diameter[8]= D - (height[8] - cylinderHeight) * D/coneHeight  
    square[8] = 3.14 * (diameter[8]**2)/4


    ## расчет пространственных скоростей
    qf=np.zeros(len(height))
    qtv_from=np.zeros(len(height))
    q=np.zeros(len(height))
    qR=np.zeros(len(height))
    qL=np.zeros(len(height))
    c1=np.zeros(len(height))
    fd=np.zeros(len(height))
    ff=np.zeros(len(height))
    I=0 

    #Qufeed=350 #Расход питающего потока
    Qinj=20 #Расход разбавления 
    Q=Qufeed+Qinj #Объемный расход всего, что поступает в сгуститель

    #Qunderfl=90
    QL=Q-Qunderfl #Расход жидкого из сгустителя
    QR=Qunderfl

    #Fifeed=0.0159 #Объемная концентраци тв в питающей пульпе
    cfeed=Fifeed*Qufeed/(Qufeed+Qinj)#Объемная доля тв в питании
    Qfloc=2 #Расход флокулянта %
    Rowater=1020 #Плотность воды
    Cfloc_w=0.005
    Gfloc=Qfloc*Rowater*Cfloc_w #Массовый расход флокулянта
    #psolid=3200 #Плотность тв
    Gtv=Qufeed*psolid*Fifeed #Массовый расход тв в питающем потоке
    R=Gfloc/Gtv
    #pfluid=1240 #Плотность жидкого
    cfeed_wt=cfeed*psolid/(psolid*cfeed+(1-cfeed)*pfluid)
    c_out=Q/Qunderfl*cfeed #Доля тв на выходе
    #muliqour=0.0021 #Вязкость раствора
    #dfloc=(708+0.1133*R-112.6*100*cfeed_wt)*0.54*0.00001 #0,001517
    dfloc =0.00282 # из модели флокуляции на данный момент 07/05/24 0,00282
    #print(dfloc)
    pfluidrazbab=(pfluid * Qufeed * (1 - Fifeed) + Rowater * Qinj) / (
                Qufeed * (1 - Fifeed) + Qinj)
    g=9.81
    v=(dfloc**2*g*(psolid-pfluidrazbab))/(18*muliqour) #Скорость осаждения Стокса

    while I<9:
        qf[I]=Q/square[I]/3600 #Скорость всего, что поступает в сгуститель
        qtv_from[I]=Qunderfl/square[I]/3600#Скорость потока тв из сгустителя
        qL[I]=QL/square[I]/3600
        c1[I]=(qtv_from[I]-qL[I])*cfeed/(qtv_from[I]+v)
        fd[I]=qtv_from[I]*c_out
        ff[I]=qf[I]*Fifeed
        I=I+1

    Cmax = 1
    n =87
    dp=psolid-pfluidrazbab
    eps1=10e-4
    fbk=0
    Fc=c_out
    qtvtek = 0.01
    x=4.35
    h=-0.0001
    ## функция для расчета концентрации 
    def fbk__fun(c,Cmax,v,n):
        if (c<Cmax):
            Fun1=v*c*(1-c)**n
        else: 
            Fun1=0      
        return Fun1

    def dsigma2__fun(c,ccr,k,sigma0): #функция для dsigma2
        if c>ccr:
            Fun2=sigma0*k/ccr*((c/ccr)**(k-1))
        else: 
            Fun2=0.00001
        return Fun2

    def a_fun(c,fbk,dsigma2,dp,g): #функция для расчета а
        if c==0:
            Fun3=0 
        else: 
            Fun3=fbk*dsigma2/(dp*g*Fc)
        return Fun3

    def FCC_fun(qtv_from,c,c_out,fbk,a,eps1):#функция для расчета концентрации
        f1=qtv_from*(c-c_out)
        f11=fbk
        f2=a
        f3=eps1
        Fun4=(f1+f11)/(f2+f3)
        return Fun4

    iter1_c=np.zeros(32000)
    iter2_c=np.zeros(32000)
    iter1_x=np.zeros(32000)
    iter2_x=np.zeros(32000)
    Solution=[]
    Ox=[]
    chet=0
    chet2=0
    while x>-2:
        if (x<=4.35) & (x>4.11):
            qtvtek=qtv_from[7]
        
        if (x<=4.11) & (x>3.81):
            qtvtek=qtv_from[7]
        
        if (x<=3.81) & (x>3.51):
            qtvtek=qtv_from[6]
        
        if (x<=3.51) & (x>3.21):
            qtvtek=qtv_from[5]
        
        if (x<=3.21) & (x>2.91):
            qtvtek=qtv_from[4]
        
        if (x<=2.91) & (x>2.61):
            qtvtek=qtv_from[3]

        if (x<=2.61) & (x>2.31):
            qtvtek=qtv_from[2]
        
        if (x<=2.31) & (x>2.01):
            qtvtek=qtv_from[1]
        
        if x<=2.01:
            qtvtek=qtv_from[0]

        ## Рунге-Кутт
        #k1
        fbk=fbk__fun(Fc,Cmax,v,n)
        dsigma2=dsigma2__fun(Fc,Cmax,v,n)
        a=a_fun(Fc,fbk,dsigma2,dp,g)
        k1=FCC_fun(qtvtek,Fc,c_out,fbk,a,eps1)
        #k2
        k2_Fc=Fc+k1*h/2
        fbk=fbk__fun(k2_Fc,Cmax,v,n)
        dsigma2=dsigma2__fun(k2_Fc,Cmax,v,n)
        a=a_fun(k2_Fc,fbk,dsigma2,dp,g)
        k2=FCC_fun(qtvtek,k2_Fc,c_out,fbk,a,eps1)
        #k3
        k3_Fc=Fc+k2*h/2
        fbk=fbk__fun(k3_Fc,Cmax,v,n)
        dsigma2=dsigma2__fun(k3_Fc,Cmax,v,n)
        a=a_fun(k3_Fc,fbk,dsigma2,dp,g)
        k3=FCC_fun(qtvtek,k3_Fc,c_out,fbk,a,eps1)
        #k4
        k4_Fc=Fc+k3*h/2
        fbk=fbk__fun(k4_Fc,Cmax,v,n)
        dsigma2=dsigma2__fun(k4_Fc,Cmax,v,n)
        a=a_fun(k4_Fc,fbk,dsigma2,dp,g)
        k4=FCC_fun(qtvtek,k4_Fc,c_out,fbk,a,eps1)

        Solution.append(Fc+h/6*(k1+2*k2+2*k3+k4))
        Fc=Fc+h/6*(k1+2*k2+2*k3+k4)

        x=x+h
        Ox.append(x)
        if chet<32000:
            iter1_c[chet]=Fc
            iter1_x[chet]=x
            chet=chet+1
        else:
            iter2_c[chet2]=Fc
            iter2_x[chet2]=x
            chet2=chet2+1
        hp=0
        first_check=0 

        while chet2 > 3:
            if iter2_c[chet] > 0.001 and first_check == 0:
                dx1 = iter2_c(chet2) - iter2_c(chet2 - 1)
                dx2 = iter2_c(chet2) - iter2_c(chet2 - 2)
                dx3 = iter2_c(chet2) - iter2_c(chet2 - 3)
                dx1 = abs(dx1) 
                dx2 = abs(dx2)
                dx3 = abs(dx3)

                if dx1 < 0.0000001 and dx2 < 0.0000001 and dx3 < 0.0000001 and dx3 + dx1 + dx2 < 0.0000001:
                    hp = iter2_x(chet2)
                    first_check = 1
            chet2 = chet2 - 1

        while chet > 3:
            if iter1_c[chet] > 0.001 and first_check == 0:
                dx1 = abs(iter1_c[chet] - iter1_c[chet - 1])
                dx2 = abs(iter1_c[chet] - iter1_c[chet - 2])
                dx3 = abs(iter1_c[chet] - iter1_c[chet - 3])
                if dx1 < 0.0000001 and dx2 < 0.0000001 and dx3 < 0.0000001 and (dx1 + dx2 + dx3) < 0.0000001:
                    hp=(iter1_x[chet])
                first_check = 1
            chet = chet - 1

    OFClar=c1*psolid*10**-3
    k0=0
    Quf=90 # из головы
    OFC = k0+0.107*Qufeed+0.0592*Quf-34.92*Qfloc-0.196*Qinj+10.28*hp
    print(OFC)
    print(Solution[len(Solution)-1])

    return Ox[0:4000], Solution[0:4000]
