import numpy as np
import urllib.request as rq
import json
from collections import Counter as c
import time
import matplotlib.pyplot as plt
import os
import pandas as pd
import operator
import datetime


print("Backend Imported")


def loadData(url):
    try:
        dataset = rq.urlopen(url)
        dataset = dataset.read()
        dataset = json.loads(dataset)
    except Exception as e:
        print('Unable to get data from flipsidecrypto API. Check the URL below: \n{}'.format(url))
    return dataset

def getTransactions(dataset):
    from_addresses = {}
    today = datetime.datetime.utcnow()
    start_month = today.month - 1
    start_day = today.day

    max_timestamp = 0

    for i, val in enumerate(dataset):
        if val['FROM_ADDRESS'] not in list(from_addresses.keys()):
            from_addresses[val['FROM_ADDRESS']] = []

        timestamp = val['BLOCK_TIMESTAMP']
        year = timestamp[:4]
        hour = timestamp[11:13]
        day = timestamp[8:10]
        month = timestamp[5:7]
        transaction_timestamp = int(year + month + day)

        if transaction_timestamp > max_timestamp:
            max_timestamp = transaction_timestamp

        if (int(day) >= start_day and int(month) == start_month) or (int(day) <= start_day and int(month) > start_month):
            from_addresses[val['FROM_ADDRESS']].append(transaction_timestamp)

    df = pd.DataFrame(columns = ['address','transactions'])
    days = []
    for key in from_addresses.keys():
        df.loc[len(df)] = [key, len(from_addresses[key])]
        days = days + from_addresses[key]
    days = np.sort(np.unique(days))
    df = df.sort_values('transactions')

    return df, from_addresses, days

def getPercentOfTop(top_amt, transactions):
    return np.sum(np.array(transactions.tail(top_amt)["transactions"])) / np.sum(np.array(transactions["transactions"]))

def plotTopOverTime(top_amt, transaction_amt, from_addresses, days, target_add_name="Transmuter"):
    fig = plt.figure(figsize=(10, 6))

    top_adds = np.flip(np.array(transaction_amt.tail(top_amt)["address"]))

    for user, key in enumerate(top_adds):
        count_arr = np.zeros((days.shape))
        (unique, counts) = np.unique(np.array(from_addresses[key]), return_counts=True)
        for i, u in enumerate(unique):
            count_arr[days == u] = counts[i]

        if key in top_adds[:10]:
            plt.plot(np.arange(days.shape[0]), count_arr, label="..."+key[-4:])
        else:
            plt.plot(np.arange(days.shape[0]), count_arr)

    day_labels = []
    for i in days:
        day_labels.append(str(i)[:4]+"-"+str(i)[4:6]+"-"+str(i)[6:])
    plt.xticks(np.arange(days.shape[0])[::2], day_labels[::2], rotation=90)
    plt.yticks(fontsize=15)
    plt.ylabel("Transactions", fontsize=18)
    plt.xlabel("Dates", fontsize=18)
    plt.legend(loc = 'upper left', ncol=2)
    plt.title("Transactions Made to "+target_add_name+" by Top "+str(top_amt)+" Most Active in Last 30 Days", fontsize=18)
    plt.show()

def reverse_lst(lst):
    return [ele for ele in reversed(lst)]

def topAmtBar(top_amt, transaction_amt, target_add_name="Transmuter"):
    top_transactions = transaction_amt.tail(top_amt)
    fig = plt.figure(figsize=(10, 6))
    addresses = reverse_lst(list(top_transactions["address"]))
    user_ids = []
    for i, val in enumerate(addresses):
        user_ids.append("..."+val[-4:])

    top_trans = np.flip(np.array(top_transactions["transactions"]))
    plt.bar(user_ids,top_trans)
    plt.ylabel("Transactions", fontsize=18)
    plt.xticks(rotation=90)
    plt.yticks(fontsize=15)
    plt.title("Transactions Made to "+target_add_name+" by Top "+str(top_amt)+" Most Active", fontsize=18)
    plt.show()
    return addresses

