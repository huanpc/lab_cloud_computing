__author__ = 'huanpc'

import constant
from random import randint
# Duong dan toi thu muc output file dataseed
DIR_OUTPUT_PATH = './output'
# Chon gia tri cho id trong bang customer
customer_id_begin = 4
product_id_begin = 0
# So ban ghi can tao
num_of_row = 100

#def createProductData():

def createCustomerData():
    first_name_list = constant.FIRST_NAME
    last_name_list = constant.LAST_NAME
    i = 0
    f = open(DIR_OUTPUT_PATH+'/customer_data_seed.csv','w')
    column_heading = ['customer_id','customer_group_id','store_id','first_name','last_name','email','telephone','fax','password','salt','cart','whistlist',
                      'newsleter','address_id','custom_field','ip','status','approves','safe','token','date_added']
    row = ['',constant.CUSTOMER_GROUP_ID,constant.STORE_ID,'','','',constant.SALT,constant.CART,constant.NEWSLETTER,constant.ADDRESS_ID,
           constant.CUSTOM_FIELD,constant.IP,constant.STATUS,constant.APPROVED,constant.SAFE,constant.TOKEN,constant.DATE_ADDED]
    while i<num_of_row:
        first_name = first_name_list[randint(0,len(first_name_list))]
        last_name = last_name_list[randint(0,len(last_name_list))]
        row[0] = str(i+customer_id_begin)
        row[2] = first_name
        row[3] = last_name
        row[4] = str(first_name+'.'+last_name+'@gmail.com').lower()
        row[5] = str(randint(11111,99999))+ str(randint(11111,99999))
        row[6] = row[5]
        line = ','.join(row)
        i+=1
        f.write(line+'\n')
    f.close()

def main():
    createCustomerData()

if __name__ == '__main__':
    main()
