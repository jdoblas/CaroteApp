# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stacklayout import StackLayout
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.listview import ListItemButton
from kivy.uix.button import Button

from kivy.properties import NumericProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder

Builder.load_file('rota.kv')
Builder.load_file('barco.kv')
Builder.load_file('resultados.kv')

import os, copy

run_path=os.path.dirname(os.path.realpath(__file__))

class ClassLoc:
    loc_id=0
    nome=''
    latitude,longitude=0.0,0.0
    distancia=0.0
    regiao=''

def CarregaLocalidades(arquivo):
    loc2=ClassLoc()
    loc3=ClassLoc()
    loc_lista=[]
    c=0
    with open(arquivo,'r') as f:
        for line in f:
            loc3.loc_id=c
            a=line.split(';')
            loc3.nome=a[0]
            loc3.regiao=a[1]
            loc3.distancia=float(a[2])
            loc3.latitude=float(a[3])
            loc3.longitude=float(a[4])
            loc_lista.append(copy.copy(loc3))
            c+=1
        return loc_lista

def CarregaBarcos(arquivo):
    dict_barco={}
    with open(arquivo,'r') as f:
        for line in f:
            a=line.split(';')
            dict_barco[(a[0],a[1])]=float(a[2])
        return dict_barco



        

# VARIAVEIS GLOBAIS: LOCALIDADES, BARCOS E ROTA
localidades=CarregaLocalidades('loc_info_ord.dat')
dict_barcos=CarregaBarcos('barco_info.dat')
barcos=[row[0] for row in dict_barcos.keys()]
motores=[row[1] for row in dict_barcos.keys()]
tipo_barcos=sorted(set(barcos))
print 'u',tipo_barcos
tipo_motores=sorted(set(motores))

coef_barco=0
coef_peso=1
coef_geral=0.6
coef_descida=0.7

rota=[]


class ClassBotaoLocalidade(ListItemButton):
    loc_botao=ListProperty()
    
class ClassBotaoRota(ListItemButton):
    loc_botao=ListProperty()

class ClassBotaoBarco(ListItemButton):
    pass
class ClassBotaoMotor(ListItemButton):
    pass

class TelaBase(TabbedPanel):

    pass

class LayoutRota(TabbedPanelItem):

    layout_rota=ObjectProperty()
    layout_barco=ObjectProperty()

    input_loc1=ObjectProperty()
    lista_rota=ObjectProperty()
    resultados_busca=ObjectProperty()

    def converter_adapter_lista_loc(self,index,loc_index):
        return {'loc_botao':(localidades[loc_index].nome,localidades[loc_index].regiao,loc_index,index)}      
    def procura_loc(self):
        lista_sel=[]
        texto=self.input_loc1.text
        print texto
        if len(texto)>0:                                #procura localidades com texto
            for loc in localidades:                     
                loc_curta=loc.nome[0:len(texto)]
                if loc_curta.upper()==texto.upper():
                    lista_sel.append(loc.loc_id)               #incrementa a lista 'lista_sel'
            lista_nomes_locs_sel=[]                     
            del self.resultados_busca.adapter.data[:]
            self.resultados_busca.adapter.data.extend(lista_sel)
            self.resultados_busca._trigger_reset_populate()
        else:
            lista_sel=range(len(localidades))
            del self.resultados_busca.adapter.data[:]
            self.resultados_busca.adapter.data.extend(lista_sel)
            self.resultados_busca._trigger_reset_populate()
    def escolheu_loc(self,loc_index):
        print 'Escolheu:',loc_index
        rota.append(loc_index)

        del self.lista_rota.adapter.data[:]
        self.lista_rota.adapter.data.extend(rota)
        self.lista_rota._trigger_reset_populate()
     
        self.resultados_busca._trigger_reset_populate()


    def escolheu_loc_rota(self,index):
        print 'Tirando:',index
        del rota[index:index+1]
        del self.lista_rota.adapter.data[:]
        self.lista_rota.adapter.data.extend(rota)
        self.lista_rota._trigger_reset_populate()

