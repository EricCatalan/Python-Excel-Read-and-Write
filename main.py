import csv
import numpy as np
import pandas as pd
import xlsxwriter

input_file_updated = open('/Users/ericcatalan/Documents/Input File.csv')
input_file_original = open('/Users/ericcatalan/Documents/Input File Empty.csv')
updated_input_csv = csv.reader(input_file_updated)
original_input_csv = csv.reader(input_file_original)
header = []
header = next(updated_input_csv)
account_list_updated = []
new_accounts = []
anomalies = []


class Anomaly:
    def __init__(self, account, advisor, sub, message):
        self.account = account
        self.advisor = advisor
        self.sub = sub
        self.message = message

    def values(self):
        return self.account, self.advisor, self.sub, self.message


class Account:
    def __init__(self, account, advisor, sub, message=None):
        self.message = message
        self.account = account
        self.advisor = advisor
        self.sub = sub
        

    def values(self):
        return self.account, self.advisor, self.sub, self.message


for account in updated_input_csv:
    new_account = Account(account[0], account[1], account[2])
    account_list_updated.append(new_account)

header = next(original_input_csv)
account_list_original = []
for account in original_input_csv:
    old_account = Account(account[0], account[1], account[2])
    account_list_original.append(old_account)


input_file_updated.close()
input_file_original.close()


def extract(lst):
    return [item[0] for item in lst]


def get_advisor(account, lst):
    for x in lst:
        if x.values()[0] == account:
            return x.values()[1]


def remove_name_anomaly_from_updated_list(name, lst):
    for account in lst[:]:
        if name == account.values()[1]:
            account.append(
                "The Advisor Name Is Different Than The Previous Advisor" + name + " And The Previous Was " + account.values()[
                    1])
            account_list_updated.remove(account)
            anomalies.append(Anomaly(account.values()[0], account.values()[1], account.values()[2], account.values()[3]))


def remove_name_anomaly_from_new_accounts_list(name, lst):
    for account in lst[:]:
        if name == account.values()[1]:
            account.append(
                "The Advisor Name Is Different Than The Previous Advisor. The New Name Is " + name + " And The Previous Was " +
                account.values()[1])
            new_accounts.remove(account)
            anomalies.append(Anomaly(account.values()[0], account.values()[1], account.values()[2], account.values()[3]))


while True:
    restart = False
    for account in account_list_updated[:]:
        if account.values()[0] in extract(account_list_original):
            if account.values()[1] == get_advisor(account.values()[0], account_list_original):
                continue
            else:
                different_name = account.values()[1]
                account.append("The Advisor Name Is Different Than The Previous Advisor. The New Name Is " + account.values()[
                    1] + " And The Previous Was " + get_advisor(account.values()[0], account_list_original))
                account_list_updated.remove(account)
                anomalies.append(Anomaly(account.values()[0], account.values()[1], account.values()[2], account.values()[3]))
                remove_name_anomaly_from_updated_list(different_name, account_list_updated)
                remove_name_anomaly_from_new_accounts_list(different_name, new_accounts)
                restart = True
                break
        else:
            new_accounts.append(account)

    if not restart:
        break

for account in new_accounts[:]:
    if account.values()[2] != '':
        account.message = "This Account Is A Sub Account"
        new_accounts.remove(account)
        anomalies.append(Anomaly(account.values()[0], account.values()[1], account.values()[2], account.values()[3]))


accountIDs_new_accounts = []
advisor_names_new_accounts = []
sub_list_new_accounts = []

for account in new_accounts:
    accountIDs_new_accounts.append(account.values()[0])
    advisor_names_new_accounts.append((account.values()[1]))
    sub_list_new_accounts.append((account.values()[2]))

accountIDs_anomalies = []
advisor_names_anomalies = []
sub_list_anomalies = []
messages_anomalies = []

for anomaly in anomalies:
    accountIDs_anomalies.append(anomaly.values()[0])
    advisor_names_anomalies.append((anomaly.values()[1]))
    sub_list_anomalies.append((anomaly.values()[2]))
    messages_anomalies.append((anomaly.values()[3]))


with pd.ExcelWriter('two_frames_one_tab.xlsx', engine='xlsxwriter') as writer:
    for account in new_accounts:
        df_first = pd.DataFrame({'Account': accountIDs_new_accounts, 'Advisor': advisor_names_new_accounts, 'Sub': sub_list_new_accounts})
        df_first.to_excel(writer, sheet_name='New Accounts', index=False)
    for anomaly in anomalies:
        df_second = pd.DataFrame(
            {'Account': accountIDs_anomalies, 'Advisor': advisor_names_anomalies, 'Sub': sub_list_anomalies, 'Reason': messages_anomalies})
        df_second.to_excel(writer, sheet_name='Anomalies', index=False)
