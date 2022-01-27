from flask import Flask
from flask import request
import threading


accounts = []
accountLock = threading.Lock()

increasingAccountNumber = 1
accountNumberLock = threading.Lock()

class Transaction:
    def __init__(self, amount, transactionType):
        self.amount = amount
        self.transactionType = transactionType


class Account:
    transactions = []

    def __init__(self, firstName, lastName):
        global increasingAccountNumber
        self.firstName = firstName
        self.lastName = lastName
        accountNumberLock.acquire()
        self.id = increasingAccountNumber
        self.accountNumber = increasingAccountNumber + 80000
        increasingAccountNumber += 1
        accountNumberLock.release()
        self.accountOpen = True

    def closeAccount(self):
        self.accountOpen = False
    

    def getBalance(self):
        curBalance = 0
        for t in self.transactions:
            curBalance += t.amount
        return curBalance
    
    def addTransaction(self, t):
        self.transactions.append(t)

def response(account):
    response = {
        "value":{
            "id": account.id,
            "firstName": account.firstName,
            "lastName": account.lastName,
            "account": {
                "id": account.id,
                "accountNumber": account.accountNumber,
                "balance": account.getBalance(),
                "status": not account.accountOpen
            },
            "accountId": account.id
        }
    }
    return response


app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

@app.route("/")
def hello():
   return "Caio!"

@app.route("/api/customerAccount/OpenCustomerAccount")
def openAccount():
    firstName = request.args.get('firstName')
    lastName = request.args.get('lastName')

    print(firstName)
    print(lastName)
    newAccount = Account(firstName, lastName)
    accountLock.acquire()
    global accounts
    accounts.append(newAccount)
    accountLock.release()

    # TODO: write response body
    return response(newAccount)

@app.route("/api/customerAccount/GetCustomerAccountByAccountNumber")
def getAccount():
    accountNumber = request.args.get('accountNumber')
    print(accountNumber)

    global accounts
    curAccount = None
    for account in accounts:
        print("account Number: ", account.accountNumber)
        if str(account.accountNumber) == accountNumber:
            curAccount = account
            break
    
    if curAccount != None:
        return response(curAccount)
    else:
        return "Account not found!"

@app.route("/api/customerAccount/CloseCustomerAccount")
def closeAccount():
    accountNumber = request.args.get('accountNumber')
    print(accountNumber)

    global accounts
    curAccount = None
    for account in accounts:
        print("account Number: ", account.accountNumber)
        if str(account.accountNumber) == accountNumber:
            curAccount = account
            break
    
    if curAccount != None:
        curAccount.closeAccount()
        return response(curAccount)
    else:
        return "Account not found!"


@app.route("/api/customerAccount/ApplyTransactionToCustomerAccountAsync")
def applyTransactionToAccount():
    accountNumber = request.args.get('accountNumber')
    amount = request.args.get('amount')
    transactionType = request.args.get('transactionType')
    print(accountNumber)

    global accounts
    curAccount = None
    for account in accounts:
        print("account Number: ", account.accountNumber)
        if str(account.accountNumber) == accountNumber:
            curAccount = account
            break
    
    if curAccount != None:
        if not curAccount.accountOpen:
            return "Account closed"
        curAccount.addTransaction(Transaction(float(amount), transactionType))
        return response(curAccount)
    else:
        return "Not found"