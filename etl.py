
import pandas as pd 
import tabula 
import os
import glob
import sys
import json

#card_end='7037'
credit_card_ending = int(sys.argv[1])

########### read PDFs (Extract )#################
current_path = os.getcwd()
folder='\data'
os.chdir(current_path)
pdf_files = glob.glob(current_path +folder+ '/*.pdf') # get files names 


dfs=[] # list of dataframes of transafactions from all pdf 
for f in pdf_files:
    df_list = tabula.read_pdf(f, pages='all', multiple_tables=True)
    dfs.append(df_list)


def catch_transactions(df_list, name='Any',carte_end='Any'):
    ### catch transactions tables from pdf by name of the ower or by the 4 last digits of card number 
    trans=[]
    for d in df_list:
        for i in list(d.columns):
            if (name in i) or (carte_end in i) :
                trans.append(d)
    return trans
            

############ transform ############################à

def transform(df):
    temp=df
    temp=temp.T.reset_index().T.drop(index=0).reset_index(drop=True)
    temp = temp.drop(index=temp.index[:3]).reset_index(drop=True)
    if len(temp.columns)==4:
        
        temp.columns=['description','place','disc','amount']
    else:
        temp.columns=['description','disc','amount']    
    t=temp['description'].str.split(' ', n=4, expand=True)
    t.columns=['transaction_day','transaction_month','inscription_day','inscription_month','description']
    resulat=pd.concat([t, temp.drop(['description'],axis=1)], axis=1)
    resulat=resulat.dropna(subset=['transaction_day'])
    resulat = resulat[~(resulat == 'TOTAL').any(axis=1)]
    resulat[['transaction_day','transaction_month','inscription_day','inscription_month']]=resulat[['transaction_day',
                                                                                                'transaction_month',
                                                                                                'inscription_day',
                                                                                                'inscription_month']].astype(int)
    resulat['amount']=resulat['amount'].str.replace('[^0-9,]', '', regex=True)
    resulat['amount']=resulat['amount'].replace(',', '.', regex=True).astype(float)
    return resulat

all_transactions=[]
a=0
for d in dfs:
    trans=catch_transactions(df_list=d,carte_end=credit_card_ending)
    try:
        if len(trans)>0:
            data=pd.concat([transform(df) for df in trans],axis=0)
            all_transactions.append(data)
    except:
        print(a)
    a=a+1
all_data=pd.concat(all_transactions,axis=0)
all_data=all_data.drop_duplicates()
print(all_data)

def creat_name(x,l):
    for i in l : 
        if i.upper() in str(x).upper():
            return i.upper()
    return None

def creat_cat(x,l):
    for i in l : 
        if i.upper() in str(x).upper():
            return True
    return False
    
with open('categories.json', 'r') as file:
    json_data = file.read()

categories=json.loads(json_data)

def get_category(text,original_dict):

    # Destination dictionary
    new_dict = {}

    # Key to move
    key_to_move = 'PLACE'

# Check if the key exists in the original dictionary
    if key_to_move in original_dict:
    # Extract the key-value pair and move it to the new dictionary
        new_dict[key_to_move] = original_dict.pop(key_to_move)
    cat='OTHER'
    name='OTHER'
    for k in original_dict.keys():
        if creat_cat(text,original_dict[k])==True:
            cat=k
            name=creat_name(text,original_dict[k])
    return cat,name


all_data[['category', 'organization']] = all_data['description'].apply(lambda x: pd.Series(get_category(x,categories)))
print(all_data)
all_data.to_csv('card_transactions.csv')