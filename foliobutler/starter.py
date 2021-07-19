from foliobutler.fb_api import get_token, get_folio, get_folios
from dotenv import dotenv_values
import os, click, logging
from ib_insync import IBC, IB, Forex, util, Stock, Order


def connected_ib(config, api_ip, api_port):
	ib = IB()
	try:
		ib.connect(api_ip, api_port, clientId=1)
	except:
		IBC_commands = {}
		for c in config:
			if c.startswith('IBC_'):
				IBC_commands[c[4:]]=config[c]
		if 'gateway' in IBC_commands:
			IBC_commands['gateway'] = IBC_commands['gateway'].upper() == 'TRUE'
		if 'ibcIniPath' in config:
			IBC_commands['ibcIni'] = os.path.join(config['ibcIniPath'], str(api_port) + '.ini')
		logging.debug(IBC_commands)
		ibc = IBC(**IBC_commands)
		ibc.start()
		IB.sleep(60)
		ib.connect(api_ip, api_port, clientId=1)
	return ib


def sync(account, config, api_ip, api_port, fb_positions, fb_orders):
	logging.debug("----SYNC---- : {} {} {}".format(account, api_ip, api_port))
	logging.debug("FB Positions: {}".format(fb_positions))
	logging.debug("FB Orders: %s ", str(fb_orders))

	ib = connected_ib(config, api_ip, api_port)
	ib.reqAllOpenOrders()
	openTrades = ib.openTrades()
	logging.debug("IB OpenTrades: %s ", openTrades)
	portfolio = ib.positions(account=account)
	logging.debug("IB Portfolio: %s ", portfolio)
	
	current_ib_stocks = [x.contract.symbol + "_" + x.contract.secType + "_" + x.contract.currency
						 for x in portfolio if x.contract.currency == 'USD']
	current_ib_orders = [x.contract.symbol + "_" + x.contract.secType + "_" + x.contract.currency
						 for x in openTrades if x.order.account==account]
	current_fb_stocks = [x  for x in fb_positions.keys()]
	current_fb_orders = [x for x in fb_orders]

	for stock in set(current_ib_stocks + current_ib_orders + current_fb_stocks + current_fb_orders):
		symbol = stock.split("_")[0]
		type = stock.split("_")[1]
		currency = stock.split("_")[-1]
		
		fb_ist = fb_positions[stock]['amount'] if stock in fb_positions else 0
		fb_soll = fb_orders[stock]['amount'] if stock in fb_orders else 0
		ib_ist = 0
		ib_soll = 0

		for ib_stock in openTrades:
			if ib_stock.contract.symbol == symbol and\
			   ib_stock.contract.currency == currency and\
			   ib_stock.contract.secType == type and\
			   ib_stock.order.account == account:
				#order = ib_stock['order']
				#print(ib_stock)
				if ib_stock.orderStatus.status in ['PreSubmitted', 'Submitted']:
					if ib_stock.order.action == 'SELL':
						ib_soll = ib_soll - ib_stock.order.totalQuantity
					else:
						ib_soll = ib_soll + ib_stock.order.totalQuantity
					
				else:
					raise Exception("Unknown status: {}".format(ib_stock['orderState'].status))
		for ib_stock in portfolio:
			if ib_stock.contract.symbol == symbol and ib_stock.contract.currency == currency and ib_stock.contract.secType == type:
				ib_ist = ib_ist + ib_stock.position

		todo = ( fb_ist + fb_soll ) - (ib_ist + ib_soll)
		if todo != 0:
			logging.info("{} {} {} {} {} => {}".format(stock, fb_ist, fb_soll, ib_ist, ib_soll, todo))
		logging.info("{} {} {} {} {} => {}".format(stock, fb_ist, fb_soll, ib_ist, ib_soll, todo))
			
		if todo == fb_soll and todo != 0:
			logging.info(fb_orders[stock])
			contract = Stock(symbol, 'SMART', currency)
			contracts = ib.qualifyContracts(contract)
			order = Order(orderType=fb_orders[stock]['ordertype'],
						  action='BUY' if todo>0 else 'SELL',
						  totalQuantity=abs(todo),
						  tif=fb_orders[stock]['timeinforce']) 
			trade = ib.placeOrder(contract, order)
	
	ib.disconnect()



def in_sync_test(config, api_ip, api_port):
	from datetime import datetime
	logging.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
	ib = connected_ib(config, api_ip, api_port)

	
	contract = Forex('EURUSD')
	bars = ib.reqHistoricalData(
		contract, endDateTime='', durationStr='120 S',
		barSizeSetting='1 min', whatToShow='MIDPOINT', useRTH=True)
	
	# convert to pandas dataframe:
	df = util.df(bars)
	print(df)
	df.to_csv(os.path.join(config['ibcIniPath'], 'my_csv.csv'), mode='a', header=False)	


def env_path():
	return os.path.join(os.path.expanduser("~"),'Documents', 'foliobutler')

def env_location():
	return os.path.join(env_path(), '.env')


@click.command()
@click.option('--env', default=env_location(),
			  help='Location of Enviroment-file. Default {}'.format(env_location()))
@click.option('--action', default='sync', help='in_sync_test, sync')
@click.option('--ip', default='127.0.0.1', help='IP')
@click.option('--port', default=1707, help='Port')
def click_starter(env, action, ip, port):
	logging.basicConfig(level=logging.INFO)
	logging.getLogger("ib_insync.wrapper").disabled = True
	logging.getLogger("ib_insync.client").disabled = True
	logging.getLogger("ib_insync.ib").disabled = True
	logging.getLogger("urllib3.connectionpool").disabled = True

	if not os.path.exists(os.path.dirname(env)):
		logging.error("Enviroment Path not exists: {}".format(os.path.dirname(env)))
		if click.confirm('Do you want to create the folder?', default=True):
			os.mkdir(os.path.dirname(env))
	if not os.path.exists(env):
		email = input("Enter your Foliobutler Email: ")
		api = input("Enter your Foliobutler Api-Key: ")
		f = open(env, "a")
		f.write("EMAIL={}\nAPI_KEY={}\n".format(email, api))
		f.close()


	config = dotenv_values(env)
	print("config:", env)
	if action.lower() == "in_sync_test":
		return in_sync_test(config, port)
	token = get_token(config['EMAIL'], config['API_KEY'])
	folios = get_folios(token)
	for folioname in list(folios)[-3:]:
		f = folios[folioname]
		if f['ib_sync']:
			sync(f['ib_account'], config, f['ib_ip'], f['ib_port'], f['positions'], f['orders'])


if __name__ == "__main__":
	os.system('cls')
	#logging.basicConfig(filename='example.log', level=logging.INFO)
	#logging.getLogger().addHandler(logging.StreamHandler())
	logging.basicConfig(level=logging.INFO)
	logging.getLogger("ib_insync.wrapper").disabled = True
	logging.getLogger("ib_insync.client").disabled = True
	logging.getLogger("ib_insync.ib").disabled = True
	logging.getLogger("urllib3.connectionpool").disabled = True
	click_starter()