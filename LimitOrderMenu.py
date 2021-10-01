from txns import Txn_bot as tx
from style import style # Later, too lazy


def CreateBuyOrder():
    print("Ok, Lets Create a Buy LimitOrder")
    token_address = input("Input TokenAddress: ")
    quantity = float(input("Input BNB amount: "))
    PriceChange = int(input("Input Price change in Percent: "))
    PC = 1 + (PriceChange/100)
    Outputquantity = 0
    slippage = int(input("Input Slippage: "))
    initBot = tx(token_address, quantity, Outputquantity, slippage)
    TokenDecimals = initBot.get_token_decimals()
    CurrentOutput = initBot.amountsOut_buy()
    Symbol = initBot.get_token_symbol()
    Outputquantity = CurrentOutput[1] * PC 
    oq = round((Outputquantity * (1 - (slippage/100))) / (10**TokenDecimals),5)
    print("Place Buy Order, for",str(quantity)+"BNB get Min", oq, Symbol)
    i = input("Place Order? y/n\n")
    if i == "y":
        Place = tx(token_address, quantity, Outputquantity, slippage)
        print(Place.placeOrderBNBToken()[1])
    else:
        print("OK, do nothing.")
    menu()



def CreateSellOrder():
    print("Ok, Lets Create a Sell LimitOrder")
    token_address = input("Input TokenAddress: ")
    quantity = float(input(f"Input Token amount: "))
    PriceChange = int(input("Input Price change in Percent: "))
    PC = 1 + (PriceChange/100)
    Outputquantity = 0
    slippage = int(input("Input Slippage: "))
    initBot = tx(token_address, quantity, Outputquantity, slippage)
    CurrentOutput = initBot.amountsOut_sell()
    Symbol = initBot.get_token_symbol()
    Outputquantity = CurrentOutput[1] * PC 
    oq = round((Outputquantity * (1 - (slippage/100))) / (10**18),5)
    print("Place SellOrder, for",quantity, str(Symbol)+"get Min", oq,"BNB")
    i = input("Place Order? y/n\n")
    if i == "y":
        Place = tx(token_address, quantity, Outputquantity, slippage)
        print(Place.placeOrderTokenBNB()[1])
    else:
        print("OK, do nothing.")
    menu()


def get_Orders():
    initBot = tx(token_address="0x34FaA80FEC0233e045eD4737cc152a71e490e2E3", quantity=0, Outputquantity=0, slippage=0)
    orders = initBot.SortOpenOrders()
    print(style().YELLOW + "OpenOrder:"+ style.RESET)
    for Order in orders:
        print(style().BLUE +"-------------------------------"+ style().RESET)
        print(style().YELLOW +"OrderID: "+ style().GREEN +str(Order[0])+ style().RESET)
        print(style().YELLOW +"TokenIn: "+ style().GREEN +str(Order[1])+ style().RESET)
        print(style().YELLOW +"TokenOut: "+ style().GREEN +str(Order[2])+ style().RESET)
        print(style().YELLOW +"AmountIn: "+ style().GREEN +str(Order[3] / (10**initBot.get_TokenDecimalsFromAddres(Order[1])))+ style().RESET)
        print(style().YELLOW +"TargetAmountOut: "+ style().GREEN +str(Order[4]/ (10**initBot.get_TokenDecimalsFromAddres(Order[2])))+ style().RESET)
        print(style().YELLOW +"MinAmountOut: "+ style().GREEN +str(Order[5]/ (10**initBot.get_TokenDecimalsFromAddres(Order[2])))+ style().RESET)
    print(style().YELLOW +"-------------------------------" + style().RESET)
    menu()


def deleteOrder():
    initBot = tx(token_address="0x34FaA80FEC0233e045eD4737cc152a71e490e2E3", quantity=0, Outputquantity=0, slippage=0)
    print("To delete Order, we need OrderID")
    i = int(input("Please Input OrderID: "))
    if isinstance(i, int) == True:
        delete = initBot.deleteLimitOrder(i)
        print(delete[1])
    else:
        print("Only input Numbers!")
    menu()
        

def menu():
    print("-------------------------------")
    print("TradingTigers LimitOrders test Menu")
    print("[1]-> Show Open Limit Orders")
    print("[2]-> Delete Limit Order")
    print("[3]-> Create BNB To Token Limit Order")
    print("[4]-> Create Token To BNB Limit Order")
    print("[5]-> Exit")
    i = int(input("Select your Option: "))
    if i == 1:
        get_Orders()
    elif i == 2:
        deleteOrder()
    elif i == 3:
        CreateBuyOrder()
    elif i == 4:
        CreateSellOrder()
    else:
        print("Wrong Input, Exit")

menu()