class LayoutBarco(TabbedPanelItem):
    barco_esc=''
    motor_esc=''
    label_barco_motor=ObjectProperty()
    escolha_peso=ObjectProperty()
    
    def escolheu_barco(self,texto):
        global coef_barco
        print 'Escolheu:',texto
        self.barco_esc=texto
        if self.motor_esc!='':
            if (self.barco_esc,self.motor_esc) in dict_barcos:
                print dict_barcos[self.barco_esc,self.motor_esc]
                self.label_barco_motor.text='Escolhido: '+self.barco_esc+' com motor '+self.motor_esc
                coef_barco=dict_barcos[self.barco_esc,self.motor_esc]
            else:
                self.label_barco_motor.text='Combinaçao embarcaçao-motor nao disponivel'
                coef_peso=0
        print 'coef_barco ',coef_barco
        
    def escolheu_motor(self,texto):
        global coef_barco
        print 'Escolheu:',texto
        self.motor_esc=texto
        if self.barco_esc!='':
            if (self.barco_esc,self.motor_esc) in dict_barcos:
                print dict_barcos[self.barco_esc,self.motor_esc]
                self.label_barco_motor.text='Escolhido: '+self.barco_esc+' com motor '+self.motor_esc
                coef_barco=dict_barcos[self.barco_esc,self.motor_esc]
            else:
                self.label_barco_motor.text='Combinaçao embarcaçao-motor nao disponivel'
                coef_barco=0
        print 'coef_barco ',coef_barco
        
    def mudou_peso(self,peso):
        global coef_peso
        coef_peso=peso
        print coef_peso
    
class LayoutResultados(TabbedPanelItem):
    label_resultados=ObjectProperty()

    def CalculaResultados(self):
        if len(rota)<2:
            self.label_resultados.text='Por favor selecione duas ou mais localidades na aba \'Rota\''
            return
        if coef_barco==0:
            self.label_resultados.text='Por favor configure o seu barco na aba \'Barco\''
            return         
        print 'calculo resultados'
        print 'coef_peso',coef_peso
        print 'coef_barco',coef_barco
        print 'coef_descida',coef_descida
        
        text_resultados='Resultados\n\n'
        comb=[]
        dist_rota=[]
        loc_anterior=rota[0]
        for i in range(len(rota)):
            if i>0:
                dist=localidades[rota[i]].distancia-localidades[rota[i-1]].distancia                
                if dist>0:
                    comb.append(dist*coef_geral*coef_barco*coef_peso)
                    dist_rota.append(dist)
                else:
                    comb.append(abs(dist*coef_geral*coef_barco*coef_peso*coef_descida))
                    dist_rota.append(abs(dist))
        for i in range(len(rota)):
            if i>0:
                a=localidades[rota[i-1]].nome+'-'+localidades[rota[i]].nome+': '+str(dist_rota[i-1])+' km., '+str(round(comb[i-1]))+' lts.\n'
                text_resultados+=a
               
        b='\nTotal viagem de ida: '+str(sum(dist_rota))+' km., '+str(round(sum(comb)))+' lts.\n\n'
        text_resultados+=b 


        rota_volta=copy.copy(rota)
        rota_volta.reverse()
        print rota
        print rota_volta
        comb_volta=[]
        dist_rota_volta=[]
        loc_anterior=rota_volta[0]
        for i in range(len(rota_volta)):
            if i>0:
                dist=localidades[rota_volta[i]].distancia-localidades[rota_volta[i-1]].distancia                
                if dist>0:
                    comb_volta.append(dist*coef_geral*coef_barco*coef_peso)
                    dist_rota_volta.append(dist)
                else:
                    comb_volta.append(abs(dist*coef_geral*coef_barco*coef_peso*coef_descida))
                    dist_rota_volta.append(abs(dist))
        c='Total viagem de volta: '+str(sum(dist_rota_volta))+' km., '+str(round(sum(comb_volta)))+' lts.\n\n'
             
        text_resultados+=c

        d='Total ida e volta: '+str(sum(dist_rota)+sum(dist_rota_volta))+' km., '+str(round(sum(comb)+sum(comb_volta)))+' lts.\n\n'
        text_resultados+=d


        
        
        self.label_resultados.text=text_resultados   
#        return comb
    
    
class MainApp(App):
    def build(self):     
        return TelaBase()


if __name__=='__main__':
    MainApp().run()