def topAmtPie(top_amt, transaction_amt, rot_angle=90, target_add_name="Transmuter"):
    top_transactions = transaction_amt.tail(top_amt)

    fig = plt.figure(figsize=(10, 6))
    addresses = reverse_lst(list(top_transactions["address"]))
    top_trans = np.flip(np.array(top_transactions["transactions"]))

    user_ids, percents, pie_colors = [], [], []
    top_trans_all = []
    for i, val in enumerate(addresses):
        user_ids.append("..."+val[-4:])
        top_trans_all.append(top_trans[i])
        pie_colors.append('b')

    user_ids.append("Other")
    top_trans_all.append(np.sum(np.array(transaction_amt["transactions"])) - np.sum(top_trans))
    pie_colors.append("g")

    perc = np.sum(top_trans) / np.sum(np.array(transaction_amt["transactions"]))


    plt.pie(top_trans_all, labels=user_ids, startangle=rot_angle, autopct='%1.1f%%', rotatelabels=True)
    plt.axis('equal')
    plt.title("Percent of Total Transactions Made to "+target_add_name+"; "+str(100*round(perc,3))+"% total", fontsize=18)
    plt.show()


def percSameAddresses(transmuter, vault, pool):
    addresses = {}
    joined_arr = transmuter + vault + pool

    for add in joined_arr:
        is_target_in_list = add.lower() in (string.lower() for string in list(addresses.keys()))

        if not is_target_in_list:
        # if add not in list(addresses.keys()):
            addresses[add] = 0
        addresses[add]+=1

    print("Addresses top 25 in all 3: ", np.count_nonzero(np.array(list(addresses.values())) == 3))
    print("Addresses top 25 in all 2: ", np.count_nonzero(np.array(list(addresses.values())) == 2))
    print("Addresses top 25 in all 1: ", np.count_nonzero(np.array(list(addresses.values())) == 1))



# url = 'https://api.flipsidecrypto.com/api/v2/queries/aa5e9f34-d5e6-43d1-9c5d-1e2fa2e14e4d/data/latest' #30 days transmuter
# dataset = loadData(url)
# transaction_amt, from_addresses, days = getTransactions(dataset)

# make bar graph here, maybe pie chart too
# addresses_transmuter = topAmtBar(25, transaction_amt, target_add_name='Transmuter')
# topAmtPie(25, transaction_amt, target_add_name='Transmuter')
# percentage = getPercentOfTop(25, transaction_amt)
# plotTopOverTime(25, transaction_amt, from_addresses, days, target_add_name="Transmuter")


# url = 'https://api.flipsidecrypto.com/api/v2/queries/3b8abf04-bb39-4408-bc34-a1b7d8cdf56f/data/latest' #vault
# dataset = loadData(url)
# transaction_amt, from_addresses, days = getTransactions(dataset)

# make bar graph here, maybe pie chart too
# addresses_transmuter = topAmtBar(25, transaction_amt, target_add_name='Vault')
# topAmtPie(25, transaction_amt, target_add_name='Vault')
# percentage = getPercentOfTop(25, transaction_amt)
# plotTopOverTime(25, transaction_amt, from_addresses, days, target_add_name="Vault")

# url = 'https://api.flipsidecrypto.com/api/v2/queries/9bf5d60e-66f7-4428-a725-5b539be0ff26/data/latest' #30 days Pools (staking)
# make bar graph here, maybe pie chart too
# addresses_transmuter = topAmtBar(25, transaction_amt, target_add_name='Pools')
# topAmtPie(25, transaction_amt, target_add_name='Pools')
# percentage = getPercentOfTop(25, transaction_amt)
# plotTopOverTime(25, transaction_amt, from_addresses, days, target_add_name="Pools")
