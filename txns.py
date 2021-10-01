from web3 import Web3
import json
from style import style

class Txn_bot():

    def __init__(self, token_address, quantity, Outputquantity, slippage):
        self.w3 = self.connect()
        self.address, self.private_key = self.set_address()
        self.token_address = Web3.toChecksumAddress(token_address)
        self.token_contract = self.set_token_contract()
        self.utils_address, self.utils = self.set_Utils()
        self.router_address, self.router = self.set_LimitOrdersRouter()
        self.quantity = quantity 
        self.output = Outputquantity
        self.TIGS_contract = self.set_TIGS_contract()
        self.slippage = 1 - (slippage/100)
        self.gas_price = 6 * (10**9)
        self.WBNB = Web3.toChecksumAddress("0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")

    def connect(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        w3 = Web3(Web3.HTTPProvider(keys["RPC"]))
        return w3

    def set_address(self):
        with open("./Settings.json") as f:
            keys = json.load(f)
        if len(keys["metamask_address"]) <= 41:
            print(style.RED +"Set your Address in the keys.json file!" + style.RESET)
        if len(keys["metamask_private_key"]) <= 42:
            print(style.RED +"Set your PrivateKey in the keys.json file!"+ style.RESET)
        return(keys["metamask_address"], keys["metamask_private_key"])

    def get_token_decimals(self):
        return self.token_contract.functions.decimals().call()

    def get_token_symbol(self):
        return self.token_contract.functions.symbol().call()


    def get_TokenDecimalsFromAddres(self,Address):
        address = Web3.toChecksumAddress(Address)
        with open("./ABIS/bep20_abi_token.json") as f:
            contract_abi = json.load(f)
        token_contract = self.w3.eth.contract(address=address, abi=contract_abi)
        return token_contract.functions.decimals().call()


    def set_LimitOrdersRouter(self):
        Utils_address = Web3.toChecksumAddress("0x7e71Db626e279FD064F0cCEEFB8776Ff29FD0c52") 
        with open("./ABIS/LimitOrder.json") as f:
            contract_abi = json.load(f)
        utils = self.w3.eth.contract(address=Utils_address, abi=contract_abi)
        return (Utils_address, utils)

    def set_Utils(self):
        Utils_address = Web3.toChecksumAddress("0xA7Dd8a34B931D2A0272218Df00D08C3b76A96578") 
        with open("./ABIS/DEX_Utils.json") as f:
            contract_abi = json.load(f)
        utils = self.w3.eth.contract(address=Utils_address, abi=contract_abi)
        return (Utils_address, utils)

    def getBlockHigh(self):
        return self.w3.eth.block_number

    def set_TIGS_contract(self):
        with open("./ABIS/bep20_abi_token.json") as f:
            contract_abi = json.load(f)
        token_contract = self.w3.eth.contract(address=Web3.toChecksumAddress("0x34FaA80FEC0233e045eD4737cc152a71e490e2E3"), abi=contract_abi)
        return token_contract

    def set_token_contract(self):
        with open("./ABIS/bep20_abi_token.json") as f:
            contract_abi = json.load(f)
        token_contract = self.w3.eth.contract(address=self.token_address, abi=contract_abi)
        return token_contract


    def get_token_balance(self): 
        return self.token_contract.functions.balanceOf(self.address).call() / (10 ** self.token_contract.functions.decimals().call())


    def deleteLimitOrder(self, i):
        try:
            txn = self.router.functions.deleteLimitOrder(
            i
            ).buildTransaction(
                {'from': self.address, 
                'gas': 100000,
                'gasPrice': self.gas_price,
                'nonce': self.w3.eth.getTransactionCount(self.address), 
                'value': 0}
                )
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(style.RED +"DeleteOrder:",txn.hex())
            txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)  
            if txn_receipt["status"] == 1: return True,style.GREEN +"\nDelete LIMITORDER Transaction Successfull!" + style.RESET
            else: return False, style.RED +"\nDelete LIMITORDER Transaction Faild!" + style.RESET 
        except Exception as e:
            print(e)
        

    def get_OpenOrders(self):
        self.OpenOrders =[]
        Open_Orders = self.router.functions.getOrdersForAddress(self.address).call()
        for OO in Open_Orders:
            Open_Order = self.router.functions.orders(OO).call()
            if Open_Order[3] == 0:
                self.OpenOrders.append(Open_Order)
        return self.OpenOrders

    def SortOpenOrders(self):
        self.OpenOrdersS =[]
        Open = self.get_OpenOrders()
        #print(Open)
        for o in Open:
            try:
                #print(o)
                ID = o[0]
                Input_Token = o[5]
                Output_Token = o[6]
                amount_In = o[8]
                MaxAmount_Out = o[9]
                MinAmount_Out = o[10]
                self.OpenOrdersS.append([ID, Input_Token, Output_Token, amount_In,MaxAmount_Out, MinAmount_Out])
            except:
                pass
        return self.OpenOrdersS

    def amountsOut_buy(self):
        Amount = self.utils.functions.getAmountsOut(
            int((self.quantity * (10** 18))),
            [self.WBNB, self.token_address],
            [0]
            ).call()
        return Amount


    def amountsOut_sell(self):
        Amount = self.utils.functions.getAmountsOut(
            int((self.quantity * (10** self.get_token_decimals()))),
            [self.token_address, self.WBNB],
            [0]
            ).call()
        return Amount


    def is_approveRouter(self):
        Approve = self.token_contract.functions.allowance(self.address ,Web3.toChecksumAddress("0x638189B1eFCEeDD2941fe2491042aAC498aB35f4")).call()
        Aproved_quantity = self.output * (10 ** self.token_contract.functions.decimals().call())
        if int(Approve) <= int(Aproved_quantity):
            return False
        else:
            return True


    def approveRouter(self):
        if self.is_approveRouter() == False:
            txn = self.token_contract.functions.approve(
                Web3.toChecksumAddress("0x638189B1eFCEeDD2941fe2491042aAC498aB35f4"),
                115792089237316195423570985008687907853269984665640564039457584007913129639935 # Max Approve
            ).buildTransaction(
                {'from': self.address, 
                'gas': 100000,
                'gasPrice': self.gas_price,
                'nonce': self.w3.eth.getTransactionCount(self.address), 
                'value': 0}
                )
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(style.GREEN +"\nApproved :",txn.hex())
            txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)   

    def is_approve(self):
        Approve = self.token_contract.functions.allowance(self.address ,self.router_address).call()
        Aproved_quantity = self.output * (10 ** self.token_contract.functions.decimals().call())
        if int(Approve) <= int(Aproved_quantity):
            return False
        else:
            return True


    def approve(self):
        if self.is_approve() == False:
            txn = self.token_contract.functions.approve(
                self.router_address,
                115792089237316195423570985008687907853269984665640564039457584007913129639935 # Max Approve
            ).buildTransaction(
                {'from': self.address, 
                'gas': 100000,
                'gasPrice': self.gas_price,
                'nonce': self.w3.eth.getTransactionCount(self.address), 
                'value': 0}
                )
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print("\nApproved :",txn.hex())
            txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)   


    def is_TIGSapproved(self):
        Approve = self.TIGS_contract.functions.allowance(self.address ,self.router_address).call()
        Aproved_quantity = 100 * (10 ** self.TIGS_contract.functions.decimals().call())
        if int(Approve) <= int(Aproved_quantity):
            return False
        else:
            return True


    def approveTIGS(self):
        if self.is_TIGSapproved() == False:
            txn = self.TIGS_contract.functions.approveMax(
                self.router_address
            ).buildTransaction(
                {'from': self.address, 
                'gas': 100000,
                'gasPrice': self.gas_price,
                'nonce': self.w3.eth.getTransactionCount(self.address), 
                'value': 0}
                )
            signed_txn = self.w3.eth.account.sign_transaction(
                txn,
                self.private_key
            )
            txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            print(style.GREEN + "\nApproved :",txn.hex()+style.RESET)
            txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)   
            if txn_receipt["status"] == 1: return True,style.GREEN +"\nApprove Successfull!"+ style.RESET
            else: return False, style.RED +"\nApprove Transaction Faild!"+ style.RESET
        else:
            return True, style.GREEN +"\nAllready approved!"+ style.RESET


    def placeOrderBNBToken(self):
        self.approveTIGS()
        txn = self.router.functions.createBNBtoTokenLimitOrder(
            self.token_address,
            int(self.output),
            int(self.output * self.slippage)
        ).buildTransaction(
            {'from': self.address, 
            'gas': 800000,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.getTransactionCount(self.address), 
            'value': Web3.toWei(self.quantity,'ether')}
            )
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(style.GREEN + "\nBUY LIMITORDER:",txn.hex() + style.RESET)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
        if txn_receipt["status"] == 1: return True,style.GREEN +"\nBUY LIMITORDER Transaction Successfull!" + style.RESET
        else: return False, style.RED +"\nBUY LIMITORDER Transaction Faild!" + style.RESET


    def placeOrderTokenBNB(self):
        self.approve()
        self.approveTIGS()
        self.approveRouter()
        txn = self.router.functions.createTokentoBNBLimitOrder(
            self.token_address,
            int(self.quantity * (10** self.get_token_decimals())),
            int(self.output),
            int(self.output * self.slippage)
        ).buildTransaction(
            {'from': self.address, 
            'gas': 800000,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.getTransactionCount(self.address), 
            'value': 0}
            )
        signed_txn = self.w3.eth.account.sign_transaction(
            txn,
            self.private_key
        )
        txn = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(style.GREEN + "\nSELL LIMITORDER:",txn.hex() + style.RESET)
        txn_receipt = self.w3.eth.waitForTransactionReceipt(txn)
        if txn_receipt["status"] == 1: return True,style.GREEN +"\nSELL LIMITORDER Transaction Successfull!" + style.RESET
        else: return False, style.RED +"\nSELL LIMITORDER Transaction Faild!" + style.RESET
