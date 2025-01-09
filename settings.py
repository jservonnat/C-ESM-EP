# -- Provide your e-mail if you want to receive an e-mail at the end of the execution of the jobs
#email = "stephane.senesi@ipsl.fr"
email = None

# Choose if you prefer one mail per C-ESM-EP run or one mail per C-ESM-EP component job
one_mail_per_component = False

# Which account / project will be charged for computing hours ?
# When C-ESM-EP is called by libIGCM, the account is set automatically
# Otherwise, if account is None,
#   - at TGCC, CCCHOME path will be used to deduce default account
#   - at IDRIS, default account is provided by command idrproj
account = None
# account = "psl@cpu"   # Example for IDRIS

# Should we publish the atlas to an http capable location such as
# thredds-su.ipsl.fr/thredds.   
publish = True
