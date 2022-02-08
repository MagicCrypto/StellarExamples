#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from stellar_sdk import Asset, Server, Keypair, TransactionBuilder, Network, ChangeTrust, LiquidityPoolAsset, LiquidityPoolId


#TODO a list of secret keys, which should be stored into KeyStore
secret_list = [\
]

DEBUG = False

# We maybe need our 
server = Server(horizon_url="https://horizon.stellar.org")
#server = Server(horizon_url="https://horizon.stellar.lobstr.co")

base_fee= 100   # 100 stroops, equivalent to 0.00001 XLM
timeout = 30    # 30 seconds; otherwise, tx_too_late

# TODO Put your receving Stellar address here, i.e., public key
main_addr = ""

native_xlm = Asset.native()
cafe_token = Asset("CAFE", "GCANS5CZ2IR7VB7KI7AT5HDRH4A3FBC2JNLPLNE45EN6TIN3E2IFWRTN")
xlm1_token = Asset("XLM1", "GCBAVBXCY5V24GQNTOP5H46GGGNJ3UONB4G5CZC2NKOY2QAGL3HLHKW3")
cafex_token = Asset("CAFEX", "GD7H42JMSSAXXFU6O3HBKJGF2MMTSKFCNADM52XZNXB2SEY25YOEOW4E")
cafex_pool = LiquidityPoolAsset(native_xlm, xlm1_token)
cafex_pool_id = cafex_pool.liquidity_pool_id
xlm_eachtime  = 0.001   # 0.001
cafe_eachtime = 0       # 0 # 2.3 # Every two hours
failed_list = []

