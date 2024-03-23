
import matplotlib.pyplot as plt


from skn.query import Query
from skn.CAN.fields.channels import *
from skn.CAN.tags.tags import *

Log_id_FSG = "CAN_2023-09-11(112931)"
Log_id_FSE = "CAN_2023-08-08(200608)"
Log_id_FSA = "CAN_2023-07-27(112806)"

FSG_query = Query().all_tags(Log_id(Log_id_FSG)).channels(AMS.STATEOFCHARGE, AMS.TSDATA, CCC.CURRENTMEASURE)
FSE_query = Query().all_tags(Log_id(Log_id_FSE)).channels(AMS.STATEOFCHARGE, AMS.TSDATA, CCC.CURRENTMEASURE)
FSA_query = Query().all_tags(Log_id(Log_id_FSA)).channels(AMS.STATEOFCHARGE, AMS.TSDATA, CCC.CURRENTMEASURE)

FSG_data = FSG_query.execute().to_dataframe().to_csv('FSG_data.csv')
FSE_data = FSE_query.execute().to_dataframe().to_csv('FSE_data.csv')
FSA_data = FSA_query.execute().to_dataframe().to_csv('FSA_data.csv')

print(FSG_data)