# foliobutler
Sync your Interactive Brokers account with your Folio in Foliobutler.\
I highly recommend to create a dedicated user with only rights to trade for each account/subaccount.\
\
\
To create the config for your FolioButler-Account, run foliobutler -action=init\
If you want to use multiple accounts, specify a different enviroment-file for each account.\
E.g. on unix/max:\
foliobutler -action=init -env=\~/.user1\
foliobutler -action=init -env=\~/.user2\
\
\
To add a config for [IBC](https://github.com/IbcAlpha/IBC), run foliobutler -action=add_account\
You can provide port, mode, user and pass in enviroment to run quiet.\
E.g. on unix/mac:\
port=4001 mode=live user=IB_Username pass=IB_Password foliobutler -action=add_account


