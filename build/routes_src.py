# -*- coding: utf-8 -*-
"""Per-country route model: passport tier x curriculum x country of residence.

Rule as always: a tier list is either from an official page with a URL and an
exact sentence, or it is not asserted. Where a country's split is the plain
EU/EEA free-movement line, the source is that country's own visa page.
"""

EU_EEA = ["Austria","Belgium","Bulgaria","Croatia","Cyprus","Czechia","Denmark","Estonia",
 "Finland","France","Germany","Greece","Hungary","Iceland","Ireland","Italy","Latvia",
 "Liechtenstein","Lithuania","Luxembourg","Malta","Netherlands","Norway","Poland","Portugal",
 "Romania","Slovakia","Slovenia","Spain","Sweden","Switzerland"]

# ICA, verified 14 September 2026
SG_VISA_REQUIRED = ["Afghanistan","Algeria","Armenia","Azerbaijan","Bangladesh","Belarus",
 "Egypt","Georgia","India","Iran","Iraq","Jordan","Kazakhstan","Kosovo","Kyrgyzstan","Lebanon",
 "Libya","Mali","Moldova","Morocco","Nigeria","Pakistan","Russia","Somalia","South Sudan",
 "Sudan","Syria","Tajikistan","Tunisia","Turkmenistan","Ukraine","Uzbekistan","Yemen"]

# ind.nl/en/mvv-exemptions, verified 14 September 2026
NL_MVV_EXEMPT = ["Australia","Canada","Japan","Monaco","New Zealand","South Korea",
 "United Kingdom","United States","Vatican City"]

# campusfrance.org FAQ, verified 14 September 2026 - keyed on RESIDENCE, not passport
EEF_COUNTRIES = ["Algeria","Angola","Argentina","Armenia","Azerbaijan","Bahrain","Benin",
 "Bolivia","Brazil","Burkina Faso","Burundi","Cambodia","Cameroon","Canada",
 "Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo",
 "Côte d'Ivoire","Democratic Republic of the Congo","Djibouti","Dominican Republic","Ecuador",
 "Egypt","Ethiopia","Gabon","Georgia","Ghana","Guinea","Haiti","Hong Kong","India","Indonesia",
 "Iran","Israel","Japan","Jordan","Kenya","Kuwait","Lebanon","Madagascar","Malaysia","Mali",
 "Mauritania","Mauritius","Mexico","Morocco","Nepal","Niger","Nigeria","Pakistan","Peru","Qatar",
 "Russia","Saudi Arabia","Senegal","Singapore","South Africa","South Korea","Taiwan","Thailand",
 "Togo","Tunisia","Turkey","Ukraine","United Kingdom","United Arab Emirates","United States",
 "Vietnam"]

# Germany's existing four tracks, already live and previously verified.
DE_B = ["Australia","Canada","Israel","Japan","New Zealand","South Korea","United Kingdom","United States"]
DE_C = ["China","India","Mongolia","Vietnam"]
DE_D = ["Algeria","Argentina","Bahrain","Bangladesh","Brazil","Colombia","Egypt","Ethiopia","Ghana",
 "Indonesia","Iraq","Jordan","Kazakhstan","Kenya","Kuwait","Lebanon","Malaysia","Mexico","Morocco",
 "Nepal","Nigeria","Oman","Pakistan","Philippines","Qatar","Saudi Arabia","South Africa","Sri Lanka",
 "Tanzania","Thailand","Tunisia","Turkey","Uganda","Ukraine","United Arab Emirates","Uzbekistan",
 "Other (non-EU)"]

BOARDS = [
 {"id":"cbse","name":"CBSE (India)","field":"cbse","indian":True},
 {"id":"isc","name":"ISC / CISCE (India)","field":"isc","indian":True},
 {"id":"state","name":"Indian state board","field":"cbse","indian":True},
 {"id":"ib","name":"IB Diploma","field":"ib","indian":False},
 {"id":"alevel","name":"A Level","field":"alevel","indian":False},
 {"id":"us","name":"US high school diploma","field":"us_diploma_gpa","indian":False},
]