"""
The main function of this python file
"""
def group_send():
    for i in range(len(secret_list)):
        key_pair = Keypair.from_secret(secret_list[i])
        public_key = key_pair.public_key
        cur_account = server.load_account(public_key)
        print('\n%d:------%s------' % (i, public_key))
        if DEBUG:
            print(cur_account.raw_data)
    
        # Retrieve the balances
        balances = cur_account.raw_data['balances']
        print('Balances: %s' % balances)
        xlm_balance = -1
        cafe_balance = -1
        cafex_pool_balance = -1
        cafex_balance = -1
        xlm1_balance = -1
        for balance in balances:
            asset_type = balance['asset_type']
            if asset_type == 'native':
                xlm_balance = balance['balance']
            elif asset_type == 'credit_alphanum4':
                asset_code = balance['asset_code']
                if asset_code == 'CAFE':
                    cafe_balance = balance['balance']
                elif asset_code == 'XLM1':
                    xlm1_balance = balance['balance']
            elif asset_type == 'credit_alphanum12':
                asset_code = balance['asset_code']
                if asset_code == 'CAFEX':
                    cafex_balance = balance['balance']
            elif asset_type == 'liquidity_pool_shares':
                pool_id = balance['liquidity_pool_id']
                if pool_id == cafex_pool_id:
                    cafex_pool_balance = balance['balance']
        print('XLM: %s' % xlm_balance)
        print('CAFE: %s' % cafe_balance)
        print('CAFEX Pool: %s' % cafex_pool_balance)
        print('CAFEX: %s' % cafex_balance)
        print('XLM1: %s' % xlm1_balance)
        xlm_balance = float(xlm_balance)
        if DEBUG:
            print('xlm_balance: %s' % xlm_balance)
        xlm_balance = float(xlm_balance - 4.009)# TODO Minus reserve XLM
        if DEBUG:
            print('xlm_balance: %f' % xlm_balance)
        cafe_balance = float(cafe_balance)      # TODO 7.6460699 7.646070 
        if DEBUG:
            print('cafe_balance: %s' % cafe_balance)
        cafex_pool_balance = float(cafex_pool_balance)
        cafex_balance = float(cafex_balance)
        xlm1_balance = float(xlm1_balance)
        is_failed = False

        # Delete the CAFEX pool if it is 0
        is_cafex_pool = False
        if cafex_pool_balance == 0.0:
            print('Delete the CAFEX pool since it is %f...' % cafex_pool_balance)
            change_trust = ChangeTrust(asset=cafex_pool, limit="0")
            transaction = (
                TransactionBuilder(
                    source_account=cur_account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=base_fee,
                )
                .append_operation(change_trust)
                .set_timeout(timeout)
                .build()
            )
            transaction.sign(key_pair)
            try:
                response = server.submit_transaction(transaction)
                print(response)
                is_cafex_pool = False 
            except:
                print('Failed!!!!')
                is_failed = True
                is_cafex_pool = True
        else:
            is_cafex_pool = True

        # Delete CAFEX if it is 0 and no CAFEX pool
        if (not is_cafex_pool) and cafex_balance == 0.0:
            print('Delete CAFEX since it is %f........' % cafex_balance)
            change_trust = ChangeTrust(asset=cafex_token, limit="0")
            transaction = (
                TransactionBuilder(
                    source_account=cur_account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=base_fee,
                )
                .append_operation(change_trust)
                .set_timeout(timeout)
                .build()
            )
            transaction.sign(key_pair)
            try:
                response = server.submit_transaction(transaction)
                print(response)
            except:
                print('Failed!!!!')
                is_failed = True

        # Delete XLM1 if it is 0 and no CAFEX pool
        if (not is_cafex_pool) and xlm1_balance == 0.0:
            print('Delete XLM1 since it is %f........' % xlm1_balance)
            change_trust = ChangeTrust(asset=xlm1_token, limit="0")
            transaction = (
                TransactionBuilder(
                    source_account=cur_account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=base_fee,
                )
                .append_operation(change_trust)
                .set_timeout(timeout)
                .build()
            )
            transaction.sign(key_pair)
            try:
                response = server.submit_transaction(transaction)
                print(response)
            except:
                print('Failed!!!!')
                is_failed = True

        # Send all of CAFE 
        if cafe_balance > cafe_eachtime:
            print('Transfer CAFE: %s.......' % cafe_balance)
            transaction = (
                TransactionBuilder(
                    source_account=cur_account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=base_fee,
                )
                .append_payment_op(main_addr, cafe_token, '%s'%cafe_balance)#Do not %f if we want to sent it all
                .set_timeout(timeout)
                .build()
            )
            transaction.sign(key_pair)
            try:
                response = server.submit_transaction(transaction)
                print(response)
            except:
                print('Failed!!!!!')
                is_failed = True

        # Delete CAFE if it is 0  TODO could be removed in the future
        if (not is_cafex_pool) and cafe_balance == 0.0:
            print('Delete CAFE since it is %f........' % cafe_balance)
            change_trust = ChangeTrust(asset=cafe_token, limit="0")
            transaction = (
                TransactionBuilder(
                    source_account=cur_account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=base_fee,
                )
                .append_operation(change_trust)
                .set_timeout(timeout)
                .build()
            )
            transaction.sign(key_pair)
            try:
                response = server.submit_transaction(transaction)
                print(response)
            except:
                print('Failed!!!!')
                is_failed = True
    
        # Send the integer of XLM
        if xlm_balance > xlm_eachtime:
            print('Transfer XLM: %f..........' % xlm_balance)
            transaction = (
                TransactionBuilder(
                    source_account=cur_account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=base_fee,
                )
                .append_payment_op(main_addr, native_xlm, '%f'%xlm_balance)#Use %f to avoid 1.5009702000000003
                .set_timeout(timeout)
                .build()
            )
            transaction.sign(key_pair)
            try:
                response = server.submit_transaction(transaction)
                print(response)
            except:
                print('Failed!!!!')
                is_failed = True
    
        # Check failed or not
        if is_failed:
            failed_list.append(i)
        if DEBUG:
            exit()
    
    # Output final result
    print('\nfailed_list: %s' % failed_list)

    # Continue if there are failed ones
    if (len(failed_list) > 0):
        failed_list[:] = []
        group_send()

# Main
group_send()
